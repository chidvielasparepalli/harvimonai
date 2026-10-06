"""Stage a private CPython installation and an explicit, secret-free app payload."""
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAGE = ROOT / 'build' / 'standalone'
RUNTIME = STAGE / 'runtime'
APP = STAGE / 'app'


def prepare():
    base = Path(sys.base_prefix)
    RUNTIME.mkdir(parents=True, exist_ok=True)
    for name in ['DLLs', 'Lib']:
        shutil.copytree(base / name, RUNTIME / name, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns('site-packages', '__pycache__', 'test', 'tests', 'idlelib'))
    for pattern in ['python*.exe', 'python*.dll', 'vcruntime*.dll', 'LICENSE*']:
        for file in base.glob(pattern):
            shutil.copy2(file, RUNTIME / file.name)
    # tkinter is part of the CPython runtime and some existing tools may use it.
    if (base / 'tcl').exists():
        shutil.copytree(base / 'tcl', RUNTIME / 'tcl', dirs_exist_ok=True)
    APP.mkdir(parents=True, exist_ok=True)
    for name in ['main.py', 'ui.py', 'personality_joystick.py']:
        shutil.copy2(ROOT / name, APP / name)
    for name in ['actions', 'core', 'Personality', 'plugins', 'memory', 'config', 'dashboard', 'blender_addon']:
        for source in (ROOT / name).rglob('*.py'):
            if source.name.startswith('test_'):
                continue
            target = APP / source.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    for name in ['assets', 'dashboard/static', 'barehands']:
        shutil.copytree(ROOT / name, APP / name, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns('__pycache__', '.git', '*.log', 'state',
                                                     'barehands.json', '.env', '.env.*'))
    for name in ['idle.mp4', 'started_talking.mp4', 'continuous_talking.mp4', 'jarvis.ico']:
        shutil.copy2(ROOT / 'config' / name, APP / 'config' / name)
    for name in ['face.png', 'config/home_scene.png']:
        if (ROOT / name).exists():
            shutil.copy2(ROOT / name, APP / name)
    shutil.copy2(ROOT / 'core/prompt.txt', APP / 'core/prompt.txt')
    for name in ['bootstrap.py', 'packaging_check.py']:
        shutil.copy2(Path(__file__).with_name(name), APP / name)
    # Explicit public defaults. Never copy or parse the developer's API-key file.
    defaults = {'assistant_name': 'CHIDVI-556', 'user_name': '', 'os_system': 'windows'}
    (APP / 'config/api_keys.json').write_text(json.dumps(defaults, indent=2), encoding='utf-8')
    manifest = {}
    for file in sorted(APP.rglob('*')):
        if file.is_file():
            manifest[file.relative_to(APP).as_posix()] = hashlib.sha256(file.read_bytes()).hexdigest()
    (STAGE / 'app-manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(f'Staged unchanged app and CPython {sys.version.split()[0]} at {STAGE}')


if __name__ == '__main__':
    prepare()

