$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
Add-Type -Path (Join-Path $PSScriptRoot 'BuildAssets.cs') -ReferencedAssemblies System.Drawing
[BuildAssets]::Run((Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path)

