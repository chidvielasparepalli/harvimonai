"""Single-file distribution launcher; all application code runs unchanged."""
import ctypes
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import traceback
import zipfile


def extract(archive, target):
    """Only extract ordinary relative files contained within the build payload."""
    with zipfile.ZipFile(archive) as bundle:
        for member in bundle.infolist():
            path = Path(member.filename)
            if path.is_absolute() or '..' in path.parts or ':' in member.filename:
                raise ValueError('Unsafe path in application payload')
        bundle.extractall(target)


def run():
    home = Path(os.environ.get('CHIDVI_HOME') or Path(os.environ['LOCALAPPDATA']) / 'CHIDVI-556')
    home.mkdir(parents=True, exist_ok=True)
    bundle = Path(getattr(sys, '_MEIPASS', Path(__file__).parent))
    release = json.loads((bundle / 'release.json').read_text(encoding='utf-8'))
    version = release['payload_sha256']
    cache = home / 'releases' / version[:16]
    payload = bundle / 'payload.zip'
    if not (cache / '.complete').exists():
        with payload.open('rb') as source:
            digest = hashlib.file_digest(source, 'sha256').hexdigest()
        if digest != version:
            raise ValueError('Application payload checksum failed. Download the EXE again.')
        cache.mkdir(parents=True, exist_ok=True)
        extract(payload, cache)
        (cache / '.complete').touch()
    app = home / 'app'
    if not (app / '.release').exists() or (app / '.release').read_text() != version:
        for source in (cache / 'app').rglob('*'):
            if not source.is_file():
                continue
            relative = source.relative_to(cache / 'app')
            target = app / relative
            # First-run API setup and user preferences persist between releases.
            if relative.as_posix() == 'config/api_keys.json' and target.exists():
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        (app / '.release').write_text(version)
    runtime = cache / 'runtime'
    env = os.environ.copy()
    for name in ['PYTHONPATH', 'PYTHONHOME', 'VIRTUAL_ENV', 'QT_PLUGIN_PATH', 'QT_QPA_PLATFORM_PLUGIN_PATH']:
        env.pop(name, None)
    env.update(CHIDVI_HOME=str(home), PYTHONHOME=str(runtime), PYTHONNOUSERSITE='1', PYTHONUTF8='1',
               PLAYWRIGHT_BROWSERS_PATH=str(cache / 'browsers'),
               PATH=os.pathsep.join([str(runtime), str(runtime / 'Scripts'),
                                     str(cache / 'tools/node'), str(cache / 'tools/adb'),
                                     str(cache / 'tools/git/cmd'), str(cache / 'tools/ffmpeg'),
                                     env.get('PATH', '')]))
    testing = '--self-test' in sys.argv
    args = [str(runtime / ('python.exe' if testing else 'pythonw.exe')), '-s', '-u', str(app / 'bootstrap.py')]
    if testing:
        args.append('--self-test')
    # External programs must load their own DLLs, not the PyInstaller launcher's.
    ctypes.windll.kernel32.SetDllDirectoryW(None)
    with (home / 'application.log').open('a', encoding='utf-8') as log:
        process = subprocess.Popen(args, cwd=app, env=env, stdout=log, stderr=log,
                                   creationflags=subprocess.CREATE_NO_WINDOW)
        code = process.wait()
        if code and not testing:
            raise RuntimeError(f'Application exited with code {code}. See {home / "application.log"}')
        return code


if __name__ == '__main__':
    kernel = ctypes.windll.kernel32
    kernel.CreateMutexW.restype = ctypes.c_void_p
    mutex = kernel.CreateMutexW(None, False, 'Local\\CHIDVI556Standalone')
    if kernel.GetLastError() == 183:
        raise SystemExit(0)
    try:
        raise SystemExit(run())
    except Exception:
        error = traceback.format_exc()
        ctypes.windll.user32.MessageBoxW(None, error, 'CHIDVI-556 startup error', 0x10)
        raise
