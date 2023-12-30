param(
    [Parameter(HelpMessage="Verifies that expected directories exist but doesn't copy anything", Mandatory=$false)]
    [switch]$Verify = $false,
    
    [Parameter(HelpMessage="Install globally or just for current user", Mandatory=$false)]
    [switch]$Global = $false,

    [Parameter(HelpMessage="Expected user name for current user", Mandatory=$false)]
    [string]$UserName = "ejpla"
)

# Expected locations in priority orders
$pythonExes = @("C:\Python27\python.exe")
$foldersGlobal = @("C:\Program Files\GIMP 2\lib\gimp\2.0\plug-ins")
$foldersLocal = @("C:\Users\{0}\AppData\Roaming\GIMP\2.10\plug-ins" -f $UserName)

# Determine locations
[string]$pythonExe = $null
foreach ($file in $pythonExes) {
    if (Test-Path -Type Leaf $file) {
        $pythonExe = $file
        break
    }
}

[string]$targetFolder = $null
if ($Global) {
    foreach ($folder in $foldersGlobal) {
        if (Test-Path -Path $folder) {
            $targetFolder = $folder
            break
        }
    }
}
else {
    foreach ($folder in $foldersLocal) {
        if (Test-Path -Path $folder) {
            $targetFolder = $folder
            break
        }
    }
}

# Get all plugins
[string]$pythonPluginsFolder = "{0}\src\plugins" -f $PSScriptRoot
[string]$pythonPluginsRegex = "(^|[\\\/])[^_]\w*\.py$" # any py file not starting with an underscore
[System.Collections.ArrayList]$pythonPluginsFiles = @()

if ([string]::IsNullOrEmpty($pythonExe)){
    Write-Error ("Python executable not found")
}

if (-not (Test-Path $pythonPluginsFolder)){
    Write-Error ("Expected plugins not found at {0}" -f $pythonPluginsFolder)
}

$pythonPluginsAllFiles = Get-ChildItem $pythonPluginsFolder
foreach ($file in $pythonPluginsAllFiles) {
    if ($file.Name -match $pythonPluginsRegex) {
        [string]$fullFileName = "{0}\{1}" -f $pythonPluginsFolder, $file.Name

        # Add if linting passes
        if ($Verify) {
            Write-Output ("Checking {0}:" -f $fullFileName)
        }
        $pylintOutput = Invoke-Expression ("{0} -m pylint {1} --generated-members=gimpfu.*" -f $pythonExe, $fullFileName)
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

# Run tests on plugin files
if ($Verify){
    Invoke-Expression ("{0} -m unittest discover -s src" -f $pythonExe)
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