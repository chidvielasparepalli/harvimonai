# Building HARVIMON-AI for Windows

Judges only download the EXE from GitHub Releases. These instructions are for maintainers.

Use Windows x64, CPython **3.11.9 x64**, internet access and at least 12 GB free disk space. From the repository run:

```powershell
.\packaging\windows\build.ps1 -Python 'C:\path\to\Python311\python.exe'
```

The script stages a private CPython runtime, installs the exact dependency lock, includes original application modules and resources, downloads pinned portable tools, bundles Chromium and wake-word resources, then uses the PyInstaller spec to create `dist/HARVIMON-AI.exe`. It generates `dist/SHA256SUMS.txt`. Keep build/dist/.venv-build out of Git. Build inputs and versions are pinned; EXE bytes may differ between rebuilds due to timestamps, so always checksum and test the actual release artifact.

The thin frozen launcher unpacks to `%LOCALAPPDATA%\CHIDVI-556`, then starts the **original** main.py with the private interpreter. Keeping a real interpreter preserves existing subprocess-based tools and file-based plugin imports. The UI is not rewritten. A single EXE download expands into its private runtime on first launch; persistent configuration/memory live in its app directory. First launch can take a few minutes and requires several GB of disk space.

## Validation

```powershell
$env:CHIDVI_HOME = Join-Path $env:TEMP ('harvimon-test-' + [guid]::NewGuid())
$p = Start-Process .\dist\HARVIMON-AI.exe -ArgumentList '--self-test' -PassThru
$p.WaitForExit()
Get-Content "$env:CHIDVI_HOME\test-report.json"
```

The self-test uses the actual bundled modules, QApplication/MainWindow, personalities, dialogs, memory implementation and assets. It writes screenshots and an explicit result. It does not claim cloud AI or physical microphone tests passed without credentials/hardware.

For clean validation, upload the exact EXE to a **draft** GitHub Release, dispatch `.github/workflows/test-release.yml` with its asset ID and SHA256, and require a passing report from a fresh Windows runner. No source checkout, project virtual environment or developer PATH is used. GitHub runners contain preinstalled software; module-path checks establish that Python dependencies are loaded exclusively from the private bundle.

Also launch normally on a Windows PC: use a private API key in the existing setup screen, verify Gemini chat, microphone capture, audio output, personality switching, all relevant dialogs and connected integrations. Never put test credentials in the build payload or GitHub workflow. Hardware/service-dependent features must be identified as unverified if unavailable.

Publish the release only after validation. Verify the uploaded asset's digest equals the tested local EXE's SHA256. Use GitHub Release assets, not Git commits, for the EXE. The official distribution repository is `chidvielasparepalli/harvimonai`.

## Dependency notices

The payload retains Python's license, installed packages' distribution metadata/license files, Qt license resources, Node's LICENSE, MinGit licenses, Android platform-tool NOTICE and barehands' license. Their respective license terms apply. The original application's source remains at its source repository; distribute corresponding source/license notices for components that require them. No private keys, personal memory, OAuth tokens or developer environment files are included.
