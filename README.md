
# TechScamBlock
> [!NOTE]
> This is not developed by me. THis is a port from Raven Software to work on linux. Releases for platform specific coming soon (tm) but the python files are done. The docs still apply, except the config directory is now /etc/techscamblock/techscamblock.conf

> [!NOTE]
> All of our free software is designed to respect your privacy, while being as simple to use as possible. Our free software is licensed under the [BSD-3-Clause license](https://ravendevteam.org/files/BSD-3-Clause.txt). By using our software, you acknowledge and agree to the terms of the license.

Block remote access programs that are used by tech support scammers.

Made for Windows 10/11.

## Installation
See [Releases](https://github.com/textdev-0/techscamblock-linux/releases/tag/1.0.0) and Download the latest version for ~~Windows~~ your Linux distro.

# Documentation
Documentation is available [here](https://docs.ravendevteam.org/techscamblock).

To install across distros from source, make sure you have Python 3.12.4 or greater, ~~and Nuitka,~~ download/pull this repo, install dependencies from the `requirements.txt`, then run ~~`build.bat`~~ `install.sh`.

To build from source, download/pull this repo, intall platform-specific tools (listed below), then run `build_YOUR-DISTRO.sh`.
This only builds the proper package file, and does not install it. You need to run the said package file (with an internet connection, due to depends)

## Platform-specific tools needed:
`build_DEB.sh`: for Pop!_OS, Ubuntu, Debian, Linux Mint, and other Debian derivatives - `dpkg-dev` (`sudo apt install dpkg-dev`)

Thats it for now

## Authors & Contributors

- [Raven Development Team](https://ravendevteam.org/)
- [Icons by Icons8](https://icons8.com/)

- [Linux port](https://github.com/textdev-0/techscamblock-linux/)


