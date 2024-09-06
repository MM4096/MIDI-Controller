#!/bin/bash
source .venv/bin/activate

echo Building EXE
pyinstaller -F textual_main.py --add-data css:css --hidden-import mido.backends.rtmidi > /dev/null
echo Copying to \"dist/MIDI-Controller-textual-linux\"
mv -f dist/textual_main dist/MIDI-Controller-textual-linux
