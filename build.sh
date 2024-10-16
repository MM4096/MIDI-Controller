#!/bin/bash

# activate venv
source .venv/bin/activate

pyinstaller --onefile main.py --hidden-import mido.backends.rtmidi
mv -f dist/main dist/MIDI-Controller-curses-linux
