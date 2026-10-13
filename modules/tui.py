#!/usr/bin/env python3
"""Terminal UI for Etherean (Arch Edition).

    python3 tui.py             # choose with the UI, then install
    python3 tui.py --dry-run   # choose with the UI, only print what would run

The plain wizard is still available with: python3 main.py
"""
import argparse
import curses
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from main import load_settings, check_for_updates, print_credits  # noqa: E402
from modules.core import get_distro_info, check_environment, run_command  # noqa: E402
from modules.plan import build_plan, execute  # noqa: E402
from modules.ui import run_wizard  # noqa: E402


def system_info():
    distro, env = get_distro_info(), check_environment()
    if env["is_root"]:
        privileges = "root"
    elif env["has_sudo"]:
        privileges = "sudo available"
    else:
        privileges = "NONE - run as root or install sudo"
    return {"name": distro["name"], "id": distro["id"], "privileges": privileges,
            "is_arch": os.path.exists("/etc/arch-release")}


def ask_reboot():
    while True:
        choice = input("\n[?] Do you want to reboot your system now? (y/n): ").strip().lower()
        if choice in ("y", "yes"):
            print("[*] Rebooting system...")
            try:
                run_command(["reboot"], as_root=True)
            except Exception as e:
                print(f"[!] Could not reboot automatically: {e}")
            return
        if choice in ("n", "no"):
            print("[*] Skipping reboot. Remember to restart later!")
            return
        print("[!] Invalid choice. Please enter 'y' or 'n'.")


def main():
    parser = argparse.ArgumentParser(description="Etherean terminal UI (Arch Edition)")
    parser.add_argument("--dry-run", action="store_true",
                        help="pick packages in the UI and print the plan without changing anything")
    parser.add_argument("--settings", default=os.path.join(HERE, "settings.json"),
                        help="path to the settings file (default: settings.json next to this script)")
    args = parser.parse_args()
    settings_path = os.path.abspath(args.settings)

    os.chdir(HERE)  # `git pull` must run inside the project
    if not args.dry_run:
        check_for_updates()

    try:
        settings = load_settings(settings_path)
    except (OSError, ValueError) as e:
        sys.exit(f"[!] Cannot read {settings_path}: {e}")

    try:
        selection = run_wizard(settings, system_info(), args.dry_run)
    except curses.error as e:
        sys.exit(f"[!] Could not start the terminal UI ({e}).\n"
                 "    Run it from a real terminal, or use the plain wizard: python3 main.py")
    except KeyboardInterrupt:
        selection = None

    if selection is None:
        print("[*] Cancelled - nothing was installed.")
        return

    failures = execute(build_plan(settings, selection), dry_run=args.dry_run)

    if args.dry_run:
        print("\n[*] Dry run finished - nothing was changed.")
        return
    if failures:
        print("\n[!] These steps reported problems:")
        for label in failures:
            print(f"    - {label}")
    print("\n[*] Installation completed!")
    print_credits()
    ask_reboot()


if __name__ == "__main__":
    main()
