import curses


def getch_char(stdscr: curses.window) -> (str, int):
    given = stdscr.getch()
    return chr(given), given


def main(stdscr: curses.window):
    while True:
        stdscr.clear()
        stdscr.addstr("Press a key: ")
        stdscr.refresh()
        key, char = getch_char(stdscr)
        stdscr.addstr(f"\nYou pressed: {key} ({char})\n")
        stdscr.refresh()
        stdscr.getch()


        # stdscr.nodelay(True)
        # stdscr.timeout(100)
        # key = stdscr.getch()
        # stdscr.addstr(f"Key: {key}\n")


curses.wrapper(main)
