Param(
    $main_url = $(throw "Usage: install-windows-bin.ps1 MAIN_URL ODBC_URL"),
    $odbc_url = $(throw "Usage: install-windows-bin.ps1 MAIN_URL ODBC_URL"),
    $start_server = "true"
)

# make sure to have something here without spaces, I don't understand
# powershell quoting and escaping well enough
$main_prefix = "C:\MonetDB"


Write-Output "main_url=$main_url"
Write-Output "odbc_url=$odbc_url"
Write-Output "main_prefix=$main_prefix"

Write-Output "========== MONETDB ========="
$main_file="c:\monetdb-main.msi"
Write-Output "---------- Download '$main_file' from '$main_url'"
(New-Object System.Net.WebClient).DownloadFile("$main_url", "$main_file");
Get-ChildItem $main_file
Write-Output "---------- Install '$main_file'"
#$main_proc = Start-Process "$main_file" -ArgumentList '/quiet /passive /qn /norestart INSTALLLEVEL=1000 MSIRMSHUTDOWN=2' -Wait
$result = Start-Process msiexec.exe -ArgumentList "/i $main_file /L* c:\main.log /passive /norestart INSTALLDIR=$main_prefix INSTALLLEVEL=1000 MSIRMSHUTDOWN=2" -Wait
Write-Output "---------- exit code ${result.ExitCode}"
Write-Output "---------- log output:"
Get-Content -Path "c:\main.log"
if ($result.ExitCode) {
    Throw "msi install failed with exit code '${result.ExitCode}'"
}
Write-Output "---------- OK"

Write-Output "========== ODBC ========="
$odbc_file="c:\monetdb-odbc.msi"
Write-Output "---------- Download '$odbc_file' from '$odbc_url'"
(New-Object System.Net.WebClient).DownloadFile("$odbc_url", "$odbc_file");
Get-ChildItem $odbc_file
Write-Output "---------- Install '$odbc_file'"
$result = Start-Process msiexec.exe -ArgumentList "/i $odbc_file /L* c:\odbc.log /passive /norestart INSTALLLEVEL=1000 MSIRMSHUTDOWN=2" -Wait
Write-Output "---------- exit code ${result.ExitCode}"
Write-Output "---------- log output:"
Get-Content -Path "c:\odbc.log"
if ($result.ExitCode) {
    Throw "msi install failed with exit code '${result.ExitCode}'"
}
Write-Output "---------- OK"


Write-Output "========== DIR DIR DIR =========="
Get-ChildItem -Path "$main_prefix" -Recurse -Depth 100 -Force

Write-Output "========== Disable embedded Python =========="
# The version of Python embedded in MonetDB is unlikely to match this system's Python.
Remove-Item "$main_prefix\pyapi_locatepython3.bat"

Write-Output "========== Update PATH =========="
Write-Output "old PATH: $env:PATH"
# write it to $GITHUB_PATH so future steps have it
Add-Content $env:GITHUB_PATH "$main_prefix"
# add it to the environment so the rest of this script has it
$env:PATH += ";$main_prefix"
# verbose is good
Write-Output "new PATH: $env:PATH"

if ($start_server -eq "true") {
    Write-Output "========== Start the server =========="
    $opts = @{
        FilePath = "$main_prefix\MSQLserver.bat"
        #NoNewWindow = $true
        #ArgumentList = "--set","embedded_py=false"
    }
    Start-Process @opts
} else {
    Write-Output "========== (Not starting the server) =========="
}

Write-Output "========== Update GitHub contexts =========="
# We write to 'github.output' rather than $env:GITHUB_OUTPUT
# because all the install scripts in this Action do that.
# Another step in the Action then copies it to $env:GITHUB_OUTPUT
Add-Content github.output "prefix=$main_prefix"
Add-Content github.output "bindir=$main_prefix"
Add-Content github.output "includedir=$main_prefix\include\monetdb"
Add-Content github.output "libdir=$main_prefix\lib"
Add-Content github.output "dynsuffix=dll"
Write-Output "---------- github.output ----------"
Get-Content $env:GITHUB_OUTPUT
Write-Output "---------- GITHUB_PATH ($env:GITHUB_PATH) ----------"
Get-Content $env:GITHUB_PATH


Write-Output "========== DONE =========="
