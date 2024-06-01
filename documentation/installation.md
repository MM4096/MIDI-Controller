# Installation
This section will guide you through the installation process of this program.

Currently, this program is built for Linux, and isn't tested/may not work on other operating systems.

***NOTE: This guide refers to the newer, documentation-still-isn't-complete project,
and as such may have undiscovered bugs and problems, alongside incomplete documentation.
If you want to use the older, slightly more stable version, go [here](old_instructions.md) for instructions on how to use that.***

## Basic Installation
To get the latest release, go to the [Releases](https://github.com/MM4096/MIDI-Controller/releases/) page, or get the latest release [here](https://github.com/MM4096/MIDI-Controller/releases/latest).
Download the `MIDI-CONTROLLER-linux` file, and place it in a directory of your choosing.

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
python3 curses_main.py
```

## Pre-requisites
This program requires the following packages to be installed:
- gedit (Ubuntu: `sudo apt-get install gedit`)


## Next Steps
To learn how to use this program, see the [Basic Usage](basic_usage.md) page, or the [In Depth Usage](in_depth_usage.md) page for more advanced usage.