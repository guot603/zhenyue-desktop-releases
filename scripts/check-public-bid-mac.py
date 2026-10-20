"""Read every public Mac byte anonymously; never execute downloaded code."""
import hashlib,json,os,re,urllib.request
from pathlib import Path
tag=os.environ.get('RELEASE_TAG','zhenyue-bid-local-0.10.0-preview.6')
assert re.fullmatch(r'zhenyue-bid-local-0\.10\.0-preview\.[1-9][0-9]*',tag)
version=tag.removeprefix('zhenyue-bid-local-')
base=f'https://github.com/guot603/zhenyue-desktop-releases/releases/download/{tag}/'
pin=os.environ['EXPECTED_MANIFEST_SHA256'];assert re.fullmatch('[a-f0-9]{64}',pin)
with urllib.request.urlopen(base+'macos-download-manifest.json',timeout=120) as response:raw=response.read(1024*1024)
assert hashlib.sha256(raw).hexdigest()==pin
m=json.loads(raw);assert m['baseUrl']==base and m['name']==f'ZhenyueBid-{version}-mac-arm64-offline.dmg'
combined=hashlib.sha256();total=0
for i,part in enumerate(m['parts'],1):
 assert part['name']==m['name']+f'.part{i:02d}'
 digest=hashlib.sha256();size=0
 with urllib.request.urlopen(base+part['name'],timeout=300) as response:
  while chunk:=response.read(8*1024*1024):
   digest.update(chunk);combined.update(chunk);size+=len(chunk)
 assert digest.hexdigest()==part['sha256'] and size==part['bytes']
 total+=size;print('PUBLIC_PART_OK',part['name'],size,flush=True)
assert combined.hexdigest()==m['sha256'] and total==m['bytes']
helper=m['helper'];assert helper['name'] in ('ZhenyueBid-macOS-Download.zip',f'ZhenyueBid-{version}-macOS-Download.zip') and helper['bytes']<1024*1024
with urllib.request.urlopen(base+helper['name'],timeout=120) as response:data=response.read(1024*1024)
assert len(data)==helper['bytes'] and hashlib.sha256(data).hexdigest()==helper['sha256']
receipt={'status':'passed','tag':tag,'anonymousPublicDownload':True,'allPartsVerified':len(m['parts']),'bytes':total,'sha256':m['sha256'],'manifestSha256':pin,'helperSha256':helper['sha256'],'nativeInstallationTestedByThisJob':False}
Path('mac-public-download-'+os.environ['GITHUB_RUN_ID']+'.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
