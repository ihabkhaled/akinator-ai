<#
.SYNOPSIS
    Install the Akinator Codex pack.

.DESCRIPTION
    Codex reads skills from, in order of scope:
        $CWD\.agents\skills   (and every directory up to the repository root)
        $HOME\.agents\skills
        /etc/codex/skills     (not written by this script)

    This script copies the generated pack into one of those locations. The pack
    is generated from the canonical Claude skills; if it is missing or drifted,
    this script regenerates it first. See rules/07-codex-pack-is-generated.md.

.PARAMETER Scope
    'User' installs to $HOME\.agents\skills (default).
    'Repo' installs to <Repo>\.agents\skills.

.PARAMETER Repo
    Target repository path. Required when -Scope Repo.

.PARAMETER Force
    Overwrite an existing akinator skill directory.

.EXAMPLE
    .\scripts\install-codex.ps1
    .\scripts\install-codex.ps1 -Scope Repo -Repo C:\src\my-project -Force
#>

[CmdletBinding()]
param(
    [ValidateSet('User', 'Repo')]
    [string]$Scope = 'User',

    [string]$Repo,

    [switch]$Force
)

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$packRoot  = Split-Path -Parent $scriptDir

# --- ensure the pack is current -------------------------------------------

$python = $null
foreach ($candidate in @('python', 'python3', 'py')) {
    $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
    if ($null -ne $cmd) { $python = $cmd.Source; break }
}

if ($null -ne $python) {
    $builder = Join-Path $packRoot 'scripts\build_codex_pack.py'
    & $python $builder $packRoot --check | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host 'Codex pack is missing or drifted - regenerating from the canonical skills.'
        & $python $builder $packRoot --write
        if ($LASTEXITCODE -ne 0) { throw 'Failed to generate the Codex pack.' }
    }
} else {
    Write-Warning 'Python not found; installing the pack as-is without a drift check.'
}

$source = Join-Path $packRoot '.agents\skills'
if (-not (Test-Path $source)) {
    throw "No generated pack at $source, and Python was unavailable to build it."
}

# --- resolve the destination ----------------------------------------------

if ($Scope -eq 'Repo') {
    if ([string]::IsNullOrWhiteSpace($Repo)) { throw '-Repo is required when -Scope is Repo.' }
    if (-not (Test-Path $Repo -PathType Container)) { throw "Not a directory: $Repo" }
    $dest = Join-Path $Repo '.agents\skills'
} else {
    $dest = Join-Path $HOME '.agents\skills'
}

if (-not (Test-Path $dest)) {
    New-Item -ItemType Directory -Path $dest -Force | Out-Null
}

# --- copy ------------------------------------------------------------------

$installed = 0
foreach ($skillDir in Get-ChildItem -Path $source -Directory | Sort-Object Name) {
    $target = Join-Path $dest $skillDir.Name

    if ((Test-Path $target) -and (-not $Force)) {
        Write-Host ("skip    {0} (already present - use -Force to overwrite)" -f $skillDir.Name)
        continue
    }

    if (Test-Path $target) { Remove-Item -Recurse -Force $target }
    New-Item -ItemType Directory -Path $target -Force | Out-Null
    Copy-Item (Join-Path $skillDir.FullName 'SKILL.md') (Join-Path $target 'SKILL.md')
    Write-Host ("install {0}" -f $skillDir.Name)
    $installed++
}

# --- AGENTS.md for repo installs ------------------------------------------

if ($Scope -eq 'Repo') {
    $targetAgents = Join-Path $Repo 'AGENTS.md'
    if (Test-Path $targetAgents) {
        Write-Host ''
        Write-Host "$targetAgents already exists - not overwritten."
        Write-Host "Merge Akinator's contract into it by hand: $(Join-Path $packRoot 'AGENTS.md')"
        Write-Host 'Adopt, never impose: keep the repo''s own content and add the loop.'
    } else {
        Copy-Item (Join-Path $packRoot 'AGENTS.md') $targetAgents
        Write-Host 'install AGENTS.md'
    }
}

Write-Host ''
Write-Host "Installed $installed skill(s) to $dest"
Write-Host ''
Write-Host 'Codex will discover them automatically. Invoke one explicitly with'
Write-Host '$akinator, or describe your task and let Codex select from the'
Write-Host 'skill descriptions.'
