$ErrorActionPreference = "Stop"

Set-Location -LiteralPath $PSScriptRoot

function Invoke-ProjectPython {
    param(
        [Parameter(Mandatory = $true)]
        [string[]] $PythonArgs
    )

    if (Get-Command python -ErrorAction SilentlyContinue) {
        & python @PythonArgs
        return
    }

    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3 @PythonArgs
        return
    }

    throw "Python was not found. Install Python 3.10 or newer, then run this script again."
}

function Build-App {
    param(
        [Parameter(Mandatory = $true)]
        [string] $EntryPoint,

        [Parameter(Mandatory = $true)]
        [string] $ExecutableName
    )

    Write-Host "Building $ExecutableName.exe from $EntryPoint..."
    Invoke-ProjectPython -PythonArgs @(
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--onefile",
        "--name",
        $ExecutableName,
        $EntryPoint
    )
}

Write-Host "Checking PyInstaller..."
Invoke-ProjectPython -PythonArgs @("-m", "PyInstaller", "--version")

Build-App -EntryPoint "main.py" -ExecutableName "SmartFileRenamer_EN"
Build-App -EntryPoint "main_es.py" -ExecutableName "RenombradorInteligente_ES"

Write-Host ""
Write-Host "Build complete. Executables:"
Write-Host "dist\SmartFileRenamer_EN.exe"
Write-Host "dist\RenombradorInteligente_ES.exe"
