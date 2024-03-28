# Path to a list of DNS blocklist
$urls = Get-Content "$PSScriptRoot/adlist.txt"

# Create a new directory
New-Item -Path "$PSScriptRoot" -Name "adlists" -ItemType "directory" -Force | Out-Null

# Get CPU Cores
#$cpu_cores = (Get-CIMInstance -Class 'CIM_Processor').NumberOfLogicalProcessors
$cpu_cores = (cat /proc/cpuinfo | grep processor | wc -l)

# Check that each DNS blocklist is available, if yes, create a file with the list contents
$urls | ForEach-Object -ThrottleLimit $cpu_cores -parallel {
    ${PSScriptRoot} = $using:PSScriptRoot
    Invoke-WebRequest -Uri $_ -OutFile ( New-Item -Path "$PSScriptRoot/adlists/$($_.ReadCount).txt" -Force ) -UseBasicParsing -SkipCertificateCheck -SkipHttpErrorCheck -TimeoutSec 10
}

# Get all DNS blocklists lines in all files that does not start with some caracters not wanted, select unique lines and export it into a single file
(Select-String -Path "$PSScriptRoot/adlists/*.txt" -NotMatch '#', '<', '!').Line | Sort-Object | Get-Unique > $PSScriptRoot/merged-dns-blocklist.txt

# Create a new directory
Remove-Item -Path "$PSScriptRoot/adlists/" -Recurse -Force | Out-Null
