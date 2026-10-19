$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
Add-Type -Path (Join-Path $PSScriptRoot 'BuildAssets.cs') -ReferencedAssemblies System.Drawing
$nonoRoot=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
[BuildAssets]::LaserUI($nonoRoot)
