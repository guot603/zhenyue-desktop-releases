"""Copy checksum-bound native release assets into an existing public draft.

The one-run source URLs are short-lived object links, never repository tokens.
This script cannot publish a release or run downloaded programs.
"""
import hashlib,json,os,re,shutil,subprocess,urllib.parse,urllib.request
from pathlib import Path

REPO='guot603/zhenyue-desktop-releases'
raw=os.environ.pop('NATIVE_ASSET_TRANSPORT')
assert hashlib.sha256(raw.encode()).hexdigest()==os.environ['TRANSPORT_SHA256']
transport=json.loads(raw)
tag=transport['tag']
assert re.fullmatch(r'zhenyue-local-\d+\.\d+\.\d+-preview\.\d+',tag)
version=tag.removeprefix('zhenyue-local-')
assert transport['platform']=='windows' and re.fullmatch('[a-f0-9]{40}',transport['sourceCommit'])
root=Path('work');root.mkdir(exist_ok=False)
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
for asset in transport['assets']:
 name=asset['name'];assert re.fullmatch(r'[A-Za-z0-9_.-]+',name) and name not in ('.','..')
 assert re.fullmatch('[a-f0-9]{64}',asset['sha256']) and 0<asset['bytes']<2*1024**3
 u=urllib.parse.urlsplit(asset['url']);assert u.scheme=='https' and u.hostname=='release-assets.githubusercontent.com' and not u.username
 p=root/name;assert not p.exists()
 with urllib.request.urlopen(asset['url'],timeout=300) as source,p.open('xb') as target:
  assert urllib.parse.urlsplit(source.geturl()).hostname=='release-assets.githubusercontent.com'
  total=0
  while chunk:=source.read(8*1024*1024):
   total+=len(chunk);assert total<=asset['bytes'];target.write(chunk)
 assert p.stat().st_size==asset['bytes'] and sha(p)==asset['sha256'],name+' checksum mismatch'
manifest=json.loads((root/'windows-download-manifest.json').read_text())
assert manifest['name']==f'Zhenyue-{version}-windows-x64-offline-with-9B.zip'
assert manifest['baseUrl']==f'https://github.com/{REPO}/releases/download/{tag}/'
combined=hashlib.sha256();size=0
for i,part in enumerate(manifest['parts'],1):
 assert part['name']==manifest['name']+f'.part{i:02d}'
 p=root/part['name'];assert sha(p)==part['sha256'] and p.stat().st_size==part['bytes']
 with p.open('rb') as f:
  while chunk:=f.read(8*1024*1024):combined.update(chunk);size+=len(chunk)
assert combined.hexdigest()==manifest['sha256'] and size==manifest['bytes']
helper=manifest['helper'];assert sha(root/helper['name'])==helper['sha256']
install=json.loads((root/'windows-install-receipt.json').read_text(encoding='utf-8-sig'))
build=json.loads((root/'windows-build-receipt.json').read_text(encoding='utf-8-sig'))
assert install['nativeWindows'] and install['publisherMetadataVerified'] and install['windowTitle']
assert build['sourceCommit']==transport['sourceCommit']
trial_sources = {
 'customer-trial-20261012': ('0.2.3-preview.2', '1e55dfa4895eb270ac6da13964206e3d82ca04c6'),
 'customer-trial-20261014': ('0.2.4-preview.3', '7e3f1e74d14673e3cbc091b0aaf8bc662ada8458'),
}
if transport.get('admission') in trial_sources:
 # The product owner explicitly requested a public, manual Windows trial on
 # October 12. This admits integrity-checked installers, not model acceptance
 # or an automatic update. Unaccepted payloads cannot enter the normal lane.
 assert (version, transport['sourceCommit']) == trial_sources[transport['admission']]
 pending=json.loads((root/'WINDOWS-CUSTOMER-QA-PENDING.json').read_text())
 assert pending['status']=='customer-acceptance-required' and pending['publicReleaseAllowed'] is False
 assert pending['nativeInstallVerified'] and pending['modelTaskPassed'] is False and pending['accountLoginTested'] is False
 assert not list(root.glob('*-application-update.exe'))
 assert not (root/'windows-model-receipt.json').exists() and not (root/'windows-update-receipt.json').exists()
 for p in root.iterdir():
  if p.name!='WINDOWS-CUSTOMER-QA-PENDING.json':assert pending['sha256'][p.name]==sha(p)
 (root/'WINDOWS-PUBLIC-TRIAL-STATUS.json').write_text(json.dumps({'status':'public-manual-trial', 'nativeInstallVerified':True,
  'modelTaskAccepted':False,'customerAccountTested':False,'automaticUpdateAllowed':False,
  'reason':'Native installation was verified, but the hosted model task was not accepted. Product owner requested public manual trial on customer Windows hardware; no automatic update is admitted.',
  'sourceCommit':transport['sourceCommit']},indent=2))
else:
 assert transport.get('admission','verified')=='verified'
 model=json.loads((root/'windows-model-receipt.json').read_text())
 update=json.loads((root/'windows-update-receipt.json').read_text())
 assert model['nativeWindows'] and model['sourceReceiptVerified'] and model['aiLabelVerified'] and not model['cloudUsed']
 assert update['nativeWindows'] and update['cachedModelReused'] and update['installedUpdate'] and update['localModelLoaded']
 assert len(list(root.glob('*-application-update.exe')))==1
releases=json.loads(subprocess.check_output(['gh','api',f'repos/{REPO}/releases?per_page=100']))
release,=[r for r in releases if r['tag_name']==tag];assert release['draft']
existing={a['name']:a for a in release['assets']}
for p in sorted(root.iterdir()):
 # Keep the private build gate as verification input. The public status file
 # states the owner's manual-trial exception without implying model acceptance.
 if p.name=='WINDOWS-CUSTOMER-QA-PENDING.json':continue
 if p.name in existing:
  assert existing[p.name]['size']==p.stat().st_size and existing[p.name]['digest']=='sha256:'+sha(p)
 else:subprocess.run(['gh','release','upload',tag,'--repo',REPO,str(p)],check=True)
print(json.dumps({'status':'integrity-checked-and-staged','acceptance':transport.get('admission','verified'),'published':False,'tag':tag,'bytes':size,'sha256':manifest['sha256'],'assets':len(transport['assets'])}))
