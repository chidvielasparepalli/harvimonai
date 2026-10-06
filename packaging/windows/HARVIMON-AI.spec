from pathlib import Path

root = Path(SPECPATH).parents[1]
payload = root / 'build' / 'standalone'
a = Analysis(
    [str(root / 'packaging/windows/launcher.py')],
    pathex=[], binaries=[],
    datas=[(str(payload / 'payload.zip'), '.'), (str(payload / 'release.json'), '.')],
    hiddenimports=[], hookspath=[], runtime_hooks=[], excludes=[], noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [],
    name='HARVIMON-AI', debug=False, strip=False, upx=False, console=False,
    icon=str(root / 'config/jarvis.ico'),
)
