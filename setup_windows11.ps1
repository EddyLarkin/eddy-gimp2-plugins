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

# Get all plugins
[string]$pythonPluginsFolder = "{0}\plugins" -f $PSScriptRoot
[string]$pythonPluginsPattern = "*.py" -f $PSScriptRoot
[System.Collections.ArrayList]$pythonPluginsFiles = @()

if (-not (Test-Path $pythonPluginsFolder)){
    Write-Error ("Expected plugins not found at {0}" -f $pythonPluginsFolder)
}

$pythonPluginsAllFiles = Get-ChildItem $pythonPluginsFolder
foreach ($file in $pythonPluginsAllFiles) {
    if ($file.Name -like $pythonPluginsPattern) {
        [string]$fullFileName = "{0}\{1}" -f $pythonPluginsFolder, $file.Name

        # Add if linting passes
        if ($Verify) {
            Write-Output ("Checking {0}:" -f $fullFileName)
        }
        $pylintOutput = pylint $fullFileName
        if ($LastExitCode -eq 0){
            [void]$pythonPluginsFiles.Add($fullFileName)
        } else {
            Write-Error ("pylint error for {0}" -f $fullFileName)
            if ($Verify){
                Write-Output $pylintOutput
            }
        }
    }
}

# Verify target locations exist
if ([string]::IsNullOrEmpty($targetFolder)){
    Write-Error ("Expected plugins directory not found for user {0}" -f $UserName)
} elseif ($Verify) {
    Write-Output ("Plugins root directory found at {0}" -f $targetFolder)
}

# Copy files over
if (-not $Verify) {
    foreach ($file in $pythonPluginsFiles) {
        Copy-Item -Path $file -Destination $targetFolder
    }
}
else {
    foreach ($file in $pythonPluginsFiles) {
        Write-Output ("Will add {0}" -f $file)
    }
}