$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
Add-Type -Path (Join-Path $PSScriptRoot 'AnimateNono.cs') -ReferencedAssemblies System.Drawing
[AnimateNono]::Run((Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path)
python (Join-Path $PSScriptRoot 'encode_animations.py')
if($LASTEXITCODE -ne 0){throw 'Animation encoder failed'}

