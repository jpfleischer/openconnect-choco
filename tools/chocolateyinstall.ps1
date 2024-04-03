$ErrorActionPreference = 'Stop';
$toolsDir   = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"
$url        = 'https://gitlab.com/openconnect/openconnect/-/jobs/6273977608/artifacts/download?file_type=archive'

$setupName = 'openconnect-installer-MinGW64-GnuTLS.exe'

$packageArgs = @{
    PackageName   = $env:ChocolateyPackageName
    url           = $url
    UnzipLocation = $toolsDir
    fileType      = 'EXE'
    Checksum      = '559C900B4DDC57424C0D4B92A4C62D59D09885D1FBB2B1E81F9298676FAEB7C5'
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