<#
    Q-SYS Plugin Encryptor - simple GUI wrapper around QSC's plugin_tool_release.exe

    What it does:
      - Finds (or lets you point to) plugin_tool_release.exe and remembers it.
      - Drag a .qplug onto the window (or Browse).
      - Auto-fills the output .qplugx path.
      - Hit Encrypt. Done.

    Underlying command this wraps:
      plugin_tool_release.exe encrypt  In.qplug  Out.qplugx

    Run it via the included Encrypt-Plugin-GUI.bat (recommended), or:
      powershell.exe -NoProfile -ExecutionPolicy Bypass -STA -File Q-SYS-Plugin-Encryptor.ps1
#>

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[System.Windows.Forms.Application]::EnableVisualStyles()

# ----- paths / config ----------------------------------------------------
$script:ScriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$script:ConfigPath = Join-Path $script:ScriptDir 'qplug-encryptor.config'
$script:ToolName   = 'plugin_tool_release.exe'

function Save-ToolPath([string]$p) {
    try { Set-Content -LiteralPath $script:ConfigPath -Value $p -Encoding UTF8 -ErrorAction Stop } catch {}
}
function Load-ToolPath {
    try {
        if (Test-Path -LiteralPath $script:ConfigPath) {
            $p = (Get-Content -LiteralPath $script:ConfigPath -ErrorAction Stop | Select-Object -First 1)
            if ($p -and (Test-Path -LiteralPath $p)) { return $p }
        }
    } catch {}
    return $null
}

