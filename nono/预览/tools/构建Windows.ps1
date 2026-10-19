$ErrorActionPreference='Stop'
$preview=Split-Path $PSScriptRoot -Parent
$app=Split-Path $preview -Parent
$compiler=Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319\csc.exe'
& $compiler /nologo /target:winexe /platform:anycpu /optimize+ /utf8output ("/out:"+(Join-Path $app '桌宠诺诺.exe')) ("/win32icon:"+(Join-Path $preview '诺诺.ico')) /reference:System.Windows.Forms.dll /reference:System.Drawing.dll /reference:System.Web.Extensions.dll /reference:System.Core.dll (Join-Path $preview 'SettingsServer.cs') (Join-Path $preview 'Program.cs') (Join-Path $preview 'PetScene.cs') (Join-Path $preview 'PetNeeds.cs') (Join-Path $preview 'NeedsVisibility.cs') (Join-Path $preview 'NeedPolicyTests.cs') (Join-Path $preview 'WeatherService.cs') (Join-Path $preview 'NonoPreview.cs')
if($LASTEXITCODE -ne 0){throw 'Windows 模拟器编译失败'}
Write-Output '已生成桌宠诺诺.exe'
