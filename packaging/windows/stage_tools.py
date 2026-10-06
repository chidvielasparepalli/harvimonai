"""Stage redistributable command-line tools; save exact download hashes."""
import hashlib
import json
from pathlib import Path
import shutil
import socket
socket.setdefaulttimeout(60)
import urllib.request
import zipfile
ROOT = Path(__file__).resolve().parents[2]
STAGE = ROOT / 'build/standalone'
TOOLS = STAGE / 'tools'
DOWNLOADS = ROOT / 'build/downloads'
DOWNLOADS.mkdir(parents=True, exist_ok=True)
lockfile = Path(__file__).with_name('tools-lock.json')
lock = json.loads(lockfile.read_text()) if lockfile.exists() else {}

def download(name, url):
    entry = lock.get(name, {'url': url})
    file = DOWNLOADS / name
    if not file.exists() or not zipfile.is_zipfile(file):
        partial = file.with_suffix('.partial')
        urllib.request.urlretrieve(entry['url'], partial)
        partial.replace(file)
    digest = hashlib.sha256(file.read_bytes()).hexdigest()
    if entry.get('sha256') and entry['sha256'] != digest:
        raise ValueError('Tool checksum mismatch: ' + name)
    lock[name] = {'url':entry['url'], 'sha256':digest}
    lockfile.write_text(json.dumps(lock, indent=2))
    return file

node = download('node.zip', 'https://nodejs.org/dist/v22.23.3/node-v22.23.3-win-x64.zip')
with zipfile.ZipFile(node) as archive:
    for member in archive.infolist():
        parts = Path(member.filename).parts[1:]
        if not parts or member.is_dir(): continue
        target = TOOLS / 'node' / Path(*parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(archive.read(member))
print('Node staged', flush=True)
if 'git.zip' in lock:
    giturl = lock['git.zip']['url']
else:
    request = urllib.request.Request('https://api.github.com/repos/git-for-windows/git/releases/latest', headers={'User-Agent':'HARVIMON-build'})
    release = json.load(urllib.request.urlopen(request))
    giturl = next(a['browser_download_url'] for a in release['assets'] if a['name'].startswith('MinGit-') and a['name'].endswith('-64-bit.zip') and 'busybox' not in a['name'])
with zipfile.ZipFile(download('git.zip', giturl)) as archive:
    archive.extractall(TOOLS / 'git')
print('MinGit staged', flush=True)
# Google's platform tools include their own notices and no user credentials.
adb = download('adb.zip', 'https://dl.google.com/android/repository/platform-tools-latest-windows.zip')
with zipfile.ZipFile(adb) as archive:
    for member in archive.infolist():
        parts = Path(member.filename).parts[1:]
        if not parts or member.is_dir(): continue
        target = TOOLS / 'adb' / Path(*parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(archive.read(member))
print('ADB staged', flush=True)

ffmpeg = download('ffmpeg.zip', 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip')
with zipfile.ZipFile(ffmpeg) as archive:
    for member in archive.infolist():
        parts = Path(member.filename).parts[1:]
        if not parts or member.is_dir(): continue
        relative = Path(*parts)
        if relative.parts[0] == 'bin': relative = Path(*relative.parts[1:])
        target = TOOLS / 'ffmpeg' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(archive.read(member))
print('FFmpeg and ffprobe staged', flush=True)
