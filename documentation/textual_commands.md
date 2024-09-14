# Sending Commands
**[EXPERIMENTAL FEATURE]**

As of `v0.5.prerelease.3`, you can send commands to the `textual` port of the program.

To send commands, append to the `commands.txt` file found in the application's data directory.

*`commands.txt` gets cleared on application start, and technically, it is safe to delete all the contents of this file at any point.*

## List of commands:
### Performance Mode
The following commands are only available in Performance Mode. If performance mode is not enabled, these commands do nothing.
- `next_patch`: Progresses to the next patch in the current list. *Equivalent to `action_next_patch()`*.
- `previous_patch`: Jumps back to the previous patch in the current list. *Equivalent to `action_previous_patch()`*
- `next_patch_file`: Progresses to the next patch *file*. Equivalent to `action_next_patch_file()`
- `previous_patch_file`: Jumps back to the previous patch *file*. Equivalent to `action_previous_patch()`
- `set_patch_index [index: int]`: Sets the current patch index to `index`. If `index` is not given or is not an integer, nothing happens.


## Notes and Warnings
- ***DO NOT*** delete the `commands.txt` file during runtime! This could lead to several unknown problems. Instead, delete the contents of the file.
