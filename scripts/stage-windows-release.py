"""Stage installer binaries in an existing draft; never publish automatically."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import urllib.parse
import urllib.request
import zipfile

TAG = 'zhenyue-local-0.1.1-preview.1'
REPO = 'guot603/zhenyue-desktop-releases'
url = os.environ.pop('ARTIFACT_URL')
expected = os.environ['ARTIFACT_SHA256'].removeprefix('sha256:')
assert re.fullmatch('[a-f0-9]{64}', expected), 'Invalid artifact hash'
origin = urllib.parse.urlsplit(url)
assert origin.scheme == 'https' and not origin.username and origin.hostname.endswith('.blob.core.windows.net'), 'Unexpected artifact source'
root = Path('work')
root.mkdir(exist_ok=False)
archive = root / 'artifact.zip'
with urllib.request.urlopen(url, timeout=180) as response, archive.open('wb') as output:
    shutil.copyfileobj(response, output, 8 * 1024 * 1024)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


assert sha(archive) == expected, 'Artifact transport checksum mismatch'
with zipfile.ZipFile(archive) as package:
    assert sum(x.file_size for x in package.infolist()) < 24 * 1024**3
    for item in package.infolist():
        path = PurePosixPath(item.filename)
        assert not path.is_absolute() and '..' not in path.parts and '\\' not in item.filename and ':' not in item.filename
        assert not stat.S_ISLNK(item.external_attr >> 16)
    package.extractall(root / 'artifact')
manifests = list((root / 'artifact').rglob('windows-download-manifest.json'))
assert len(manifests) == 1, 'One Windows manifest required'
manifest_path = manifests[0]
manifest = json.loads(manifest_path.read_text())
assert manifest['platform'] == 'windows' and manifest['schema'] == 1
assert manifest['name'] == 'Zhenyue-0.1.1-windows-x64-offline-with-9B.zip'
assert manifest['baseUrl'] == f'https://github.com/{REPO}/releases/download/{TAG}/'
receipts = list((root / 'artifact').rglob('windows-install-receipt.json'))
assert len(receipts) == 1
receipt = json.loads(receipts[0].read_text(encoding='utf-8-sig'))
assert receipt['nativeWindows'] and receipt['installedFilesVerified'] > 5 and receipt['frozenWorkerProtocol']
assert receipt['windowTitle'], 'Native window acceptance missing'
all_hash = hashlib.sha256()
size = 0
files = [manifest_path, receipts[0]]
for index, part in enumerate(manifest['parts'], 1):
    assert part['name'] == manifest['name'] + f'.part{index:02d}'
    path = manifest_path.parent / part['name']
    assert path.is_file() and path.stat().st_size == part['bytes'] < 2 * 1024**3
    assert sha(path) == part['sha256']
    with path.open('rb') as stream:
        while chunk := stream.read(8 * 1024 * 1024):
            all_hash.update(chunk)
            size += len(chunk)
    files.append(path)
assert size == manifest['bytes'] and all_hash.hexdigest() == manifest['sha256'], 'Complete installer reconstruction failed'
helper = manifest_path.parent / manifest['helper']['name']
assert helper.name == 'Zhenyue-Windows-Download.zip'
assert sha(helper) == manifest['helper']['sha256'] and helper.stat().st_size == manifest['helper']['bytes']
files.append(helper)
for name in ['windows-build-receipt.json', 'windows-launch.png']:
    found = list((root / 'artifact').rglob(name))
    assert len(found) == 1
    files.append(found[0])
releases = json.loads(subprocess.check_output(['gh', 'api', f'repos/{REPO}/releases?per_page=100']))
release, = [r for r in releases if r['tag_name'] == TAG]
assert release['draft'], 'Only an unpublished draft may be staged'
existing = {asset['name']: asset for asset in release['assets']}
checksums = root / 'WINDOWS-SHA256SUMS.txt'
checksums.write_text(''.join(f'{sha(path)}  {path.name}\n' for path in files))
files.append(checksums)
for path in files:
    if path.name in existing:
        asset = existing[path.name]
        assert asset['digest'] == 'sha256:' + sha(path) and asset['size'] == path.stat().st_size, 'Existing release asset differs'
        continue
    subprocess.run(['gh', 'release', 'upload', TAG, '--repo', REPO, str(path)], check=True)
print(json.dumps({'state': 'verified-and-staged', 'published': False, 'bytes': size, 'sha256': manifest['sha256'], 'files': [p.name for p in files]}))
