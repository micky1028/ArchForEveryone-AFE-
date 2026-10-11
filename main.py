import json
from modules.core import run_command, get_distro_info, enable_multilib
from modules.packages import install_pacman_packages, install_aur_packages
from modules.dotfile import create_symlink
from modules.services import enable_service

def load_settings(filepath="settings.json"):
    with open(filepath, "r") as f:
        return json.load(f)

def print_credits():
    print("========================================")
    print("        Linux For Everyone Setup        ")
    print("      Author: micky1028 (GitHub)        ")
    print("========================================")

def check_for_updates():
    print("[*] Checking for updates from GitHub...")
    try:
        run_command(["git", "pull"], as_root=False)
    except Exception as e:
        print(f"[!] Update check skipped or failed: {e}")

def select_multiple_items(items, title):
    if not items:
        return []
    print(f"\n[?] {title}:")
    print(f"    A) Install all")
    for idx, item in enumerate(items, 1):
        print(f"    {idx}) {item}")
    print(f"    0) Skip")
    
    while True:
        choice = input("\nEnter choices (e.g., '1 3', 'A' for all): ").strip().lower()
        if choice == "0" or not choice:
            return []
        if choice == "a":
            return items
        
        parts = choice.split()
        selected = []
        valid = True
        for p in parts:
            if p.isdigit() and 1 <= int(p) <= len(items):
                selected.append(items[int(p) - 1])
            else:
                valid = False
                break
        
        if valid:
            return selected
        print("[!] Invalid selection, try again.")

def select_item(items, title):
    if not items:
        return None
    print(f"\n[?] {title}:")
    print(f"    A) Install all (or first)")
    for idx, item in enumerate(items, 1):
        print(f"    {idx}) {item}")
    print(f"    0) Skip")
    
    while True:
        choice = input("\nEnter choice number or 'A': ").strip().lower()
        if choice == "0":
            return None
        if choice == "a":
            return items[0]
        if choice.isdigit() and 1 <= int(choice) <= len(items):
            return items[int(choice) - 1]
        print("[!] Invalid selection, try again.")

def main():
    check_for_updates()

    settings = load_settings()
    distro = get_distro_info()
    print(f"[*] Detected distribution: {distro['name']} ({distro['id']})")
    
    enable_multilib()

    print("[*] Synchronizing package databases...")
    try:
        run_command(["pacman", "-Sy", "--noconfirm"], as_root=True)
    except RuntimeError as e:
        print(f"[!] Warning during pacman sync: {e}")

    if settings.get("pacman_packages"):
        print("[*] Installing base pacman packages...")
        install_pacman_packages(settings["pacman_packages"])

    if settings.get("aur_packages"):
        print("[*] Installing AUR packages...")
        install_aur_packages(settings["aur_packages"])

    if settings.get("drivers"):
        selected_driver = select_item(settings["drivers"], "Select a GPU driver to install")
        if selected_driver:
            print(f"[*] Installing driver: {selected_driver}")
            try:
                install_pacman_packages([selected_driver])
            except RuntimeError as e:
                print(f"[!] Warning: Could not install driver '{selected_driver}': {e}")

    if settings.get("desktop_enviroments"):
        selected_de = select_item(settings["desktop_enviroments"], "Select a desktop environment to install")
        if selected_de:
            print(f"[*] Installing desktop environment: {selected_de}")
            install_pacman_packages([selected_de])

    if settings.get("browsers"):
        selected_browser = select_item(settings["browsers"], "Select a web browser to install")
        if selected_browser:
            print(f"[*] Installing browser: {selected_browser}")
            if selected_browser.endswith("-bin"):
                install_aur_packages([selected_browser])
            else:
                install_pacman_packages([selected_browser])

    interactive_categories = [
        "shells", 
        "programming_languages", 
        "office", 
        "multimedia", 
        "system_utilities", 
        "fonts", 
        "games"
    ]

    for category in interactive_categories:
        available_items = settings.get(category, [])
        if available_items:
            selected_items = select_multiple_items(available_items, f"Select {category} to install")
            if selected_items:
                print(f"[*] Installing selected {category}...")
                pacman_list = [p for p in selected_items if not p.endswith("-bin")]
                aur_list = [p for p in selected_items if p.endswith("-bin")]
                
                if pacman_list:
                    install_pacman_packages(pacman_list)
                if aur_list:
                    install_aur_packages(aur_list)

    services = settings.get("services", [])
    if services:
        print("[*] Enabling system services...")
        for srv in services:
            enable_service(srv)

    print("\n[*] Installation completed successfully!")
    print_credits()

if __name__ == "__main__":
    main()
    # 1. Aggiornamento finale del sistema
    print("\n[*] Performing final system update...")
    try:
        run_command(["pacman", "-Syu", "--noconfirm"], as_root=True)
    except RuntimeError as e:
        print(f"[!] Warning during final system upgrade: {e}")

    print("\n[*] Installation completed successfully!")
    print_credits()

    # 2. Richiesta di riavvio (y/n)
    while True:
        choice = input("\n[?] Do you want to reboot your system now? (y/n): ").strip().lower()
        if choice in ["y", "yes"]:
            print("[*] Rebooting system...")
            try:
                run_command(["reboot"], as_root=True)
            except Exception as e:
                print(f"[!] Could not reboot automatically: {e}")
            break
        elif choice in ["n", "no"]:
            print("[*] Skipping reboot. Remember to restart later!")
            break
        else:
            print("[!] Invalid choice. Please enter 'y' or 'n'.")