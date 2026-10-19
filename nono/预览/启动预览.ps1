param([switch]$Snapshot, [switch]$Verify, [string]$Activity)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type -Path @((Join-Path $PSScriptRoot 'SettingsServer.cs'),(Join-Path $PSScriptRoot 'PetScene.cs'),(Join-Path $PSScriptRoot 'NonoPreview.cs')) -ReferencedAssemblies System.Windows.Forms,System.Drawing,System.Web.Extensions,System.Core
[void][NonoPreview]::SetProcessDPIAware()
[System.Windows.Forms.Application]::EnableVisualStyles()
$root=(Resolve-Path (Join-Path $PSScriptRoot '..\代码')).Path
if($Verify){
    [PetScene]::Verify($root,(Join-Path $PSScriptRoot '验证'))
}elseif($Snapshot){
    $scene=New-Object PetScene($root)
    try{$scene.Snapshot((Join-Path $PSScriptRoot '诺诺-初版预览.png'),0,[DateTime]::Now)}finally{$scene.Dispose()}
}else{
    $window=New-Object NonoPreview($root)
    if($Activity){$window.PlayActivity($Activity)}
    [System.Windows.Forms.Application]::Run($window)
}

