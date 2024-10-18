#!/bin/bash

# activate venv
source .venv/bin/activate

pyinstaller --onefile curses_main.py --hidden-import mido.backends.rtmidi
mv -f dist/curses_main dist/MIDI-Controller-curses-linux
