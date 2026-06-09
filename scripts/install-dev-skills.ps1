param(
  [string]$Dest = $(if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'skills' } else { Join-Path $env:USERPROFILE '.codex\skills' }),
  [switch]$IncludeRecommended,
  [switch]$IncludeMisc,
  [switch]$InstallCompoundEngineering,
  [switch]$UpdateCompoundEngineering,
  [switch]$CheckCompoundEngineering,
  [switch]$SkillsOnly,
  [switch]$CeOnly,
  [switch]$Force
)

$ErrorActionPreference = 'Stop'

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
$manifestPath = Join-Path $repoRoot 'skills.json'
$manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
$ceMarketplace = 'compound-engineering-plugin'
$ceMarketplaceSource = 'EveryInc/compound-engineering-plugin'
$cePlugin = 'compound-engineering'
$ceSelector = "$cePlugin@$ceMarketplace"
$ceUpstreamPluginJson = 'https://raw.githubusercontent.com/EveryInc/compound-engineering-plugin/main/plugins/compound-engineering/.codex-plugin/plugin.json'
$protectedRemoveNames = @($cePlugin, $ceMarketplace)

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

function Get-InstalledCompoundEngineering {
  if (-not (Get-Command codex -ErrorAction SilentlyContinue)) {
    return $null
  }

  try {
    $data = codex plugin list --json | ConvertFrom-Json
  } catch {
    $data = $null
  }

  if ($data -and $data.installed) {
    foreach ($plugin in $data.installed) {
      if (($plugin.name -eq $cePlugin) -or ($plugin.pluginId -eq $ceSelector)) {
        return $plugin
      }
    }
  }

  $cacheRoot = Join-Path $env:USERPROFILE ".codex\plugins\cache\$ceMarketplace\$cePlugin"
  if (-not (Test-Path $cacheRoot)) {
    return $null
  }

  $versionDir = Get-ChildItem -Path $cacheRoot -Directory |
    Sort-Object Name -Descending |
    Select-Object -First 1
  if (-not $versionDir) {
    return $null
  }

  $pluginJson = Join-Path $versionDir.FullName '.codex-plugin\plugin.json'
  if (-not (Test-Path $pluginJson)) {
    return $null
  }

  $pluginData = Get-Content $pluginJson -Raw | ConvertFrom-Json
  return [pscustomobject]@{
    pluginId = $ceSelector
    name = $cePlugin
    marketplaceName = $ceMarketplace
    version = $pluginData.version
    enabled = $null
  }
}

function Get-UpstreamCompoundEngineeringVersion {
  try {
    $data = Invoke-RestMethod -Uri $ceUpstreamPluginJson
    return [string]$data.version
  } catch {
    return $null
  }
}

function Write-CompoundEngineeringStatus {
  $installed = Get-InstalledCompoundEngineering
  $upstream = Get-UpstreamCompoundEngineeringVersion

  Write-Host ''
  Write-Host 'Compound Engineering status:'
  if ($installed) {
    Write-Host '- Installed: yes'
    Write-Host "- Plugin: $($installed.pluginId)"
    Write-Host "- Version: $($installed.version)"
    Write-Host "- Enabled: $(if ($null -ne $installed.enabled) { $installed.enabled } else { 'unknown' })"
  } else {
    Write-Host '- Installed: no'
  }
  Write-Host "- Upstream version: $(if ($upstream) { $upstream } else { 'unknown' })"

  if ($installed -and $installed.version -and $upstream) {
    if ([string]$installed.version -eq $upstream) {
      Write-Host '- Status: up to date'
    } else {
      Write-Host '- Status: update available'
    }
  } elseif (-not $upstream) {
    Write-Host '- Status: could not fetch upstream version'
  }
}

function Install-CompoundEngineering {
  param([switch]$Update)

  Write-Host ''
  if ($Update) {
    Write-Host 'Updating Compound Engineering external workflow...'
  } else {
    Write-Host 'Installing Compound Engineering external workflow...'
  }

  if (-not (Get-Command codex -ErrorAction SilentlyContinue)) {
    throw 'Required command not found: codex. Install Codex CLI first or run the Compound Engineering install manually.'
  }

  if (-not (Get-Command bunx -ErrorAction SilentlyContinue)) {
    throw 'Required command not found: bunx. Install Bun first or run the Compound Engineering install manually.'
  }

  if ($Update) {
    try {
      codex plugin marketplace upgrade $ceMarketplace
    } catch {
      Write-Host 'Marketplace upgrade failed; continuing with marketplace add/install.'
    }
  }

  codex plugin marketplace add $ceMarketplaceSource
  codex plugin add $ceSelector
  bunx -p @every-env/compound-plugin compound-plugin install compound-engineering --to codex

  Write-CompoundEngineeringStatus
  Write-Host ''
  Write-Host 'Compound Engineering marketplace, Codex plugin, and companion agents are installed. Restart Codex to apply plugin changes.'
}

$ceRequested = $InstallCompoundEngineering -or $UpdateCompoundEngineering -or $CheckCompoundEngineering
if ($SkillsOnly -and $CeOnly) {
  throw '-SkillsOnly and -CeOnly cannot be used together.'
}
if ($SkillsOnly -and $ceRequested) {
  throw '-SkillsOnly cannot be combined with Compound Engineering actions.'
}

$installSkills = -not $CeOnly
if ($ceRequested -and -not $Force) {
  $installSkills = $false
}

$results = @()

if ($installSkills) {
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
    if ($protectedRemoveNames -contains $name) {
      $results += [pscustomobject]@{ Skill = $name; Status = 'protected'; Destination = (Join-Path $Dest $name) }
      continue
    }

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
}

if ($CheckCompoundEngineering) {
  Write-CompoundEngineeringStatus
}

if ($UpdateCompoundEngineering) {
  Install-CompoundEngineering -Update
}

if ($InstallCompoundEngineering) {
  Install-CompoundEngineering
}
