"""Test a pinned public helper with tiny native Windows fixtures, no app source."""
import functools
import hashlib
import http.server
import io
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import threading
import urllib.request
import zipfile

BASE = "https://github.com/guot603/zhenyue-desktop-releases/releases/download/zhenyue-bid-local-0.10.0-preview.6/"


def digest(data):
    return hashlib.sha256(data).hexdigest()


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def do_GET(self):
        self.server.requests.append(self.path)
        if self.server.unavailable:
            self.send_error(503)
        else:
            super().do_GET()


def replace_manifest(original, match, manifest):
    payload = json.dumps(manifest, separators=(",", ":")).replace('"', '\\"')
    return original[:match.start(1)] + payload + original[match.end(1):]


def replace_curl(command, filename):
    old = 'set "ZHENYUE_CURL_EXE=%ZHENYUE_SYSTEM%\\curl.exe"'
    assert command.count(old) == 1
    return command.replace(old, f'set "ZHENYUE_CURL_EXE=%ZHENYUE_DOWNLOAD_DIR%{filename}"')


def native_run(command, working, system, *, wow64=False, missing_ps=False, launch_setup=False):
    script = working / "下载并安装.cmd"
    script.write_bytes(command.encode("ascii"))
    env = dict(os.environ)
    env["PATH"] = ""
    if missing_ps:
        env["SystemRoot"] = str(working / "missing-windows")
    cmd = system / ("SysWOW64" if wow64 else "System32") / "cmd.exe"
    assert cmd.is_file(), f"Native launcher missing: {cmd}"
    arguments = "" if launch_setup else " --download-only"
    launch = f'"{cmd}" /d /s /v:off /c ""{script}"{arguments}"'
    result = subprocess.run(launch, cwd=working, env=env, input=b"\r\n\r\n",
                            capture_output=True, timeout=180)
    return result, (result.stdout + result.stderr).decode("utf-8", errors="replace")


