#!/bin/bash

# activate venv
source .venv/bin/activate

pyinstaller --onefile main.py
mv -f dist/main dist/MIDI-Controller-linux
