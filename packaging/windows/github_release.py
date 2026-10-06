"""Authenticated GitHub release operations; credentials never enter logs or files."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.request

REPO = 'chidvielasparepalli/harvimonai'
credential = subprocess.run(['C:/Program Files/Git/cmd/git.exe', 'credential', 'fill'],
    input='protocol=https\nhost=github.com\n\n', text=True, capture_output=True, check=True)
fields = dict(line.split('=', 1) for line in credential.stdout.splitlines() if '=' in line)
TOKEN = fields['password']

def api(path, method='GET', body=None):
    url = path if path.startswith('https://') else 'https://api.github.com/repos/' + REPO + path
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(url, data=data, method=method, headers={
        'Authorization': 'Bearer ' + TOKEN, 'Accept': 'application/vnd.github+json',
        'User-Agent': 'HARVIMON-AI-release', 'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.load(response)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['info', 'draft', 'upload', 'publish', 'runs', 'dispatch'])
    parser.add_argument('--file')
    parser.add_argument('--id')
    args = parser.parse_args()
    if args.command == 'info':
        info = api('')
        print(json.dumps({k: info.get(k) for k in ['full_name','default_branch','size','permissions']}, indent=2))
        print(json.dumps(api('/releases'), indent=2))
    elif args.command == 'draft':
        notes = Path(args.file).read_text(encoding='utf-8')
        release = api('/releases', 'POST', {'tag_name':'v1.0.0', 'target_commitish':'main',
            'name':'HARVIMON-AI v1.0.0', 'body':notes, 'draft':True})
        print(json.dumps({'id':release['id'], 'url':release['html_url']}))
    elif args.command == 'upload':
        import http.client
        from urllib.parse import quote
        file = Path(args.file)
        connection = http.client.HTTPSConnection('uploads.github.com', timeout=600)
        connection.putrequest('POST', f'/repos/{REPO}/releases/{args.id}/assets?name={quote(file.name)}')
        for key,value in {'Authorization':'Bearer '+TOKEN, 'Content-Type':'application/octet-stream',
                          'Content-Length':str(file.stat().st_size), 'User-Agent':'HARVIMON-AI-release'}.items():
            connection.putheader(key,value)
        connection.endheaders()
        with file.open('rb') as source:
            sent = 0
            while block := source.read(1024*1024):
                connection.send(block)
                sent += len(block)
                if sent % (64*1024*1024) == 0:
                    print(f'Uploaded {sent // (1024*1024)} MiB', flush=True)
        response = connection.getresponse()
        result = json.loads(response.read())
        assert response.status == 201, result
        print(json.dumps({k:result.get(k) for k in ['id','name','size','digest','browser_download_url']}))
    elif args.command == 'publish':
        print(api('/releases/'+args.id, 'PATCH', {'draft':False})['html_url'])
    elif args.command == 'runs':
        runs = api('/actions/runs?per_page=3')['workflow_runs']
        print(json.dumps([{k:r.get(k) for k in ['id','status','conclusion','html_url']} for r in runs], indent=2))
    elif args.command == 'dispatch':
        request = urllib.request.Request('https://api.github.com/repos/'+REPO+'/actions/workflows/test-release.yml/dispatches',
            data=json.dumps({'ref':'main','inputs':json.loads(Path(args.file).read_text())}).encode(),
            headers={'Authorization':'Bearer '+TOKEN,'User-Agent':'HARVIMON-AI-release','Content-Type':'application/json'})
        print(urllib.request.urlopen(request).status)
