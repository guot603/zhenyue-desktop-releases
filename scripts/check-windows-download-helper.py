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


def main():
    if os.name != "nt":
        raise SystemExit("Native Windows required")
    name = os.environ["CANDIDATE_HELPER_NAME"]
    expected = os.environ["EXPECTED_CANDIDATE_HELPER_SHA256"]
    if not re.fullmatch(r"ZhenyueBid-Windows-Download-Fix-\d{8}\.zip", name):
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
                if not options.get("online"):
                    (working / part_name).write_bytes(chunk)
            if options.get("corrupt_part"):
                (served / manifest["parts"][-1]["name"]).write_bytes(b"corrupted fixture")
            if options.get("bad_archive"):
                manifest["sha256"] = "0" * 64
            with http.server.ThreadingHTTPServer(("127.0.0.1", 0),
                    functools.partial(QuietHandler, directory=str(served))) as server:
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                try:
                    manifest["baseUrl"] = f"http://127.0.0.1:{server.server_port}/"
                    payload = json.dumps(manifest, separators=(",", ":")).replace('"', '\\"')
                    match = matches[0]
                    command = original[:match.start(1)] + payload + original[match.end(1):]
                    if options.get("no_curl"):
                        old = 'set "ZHENYUE_CURL_EXE=%ZHENYUE_SYSTEM%\\curl.exe"'
                        assert command.count(old) == 1
                        command = command.replace(old, 'set "ZHENYUE_CURL_EXE=%ZHENYUE_DOWNLOAD_DIR%missing-curl.exe"')
                    script = working / "下载并安装.cmd"
                    script.write_bytes(command.encode("ascii"))
                    env = dict(os.environ)
                    if options.get("empty_path"):
                        env["PATH"] = ""
                    if options.get("missing_powershell"):
                        env["SystemRoot"] = str(root / "missing-windows")
                    cmd = system / ("SysWOW64" if options.get("wow64") else "System32") / "cmd.exe"
                    assert cmd.is_file(), f"Native launcher missing: {cmd}"
                    arguments = "" if case_name == "offline-launch" else " --download-only"
                    launch = f'"{cmd}" /d /s /v:off /c ""{script}"{arguments}"'
                    result = subprocess.run(launch, cwd=working, env=env, input=b"\r\n\r\n",
                                            capture_output=True, timeout=90)
                    output = (result.stdout + result.stderr).decode("utf-8", errors="replace")
                    target = working / "offline-install"
                    if options.get("missing_powershell"):
                        assert result.returncode == 2 and "Windows PowerShell was not found" in output, output
                        assert not target.exists()
                    elif options.get("corrupt_part") or options.get("bad_archive"):
                        assert result.returncode != 0 and "checksum mismatch" in output, output
                        assert not target.exists()
                    else:
                        assert result.returncode == 0, output
                        assert (target / "真玥离线安装/Fixture-Setup.exe").is_file()
                        assert digest((working / "fixture.zip").read_bytes()) == digest(data)
                    passed.append(case_name)
                    print(f"PASS: {case_name}", flush=True)
                finally:
                    server.shutdown()
                    thread.join(timeout=5)
    receipt = {"status": "passed", "helperName": name, "helperSha256": expected,
               "syntheticCases": passed, "customerData": False,
               "windows10Or11HardwareTested": False, "sourceCommit": os.getenv("GITHUB_SHA")}
    Path("windows-helper-fixtures.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
