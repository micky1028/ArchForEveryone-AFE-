import json
from modules.core import run_command, get_distro_info, enable_multilib
from modules.packages import install_pacman_packages, install_aur_packages
from modules.services import enable_service
from modules.ui import run_wizard

def load_settings(filepath="settings.json"):
    with open(filepath, "r") as f:
        return json.load(f)

def print_credits():
    print("========================================")
    print("        Etherean Arch Setup Wizard      ")
    print("      Author: micky1028 (GitHub)        ")
    print("========================================")

def check_for_updates():
    print("[*] Checking for updates from GitHub...")
    try:
        run_command(["git", "pull"], as_root=False)
    except Exception as e:
        print(f"[!] Update check skipped or failed: {e}")

def main():
    check_for_updates()

    settings = load_settings()
    distro = get_distro_info()

    # 1. Abilitazione silenziosa del multilib in background
    enable_multilib()

    # 2. Avvio del Wizard interattivo con Curses (con controllo errori)
    print("[*] Starting Etherean TUI configuration wizard...")
    try:
        user_choices = run_wizard(settings, distro)
    except Exception as e:
        import traceback
        print(f"\n[!] ERROR in Wizard Curses: {e}")
        traceback.print_exc()
        input("\nPress Enter to exit...")
        return

    # Se l'utente preme 'q' o esce dal wizard senza confermare
    if user_choices is None:
        print("\n[!] Setup aborted by user. Exiting.")
        return

    print("\n[*] Synchronizing package databases...")
    try:
        run_command(["pacman", "-Sy", "--noconfirm"], as_root=True)
    except RuntimeError as e:
        print(f"[!] Warning during pacman sync: {e}")

    # 3. Installazione dei pacchetti base fissi da settings.json
    if settings.get("pacman_packages"):
        print("[*] Installing base pacman packages...")
        install_pacman_packages(settings["pacman_packages"])

    if settings.get("aur_packages"):
        print("[*] Installing base AUR packages...")
        install_aur_packages(settings["aur_packages"])

    # 4. Installazione dei componenti scelti interattivamente tramite il Wizard
    for key, choice in user_choices.items():
        if not choice:
            continue

        items_to_install = [choice] if isinstance(choice, str) else choice

        if items_to_install:
            print(f"[*] Installing {key}: {', '.join(items_to_install)}")
            pacman_list = [p for p in items_to_install if not p.endswith("-bin")]
            aur_list = [p for p in items_to_install if p.endswith("-bin")]

            if pacman_list:
                install_pacman_packages(pacman_list)
            if aur_list:
                install_aur_packages(aur_list)

    # 5. Attivazione dei servizi di sistema
    services = settings.get("services", [])
    if services:
        print("[*] Enabling system services...")
        for srv in services:
            enable_service(srv)

    # 6. Aggiornamento finale del sistema (pacman -Syu)
    print("\n[*] Performing final system upgrade...")
    try:
        run_command(["pacman", "-Syu", "--noconfirm"], as_root=True)
    except RuntimeError as e:
        print(f"[!] Warning during final system upgrade: {e}")

    print("\n[*] Installation completed successfully!")
    print_credits()

    # 7. Richiesta finale di riavvio (y/n)
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

if __name__ == "__main__":
    main()
