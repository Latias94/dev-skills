param(
  [string]$Dest = $(if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'skills' } else { Join-Path $env:USERPROFILE '.codex\skills' }),
  [switch]$IncludeRecommended,
  [switch]$IncludeMisc,
  [switch]$Force
)

$ErrorActionPreference = 'Stop'

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
$manifestPath = Join-Path $repoRoot 'skills.json'
$manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json

New-Item -ItemType Directory -Path $Dest -Force | Out-Null

function Copy-Skill {
  param(
    [Parameter(Mandatory = $true)][string]$Name,
    [Parameter(Mandatory = $true)][string]$Source
  )

  $target = Join-Path $Dest $Name
  if (Test-Path $target) {
    if (-not $Force) {
      [pscustomobject]@{ Skill = $Name; Status = 'skipped existing'; Destination = $target }
      return
    }
    Remove-Item -LiteralPath $target -Recurse -Force
  }

  Copy-Item -Path $Source -Destination $target -Recurse
  [pscustomobject]@{ Skill = $Name; Status = 'installed'; Destination = $target }
}

function Find-LocalSkillPath {
  param(
    [Parameter(Mandatory = $true)][string]$Root,
    [Parameter(Mandatory = $true)][string]$Name
  )

  $matches = Get-ChildItem -Path (Join-Path $Root 'skills') -Directory -Recurse -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -eq $Name -and (Test-Path (Join-Path $_.FullName 'SKILL.md')) }

  $match = $matches | Select-Object -First 1
  if (-not $match) {
    throw "Could not find local skill '$Name' under $(Join-Path $Root 'skills')"
  }

  return $match.FullName
}

function Has-Property {
  param(
    [Parameter(Mandatory = $true)][object]$Object,
    [Parameter(Mandatory = $true)][string]$Name
  )

  return $Object.PSObject.Properties.Name -contains $Name
}

function Get-UniqueNames {
  param([object[]]$Names)

  $Names |
    Where-Object { $_ } |
    ForEach-Object { [string]$_ } |
    Select-Object -Unique
}

$results = @()

$localNames = @()
if (Has-Property -Object $manifest.local -Name 'core') {
  $localNames += $manifest.local.core
} else {
  $localNames += $manifest.local.required
  if ($IncludeRecommended -and $manifest.local.recommended) {
    $localNames += $manifest.local.recommended
  }
  if ($IncludeMisc -and $manifest.local.misc) {
    $localNames += $manifest.local.misc
  }
}
$localNames = Get-UniqueNames -Names $localNames

$desired = @{}
foreach ($name in $localNames) {
  $desired[$name] = $true
}

$removedNames = @()
if (Has-Property -Object $manifest.local -Name 'removed') {
  $removedNames += $manifest.local.removed
}
if ((Has-Property -Object $manifest -Name 'remove') -and (Has-Property -Object $manifest.remove -Name 'skills')) {
  $removedNames += $manifest.remove.skills
}
$removedNames = Get-UniqueNames -Names $removedNames | Where-Object { -not $desired.ContainsKey($_) }

foreach ($name in $removedNames) {
  $target = Join-Path $Dest $name
  if (Test-Path $target) {
    Remove-Item -LiteralPath $target -Recurse -Force
    $results += [pscustomobject]@{ Skill = $name; Status = 'removed obsolete'; Destination = $target }
  }
}

foreach ($name in $localNames) {
  $source = Find-LocalSkillPath -Root $repoRoot -Name $name
  if (-not (Test-Path (Join-Path $source 'SKILL.md'))) {
    throw "Local skill '$name' is missing at $source"
  }
  $results += Copy-Skill -Name $name -Source $source
}

$results | Sort-Object Skill | Format-Table -AutoSize
Write-Host ''
Write-Host 'Restart Codex to pick up newly installed or updated skills.'
