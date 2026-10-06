"""Private-runtime entry point; the real desktop application remains unchanged."""
import os
from pathlib import Path
import runpy
import sys

APP = Path(__file__).resolve().parent
os.chdir(APP)
sys.path.insert(0, str(APP))
if len(sys.argv) > 1 and sys.argv[1] == '--self-test':
    runpy.run_path(str(APP / 'packaging_check.py'), run_name='__main__')
else:
    sys.argv = [str(APP / 'main.py')]
    runpy.run_path(str(APP / 'main.py'), run_name='__main__')
