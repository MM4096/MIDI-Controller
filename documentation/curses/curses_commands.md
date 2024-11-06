# Curses Commands
This page lists all the commands available in the `curses` port of the program.
## How to access commands
To enter a command, press `:` in the performance page. Then, start typing. While editing a command, you will not be able to progress in any way through the patches. Pressing either `Enter` or `Esc` will leave the command editing area.

At all times while editing the command, a description of the command you entered (if valid) will be displayed on the first line.

## List of commands
| **Command** | **Description**                                                       | **Arguments**     |
|-------------|-----------------------------------------------------------------------|-------------------|
| `goto`      | Go to the first patch that matches the given name (see [goto](#goto)) | `patch_name: str` |
| `exit`      | Leave performance mode and return to the main menu                    | None              |
| `next`      | Progress to the next patch *file* in the list                         | None              |
| `prev`      | Jump back to the previous patch *file* in the list                    | None              |

## Specifics
### General
*Name of Patch* refers to the name of the patch as displayed in the patch list.
### `goto`
The command will return a patch by following these steps:
1. If the given input matches the name of a patch completely, the program will go to that patch.
2. If a patch name starts with the given input, the program will go to the first patch that matches the input.
3. If a patch name contains the given input, the program will go to the first patch that matches the input.
4. If no patch matches the input, nothing will happen.