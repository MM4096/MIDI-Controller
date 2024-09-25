# Installation
This section will guide you through the installation process of the `textual` port of this program.

Currently, this program is built for Linux, and isn't tested/may not work on other operating systems.

## Basic Installation
To see the releases, go to the [Releases](https://github.com/MM4096/MIDI-Controller/releases/) page, or get the latest release [here](https://github.com/MM4096/MIDI-Controller/releases/latest).

Download the `MIDI-Controller-textual-linux` file, and place it in a directory of your choosing.
**Note: For versions before v0.5.prerelease.1, this port doesn't exist.**

In a terminal, navigate to the directory with the executable in it, and run the following command to make it executable (one time):
```bash
chmod +x MIDI-CONTROLLER-textual-linux
```

Then, run the following command to start the program:
```bash
./MIDI-CONTROLLER-textual-linux
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

Install the required packages with the following command (*NOTE: Some packages may not be needed, and some may be missing*):
```bash
pip install -r requirements.txt
```

The main file is `textual_main.py`, and can be run with the following command(s):
```bash
# Use this command if running with python
python3 textual_main.py

# Use this command if running with textual, for debugging
textual run textual_main.py --dev

# If using textual, you can also run the following command to start a console:
textual console -x SYSTEM -x EVENT -x DEBUG -x INFO
```