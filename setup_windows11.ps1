param(
    [Parameter(HelpMessage="Verifies that expected directories exist but doesn't copy anything", Mandatory=$false)]
    [switch]$Verify = $false,
    
    [Parameter(HelpMessage="Install globally or just for current user", Mandatory=$false)]
    [switch]$Global = $false,

    [Parameter(HelpMessage="Expected user name for current user", Mandatory=$false)]
    [string]$UserName = "ejpla"
)

# Expected locations in priority orders
$foldersGlobal = @("C:\Program Files\GIMP 2\lib\gimp\2.0\plug-ins")
$foldersLocal = @("C:\Users\{0}\AppData\Roaming\GIMP\2.10\plug-ins" -f $UserName)

# Determine locations
[string]$targetFolder = $null
if ($Global) {
    foreach ( $folder in $foldersGlobal) {
        if (Test-Path -Path $folder) {
            $targetFolder = $folder
            break
        }
    }
}
else {
    foreach ( $folder in $foldersLocal) {
        if (Test-Path -Path $folder) {
            $targetFolder = $folder
            break
        }
    }
}

[string]$sourcePlugins = "{0}\plugins\*.py" -f $PSScriptRoot

# Verify target locations exist
if ([string]::IsNullOrEmpty($targetFolder)){
    Write-Error ("Expected plugins directory not found for user {0}" -f $UserName)
} elseif ($Verify) {
    Write-Output ("Plugins root directory found at {0}" -f $targetFolder)
}

# Verify source location exists
if (-not (Test-Path $sourcePlugins)){
    Write-Error ("Expected plugins not found at {0}" -f $sourcePlugins)
}

# Copy files over
if (-not $Verify) {
    Copy-Item -Path $sourcePlugins -Destination $targetFolder
}