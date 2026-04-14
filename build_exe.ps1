$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$iconPath = Join-Path $projectRoot "assets\toggle.ico"
$assetsPath = Join-Path $projectRoot "assets"
$distPath = Join-Path $projectRoot "dist"
$buildPath = Join-Path $projectRoot "build"

$pythonCommand = $null
foreach ($candidate in @(
    @{ Name = "py"; Args = @("-3") },
    @{ Name = "python"; Args = @() }
)) {
    $command = Get-Command $candidate.Name -ErrorAction SilentlyContinue
    if ($command) {
        $pythonCommand = @{ Name = $command.Source; Args = $candidate.Args }
        break
    }
}

if ($null -eq $pythonCommand) {
    throw "Python nao foi encontrado no PATH."
}

if (-not (Test-Path $iconPath)) {
    throw "Nao foi encontrado o icone obrigatorio: $iconPath"
}

if (-not (Test-Path $assetsPath)) {
    throw "Nao foi encontrada a pasta de assets: $assetsPath"
}

& $pythonCommand.Name @($pythonCommand.Args + @("-m", "PyInstaller", "--version")) | Out-Null

if (Test-Path $buildPath) {
    Remove-Item -Path $buildPath -Recurse -Force
}

if (Test-Path $distPath) {
    Remove-Item -Path $distPath -Recurse -Force
}

$pyInstallerArgs = @(
    "-m", "PyInstaller",
    "--noconfirm",
    "--clean",
    "--onefile",
    "--windowed",
    "--name", "CorreRafa",
    "--specpath", $buildPath,
    "--icon", $iconPath,
    "--add-data", "$assetsPath;assets",
    "game_logic.py"
)

if (-not (Test-Path $buildPath)) {
    New-Item -Path $buildPath -ItemType Directory | Out-Null
}

Push-Location $projectRoot
try {
    & $pythonCommand.Name @($pythonCommand.Args + $pyInstallerArgs)
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller terminou com codigo de saida $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}

if (-not (Test-Path (Join-Path $distPath 'CorreRafa.exe'))) {
    throw "Build concluida sem gerar dist\\CorreRafa.exe"
}

Write-Host "Executavel atualizado em: $(Join-Path $distPath 'CorreRafa.exe')"
Write-Host "Spec temporario em: $(Join-Path $buildPath 'CorreRafa.spec')"
Write-Host "Icone embutido a partir de: $iconPath"
