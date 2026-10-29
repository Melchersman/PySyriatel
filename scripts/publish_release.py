"""Publish the tested distributions as a versioned GitHub release."""
import hashlib
import json
import os
from pathlib import Path
import tomllib
import urllib.error
import urllib.request

version=tomllib.loads(Path('pyproject.toml').read_text())['project']['version']
tag='v'+version
repository=os.environ['GITHUB_REPOSITORY']
headers={'Authorization':'Bearer '+os.environ['RELEASE_TOKEN'],'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'}
base='https://api.github.com/repos/'+repository


def request(url,data=None,content_type='application/json'):
    payload=json.dumps(data).encode() if isinstance(data,dict) else data
    req=urllib.request.Request(url,data=payload,headers={**headers,'Content-Type':content_type})
    with urllib.request.urlopen(req,timeout=60) as response:return json.load(response)


try:
    release=request(base+'/releases/tags/'+tag)
    print('RELEASE_EXISTS '+release['html_url'])
except urllib.error.HTTPError as error:
    if error.code!=404:raise
    notes=Path('CHANGELOG.md').read_text().split('## '+version,1)[1].strip()
    release=request(base+'/releases',{'tag_name':tag,'target_commitish':os.environ['GITHUB_SHA'],'name':'PySyriatel '+version,'body':notes+'\n\nInstall from PyPI: `pip install --upgrade PySyriatel`. API reference: https://api.melchersman.com/syr-cash/en/docs','draft':False,'prerelease':False})
    artifacts=sorted(Path('dist').glob('*'))
    Path('dist/SHA256SUMS').write_text(''.join(hashlib.sha256(path.read_bytes()).hexdigest()+'  '+path.name+'\n' for path in artifacts))
    for path in sorted(Path('dist').glob('*')):
        endpoint=release['upload_url'].split('{')[0]+'?name='+path.name
        request(endpoint,path.read_bytes(),'application/octet-stream')
    print('RELEASE_PUBLISHED '+release['html_url'])
