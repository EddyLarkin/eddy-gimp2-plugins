# Eddy's plugins for GIMP2

Some plugins to help draw levels and assets for games using GIMP.

## Installing

### Windows 11

#### Prerequisites

* Have installed the following
    * GIMP 2

* Have the following Python libraries
    * `pylint`

#### Building

* Run `setup_windows11.ps1` in Powershell console
    * set `-Global` flag to copy plugins for all users (`setup_windows11.ps1 -Global`), or
    * set `-UserName` instead to choose the current user to copy plugin for (`setup_windows11.ps1 -User myUserName`)
    * set `-Verify` flag for a dry run, linting plugin code and previewing commands

* The script assumes all folders are in default locations - just edit `$foldersGlobal` / `$foldersLocal` if this isn't the case.

## Details

* Due to some difficulty getting GIMP plugins to work if they require multiple local files, plugins are built into single files using the `combine_plugins.py` script.
* Files matching the pattern `src/plugins/*.py` are automatically combined into single files in `out/*.py`
* `src/plugins/common` contains implementation details and shared code.
* `src/test` contains unit tests for code in `src/plugins/common`.
* `src/plugins/common` should **NOT** import `gimpfu` directly due to difficulties getting it to play nicely with the unit testing module.