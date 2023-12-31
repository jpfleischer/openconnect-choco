$ErrorActionPreference = 'Stop';
$toolsDir   = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"
$url        = 'https://gitlab.com/openconnect/openconnect/-/jobs/5809119325/artifacts/download?file_type=archive'

$setupName = 'openconnect-installer-MinGW64-GnuTLS.exe'

$packageArgs = @{
    PackageName   = $env:ChocolateyPackageName
    url           = $url
    UnzipLocation = $toolsDir
    fileType      = 'EXE'
    Checksum      = 'BA844FBC912AC57FC2807BAD225A0A7F9623080C8E659F340FF8142BFA32A576'
    ChecksumType  = 'sha256'
    softwareName  = 'openconnect*'
    silentArgs    = '/S'
}

Install-ChocolateyZipPackage @packageArgs

$files = get-childitem $toolsDir -include openconnect-installer*.exe -recurse

foreach ($file in $files) {
  #generate an ignore file
  New-Item "$file.ignore" -type file -force | Out-Null
}

$packageArgs.file = Join-Path -Path $toolsDir -ChildPath $setupName
Install-ChocolateyInstallPackage @packageArgs

Install-BinFile 'openconnect' "$($env:SystemDrive)\Program Files\OpenConnect\openconnect.exe"

Install-BinFile 'list-system-keys' "$($env:SystemDrive)\Program Files\OpenConnect\list-system-keys.exe"