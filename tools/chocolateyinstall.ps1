$ErrorActionPreference = 'Stop';
$toolsDir   = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"
$url        = 'https://gitlab.com/openconnect/openconnect/-/jobs/8818234827/artifacts/download?file_type=archive'

$setupName = 'openconnect-installer-MinGW64-GnuTLS.exe'

$packageArgs = @{
    PackageName   = $env:ChocolateyPackageName
    url           = $url
    UnzipLocation = $toolsDir
    fileType      = 'EXE'
    Checksum      = 'D85C0DE25B600428004C188A9C5AC44BFE106ED0D7203EE7CDB9DA064023FB55'
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