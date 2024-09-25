# Usage
The program is split into two main parts: [performance](#Performance) and [patch management]().

## Performance
**Remember to plug in your Kross 2 before following the steps below**

To start a performance, select `Performance Mode` from the Main Menu. You will then be prompted to select a few files and folders to load.
You can re-arrange the files manually by pressing `Move Up`, `Move Down` and `Delete` to remove a file from the list.
Pressing the `Sort` button will sort the files by the criteria listed [here](#File-sorting).

Once you have selected the files, press `Start Performance` to start the performance. You will be asked to select a MIDI device to send the messages to.

### Performing
Once starting the performance, you will be able to navigate the lists with `Space` being next patch, and `Backspace` being the previous patch.

The `a` key will progress to the previous song, and the `d` key will progress to the next song.

#### Calibrating a switch pedal
This program recognizes switch pedals set up in a specific way. To calibrate your switch pedal, follow these steps:
1. Plug in a pedal into the `switch` port on your Korg Kross 2.
2. On the Kross, go to `GLOBAL/MEDIA > G-INPUT/CTRL > FOOT SW Assign` and set to `Foot Switch`
3. The program should now recognize your pedal as a switch pedal, and you can use it to progress through the patches.

## Patch Management
Patches are lists of sounds (and comments) that help you during your performance.

Configs provide a readable, rememberable name for a sound in your sound bank.

### Creating 

## File sorting
With the `Sort` button, the files are sorted by the following criteria:

File syntax (expected): `[number][captial_letter][space][name].midipatch`

Firstly, the files are sorted by the number, then by the capital letter, and finally by the name. If `[number]` isn't given, the file will be placed after all the numbered files.

Then, the files are sorted by the capital letter, and finally by the name. If `[capital_letter]` isn't given, it is ordered above all other files with numbers and a letter..

Finally, the files are sorted by the name.

Example:
```text
1 Song 1.midipatch
1A Song 1A.midipatch

2 Song 2.midipatch

A Song A.midipatch
B Song B.midipatch
Song C.midipatch
```