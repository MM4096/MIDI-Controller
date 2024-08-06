#!/bin/bash

# activate venv
source .venv/bin/activate

pyinstaller --onefile curses_main.py
mv -f dist/curses_main dist/MIDI-Controller-linux
