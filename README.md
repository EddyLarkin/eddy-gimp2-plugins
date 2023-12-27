# Eddy's plugins for GIMP2

Some plugins to help draw levels and assets for my games using GIMP.

## Windows 11

### Prerequisites

* Have installed the following in default locations
  * GIMP 2

* Have the following Python libraries
  * `pylint`
  * `bitarray`

### Installing

* Run `setup_windows11.ps1` in Powershell console
    * set `-Global` flag to copy plugins for all users (`setup_windows11.ps1 -Global`), or
    * set `-UserName` instead to choose the current user to copy plugin for (`setup_windows11.ps1 -User myUserName`)

* The script assumes all folders are in default locations - just edit `$foldersGlobal` / `$foldersLocal` if this isn't the case.