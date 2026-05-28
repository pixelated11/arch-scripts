# Arch Linux scripts
A simple CLI tool, to configure, update, and install things on arch easily.
> [!NOTE]
> Software is **not** ready for production use. It is on pre-release stage.
> If you do encounter bugs, please, let me know in the issues section.

## Usage

**Arguments:**
`--help`: Displays a help message, and exits

**Subcommands:**
<br>
`update`: Updates system using pacman. Update AUR packages if you want. <br>
`install`: Install a pack of useful packages, such as base-devel, or complete QEMU VM with configurations. <br>
`config`: Configures <option>. List of configurations available to be edited will be listed below. <br>
<br>
Note that the --help, or -h argument can be used in subcommands too.
## Available configurations to be edited
- DNS, using systemd-resolved
- Hostname
- Shell

## Installation
Install the package from the AUR using an AUR helper:
```
yay -S arch-scripts
```
Your AUR helper may be other than yay.
***
Or, build the package manually:
```
git clone https://github.com/pixelated11/arch-scripts.git && cd arch-scripts
```
Then, run makepkg:
```
makepkg -si
```
Arch-scripts should be installed.

## Contributions
Contributions are welcome. Refer to the code of conduct before contributing. E-mail itspixelatd@proton.me to as for contribution permission.
