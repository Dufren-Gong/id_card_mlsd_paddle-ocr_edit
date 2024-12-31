param (
    [string]$flag_file,
    [string]$exe_name
)

New-Item -Path $flag_file -ItemType File -Force

Start-Process -FilePath $exe_name