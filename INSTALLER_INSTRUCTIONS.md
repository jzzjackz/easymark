# EasyMark Converter - Installer Setup Instructions

## Prerequisites
1. Install **Inno Setup** from https://jrsoftware.org/isdl.php
2. Make sure your `EasyMarkConverter.exe` is in the `dist` folder

## Building the Installer

1. **Ensure your executable exists:**
   - The script looks for `dist\EasyMarkConverter.exe`
   - If your exe has a different name, rename it to `EasyMarkConverter.exe` or update line 36-37 in `EasyMarkConverter.iss`

2. **Open the script:**
   - Double-click `EasyMarkConverter.iss` (or open it in Inno Setup)

3. **Build the installer:**
   - In Inno Setup, go to: **Build → Compile** (or press `Ctrl+F9`)
   - The installer will be created in the `installer` folder as `EasyMarkConverter-Setup.exe`

## Customization Options

You can customize the installer by editing `EasyMarkConverter.iss`:

- **AppVersion**: Update the version number
- **SetupIconFile**: Add an icon file path (e.g., `"icon.ico"`) for a custom installer icon
- **LicenseFile**: Add a license file path if you have one
- **OutputBaseFilename**: Change the installer filename

## What the Installer Does

- Installs EasyMark Converter to `Program Files\EasyMark Converter`
- Creates a Start Menu shortcut
- Optionally creates Desktop and Quick Launch shortcuts (user choice during installation)
- Adds an uninstaller
- Can launch the app after installation

## Distribution

The final installer (`EasyMarkConverter-Setup.exe`) is a standalone file that can be distributed to users. They just need to run it to install EasyMark Converter.