def main():
    if os.name != "nt":
        raise SystemExit("Native Windows required")
    name = os.environ["CANDIDATE_HELPER_NAME"]
    expected = os.environ["EXPECTED_CANDIDATE_HELPER_SHA256"]
    if not re.fullmatch(r"ZhenyueBid-Windows-Download-Fix-\d{8}(?:-network)?\.zip", name):
        raise ValueError("Unexpected candidate filename")
    if not re.fullmatch(r"[a-f0-9]{64}", expected):
        raise ValueError("Pinned helper SHA-256 required")
    with urllib.request.urlopen(BASE + name, timeout=60) as response:
        raw_zip = response.read(1024 * 1024 + 1)
    assert len(raw_zip) <= 1024 * 1024, "Helper is unexpectedly large"
    assert digest(raw_zip) == expected, "Public helper integrity failed"
    with zipfile.ZipFile(io.BytesIO(raw_zip)) as package:
        original = package.read("Zhenyue-Download/下载并安装.cmd").decode("ascii")
    assert original.count("\r\n") == original.count("\n"), "Real CRLF required"
    assert max(map(len, original.splitlines())) <= 7800, "CMD line too long"
    matches = list(re.finditer(r"\$m='([^']+)'\|ConvertFrom-Json", original))
    assert len(matches) == 1, "Expected one embedded manifest"
    embedded = json.loads(matches[0][1].replace('\\"', '"'))
    assert embedded["baseUrl"] == BASE
    assert embedded["sha256"] == "3d97f16aefe97727cdd971a0dbbd668268df31c8dbc49d7004366370ee8894b7"
    system = Path(os.environ["SystemRoot"])
    scenarios = [
        ("offline-launch", {}),
        ("offline-empty-path", {"empty_path": True}),
        ("wow64-empty-path", {"empty_path": True, "wow64": True}),
        ("download-empty-path", {"empty_path": True, "online": True}),
        ("download-without-curl", {"empty_path": True, "online": True, "no_curl": True}),
        ("corrupt-download", {"empty_path": True, "online": True, "corrupt_part": True}),
        ("corrupt-full-archive", {"empty_path": True, "bad_archive": True}),
        ("missing-powershell", {"empty_path": True, "missing_powershell": True}),
        ("curl-reset-recovers", {"online": True, "transient_curl": True}),
        ("curl-reset-fallback", {"online": True, "curl_failure": True}),
        ("network-unavailable", {"online": True, "curl_failure": True, "unavailable": True}),
        ("fallback-corrupt-download", {"online": True, "curl_failure": True, "corrupt_part": True}),
        ("verified-part-reuse-after-reset", {"online": True, "curl_failure": True, "reuse_first": True}),
    ]
    passed = []
    with tempfile.TemporaryDirectory(prefix="真玥 中文 &()! ") as temp:
        root = Path(temp)
        fixture = io.BytesIO()
        with zipfile.ZipFile(fixture, "w", zipfile.ZIP_DEFLATED) as package:
            package.write(system / "System32/whoami.exe", "真玥离线安装/Fixture-Setup.exe")
        data = fixture.getvalue()
        chunks = [data[:len(data) // 2], data[len(data) // 2:]]
        for case_name, options in scenarios:
            working = root / case_name
            working.mkdir()
            served = root / (case_name + "-http")
            served.mkdir()
            manifest = {"schema": 1, "platform": "windows", "name": "fixture.zip",
                        "bytes": len(data), "sha256": digest(data), "parts": []}
            for index, chunk in enumerate(chunks, 1):
                part_name = f"fixture.zip.part{index:02d}"
                manifest["parts"].append({"name": part_name, "bytes": len(chunk), "sha256": digest(chunk)})
                (served / part_name).write_bytes(chunk)
                if not options.get("online") or (options.get("reuse_first") and index == 1):
                    (working / part_name).write_bytes(chunk)
            if options.get("corrupt_part"):
                (served / manifest["parts"][-1]["name"]).write_bytes(b"corrupted fixture")
            if options.get("bad_archive"):
                manifest["sha256"] = "0" * 64
            with http.server.ThreadingHTTPServer(("127.0.0.1", 0),
                    functools.partial(QuietHandler, directory=str(served))) as server:
                server.requests = []
                server.unavailable = options.get("unavailable", False)
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                try:
                    manifest["baseUrl"] = f"http://127.0.0.1:{server.server_port}/"
                    command = replace_manifest(original, matches[0], manifest)
                    if options.get("no_curl"):
                        command = replace_curl(command, "missing-curl.exe")
                    if options.get("curl_failure") or options.get("transient_curl"):
                        stub = ['@echo off']
                        if options.get("transient_curl"):
                            stub += ['if exist "%~dp0curl-attempts.txt" goto transfer']
                        stub += ['echo reset>>"%~dp0curl-attempts.txt"', 'exit /b 35']
                        if options.get("transient_curl"):
                            stub += [':transfer', 'echo retry>>"%~dp0curl-attempts.txt"',
                                     '"%SystemRoot%\\System32\\curl.exe" %*', 'exit /b %errorlevel%']
                        (working / 'fake-curl.cmd').write_bytes(('\r\n'.join(stub) + '\r\n').encode())
                        command = replace_curl(command, "fake-curl.cmd")
                    result, output = native_run(command, working, system,
                        wow64=options.get("wow64"), missing_ps=options.get("missing_powershell"),
                        launch_setup=case_name == "offline-launch")
                    target = working / "offline-install"
                    if options.get("missing_powershell"):
                        assert result.returncode == 2 and "Windows PowerShell was not found" in output, output
                        assert not target.exists()
                    elif options.get("unavailable"):
                        assert result.returncode != 0 and 'NETWORK DOWNLOAD FAILED' in output, output
                        assert 'download-log.txt' in output, output
                        assert len(server.requests) == 1, server.requests
                        assert not target.exists()
                        assert not (working / manifest['parts'][0]['name']).exists()
                    elif options.get("corrupt_part") or options.get("bad_archive"):
                        assert result.returncode != 0 and "checksum mismatch" in output, output
                        assert not target.exists()
                    else:
                        assert result.returncode == 0, output
                        assert (target / "真玥离线安装/Fixture-Setup.exe").is_file()
                        assert digest((working / "fixture.zip").read_bytes()) == digest(data)
                    if options.get("curl_failure") or options.get("transient_curl"):
                        log = (working / 'download-log.txt').read_text(encoding='utf-8-sig')
                        assert 'curl failed, code 35' in log, log
                        attempts = (working / 'curl-attempts.txt').read_text().splitlines()
                        expected_attempts = 3 if options.get('transient_curl') else (2 if options.get('unavailable') or options.get('reuse_first') else 4)
                        assert len(attempts) == expected_attempts, (attempts, output)
                        assert ('via Windows HTTP' if options.get('curl_failure') else 'attempt 2/3 via curl') in log, log
                    if options.get('reuse_first'):
                        assert '/' + manifest['parts'][0]['name'] not in server.requests
                        assert digest((working / manifest['parts'][0]['name']).read_bytes()) == digest(chunks[0])
                    passed.append(case_name)
                    print(f"PASS: {case_name}", flush=True)
                finally:
                    server.shutdown()
                    thread.join(timeout=5)
        # Test both HTTP clients against actual GitHub HTTPS and release-asset
        # redirects using a small pinned public ZIP, without redownloading 9 GB.
        # It contains no Setup.exe: successful transport must stop at that guard.
        manifest_sha = os.environ['EXPECTED_MANIFEST_SHA256']
        assert re.fullmatch(r'[a-f0-9]{64}', manifest_sha)
        with urllib.request.urlopen(BASE + 'windows-download-manifest.json', timeout=60) as response:
            public_manifest = response.read(1024 * 1024)
        assert digest(public_manifest) == manifest_sha
        small = json.loads(public_manifest)['helper']
        assert small['name'] == 'ZhenyueBid-Windows-Download.zip'
        for method in ['curl', 'Windows-HTTP']:
            case_name = 'public-https-' + method
            working = root / case_name
            working.mkdir()
            manifest = {'schema': 1, 'platform': 'windows', 'baseUrl': BASE,
                        'name': 'transport-check.zip', 'bytes': small['bytes'],
                        'sha256': small['sha256'], 'parts': [small]}
            command = replace_manifest(original, matches[0], manifest)
            if method == 'Windows-HTTP':
                command = replace_curl(command, 'missing-curl.exe')
            result, output = native_run(command, working, system)
            assert result.returncode != 0 and 'Installer missing' in output, output
            assert digest((working / 'transport-check.zip').read_bytes()) == small['sha256']
            assert (working / 'offline-install/Zhenyue-Download/下载并安装.cmd').is_file()
            passed.append(case_name)
            print(f'PASS: {case_name}', flush=True)
    receipt = {"status": "passed", "helperName": name, "helperSha256": expected,
               "syntheticCases": [p for p in passed if not p.startswith('public-https-')],
               "publicHttpsCases": [p for p in passed if p.startswith('public-https-')],
               "manifestSha256": manifest_sha, "nativeApplicationInstallTested": False, "customerData": False,
               "windows10Or11HardwareTested": False, "sourceCommit": os.getenv("GITHUB_SHA")}
    Path("windows-helper-fixtures.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