# Fast, deterministic lookup (no slow recursive scan at startup).
function Find-Tool-Quick {
    $candidates = @(
        (Load-ToolPath),
        (Join-Path $script:ScriptDir $script:ToolName),
        (Join-Path $script:ScriptDir ('release\' + $script:ToolName)),
        (Join-Path (Split-Path -Parent $script:ScriptDir) $script:ToolName),
        (Join-Path (Split-Path -Parent $script:ScriptDir) ('release\' + $script:ToolName))
    )
    foreach ($c in $candidates) {
        if ($c -and (Test-Path -LiteralPath $c)) { return (Resolve-Path -LiteralPath $c).Path }
    }
    return $null
}

# Opt-in deeper search of the usual download/desktop spots (button-triggered).
function Find-Tool-Deep {
    $roots = @(
        [Environment]::GetFolderPath('Desktop'),
        [Environment]::GetFolderPath('UserProfile'),
        (Join-Path ([Environment]::GetFolderPath('UserProfile')) 'Downloads'),
        [Environment]::GetFolderPath('MyDocuments')
    ) | Where-Object { $_ -and (Test-Path -LiteralPath $_) } | Select-Object -Unique
    foreach ($r in $roots) {
        try {
            $hit = Get-ChildItem -LiteralPath $r -Filter $script:ToolName -Recurse -Depth 4 -File -ErrorAction SilentlyContinue |
                   Select-Object -First 1
            if ($hit) { return $hit.FullName }
        } catch {}
    }
    return $null
}

# ----- form --------------------------------------------------------------
$font = New-Object System.Drawing.Font('Segoe UI', 9.75)

$form = New-Object System.Windows.Forms.Form
$form.Text = 'Q-SYS Plugin Encryptor'
$form.Size = New-Object System.Drawing.Size(640, 560)
$form.StartPosition = 'CenterScreen'
$form.FormBorderStyle = 'FixedSingle'
$form.MaximizeBox = $false
$form.Font = $font
$form.BackColor = [System.Drawing.Color]::White
$form.AllowDrop = $true

$accent = [System.Drawing.Color]::FromArgb(0, 120, 215)
$okGreen = [System.Drawing.Color]::FromArgb(16, 124, 16)
$errRed  = [System.Drawing.Color]::FromArgb(196, 43, 28)

# Header
$header = New-Object System.Windows.Forms.Label
$header.Text = 'Q-SYS Plugin Encryptor'
$header.Font = New-Object System.Drawing.Font('Segoe UI', 15, [System.Drawing.FontStyle]::Bold)
$header.ForeColor = $accent
$header.AutoSize = $true
$header.Location = New-Object System.Drawing.Point(18, 14)
$form.Controls.Add($header)

# --- 1. Tool ---
$grpTool = New-Object System.Windows.Forms.GroupBox
$grpTool.Text = '1. Encryption tool'
$grpTool.Location = New-Object System.Drawing.Point(18, 52)
$grpTool.Size = New-Object System.Drawing.Size(600, 78)
$form.Controls.Add($grpTool)

$txtTool = New-Object System.Windows.Forms.TextBox
$txtTool.Location = New-Object System.Drawing.Point(14, 26)
$txtTool.Size = New-Object System.Drawing.Size(420, 24)
$txtTool.ReadOnly = $true
$txtTool.BackColor = [System.Drawing.Color]::FromArgb(245, 245, 245)
$grpTool.Controls.Add($txtTool)

$btnToolBrowse = New-Object System.Windows.Forms.Button
$btnToolBrowse.Text = 'Browse...'
$btnToolBrowse.Location = New-Object System.Drawing.Point(444, 25)
$btnToolBrowse.Size = New-Object System.Drawing.Size(70, 26)
$grpTool.Controls.Add($btnToolBrowse)

$btnToolFind = New-Object System.Windows.Forms.Button
$btnToolFind.Text = 'Auto-find'
$btnToolFind.Location = New-Object System.Drawing.Point(518, 25)
$btnToolFind.Size = New-Object System.Drawing.Size(70, 26)
$grpTool.Controls.Add($btnToolFind)

$lblTool = New-Object System.Windows.Forms.Label
$lblTool.Location = New-Object System.Drawing.Point(14, 53)
$lblTool.Size = New-Object System.Drawing.Size(570, 18)
$lblTool.Text = ''
$grpTool.Controls.Add($lblTool)

# --- 2. Drop zone ---
$drop = New-Object System.Windows.Forms.Panel
$drop.Location = New-Object System.Drawing.Point(18, 142)
$drop.Size = New-Object System.Drawing.Size(600, 96)
$drop.BorderStyle = 'FixedSingle'
$drop.BackColor = [System.Drawing.Color]::FromArgb(248, 250, 252)
$drop.AllowDrop = $true
$form.Controls.Add($drop)

$lblDrop = New-Object System.Windows.Forms.Label
$lblDrop.Text = "Drag your  .qplug  file here"
$lblDrop.Font = New-Object System.Drawing.Font('Segoe UI', 12)
$lblDrop.ForeColor = [System.Drawing.Color]::FromArgb(90, 90, 90)
$lblDrop.TextAlign = 'MiddleCenter'
$lblDrop.Dock = 'Top'
$lblDrop.Height = 44
$lblDrop.AllowDrop = $true
$drop.Controls.Add($lblDrop)

$btnInBrowse = New-Object System.Windows.Forms.Button
$btnInBrowse.Text = '...or Browse for a .qplug'
$btnInBrowse.Size = New-Object System.Drawing.Size(200, 28)
$btnInBrowse.Location = New-Object System.Drawing.Point(200, 52)
$drop.Controls.Add($btnInBrowse)

# --- input path display ---
$lblIn = New-Object System.Windows.Forms.Label
$lblIn.Text = 'Input:'
$lblIn.Location = New-Object System.Drawing.Point(18, 250)
$lblIn.Size = New-Object System.Drawing.Size(50, 22)
$form.Controls.Add($lblIn)

$txtIn = New-Object System.Windows.Forms.TextBox
$txtIn.Location = New-Object System.Drawing.Point(70, 247)
$txtIn.Size = New-Object System.Drawing.Size(548, 24)
$txtIn.ReadOnly = $true
$txtIn.BackColor = [System.Drawing.Color]::FromArgb(245, 245, 245)
$form.Controls.Add($txtIn)

# --- 3. output ---
$lblOut = New-Object System.Windows.Forms.Label
$lblOut.Text = 'Output:'
$lblOut.Location = New-Object System.Drawing.Point(18, 284)
$lblOut.Size = New-Object System.Drawing.Size(50, 22)
$form.Controls.Add($lblOut)

$txtOut = New-Object System.Windows.Forms.TextBox
$txtOut.Location = New-Object System.Drawing.Point(70, 281)
$txtOut.Size = New-Object System.Drawing.Size(470, 24)
$form.Controls.Add($txtOut)

$btnOutBrowse = New-Object System.Windows.Forms.Button
$btnOutBrowse.Text = 'Save as...'
$btnOutBrowse.Location = New-Object System.Drawing.Point(548, 280)
$btnOutBrowse.Size = New-Object System.Drawing.Size(70, 26)
$form.Controls.Add($btnOutBrowse)

# --- encrypt button ---
$btnGo = New-Object System.Windows.Forms.Button
$btnGo.Text = 'Encrypt  ->  .qplugx'
$btnGo.Location = New-Object System.Drawing.Point(18, 320)
$btnGo.Size = New-Object System.Drawing.Size(600, 44)
$btnGo.Font = New-Object System.Drawing.Font('Segoe UI', 12, [System.Drawing.FontStyle]::Bold)
$btnGo.BackColor = $accent
$btnGo.ForeColor = [System.Drawing.Color]::White
$btnGo.FlatStyle = 'Flat'
$btnGo.FlatAppearance.BorderSize = 0
$form.Controls.Add($btnGo)

# --- log ---
$txtLog = New-Object System.Windows.Forms.TextBox
$txtLog.Location = New-Object System.Drawing.Point(18, 376)
$txtLog.Size = New-Object System.Drawing.Size(600, 110)
$txtLog.Multiline = $true
$txtLog.ReadOnly = $true
$txtLog.ScrollBars = 'Vertical'
$txtLog.BackColor = [System.Drawing.Color]::FromArgb(30, 30, 30)
$txtLog.ForeColor = [System.Drawing.Color]::Gainsboro
$txtLog.Font = New-Object System.Drawing.Font('Consolas', 9)
$form.Controls.Add($txtLog)

# --- status line ---
$lblStatus = New-Object System.Windows.Forms.Label
$lblStatus.Location = New-Object System.Drawing.Point(18, 492)
$lblStatus.Size = New-Object System.Drawing.Size(600, 22)
$lblStatus.Text = 'Ready.'
$form.Controls.Add($lblStatus)

# ----- helpers -----------------------------------------------------------
function Log([string]$msg) {
    $txtLog.AppendText($msg + "`r`n")
}
function Set-Status([string]$msg, [System.Drawing.Color]$color) {
    $lblStatus.Text = $msg
    $lblStatus.ForeColor = $color
}

function Set-Tool([string]$path) {
    if ($path -and (Test-Path -LiteralPath $path)) {
        $script:Tool = (Resolve-Path -LiteralPath $path).Path
        $txtTool.Text = $script:Tool
        $lblTool.Text = '[OK] Tool found'
        $lblTool.ForeColor = $okGreen
        Save-ToolPath $script:Tool
    } else {
        $script:Tool = $null
        $txtTool.Text = ''
        $lblTool.Text = '[X] Tool not set - Browse, Auto-find, or drop plugin_tool_release.exe here'
        $lblTool.ForeColor = $errRed
    }
}

function Set-Input([string]$path) {
    if (-not ($path -and (Test-Path -LiteralPath $path))) { return }
    $full = (Resolve-Path -LiteralPath $path).Path
    $script:InFile = $full
    $txtIn.Text = $full
    $ext = [System.IO.Path]::GetExtension($full)
    if ($ext -ne '.qplug') {
        Set-Status "Note: '$ext' is not a .qplug - you can still encrypt it if you're sure." $errRed
    } else {
        Set-Status 'Input loaded.' $okGreen
    }
    # auto-derive output: same folder, same base name, .qplugx
    $dir  = [System.IO.Path]::GetDirectoryName($full)
    $base = [System.IO.Path]::GetFileNameWithoutExtension($full)
    $txtOut.Text = (Join-Path $dir ($base + '.qplugx'))
}

function Handle-Drop($data) {
    if (-not $data.GetDataPresent([System.Windows.Forms.DataFormats]::FileDrop)) { return }
    $files = $data.GetData([System.Windows.Forms.DataFormats]::FileDrop)
    foreach ($f in $files) {
        $ext = ([System.IO.Path]::GetExtension($f)).ToLower()
        if ($ext -eq '.exe')   { Set-Tool  $f; continue }
        if ($ext -eq '.qplugx'){ continue }   # already encrypted, ignore
        Set-Input $f                          # .qplug (or anything else) -> input
    }
}

function Invoke-Encrypt {
    $txtLog.Clear()
    if (-not ($script:Tool -and (Test-Path -LiteralPath $script:Tool))) {
        Set-Status 'No encryption tool selected.' $errRed; return
    }
    if (-not ($script:InFile -and (Test-Path -LiteralPath $script:InFile))) {
        Set-Status 'No input .qplug selected.' $errRed; return
    }
    $out = $txtOut.Text.Trim()
    if (-not $out) { Set-Status 'No output path.' $errRed; return }

    if (Test-Path -LiteralPath $out) {
        $r = [System.Windows.Forms.MessageBox]::Show(
            "Output already exists:`n$out`n`nOverwrite it?", 'Overwrite?',
            [System.Windows.Forms.MessageBoxButtons]::YesNo,
            [System.Windows.Forms.MessageBoxIcon]::Warning)
        if ($r -ne [System.Windows.Forms.DialogResult]::Yes) { Set-Status 'Cancelled.' $errRed; return }
        try { Remove-Item -LiteralPath $out -Force -ErrorAction Stop } catch {
            Set-Status "Couldn't remove existing output: $($_.Exception.Message)" $errRed; return
        }
    }

    Set-Status 'Encrypting...' $accent
    $btnGo.Enabled = $false
    $form.Refresh()

    $argStr = ('encrypt "{0}" "{1}"' -f $script:InFile, $out)
    Log "> `"$($script:Tool)`" $argStr"

    try {
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = $script:Tool
        $psi.Arguments = $argStr
        $psi.WorkingDirectory = [System.IO.Path]::GetDirectoryName($script:Tool)
        $psi.UseShellExecute = $false
        $psi.RedirectStandardOutput = $true
        $psi.RedirectStandardError = $true
        $psi.CreateNoWindow = $true
        $p = [System.Diagnostics.Process]::Start($psi)
        $so = $p.StandardOutput.ReadToEnd()
        $se = $p.StandardError.ReadToEnd()
        $p.WaitForExit()
        $code = $p.ExitCode

        if ($so) { Log $so.TrimEnd() }
        if ($se) { Log $se.TrimEnd() }
        Log "[exit code $code]"

        if (Test-Path -LiteralPath $out) {
            $sz = (Get-Item -LiteralPath $out).Length
            Set-Status "[OK] Encrypted: $out  ($sz bytes)" $okGreen
            Log "Wrote $out ($sz bytes)."
        } else {
            Set-Status "[X] Failed - no output file produced (exit code $code). See log." $errRed
        }
    } catch {
        Log "ERROR: $($_.Exception.Message)"
        Set-Status "[X] Error running tool: $($_.Exception.Message)" $errRed
    } finally {
        $btnGo.Enabled = $true
    }
}

# ----- wire events -------------------------------------------------------
$dragEnter = {
    param($s, $e)
    if ($e.Data.GetDataPresent([System.Windows.Forms.DataFormats]::FileDrop)) {
        $e.Effect = [System.Windows.Forms.DragDropEffects]::Copy
    }
}
$dragDrop = { param($s, $e) Handle-Drop $e.Data }

foreach ($ctl in @($form, $drop, $lblDrop)) {
    $ctl.Add_DragEnter($dragEnter)
    $ctl.Add_DragDrop($dragDrop)
}

$btnToolBrowse.Add_Click({
    $ofd = New-Object System.Windows.Forms.OpenFileDialog
    $ofd.Title = 'Locate plugin_tool_release.exe'
    $ofd.Filter = 'Encryption tool (plugin_tool_release.exe)|plugin_tool_release.exe|Executables (*.exe)|*.exe|All files (*.*)|*.*'
    if ($ofd.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) { Set-Tool $ofd.FileName }
})

$btnToolFind.Add_Click({
    Set-Status 'Searching common folders...' $accent; $form.Refresh()
    $hit = Find-Tool-Quick
    if (-not $hit) { $hit = Find-Tool-Deep }
    if ($hit) { Set-Tool $hit; Set-Status 'Tool found.' $okGreen }
    else { Set-Status 'Tool not found - use Browse to locate plugin_tool_release.exe.' $errRed }
})

$btnInBrowse.Add_Click({
    $ofd = New-Object System.Windows.Forms.OpenFileDialog
    $ofd.Title = 'Select a .qplug to encrypt'
    $ofd.Filter = 'Q-SYS plugin (*.qplug)|*.qplug|All files (*.*)|*.*'
    if ($ofd.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) { Set-Input $ofd.FileName }
})

$btnOutBrowse.Add_Click({
    $sfd = New-Object System.Windows.Forms.SaveFileDialog
    $sfd.Title = 'Save encrypted plugin as'
    $sfd.Filter = 'Encrypted Q-SYS plugin (*.qplugx)|*.qplugx|All files (*.*)|*.*'
    $sfd.DefaultExt = 'qplugx'
    if ($txtOut.Text) {
        $sfd.InitialDirectory = [System.IO.Path]::GetDirectoryName($txtOut.Text)
        $sfd.FileName = [System.IO.Path]::GetFileName($txtOut.Text)
    }
    if ($sfd.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) { $txtOut.Text = $sfd.FileName }
})

$btnGo.Add_Click({ Invoke-Encrypt })

# ----- startup -----------------------------------------------------------
$script:Tool = $null
$script:InFile = $null
$found = Find-Tool-Quick
if ($found) { Set-Tool $found } else { Set-Tool $null }

[void]$form.ShowDialog()
