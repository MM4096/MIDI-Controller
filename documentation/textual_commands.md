# Info
You can send and receive messages to the `textual` port of this program through `comamnds.txt` and `output.txt` respectively.

For more information, see:
- [Sending Commands](#sending-commands)
- [Receiving Commands](#receiving-messages)

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


# Receiving Messages
**[EXPERIMENTAL FEATURE]**

As of `v0.5.prerelease.3`, you can also receive commands to the `textual` port of the program.

To receive commands, read the `output.txt` file found in the application's data directory.

*`output.txt` gets cleared on application start, and it is safe to delete the contents of this file at any time, given the receiver can handle this*.

## List of Messages:
| **Message**           | **Description**                                                                                          |
|-----------------------|----------------------------------------------------------------------------------------------------------|
| `performance_started` | Emitted when a new performance is started. Specifically, when `PerformanceScreen` is mounted.            |
| `performance_ended`   | Emitted when a performance is ended. Specifically, when `PerformanceScreen` is unmounted.                |
| `performance_updated` | Emitted when the performance patch is updated, either from pedal inputs or from the `commands.txt` file. | 


## Specifics
This section will detail the specifics of more complicated messages, and what they mean.

### performance_updated
This is emitted when the `update()` function is called on `PerformanceScreen`, usually from performance progression.

#### Syntax:
`performance_updated<~separator~>[current_file_path: str]<~separator~>[file_list: list[str]]<~separator~>[current_patch_list: list]<~separator~>[current_patch_name: str]<~separator~>[current_patch_index: int]`

#### Args:
- `current_file_path: str`: The local path of the patch file (absolute)
- `file_list: list[str]`: A list of paths for the current performance, in performance order
- `current_patch_list: list`: The current patch list, a dumped `json` object containing a list of the format `{sound: [sound: str], comments: [comments: str]}`
- `current_patch_index: str`: The name of the current patch list
- `current_patch_index: int`: The index of the currently-selected patch