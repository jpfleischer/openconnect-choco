Uninstall-BinFile 'openconnect'
Uninstall-ChocolateyPackage -PackageName 'openconnect' `
                                -FileType 'EXE' `
                                -SilentArgs "/S" `
                                -File "$($env:SystemDrive)\Program Files\OpenConnect\Uninstall OpenConnect.exe"