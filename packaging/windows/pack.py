"""Create an auditable payload for the PyInstaller one-file launcher."""
import hashlib
import json
import re
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[2]
STAGE = ROOT / 'build/standalone'
DENIED = {'long_term.json', 'token.json', 'credentials.json', 'client_secret.json'}


def pack():
    files = []
    for folder in ['app', 'runtime', 'browsers', 'tools']:
        for file in sorted((STAGE / folder).rglob('*')):
            if not file.is_file() or '__pycache__' in file.parts or file.suffix == '.pyc':
                continue
            relative = file.relative_to(STAGE).as_posix()
            if relative.startswith('app/'):
                if file.name in DENIED or file.name.startswith('.env') or '/certs/' in relative:
                    raise ValueError(f'Private file unexpectedly staged: {relative}')
                if file.suffix.lower() in {'.py', '.json', '.js', '.html', '.txt', '.md', '.pem'}:
                    text = file.read_text(encoding='utf-8', errors='ignore')
                    if re.search(r'AIza[0-9A-Za-z_-]{35}|gh[pousr]_[0-9A-Za-z]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----', text):
                        raise ValueError('Potential secret in staged file: ' + relative)
                if file.name == 'api_keys.json':
                    data = json.loads(file.read_text())
                    assert set(data) <= {'assistant_name', 'user_name', 'os_system'}, 'Secret/config contamination'
            files.append((file, relative))
    with zipfile.ZipFile(STAGE / 'payload.zip', 'w', zipfile.ZIP_DEFLATED, compresslevel=1) as archive:
        for file, relative in files:
            archive.write(file, relative)
    with (STAGE / 'payload.zip').open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    release = {'payload_sha256': digest, 'files': len(files), 'python': '3.11.9', 'architecture': 'Windows x64'}
    (STAGE / 'release.json').write_text(json.dumps(release, indent=2), encoding='utf-8')
    print(json.dumps(release))


if __name__ == '__main__':
    pack()
