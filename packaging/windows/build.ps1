param([string]$Python = 'python')
$ErrorActionPreference = 'Stop'
Set-Location (Resolve-Path (Join-Path $PSScriptRoot '../..'))
function Invoke-Checked([string]$Exe, [string[]]$Arguments) {
    & $Exe @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Command failed ($LASTEXITCODE): $Exe $Arguments" }
}
Invoke-Checked $Python @('-c', 'import sys,struct; assert sys.platform == "win32" and struct.calcsize("P")==8; assert sys.version_info[:3] == (3,11,9), "Use CPython 3.11.9 x64"')
Invoke-Checked $Python @('packaging/windows/prepare.py')
$runtime = Join-Path $pwd 'build/standalone/runtime/python.exe'
Invoke-Checked $runtime @('-m','ensurepip')
$lock = 'packaging/windows/requirements-lock.txt'
if (Test-Path $lock) {
    Invoke-Checked $runtime @('-m','pip','install','--extra-index-url','https://download.pytorch.org/whl/cpu','-r',$lock)
} else {
    Invoke-Checked $runtime @('-m','pip','install','torch','--index-url','https://download.pytorch.org/whl/cpu')
    Invoke-Checked $runtime @('-m','pip','install','-r','packaging/windows/requirements.in')
}
Invoke-Checked $runtime @('-m','pip','check')
& $runtime -m pip freeze --all | Set-Content $lock -Encoding utf8
Invoke-Checked $Python @('packaging/windows/stage_tools.py')
$env:PLAYWRIGHT_BROWSERS_PATH = Join-Path $pwd 'build/standalone/browsers'
Invoke-Checked $runtime @('-m','playwright','install','chromium')
Invoke-Checked $runtime @('-c','from openwakeword.utils import download_models; download_models(["hey_jarvis"])')
Invoke-Checked $Python @('packaging/windows/test_launcher.py')
Invoke-Checked $Python @('packaging/windows/pack.py')
Invoke-Checked $Python @('-m','venv','.venv-build')
$builder = Join-Path $pwd '.venv-build/Scripts/python.exe'
Invoke-Checked $builder @('-m','pip','install','pyinstaller==6.22.0')
Invoke-Checked $builder @('-m','PyInstaller','--noconfirm','packaging/windows/HARVIMON-AI.spec')
$hash = (Get-FileHash dist/HARVIMON-AI.exe -Algorithm SHA256).Hash.ToLowerInvariant()
"$hash  HARVIMON-AI.exe" | Set-Content dist/SHA256SUMS.txt -Encoding ascii
Write-Output 'Built dist/HARVIMON-AI.exe. Run validation before publishing.'
