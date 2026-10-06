"""Exercise the real packaged UI and file-discovered extensions without credentials."""
import importlib
import json
import os
from pathlib import Path
import sys
import subprocess
import traceback

HOME = Path(os.environ['CHIDVI_HOME'])
APP = Path(__file__).parent
report = {'passed': False, 'python': sys.executable, 'checks': [], 'limitations': [
    'Cloud AI and live voice require a user API key, network and audio hardware.',
    'External-device integrations require their target device/application.']}

def check(name, condition=True):
    assert condition, name
    report['checks'].append(name)

def run():
    check('private Python runtime', Path(sys.executable).is_relative_to(HOME))
    for name in ['PyQt6.QtWidgets', 'PyQt6.QtMultimedia', 'PyQt6.QtWebEngineWidgets',
                 'sounddevice', 'soundfile', 'numpy', 'google.genai', 'cv2', 'mss',
                 'pyautogui', 'win32api', 'pythoncom', 'pycaw.pycaw', 'cryptography',
                 'playwright.sync_api', 'fastapi', 'torch', 'faster_whisper',
                 'vosk', 'edge_tts', 'kokoro', 'openwakeword', 'docx', 'pptx',
                 'openpyxl', 'pdfplumber', 'pandas', 'ddgs']:
        module = importlib.import_module(name)
        check('import ' + name, Path(module.__file__).is_relative_to(HOME))
    import main
    check('main runtime imports')
    from core.action_loader import discover_actions
    from core.plugin_loader import discover_plugins
    from Personality.loader import discover_personalities
    actions = discover_actions(APP / 'actions')
    plugins = discover_plugins(APP / 'plugins', set())
    report['actions'] = sorted(actions.names())
    report['plugins'] = plugins.list_for_ui()
    report['source_rejections'] = [r.error for r in actions._all_records if not r.valid]
    check('18 existing actions discovered', len(actions.names()) == 18)
    check('7 existing plugins discovered', len([r for r in plugins.list_for_ui() if r['valid']]) == 7)
    personas = discover_personalities()
    check('10 personalities discovered', len(personas) == 10)
    from PyQt6.QtTest import QTest
    from PyQt6.QtWidgets import QLineEdit
    from ui import JarvisUI
    ui = JarvisUI(str(APP / 'face.png'))
    ui.get_plugins = plugins.list_for_ui
    ui.get_plugin_settings = plugins.settings_schemas
    QTest.qWait(3000)
    check('main window visible', ui._win.isVisible())
    check('first-run setup', ui._win._overlay is not None and ui._win._overlay.isVisible())
    check('UI screenshot saved', ui._win.grab().save(str(HOME / 'first-run.png')))
    for name in ['idle.mp4', 'started_talking.mp4', 'continuous_talking.mp4', 'jarvis.ico']:
        check('asset ' + name, (APP / 'config' / name).stat().st_size > 1000)
    ui._win._overlay.hide()
    QTest.keyClicks(ui._win._input, 'packaged keyboard check')
    check('keyboard input', ui._win._input.text() == 'packaged keyboard check')
    ui._win._input.clear()
    from PyQt6.QtMultimedia import QMediaPlayer
    players = ui._win.findChildren(QMediaPlayer)
    check('three avatar animations loaded', len(players) >= 3 and all(p.error() == QMediaPlayer.Error.NoError for p in players))
    check('video frame rendered', any(p.videoSink() and p.videoSink().videoFrame().isValid() for p in players))
    for persona in personas:
        ui.set_personality_state(persona)
        QTest.qWait(100)
        check('personality ' + persona, ui._win._personality_joystick._current_id == persona)
    check('personality rendering')
    for method, attribute in [('_open_audio_devices', '_audio_overlay'),
                              ('_open_memory_panel', '_memory_overlay'),
                              ('_open_customize', '_customize_overlay'),
                              ('_open_plugin_manager', '_plugin_manager_overlay'),
                              ('_open_plugin_settings', '_plugin_settings_overlay')]:
        getattr(ui._win, method)()
        QTest.qWait(150)
        overlay = getattr(ui._win, attribute)
        check(method, overlay.isVisible())
        overlay.hide()
    from memory import memory_manager as memory
    original = memory.MEMORY_PATH
    memory.MEMORY_PATH = HOME / 'memory-test.json'
    try:
        sample = memory.load_memory()
        sample['notes']['packaging'] = {'value': 'persistent memory test'}
        memory.save_memory(sample)
        check('memory reload', memory.load_memory()['notes']['packaging']['value'] == 'persistent memory test')
    finally:
        memory.MEMORY_PATH = original
    check('no external site-packages', all('site-packages' not in p or Path(p).is_relative_to(HOME) for p in sys.path))
    check('main UI screenshot saved', ui._win.grab().save(str(HOME / 'main-window.png')))
    tools = Path(sys.executable).parent.parent / 'tools'
    for tool, argument in [('node/node.exe', '--version'), ('git/cmd/git.exe', '--version'),
                           ('adb/adb.exe', 'version'), ('ffmpeg/ffmpeg.exe', '-version'),
                           ('ffmpeg/ffprobe.exe', '-version')]:
        result = subprocess.run([str(tools / tool), argument], capture_output=True, timeout=30)
        check('portable tool ' + tool, result.returncode == 0)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content('<title>HARVIMON packaged browser test</title>')
        check('bundled browser automation', page.title() == 'HARVIMON packaged browser test')
        browser.close()
    report['passed'] = True

try:
    run()
except BaseException:
    report['error'] = traceback.format_exc()
finally:
    (HOME / 'test-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2), flush=True)
    os._exit(0 if report['passed'] else 1)
