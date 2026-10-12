"""Synthetic native Windows acceptance using only the verified installer.

No account login, real documents, external model API or cloud business actions.
"""
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.request
import uuid
import xml.etree.ElementTree as ET
import zipfile

root = Path(sys.argv[1]).resolve()
manifest_path = next((root / 'artifact').rglob('windows-download-manifest.json'))
manifest = json.loads(manifest_path.read_text())
offline = root / manifest['name']
with offline.open('wb') as output:
    for item in manifest['parts']:
        with (manifest_path.parent / item['name']).open('rb') as source:
            while chunk := source.read(8 * 1024 * 1024):
                output.write(chunk)
with zipfile.ZipFile(offline) as archive:
    archive.extractall(root / 'offline')
setup, = (root / 'offline').rglob('*-Setup.exe')
installed = root / 'native-installed'
subprocess.run([str(setup), '/S', '/D=' + str(installed)], check=True, timeout=300)
bundle = installed / 'resources/model-bundle'
spec = json.loads((bundle / 'bundle.json').read_text())
assert spec['platform'] == 'win32' and spec['arch'] == 'x64'
with socket.socket() as sock:
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
environment = {k: v for k, v in os.environ.items() if k.upper() in ('SYSTEMROOT', 'WINDIR', 'TEMP', 'TMP', 'PATH')}
environment.update(OLLAMA_HOST=f'127.0.0.1:{port}', OLLAMA_MODELS=str(bundle / 'models'),
                   OLLAMA_NO_CLOUD='1', OLLAMA_NUM_PARALLEL='1', OLLAMA_MAX_LOADED_MODELS='1',
                   OLLAMA_CONTEXT_LENGTH='16384', USERPROFILE=str(root / 'isolated-model-home'))
endpoint = f'http://127.0.0.1:{port}'
log = (root / 'native-model.log').open('wb')
server = subprocess.Popen([str(bundle / spec['executable']), 'serve'], env=environment, stdout=log, stderr=log)
started = time.monotonic()


def post(path, payload):
    request = urllib.request.Request(endpoint + path, json.dumps(payload).encode(), {'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=300) as response:
        return json.load(response)


def rows(path):
    with zipfile.ZipFile(path) as archive:
        sheet = ET.fromstring(archive.read('xl/worksheets/sheet1.xml'))
    ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    values = []
    for row in sheet.findall('.//s:sheetData/s:row', ns):
        cells = []
        for cell in row.findall('s:c', ns):
            if cell.get('t') == 'inlineStr':
                cells.append(''.join(cell.itertext()))
            else:
                value = cell.find('s:v', ns)
                cells.append(float(value.text) if value is not None and value.text else None)
        values.append(cells + [None] * max(0, 2-len(cells)))
    return values


try:
    for _ in range(90):
        try:
            with urllib.request.urlopen(endpoint + '/api/tags', timeout=2) as response:
                tags = json.load(response)
            assert any(x['name'] == spec['model'] for x in tags['models'])
            break
        except Exception:
            if server.poll() is not None:
                raise RuntimeError('Bundled Ollama exited')
            time.sleep(1)
    else:
        raise RuntimeError('Bundled Ollama did not start')
    warmup = post('/api/generate', {'model': spec['model'], 'prompt': '请只回复：本地模型已就绪',
                                  'stream': False, 'think': False,
                                  'options': {'num_ctx': 16384, 'num_predict': 32, 'temperature': 0}})
    assert warmup.get('response', '').strip(), 'No native model response'
    owner = hashlib.sha256(uuid.uuid4().bytes).hexdigest()
    thread = str(uuid.uuid4())
    workspace = (root / 'synthetic' / owner / 'threads' / thread).resolve()
    (workspace / 'sources').mkdir(parents=True)
    (workspace / 'outputs').mkdir()
    data = '事项,金额\n办公用品,120.50\n交通费,80.00\n资料费,99.80\n退款,-20.30\n'.encode()
    file_id = str(uuid.uuid4())
    imported = workspace / 'sources' / (file_id + '.csv')
    imported.write_bytes(data)
    request = {'directory': str(workspace), 'ownerId': owner, 'threadId': thread, 'history': [],
               'mode': 'local', 'model': spec['model'], 'modelUrl': endpoint + '/v1', 'modelToken': 'local-only',
               'systemPrompt': '你是真玥，本地资料助手。',
               'files': [{'id': file_id, 'name': '合成费用.csv', 'storedName': imported.name,
                          'size': len(data), 'sha256': hashlib.sha256(data).hexdigest()}],
               'text': '这是明确标注的合成测试数据。请读取 CSV，并真正生成 Excel 草稿：严格只要事项、金额两列，保留四笔明细，另加金额合计行。不要只回复文字表格；用工具生成文件。'}
    worker = installed / 'resources/worker/zhenyue-worker.exe'
    result = subprocess.run([str(worker)], input=json.dumps(request, ensure_ascii=False).encode(),
                            capture_output=True, env=environment, timeout=600, cwd=workspace)
    events = [json.loads(line) for line in result.stdout.decode('utf-8').splitlines() if line.startswith('{')]
    (root / 'native-worker-events.json').write_text(json.dumps(events, ensure_ascii=False, indent=2), encoding='utf-8')
    assert result.returncode == 0 and any(x.get('type') == 'result' for x in events), 'Frozen worker task failed'
    assert any(x.get('name') in ('read_document', 'inspect_table') and x.get('state') == 'complete' for x in events)
    outputs = list((workspace / 'outputs').glob('*.xlsx'))
    expected = [['AI 生成工作草稿，请人工复核。', None], ['事项', '金额'], ['办公用品', 120.5], ['交通费', 80], ['资料费', 99.8], ['退款', -20.3], ['合计', 280]]
    assert any(rows(path) == expected for path in outputs), 'The native workbook did not contain the exact details and computed total'
    assert imported.read_bytes() == data, 'Source document changed'
    receipt = {'nativeWindows': True, 'syntheticOnly': True, 'accountLoginTested': False,
               'localModel': spec['model'], 'context': 16384, 'cloudUsed': False,
               'modelResponse': warmup['response'], 'workbookRows': expected,
               'frozenWorkerUtf8': True, 'seconds': round(time.monotonic() - started, 1)}
    (root / 'windows-model-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    # Hosted Windows may use a legacy console code page. The UTF-8 receipt is
    # already saved; ASCII JSON keeps successful Chinese results printable.
    print(json.dumps(receipt), flush=True)
finally:
    subprocess.run(['taskkill.exe', '/PID', str(server.pid), '/T', '/F'], capture_output=True)
    log.close()
