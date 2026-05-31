param(
  [string]$Dest = $(if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'skills' } else { Join-Path $env:USERPROFILE '.codex\skills' }),
  [switch]$IncludeRecommended,
  [switch]$IncludeOptional,
  [switch]$IncludeMisc,
  [switch]$Force,
  [string]$MattPocockSkillsPath
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

function Find-UpstreamSkillPath {
  param(
    [Parameter(Mandatory = $true)][string]$Root,
    [Parameter(Mandatory = $true)][string]$Name
  )

  $matches = Get-ChildItem -Path (Join-Path $Root 'skills') -Directory -Recurse -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -eq $Name -and (Test-Path (Join-Path $_.FullName 'SKILL.md')) }

  $match = $matches | Select-Object -First 1
  if (-not $match) {
    throw "Could not find upstream skill '$Name' under $Root"
  }

  return $match.FullName
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

$results = @()

if ($manifest.local.removed) {
  foreach ($name in $manifest.local.removed) {
    $target = Join-Path $Dest $name
    if (Test-Path $target) {
      Remove-Item -LiteralPath $target -Recurse -Force
      $results += [pscustomobject]@{ Skill = $name; Status = 'removed deprecated'; Destination = $target }
    }
  }
}

$localNames = @()
$localNames += $manifest.local.required
if ($IncludeRecommended -and $manifest.local.recommended) {
  $localNames += $manifest.local.recommended
}
if ($IncludeMisc -and $manifest.local.misc) {
  $localNames += $manifest.local.misc
}
$localNames = $localNames | Select-Object -Unique

foreach ($name in $localNames) {
  $source = Find-LocalSkillPath -Root $repoRoot -Name $name
  if (-not (Test-Path (Join-Path $source 'SKILL.md'))) {
    throw "Local skill '$name' is missing at $source"
  }
  $results += Copy-Skill -Name $name -Source $source
}

$upstreamNames = @()
$upstreamNames += $manifest.upstream.required
if ($IncludeRecommended) {
  $upstreamNames += $manifest.upstream.recommended
}
if ($IncludeOptional) {
  $upstreamNames += $manifest.upstream.optional
}
$upstreamNames = $upstreamNames | Select-Object -Unique

if ($upstreamNames.Count -gt 0) {
  if (-not $MattPocockSkillsPath) {
    $candidate = Join-Path (Split-Path $repoRoot -Parent) 'skills'
    if (Test-Path (Join-Path $candidate 'skills')) {
      $MattPocockSkillsPath = $candidate
    }
  }

  $cleanup = $null
  if (-not $MattPocockSkillsPath) {
    $cleanup = Join-Path ([System.IO.Path]::GetTempPath()) ("mattpocock-skills-" + [System.Guid]::NewGuid().ToString('N'))
    git clone --depth 1 https://github.com/mattpocock/skills.git $cleanup | Out-Null
    $MattPocockSkillsPath = $cleanup
  }

  try {
    foreach ($name in $upstreamNames) {
      $source = Find-UpstreamSkillPath -Root $MattPocockSkillsPath -Name $name
      $results += Copy-Skill -Name $name -Source $source
    }
  } finally {
    if ($cleanup -and (Test-Path $cleanup)) {
      Remove-Item -LiteralPath $cleanup -Recurse -Force
    }
  }
}

$results | Sort-Object Skill | Format-Table -AutoSize
Write-Host ''
Write-Host 'Restart Codex to pick up newly installed or updated skills.'
