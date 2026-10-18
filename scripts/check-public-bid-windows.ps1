$ErrorActionPreference = 'Stop'
if (-not $IsWindows -or $env:EXPECTED_MANIFEST_SHA256 -notmatch '^[a-f0-9]{64}$') { throw 'Native Windows and pinned manifest required' }
$tag = 'zhenyue-bid-local-0.9.0-preview.14'
$base = "https://github.com/guot603/zhenyue-desktop-releases/releases/download/$tag/"
$work = Join-Path $env:RUNNER_TEMP '真玥 官网下载与安装'
New-Item -ItemType Directory -Path $work | Out-Null
$manifestPath = Join-Path $work 'windows-download-manifest.json'
& curl.exe --fail --location --retry 3 --output $manifestPath ($base + 'windows-download-manifest.json')
if ($LASTEXITCODE -ne 0 -or (Get-FileHash $manifestPath).Hash.ToLower() -ne $env:EXPECTED_MANIFEST_SHA256) { throw 'Public manifest integrity failed' }
$m = Get-Content $manifestPath -Raw | ConvertFrom-Json
if ($m.baseUrl -ne $base -or $m.name -ne 'ZhenyueBid-0.9.0-preview.14-windows-x64-offline.zip' -or $m.helper.name -ne 'ZhenyueBid-Windows-Download.zip') { throw 'Unexpected public release identity' }
$helper = Join-Path $work $m.helper.name
& curl.exe --fail --location --retry 3 --output $helper ($base + $m.helper.name)
if ($LASTEXITCODE -ne 0 -or (Get-FileHash $helper).Hash.ToLower() -ne $m.helper.sha256) { throw 'Public helper integrity failed' }
Expand-Archive -LiteralPath $helper -DestinationPath $work
$command = @(Get-ChildItem $work -Recurse -Filter '*.cmd')
if ($command.Count -ne 1 -or (Get-Content $command[0].FullName -Raw) -notmatch '--download-only') { throw 'Expected public offline-distribution command' }
# Execute exactly the published assistant in a Chinese/spaced directory. Its
# supported offline-distribution mode downloads, hashes, assembles and extracts.
& $command[0].FullName --download-only
if ($LASTEXITCODE -ne 0) { throw 'Published download assistant failed' }
$archive = Join-Path $command[0].DirectoryName $m.name
if ((Get-Item $archive).Length -ne $m.bytes -or (Get-FileHash $archive).Hash.ToLower() -ne $m.sha256) { throw 'Full public archive mismatch' }
$setup = @(Get-ChildItem (Join-Path $command[0].DirectoryName 'offline-install') -Recurse -Filter '*-Setup.exe')
if ($setup.Count -ne 1) { throw 'Public native installer missing' }
$install = Join-Path $work '已安装 真玥投标'
$p = Start-Process $setup[0].FullName -ArgumentList @('/S', "/D=$install") -PassThru
if (-not $p.WaitForExit(600000)) { & taskkill.exe /PID $p.Id /T /F | Out-Null; throw 'Public installation timeout' }
$p.Refresh(); if ($p.ExitCode -ne 0) { throw "Public installation failed: $($p.ExitCode)" }
$exe = Join-Path $install '真玥投标数字员工.exe'
$info = (Get-Item $exe).VersionInfo
if ($info.CompanyName -ne '蚁链（山东）人工智能科技有限公司' -or $info.ProductVersion -notlike '0.9.0*') { throw 'Public product identity mismatch' }
$bundle = Get-Content "$install/resources/model-bundle/bundle.json" -Raw | ConvertFrom-Json
foreach ($file in $bundle.files) {
  $path = Join-Path "$install/resources/model-bundle" $file.path
  if ((Get-Item $path).Length -ne $file.size -or (Get-FileHash $path).Hash.ToLower() -ne $file.sha256) { throw "Installed model checksum failed: $($file.path)" }
}
$office = Get-Content "$install/resources/legal/office/provenance.json" -Raw | ConvertFrom-Json
if ($office.nativeRuntime.Count -ne 20) { throw 'Bundled Office native runtime inventory missing' }
foreach ($file in $office.nativeRuntime) {
  if ($file.file -notmatch '^(program|program/python-core-3\.12\.13/bin)/[a-z0-9_]+\.dll$' -or $file.peMachine -ne 'AMD64') { throw 'Invalid Office runtime identity' }
  $path = Join-Path "$install/resources/office/LibreOffice" $file.file
  if ((Get-FileHash -LiteralPath $path).Hash.ToLower() -ne $file.sha256) { throw 'Public Office native runtime mismatch' }
}
$psi = [Diagnostics.ProcessStartInfo]::new()
$psi.FileName = Join-Path $install 'resources/bid-worker/zhenyue-bid-worker.exe'
$psi.WorkingDirectory = $work; $psi.UseShellExecute = $false
$psi.RedirectStandardInput = $true; $psi.RedirectStandardOutput = $true; $psi.RedirectStandardError = $true
$psi.Environment.Clear()
foreach ($name in @('SystemRoot','WINDIR','TEMP','TMP')) { $psi.Environment[$name] = [Environment]::GetEnvironmentVariable($name) }
$psi.Environment['PATH'] = "$env:SystemRoot\System32"; $psi.Environment['PYTHONUTF8']='1'; $psi.Environment['OMP_NUM_THREADS']='2'
$worker = [Diagnostics.Process]::Start($psi)
$worker.StandardInput.Write('{"operation":"health"}'); $worker.StandardInput.Close()
$stdoutTask=$worker.StandardOutput.ReadToEndAsync();$stderrTask=$worker.StandardError.ReadToEndAsync()
if (-not $worker.WaitForExit(120000)) { & taskkill.exe /PID $worker.Id /T /F | Out-Null; throw 'Installed public OCR health timeout' }
$result=$stdoutTask.GetAwaiter().GetResult() | ConvertFrom-Json
if ($worker.ExitCode -ne 0 -or -not $result.ok) { throw ('Installed public OCR health failed: '+$stderrTask.GetAwaiter().GetResult()) }
$app = Start-Process $exe -PassThru
try {
  for ($i=0; $i -lt 90; $i++) {
    Start-Sleep -Seconds 2; $app.Refresh()
    if ($app.HasExited) { throw 'Public app exited before window appeared' }
    if ($app.MainWindowHandle -ne 0) { break }
  }
  if ($app.MainWindowHandle -eq 0) { throw 'Public app window missing' }
  $receipt = @{status='passed'; tag=$tag; anonymousDownload=$true; publishedHelperExecuted=$true; chineseDownloadAndInstallPaths=$true; archiveBytes=$m.bytes; archiveSha256=$m.sha256; manifestSha256=$env:EXPECTED_MANIFEST_SHA256; nativeInstall=$true; modelFilesVerified=$bundle.files.Count; installedOCRHealth=$true; officeNativeRuntimeFilesVerified=$office.nativeRuntime.Count; windowTitle=$app.MainWindowTitle; os=[Environment]::OSVersion.VersionString; accountLoginTested=$false; generationModelCalled=$false; windows10Or11HardwareTested=$false; digitallySigned=$false}
  $receipt | ConvertTo-Json | Tee-Object -FilePath "windows-public-download-install-$env:GITHUB_RUN_ID.json"
} finally { if (-not $app.HasExited) { & taskkill.exe /PID $app.Id /T /F | Out-Null } }
$global:LASTEXITCODE = 0
