# Installation
This section will guide you through the installation process of the `curses` port of this program.

Currently, this program is built for Linux, and isn't tested/may not work on other operating systems.

## Basic Installation
To see the releases, go to the [Releases](https://github.com/MM4096/MIDI-Controller/releases/) page, or get the latest release [here](https://github.com/MM4096/MIDI-Controller/releases/latest).
Download the `MIDI-Controller-curses-linux` file, and place it in a directory of your choosing.
**Note: For versions before v0.5.prerelease.1, the file is named `MIDI-Controller-linux`.**

In a terminal, navigate to the directory with the executable in it, and run the following command:
```bash
./MIDI-CONTROLLER-linux
```
If this doesn't work, you may need to run the following command:
```bash
chmod +x ./MIDI-CONTROLLER-linux
```
**NOTE:** You need to run the executable from the terminal, as it will not work if you double-click it. `sudo` is not needed to run this program.

## Pulling this repo
If, for some reason, you want to pull this repo, run the following command in the directory of your choosing:
```bash
git clone https://github.com/MM4096/MIDI-Controller.git
```
Then, activate the virtual environment with the following command:
```bash
source .venv/bin/activate
```
The main file is `curses_main.py`, and can be run with the following command:
```bash
python3 MIDI-Controller-linux.py
```

## Pre-requisites
This program requires the following packages to be installed:

(One of)
- nano (Should be installed by default on most distros)
- gedit (Ubuntu: `sudo apt-get install gedit`)


## Next Steps
To learn how to use this program, see the [Basic Usage](basic_usage.md) page, or the [In Depth Usage](in_depth_usage.md) page for more advanced usage.