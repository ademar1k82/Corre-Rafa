$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$launcherPath = Join-Path $projectRoot "launch_game.vbs"
$iconPath = Join-Path $projectRoot "assets\toggle.ico"
$exePath = Join-Path $projectRoot "dist\CorreRafa.exe"
$wsh = New-Object -ComObject WScript.Shell
$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktopPath "Corre Rafa.lnk"

if (-not (Test-Path $iconPath)) {
    throw "Nao foi encontrado o icone obrigatorio: $iconPath"
}

$targetPath = $exePath
$resolvedIcon = "$exePath,0"

if (-not (Test-Path $exePath)) {
    # Fallback para desenvolvimento sem executável empacotado.
    $launcherContent = @"
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
projectRoot = fso.GetParentFolderName(WScript.ScriptFullName)
command = "cmd /c cd /d """ & projectRoot & """ && (pythonw game_logic.py || pyw -3 game_logic.py || py -3w game_logic.py)"
shell.Run command, 0, False
"@
    Set-Content -Path $launcherPath -Value $launcherContent -Encoding Ascii
    $targetPath = $launcherPath
    $resolvedIcon = "$iconPath,0"
}
elseif (Test-Path $launcherPath) {
    Remove-Item -Path $launcherPath -Force
}

# Recria o atalho para garantir que o Windows atualize o caminho do icone.
if (Test-Path $shortcutPath) {
    Remove-Item -Path $shortcutPath -Force
}

$shortcut = $wsh.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $targetPath
$shortcut.WorkingDirectory = $projectRoot
$shortcut.WindowStyle = 1
$shortcut.Description = "Abrir Corre Rafa"
$shortcut.IconLocation = $resolvedIcon
$shortcut.Save()

Write-Host "Atalho criado no Ambiente de Trabalho: $shortcutPath"
Write-Host "Destino usado: $($shortcut.TargetPath)"
Write-Host "Icone usado: $($shortcut.IconLocation)"



