<#
.SYNOPSIS
    Akinator installer for Windows - Claude Code, Codex and Cursor, from GitHub.

.DESCRIPTION
    Akinator is ONE skill with ONE command on every platform:
        Claude Code   /akinator:everything   plugin, always-on through its SessionStart hook
        Codex         $akinator              the skill + an always-on block in AGENTS.md
        Cursor        /akinator              the skill + an alwaysApply rule

    Codex and Cursor both read skills from ~\.agents\skills (or <repo>\.agents\skills),
    so one installed folder serves both.

    One line, no clone:
        irm https://raw.githubusercontent.com/ihabkhaled/akinator-ai/main/install.ps1 | iex
    With options:
        & ([scriptblock]::Create((irm https://raw.githubusercontent.com/ihabkhaled/akinator-ai/main/install.ps1))) -Repo C:\src\app

    Re-running updates in place. The installer only ever removes what it can
    recognise as its own: skill folders carrying the Akinator banner, the marked
    akinator:begin/akinator:end block, and its own rule file.

    Environment (mostly for testing): AKINATOR_SOURCE, AKINATOR_USER_HOME,
    CODEX_HOME, AKINATOR_CLAUDE_BIN ('none' to skip), AKINATOR_REPO_URL.

.PARAMETER Claude
    Install for Claude Code. With no platform switch, every detected platform is used.
.PARAMETER Codex
    Install for Codex.
.PARAMETER Cursor
    Install for Cursor.
.PARAMETER Repo
    Install into one repository instead of your user profile.
.PARAMETER Ref
    A branch or tag of the GitHub repository. Default: main.
.PARAMETER Uninstall
    Remove everything this installer put in place.
#>
[CmdletBinding()]
param(
    [switch]$Claude,
    [switch]$Codex,
    [switch]$Cursor,
    [string]$Repo,
    [string]$Ref = 'main',
    [switch]$Uninstall
)

$ErrorActionPreference = 'Stop'

$RepoUrl = if ($env:AKINATOR_REPO_URL) { $env:AKINATOR_REPO_URL } else { 'https://github.com/ihabkhaled/akinator-ai.git' }
$UserHome = if ($env:AKINATOR_USER_HOME) { $env:AKINATOR_USER_HOME } elseif ($env:USERPROFILE) { $env:USERPROFILE } else { $HOME }
$CodexDir = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $UserHome '.codex' }
$BeginMark = '<!-- akinator:begin'
$EndMark = '<!-- akinator:end -->'
$Utf8 = New-Object System.Text.UTF8Encoding($false)

function Say([string]$Text) { Write-Host $Text }
function Warn([string]$Text) { Write-Warning $Text }

function Write-Utf8([string]$Path, [string]$Text) {
    $dir = Split-Path -Parent $Path
    if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    [System.IO.File]::WriteAllText($Path, $Text, $Utf8)
}

function Read-Utf8([string]$Path) { [System.IO.File]::ReadAllText($Path, $Utf8) -replace "`r`n", "`n" }

# A user's file keeps its own line endings: edited in LF, written back as CRLF
# if it was CRLF. Otherwise installing Akinator rewrote every line ending of a
# Windows user's AGENTS.md, and uninstall could not restore it.
function Test-Crlf([string]$Path) {
    (Test-Path $Path) -and [System.IO.File]::ReadAllText($Path, $Utf8).Contains("`r`n")
}
function Write-Endings([string]$Path, [string]$Text, [bool]$Crlf) {
    if ($Crlf) { $Text = $Text -replace "`n", "`r`n" }
    Write-Utf8 $Path $Text
}

if ($Repo) {
    if (-not (Test-Path $Repo -PathType Container)) { throw "not a directory: $Repo" }
    $Repo = (Resolve-Path $Repo).Path
}

# --- the Claude CLI: on PATH, or the one bundled inside the VS Code extension ---

function Find-Claude {
    if ($env:AKINATOR_CLAUDE_BIN) {
        if ($env:AKINATOR_CLAUDE_BIN -eq 'none') { return $null }
        return $env:AKINATOR_CLAUDE_BIN
    }
    $cmd = Get-Command claude -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $ext = Join-Path $UserHome '.vscode\extensions'
    if (Test-Path $ext) {
        $bundled = Get-ChildItem $ext -Directory -Filter 'anthropic.claude-code-*' -ErrorAction SilentlyContinue |
            ForEach-Object { Join-Path $_.FullName 'resources\native-binary\claude.exe' } |
            Where-Object { Test-Path $_ } |
            Sort-Object { [version](($_ -split 'anthropic\.claude-code-')[1] -split '-')[0] } |
            Select-Object -Last 1
        if ($bundled) { return $bundled }
    }
    return $null
}

$ClaudeBin = Find-Claude

# --- which platforms --------------------------------------------------------

if (-not ($Claude -or $Codex -or $Cursor)) {
    if ($ClaudeBin) { $Claude = $true }
    if ((Get-Command codex -ErrorAction SilentlyContinue) -or (Test-Path $CodexDir)) { $Codex = $true }
    if ((Get-Command cursor -ErrorAction SilentlyContinue) -or (Test-Path (Join-Path $UserHome '.cursor'))) { $Cursor = $true }
    # A repository install is for whoever opens it next, with any tool.
    if ($Repo) { $Codex = $true; $Cursor = $true }
    if (-not ($Claude -or $Codex -or $Cursor)) {
        throw 'found none of Claude Code, Codex or Cursor. Name one: -Claude, -Codex or -Cursor.'
    }
}

# --- the source: this checkout, or a download --------------------------------

function Test-Checkout([string]$Dir) {
    (Test-Path (Join-Path $Dir 'skills\everything\SKILL.md')) -and
    (Test-Path (Join-Path $Dir '.agents\skills\akinator\SKILL.md'))
}

$LocalSource = $false
$Src = $null
if ($env:AKINATOR_SOURCE) {
    if (-not (Test-Checkout $env:AKINATOR_SOURCE)) { throw "AKINATOR_SOURCE is not an Akinator checkout: $($env:AKINATOR_SOURCE)" }
    $Src = (Resolve-Path $env:AKINATOR_SOURCE).Path; $LocalSource = $true
} elseif ($PSScriptRoot -and (Test-Checkout $PSScriptRoot)) {
    $Src = $PSScriptRoot; $LocalSource = $true
}

if (-not $Src -and -not $Uninstall -and ($Codex -or $Cursor)) {
    $Src = Join-Path $UserHome '.akinator\src'
    if (Get-Command git -ErrorAction SilentlyContinue) {
        if (Test-Path (Join-Path $Src '.git')) {
            Say "updating $Src"
            git -C $Src fetch --quiet --depth 1 origin $Ref; if ($LASTEXITCODE) { throw 'git fetch failed' }
            git -C $Src checkout --quiet --force FETCH_HEAD; if ($LASTEXITCODE) { throw 'git checkout failed' }
        } else {
            Say "downloading Akinator ($Ref) to $Src"
            if (Test-Path $Src) { Remove-Item -Recurse -Force $Src }
            git clone --quiet --depth 1 --branch $Ref $RepoUrl $Src; if ($LASTEXITCODE) { throw 'git clone failed' }
        }
    } else {
        Say "downloading Akinator ($Ref) to $Src"
        $zip = Join-Path ([System.IO.Path]::GetTempPath()) "akinator-$Ref.zip"
        $unpack = Join-Path ([System.IO.Path]::GetTempPath()) "akinator-$Ref"
        Invoke-WebRequest -UseBasicParsing -Uri "https://codeload.github.com/ihabkhaled/akinator-ai/zip/$Ref" -OutFile $zip
        if (Test-Path $unpack) { Remove-Item -Recurse -Force $unpack }
        Expand-Archive -Path $zip -DestinationPath $unpack
        $inner = Get-ChildItem $unpack -Directory | Select-Object -First 1
        if (Test-Path $Src) { Remove-Item -Recurse -Force $Src }
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Src) | Out-Null
        Move-Item $inner.FullName $Src
        Remove-Item -Force $zip; Remove-Item -Recurse -Force $unpack
    }
    if (-not (Test-Checkout $Src)) { throw "the download at $Src is not a complete Akinator checkout" }
}

# --- helpers ----------------------------------------------------------------

function Test-Ours([string]$Dir) {
    $skill = Join-Path $Dir 'SKILL.md'
    (Test-Path $skill) -and (Select-String -Path $skill -Pattern 'Akinator plugin|build_codex_pack\.py' -Quiet)
}

function Remove-OurSkills([string]$Root) {
    if (-not (Test-Path $Root)) { return }
    Get-ChildItem $Root -Directory | Where-Object { $_.Name -eq 'akinator' -or $_.Name -like 'akinator-*' } | ForEach-Object {
        if (Test-Ours $_.FullName) { Remove-Item -Recurse -Force $_.FullName; Say "removed $($_.FullName)" }
    }
}

function Remove-BlockText([string]$Text) {
    $pattern = '(?ms)^' + [regex]::Escape($BeginMark) + '.*?^' + [regex]::Escape($EndMark) + '[^\n]*\n?'
    [regex]::Replace($Text, $pattern, '')
}

function Write-Block([string]$File) {
    $contract = Read-Utf8 (Join-Path $Src '.agents\AGENTS.md')
    $body = $contract.Substring($contract.IndexOf("`n-->`n") + 5)
    $block = "$BeginMark - installed from the Akinator plugin; reinstall to update. Everything up to akinator:end is replaced on reinstall. -->`n" +
             $body.TrimEnd("`n") + "`n$EndMark`n"
    $crlf = Test-Crlf $File
    $existing = if (Test-Path $File) { Remove-BlockText (Read-Utf8 $File) } else { '' }
    $existing = $existing.TrimEnd("`n", ' ', "`t")
    $text = if ($existing) { "$existing`n`n$block" } else { $block }
    Write-Endings $File $text $crlf
    Say "wrote the Akinator block in $File"
    $override = Join-Path (Split-Path -Parent $File) 'AGENTS.override.md'
    # Codex reads AGENTS.override.md instead: globally when non-empty, in a
    # repository directory whenever it exists at all.
    if ((Test-Path $override) -and ($Repo -or (Get-Item $override).Length -gt 0)) {
        Warn "$override exists; Codex reads it INSTEAD of AGENTS.md there, so merge the block into it."
    }
}

function Remove-Block([string]$File) {
    if (-not (Test-Path $File)) { return }
    $crlf = Test-Crlf $File
    $text = Read-Utf8 $File
    if (-not $text.Contains($BeginMark)) { return }
    $rest = (Remove-BlockText $text).TrimEnd("`n", ' ', "`t")
    if ($rest) { Write-Endings $File "$rest`n" $crlf; Say "removed the Akinator block from $File" }
    else { Remove-Item -Force $File; Say "removed $File" }
}

# --- scope --------------------------------------------------------------------

if ($Repo) {
    $SkillsRoot = Join-Path $Repo '.agents\skills'
    $ContractFile = Join-Path $Repo 'AGENTS.md'
    $CursorRule = Join-Path $Repo '.cursor\rules\akinator.mdc'
    $ClaudeScope = 'project'
} else {
    $SkillsRoot = Join-Path $UserHome '.agents\skills'
    $ContractFile = Join-Path $CodexDir 'AGENTS.md'
    $CursorRule = Join-Path $UserHome '.cursor\rules\akinator.mdc'
    $ClaudeScope = 'user'
}

function Invoke-Claude([string[]]$Arguments) {
    if ($Repo) { Push-Location $Repo }
    # Output goes to the host, never down the pipeline - otherwise the caller's
    # "$code = Invoke-Claude ..." would capture claude's text along with the code.
    try { & $ClaudeBin @Arguments | Out-Host; return $LASTEXITCODE } finally { if ($Repo) { Pop-Location } }
}

# --- uninstall ----------------------------------------------------------------

if ($Uninstall) {
    if ($Claude -and $ClaudeBin) {
        $null = Invoke-Claude @('plugin', 'uninstall', 'akinator@akinator', '--scope', $ClaudeScope)
        Say "Claude Code: uninstalled akinator@akinator ($ClaudeScope scope)"
    }
    if ($Codex -or $Cursor) { Remove-OurSkills $SkillsRoot }
    if ($Codex) { Remove-Block $ContractFile }
    if ($Cursor -and (Test-Path $CursorRule) -and (Select-String -Path $CursorRule -Pattern 'Akinator plugin' -Quiet)) {
        Remove-Item -Force $CursorRule; Say "removed $CursorRule"
    }
    # Leave no empty directories this installer created.
    foreach ($dir in @($SkillsRoot, (Split-Path -Parent $SkillsRoot), (Split-Path -Parent $CursorRule), (Split-Path -Parent (Split-Path -Parent $CursorRule)))) {
        if ((Test-Path $dir) -and -not (Get-ChildItem -Force $dir)) { Remove-Item -Force $dir }
    }
    Say 'Akinator uninstalled.'
    return
}

# --- install: Claude Code -----------------------------------------------------

if ($Claude) {
    if (-not $ClaudeBin) {
        Warn "Claude Code CLI not found. In the VS Code extension: type /plugins, open Marketplaces, add $RepoUrl, then install Akinator."
    } else {
        $market = if ($LocalSource) { $Src } else { "$RepoUrl#$Ref" }
        # Adding a marketplace whose name already exists replaces its source.
        $code = Invoke-Claude @('plugin', 'marketplace', 'add', $market, '--scope', $ClaudeScope)
        if ($code) { throw "claude plugin marketplace add failed ($code)" }
        $null = Invoke-Claude @('plugin', 'install', 'akinator@akinator', '--scope', $ClaudeScope)
        $null = Invoke-Claude @('plugin', 'update', 'akinator@akinator', '--scope', $ClaudeScope) 2>$null
        Say "Claude Code: akinator@akinator installed ($ClaudeScope scope). Restart Claude, then /akinator:everything."
    }
}

# --- install: the one skill, for Codex and Cursor ---------------------------

if ($Codex -or $Cursor) {
    Remove-OurSkills $SkillsRoot
    New-Item -ItemType Directory -Force -Path $SkillsRoot | Out-Null
    Copy-Item -Recurse -Force (Join-Path $Src '.agents\skills\akinator') (Join-Path $SkillsRoot 'akinator')
    Get-ChildItem (Join-Path $SkillsRoot 'akinator') -Recurse -Directory -Filter '__pycache__' -ErrorAction SilentlyContinue |
        Remove-Item -Recurse -Force
    Say "installed the akinator skill to $(Join-Path $SkillsRoot 'akinator')"
}

if ($Codex) {
    Write-Block $ContractFile
    Say 'Codex: $akinator is the one entry point; the block makes it always on.'
}

if ($Cursor) {
    Write-Utf8 $CursorRule (Read-Utf8 (Join-Path $Src '.agents\cursor\akinator.mdc'))
    Say "wrote $CursorRule"
    Say 'Cursor: /akinator is the one entry point; the rule makes it always on.'
}

Say ''
Say 'Done. Re-run this installer to update; add -Uninstall to remove.'
