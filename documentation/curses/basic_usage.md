# Basic Usage
If you have not installed the program yet, see the [Installation](installation.md) page.
### Table of Contents
- [Overview](#overview)
- [Performance Mode](#performance-mode)
  - [Performing a single patch](#performing-a-single-patch) 
  - [Performing a list of patches (folder)](#performing-a-list-of-patches-folder)
  - [Actually performing](#actually-performing)
    - [Keybinds](#keybinds)
  - [Calibrating a switch pedal](#calibrating-a-switch-pedal)
- [Navigating the file system](#navigating-the-file-system)
  - [File selection](#file-selection)
  - [Folder selection](#folder-selection)

## Overview
This app is divided into two main parts: **Performance Mode** and **Patch Editing**.

To navigate the app, use the arrow keys to move up and down, and the `Enter` key to select an option.

For input, use the `Enter` key to confirm, and the `Backspace` key to delete characters.

## Patch/Config Editing
This is where you can create and edit patches and configs. To get to this page, run the program and select `Patch/Config Editing`.
### How this works
This is a very brief overview of how the patch/config system works. For more information, see the [In Depth Usage](in_depth_usage.md) page.

When performing, a patch is loaded. This patch file contains the following:
- The name of the patch (if not specified, the file name is used)
- A config section, with support for adding in a preset. This is a list of keys and values, with the key being the alias and the value being the sound in question in your sound bank.
This is to massively simplify the process of creating a patch, as you can just select the alias instead of the sound number.
  - If a preset is added, the preset, which is just a "global config" that can be used for multiple patches (like one for an entire show), will be loaded alongside the config specified in the patch file. 

### Sound bank numbers
The Korg Kross 2 has 8 sound banks, each storing 16 sounds, for a total of 128.
These sounds are 0-indexed, so the first sound in the first bank is 0, and the last sound in the last bank is 127.
For example, the first sound in bank A is 0, and first sound in bank B is 15.


### Creating/Editing a patch
Select the `Create/Edit patches` option. Then, select `Create a patch` to create a new patch, or `Edit a patch` to edit an existing patch.
#### Creating a patch
You will be prompted to select a folder to store your patch in. Note that there is no way of creating folders currently, this feature will be added in later releases. To add a folder, you will need to visit
the `user_data_dir()` and create a folder there (see [In-Depth Usage](in_depth_usage.md) for details).

Then, enter a filename at the prompt. **DO NOT** include the `.midipatch` extension, as the program will do so automatically.

Then, see [Editing a patch](#editing-a-patch) to see how to edit your newly-created patch.

#### Editing a patch
Here, there are 3 options, `Edit patch config`, `Edit patch list`, and `Back`.
Each process will save the file automatically, so you don't need to worry about that.

`Edit patch config` will allow you to edit the config section of the patch. This is where you can add presets, or change the keys/values of the patch.
See [Creating/Editing configs](#creatingediting-configs) for more information.

`Edit patch list` will open `gedit` with the patch file. Here, you can edit the patch list, which is the order of sounds to play in the patch. This is a list of sound aliases, or sound numbers in your sound bank.
Just follow the instructions given, they should be quite easy to understand. 

After making your changes, save the file with `CTRL + S` then close `gedit`. These changes will be updated in your patch file.

***NOTE:*** The name of a patch is currently bugged and doesn't work.

### Creating/Editing configs
If you are creating a pure config file, you will be asked to either select an existing config file or
to create one. **DO NOT** include the `.midiconfig` extension, as the program will do so automatically.

The config editor is quite simple, and hopefully intuitive, you can select a key to edit it, or remove a key, or create a key.

The name of your key is the alias, and you can use that instead of bank numbers for simplicity's sake.

The value of your key is the [sound bank number](#sound-bank-numbers) that corresponds to that sound.

**If you chose this option when editing a patch**: You will get the `Add Preset` option, which will allow you to specify
a config file to use. Pass in the name of your config file, excluding the `.midiconfig` part, so if you named your config file `test`,
put `test` as the preset value. *You can only have one preset per patch*, and this will allow you to use keys from your config file
in your patch without having to copy the configs into the patch's own config section.


## Performance Mode
This is the main star of this project, allowing for playback of created lists. To get to this page, run the program and select `Performance Mode`.

You will then need to choose your Korg Kross 2 in the options given. If you want to test features, select the default `Midi Through` option.

Then, depending on your choice, select a mode of playback:
### Performing a single patch
Select a `.midipatch` file to play. See [File selection](#file-selection) for more information.

A prompt will ask you to confirm your choice. Selecting `No` will bring you back out to `Performance Mode`
### Performing a list of patches (folder)
Select a folder to play. See [Folder selection](#folder-selection) for more information.

This will play all `.midipatch` files in the selected folder. A prompt will ask you to confirm your choice. Selecting `No` will bring you back out to `Performance Mode`.

It is recommended to append the order to the beginning of each patch to ensure the correct order of playback.

### Actually performing
Select which patch to play first. The current patch will be shown, with all the soundlists given. The current sound is marked with a `>`. Pressing `[Enter]` will go to the next patch in this list.

When reaching the end of the list, a second `[Enter]` press is needed to bring you to the next list as shown below all the options. If there are no more, a loop back to the start will commence.

#### Keybinds
In `Performance Mode`, the following keybinds are available:
- `Enter`/`Space`/`Switch Pedal` (if calibrated, see [calibrating a switch pedal](#calibrating-a-switch-pedal)): Next patch
- `Backspace`/`Up_arrow`: Previous patch (***NOTE: AS OF VERSION 0.3, UP_ARROW does not bring you back a patch***)
- `Escape`: Go back to the `Performance Mode` menu

### Calibrating a switch pedal
This program recognizes switch pedals set up in a specific way. To calibrate your switch pedal, follow these steps:
1. Plug in a pedal into the `switch` port on your Korg Kross 2.
2. On the Kross, go to `GLOBAL/MEDIA > G-INPUT/CTRL > FOOT SW Assign` and set to `Foot Switch`
3. The program should now recognize your pedal as a switch pedal.


## Navigating the file system
There are two *different* file system types: **file selection** and **folder selection**.

### General navigation
Again, use the arrow keys to move up and down, and the `Enter` key to select an option.

There is a line showing the current directory you are in.

The `..` option brings you out a directory. 

**NOTE:** you *cannot* leave the user data directory. This is to stop you from accidentally deleting/overwriting important files.

Any line starting with a `/` is a directory, and they will always appear first in the list.
To enter a directory, select it with the `Enter` key.
### File selection
Here, the file selection process will continue until you select a file. 

**NOTE**: Depending on the current action, only certain files will be shown. For example, when selecting a patch, only `.midipatch` files will be shown.

### Folder selection
No files are shown in this mode.

To select a folder, enter the folder with the `Enter` key, then press `Select` to confirm your choice.

To create a new folder, select `Create new folder` and enter the name of the folder. This will create a new folder in the current directory.

## Patch/Config Creation/Editing
This is where you can create and edit patches and configs. To get to this page, run the program and select `Patch/Config Editing`.
### The basics
In this controller, patches are the main way of playing sounds. A patch is a list of sounds to play, and a config is a list of keys and values that correspond to the sounds in your sound bank.

When performing, a patch is loaded. This patch file contains the following:
- The name of the patch (if not specified, the file name is used)
- A config section, with support for adding in a preset. This is a list of keys and values, with the key being the alias and the value being the sound in question in your sound bank.
- A list of sounds to play, in the order specified.

A preset can be defined (an external config file), and the patch will use the keys from the preset and the keys from the config, with the preset's keys taking priority.

### Sound bank numbers
The Korg Kross 2 has 8 sound banks, each storing 16 sounds, for a total of 128.
The banks are lettered A-H, and the numbers are numbered from 1-16.

To convert a bank number to a sound number, use the formula `(bank_number - 1) * 16 + (sound_number - 1)`.

*Some examples*:
- The first sound in bank A is 0
- The second sound in bank B is `(2 - 1) * 16 + (2 - 1) = 17`

### Creating/Editing a patch
Select the `Create/Edit patches` option. Then, select `Create a patch` to create a new patch, or `Edit a patch` to edit an existing patch.

If a default preset is set, you will be asked if you want to use the preset. If you select `Yes`, the preset will be loaded alongside the patch's config.

Then, select one of the following options:
- `Edit patch config`: Edit the config section of the patch. This is where you can add presets, or change the keys/values of the patch.
- `Edit patch list`: Edit the list of sounds to play in the patch. This is a list of sound aliases, or sound numbers in your sound bank.
- `Back`: Save and return.

#### Edit patch config
See [Creating/Editing configs](#creatingediting-configs) for more information. There is an extra option: `add preset`, which will allow you to specify a config file to use as a preset. This defaults to `user_data_dir()/presets/{given name}`.

#### Edit patch list
This opens the list in an external editor (`nano`, unless specified in the Preferences).

Follow the instructions given in the file. Comments start with a `#`.

The first non-commented line is the title line, where the filename is filled in. Changing this changes the name of the patch.

A list of usable sounds is given at the top of the file, and you can use these to specify the sounds in your patch. This is loaded from the config.
Otherwise, you can use integers (`0 <= x <= 127`) to specify the sound in your sound bank.
Put this list at the end of the file, separating each sound with a newline.

If you want to add notes to a sound, add ` -- ` to the end of the sound, then write your note. This will be shown in the performance mode.
When finished, save and exit the file. Your changes will be parsed and saved (`Control + S` then `Control + X` in `nano`)

## Creating/Editing configs
If you are creating a pure config file, you will be asked to either select an existing config file or create a new one.

The default

