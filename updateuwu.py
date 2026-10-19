#!/usr/bin/env python3
import curses
import shutil
import subprocess
import sys

ASCII_ART = [
    r"        /\_____/\        ",
    r"       /  /   \  \       ",
    r"      /  /  /\ \  \      ",
    r"     |  | (•) (•) | |    ╭──────────────────────────────────────────╮",
    r"     |  |  \" ◡ \"  | |    │  Okaeri, Arch-sama! ~                    │",
    r"     |   \       /  |    │  Which repo are we updating today? uwu   │",
    r"      \   '-----'  /     ╰──────────────────────────────────────────╯",
    r"      / '-._____.-' \    ",
    r"     /   /       \   \   ",
]

MENU_ITEMS = [
    ("📦 Update Pacman Repo Only", "pacman"),
    ("✨ Update AUR Repo Only", "aur"),
    ("🚀 Update Both (Pacman + AUR)", "both"),
    ("🧹 Clean Package Cache", "clean"),
    ("❌ Exit uwu", "exit"),
]


def get_aur_helper():
    for helper in ("paru", "yay"):
        if shutil.which(helper):
            return helper
    return None


def run_update_command(choice):
    aur_helper = get_aur_helper()

    print("\033[1;35m" + "═" * 56 + "\033[0m")
    if choice == "pacman":
        print("\033[1;36m[updateuwu] Running Official Pacman Update (sudo pacman -Syu)...\033[0m\n")
        subprocess.run(["sudo", "pacman", "-Syu"])

    elif choice == "aur":
        if not aur_helper:
            print("\033[1;31m[!] Neither 'yay' nor 'paru' was found on your system!\033[0m")
        else:
            print(f"\033[1;36m[updateuwu] Running AUR-Only Update ({aur_helper} -Sua)...\033[0m\n")
            subprocess.run([aur_helper, "-Sua"])

    elif choice == "both":
        if not aur_helper:
            print("\033[1;33m[!] No AUR helper found. Falling back to sudo pacman -Syu...\033[0m\n")
            subprocess.run(["sudo", "pacman", "-Syu"])
        else:
            print(f"\033[1;36m[updateuwu] Running Full System Update ({aur_helper} -Syu)...\033[0m\n")
            subprocess.run([aur_helper, "-Syu"])

    elif choice == "clean":
        if aur_helper:
            print(f"\033[1;36m[updateuwu] Cleaning cache with {aur_helper} -Sc...\033[0m\n")
            subprocess.run([aur_helper, "-Sc"])
        else:
            print("\033[1;36m[updateuwu] Cleaning cache with sudo pacman -Sc...\033[0m\n")
            subprocess.run(["sudo", "pacman", "-Sc"])

    print("\n\033[1;35m" + "═" * 56 + "\033[0m")
    input("\033[1;32m✔ All done, Senpai! Press [Enter] to return to updateuwu...\033[0m")


def draw_menu(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)

    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_MAGENTA, -1)  # Anime art & borders
        curses.init_pair(2, curses.COLOR_CYAN, -1)     # Title & highlights
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_MAGENTA)  # Selected item
        curses.init_pair(4, curses.COLOR_WHITE, -1)    # Unselected item

    current_row = 0
    aur_helper = get_aur_helper() or "None detected"

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        try:
            # Header
            title = "🌸  U P D A T E U W U  —  A R C H   U P D A T E R  🌸"
            stdscr.addstr(1, max(2, (width - len(title)) // 2), title, curses.color_pair(2) | curses.A_BOLD)

            # ASCII Anime Girl
            for idx, line in enumerate(ASCII_ART):
                stdscr.addstr(3 + idx, 4, line, curses.color_pair(1) | curses.A_BOLD)

            # Status bar
            status_line = f"Detected AUR Helper: {aur_helper}  |  Navigate: ↑/↓ or j/k  |  Select: Enter  |  Quit: q"
            stdscr.addstr(13, 4, status_line, curses.color_pair(2))
            stdscr.addstr(14, 4, "─" * min(width - 8, 72), curses.color_pair(1))

            # Menu Options
            for idx, (label, _) in enumerate(MENU_ITEMS):
                y = 16 + idx
                if idx == current_row:
                    stdscr.addstr(y, 6, f" ▶  {label}  ", curses.color_pair(3) | curses.A_BOLD)
                else:
                    stdscr.addstr(y, 6, f"    {label}  ", curses.color_pair(4))

        except curses.error:
            # Prevent crash if terminal window is resized too small
            stdscr.addstr(0, 0, "Please enlarge your terminal window uwu!")

        stdscr.refresh()
        key = stdscr.getch()

        if key in (curses.KEY_UP, ord("k")) and current_row > 0:
            current_row -= 1
        elif key in (curses.KEY_DOWN, ord("j")) and current_row < len(MENU_ITEMS) - 1:
            current_row += 1
        elif key in (ord("q"), ord("Q"), 27):  # q or ESC
            break
        elif key in (curses.KEY_ENTER, 10, 13):
            selected_action = MENU_ITEMS[current_row][1]
            if selected_action == "exit":
                break

            # Temporarily suspend curses so pacman/yay works natively in the terminal
            curses.def_prog_mode()
            curses.endwin()
            subprocess.run(["clear"])
            run_update_command(selected_action)
            curses.reset_prog_mode()
            stdscr.refresh()


def main():
    try:
        curses.wrapper(draw_menu)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()