# MIDI-CONTROLLER
## Overview
This is a project I started due to a lack of proper resources for creating patch lists for my Korg Kross 2 on Ubuntu.

This program is a command-line interface (CLI) program, built with Python, using the `mido` library for midi control, and the `curses` library for terminal styling.

## Ports
There are two ports to this program: `curses` and `textual`.

As of `v0.5`, the `curses` will no longer receive constant updates, with only bug fixes and minor features being added. It is highly recommended to use the `textual` port, which is compatible with the `curses` port, and has more features. At any time, it is possible to change ports without anything serious (*hopefully*) happening.

## Textual
This section refers to the `textual` port of the program. It is recommended to use this port, as it has more features and receives more frequent updates.
### Installation
Refer to the [Installation](documentation/textual/installation.md) page for more information.

### Usage
Refer to the [Usage](documentation/textual/usage.md) page for more information.

## Curses
This section refers to the `curses` port of the program. It is recommended to use the `textual` port, as it has more features and receives more frequent updates.
### Installation
Refer to the [Installation](documentation/curses/installation.md) page for more information.

### Basic Usage
Refer to the [Basic Usage](documentation/curses/basic_usage.md) page for more information.

## Something Missing?
If you think something isn't well-documented, or can't find a certain thing, see the [old instructions](documentation/curses/old_instructions.md) for the older version of this program.

If you think something is missing, or you have a suggestion, feel free to open an issue or a pull request!