# MIDI-CONTROLLER
## Overview
This is a project I started due to a lack of proper resources for creating patch lists for my Korg Kross 2 on Ubuntu.
This project is built with Python, using the `mido` library.

## Installation / Pulling this repo
To pull this repo, run the following command in the directory of your choosing:
`git clone https://github.com/MM4096/MIDI-Controller.git`
To update, run `git pull`.

**NOTE**: I cannot find a way to package this into an executable.

## Usage
- Activate the virtual environment given. This is done by using the `source .venv/bin/activate` command in your directory.
- Run the `main.py` file using `python3 main.py`.
- Follow the instructions given, or look at the `In Depth Usage section` below.
- Remember to connect your Kross 2 to your computer via a USB cable!

## Contributions
All contributions are welcome, and you are allowed to use this source code to do whatever you feel like doing with it. Keep in mind that this is primarily designed for the Korg Kross 2.

## In Depth Usage

Here's a list of options and what they do:

- **Select Midi Port**
  - This option currently just lists all the available MIDI ports and doesn't serve any practical function yet.
- **Performance Mode**
  - The main star of this project, this mode allows for playback of created lists. Always remember, press **`CTRL + C`** to quit.
  - You need to choose your Korg Kross in the options given.
  - Then, select a mode of playback.
    - Perform a single patch ***DOESN'T WORK, NEEDS FIXING***
      - In the prompt given, select your file of choice. The `..` option brings you out a directory. This is the `user_data_dir()` as given by `platformdirs`, and cannot be left through `..`. **Only .midipatch files are shown.**
        - The cancel option brings you back to the mode of playback selection.
    - Perform a list of patches (folder)
      - In the prompt given, select a folder. As before, you cannot leave the `user_data_dir()`. When in your folder of choice, press `Select`.
  - After this, a list of all the patches to play will show up. Typing anything but `y`, `Y`, ` ` will take you back to the selection menu.
  - Some info will be shown. Press `[Enter]` to continue.
  - Your current/first patch will be shown, with all the soundlists given. The current sound is marked with a `>`. Pressing `[Enter]` will go to the next patch in this list.
  - When reaching the end of the list, a second `[Enter]` press is needed to bring you to the next list as shown below all the options. If there are no more, a loop back to the start will commence.
- **Open Program Data**
  - Options for config stuff and the main program folder. Editing the config *should* have some effect, but doesn't currently.
- **Patch Editing**
  - Edit patches and configs here.
    - **Create a patch**
      - Enter a name at the prompt. To create a folder, use the `[FOLDER_NAME]/[FILENAME]` syntax. **DO NOT** include any extentions, the program will do so automatically.
      - If editing, select `Overwrite` at the prompt given. This will allow for editing of an existing patch.
      - Select an option.
        - **Update patch list**
          - ***YOU MUST HAVE `gedit` INSTALLED TO USE THIS FEATURE!*** gedit was removed in Ubuntu 24 I think.
          - Enter your patch name on the line specified. This is what shows up in *Performance Mode*, and can be left blank. Defaults to the name specified for the file.
          - After the `startlist` line, write either names specified in a **Config File** or an index corresponding to the sound on your Korg Kross 2 (in banks).
          - Save and close the file when done; the program will automatically do the rest for you.
        - **Update config list**
          - See **Config Editing**.
    - **Create a config**
      - Follow the same steps as if creating a patch. If editing an existing config, select `Overwrite` when prompted.
      - See **Config Editing**


## Config Editing 
A list of your current keys will be presented to you, along with the options of `Create new entry`, `Exit`, and `Add preset` (Patch config editing only).
### Creating a new entry
All config values are stored as a [key, value] pair, with `key` being the alias and `value` being the sound in question in your sound bank.
When creating a new entry, you are prompted to enter both a key and a value. The value *must* be of type [int]. This will bring you back to the previous menu.
### Editing an existing entry
The previous key and value will be presented to you, with the option to edit both.
### Exit
Saves all changes and exits.
### Add preset
Adds a path to a specific config file. If you named your config file `test` (shows up as `test.midiconfig`), add the value `test` to reference that config. When completed, any value in `test` can be used in your patches.


## Stuffs that need doing
- Selecting a single file does God knows what right now
- Saving a MIDI port. The functionality is there, but config overwrites every time (to use this feature anyways, go to `json_default.py` and remove the `write_main_json_file()` function (removing the body, not the function itself) after **running the program once**.

