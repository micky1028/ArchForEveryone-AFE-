import shutil
import subprocess
from modules.core import run_command

def install_pacman_packages(packages):
    if not packages:
        return
    print(f"[*] Installing pacman packages: {', '.join(packages)}")
    for pkg in packages:
        try:
            run_command(["pacman", "-S", "--noconfirm", "--needed", pkg], as_root=True)
        except RuntimeError as e:
            print(f"[!] Warning: Could not install package '{pkg}': {e}")

def install_yay():
    if shutil.which("yay"):
        print("[*] Yay is already installed. Skipping.")
        return

    print("[*] Yay not found. Installing yay-bin...")
    run_command(["pacman", "-S", "--noconfirm", "--needed", "git", "base-devel"], as_root=True)
    subprocess.run("git clone https://aur.archlinux.org/yay-bin.git /tmp/yay-bin", shell=True, check=True)
    subprocess.run("cd /tmp/yay-bin && makepkg -si --noconfirm", shell=True, check=True)
    subprocess.run("rm -rf /tmp/yay-bin", shell=True, check=True)

def install_paru():
    if shutil.which("paru"):
        print("[*] Paru is already installed. Skipping.")
        return

    print("[*] Paru not found. Installing paru-bin...")
    run_command(["pacman", "-S", "--noconfirm", "--needed", "git", "base-devel"], as_root=True)
    subprocess.run("git clone https://aur.archlinux.org/paru-bin.git /tmp/paru-bin", shell=True, check=True)
    subprocess.run("cd /tmp/paru-bin && makepkg -si --noconfirm", shell=True, check=True)
    subprocess.run("rm -rf /tmp/paru-bin", shell=True, check=True)

def install_aur_packages(packages, aur_helper="yay"):
    if not packages:
        return
    
    # Assicura che l'helper scelto sia installato prima di usarlo
    if aur_helper == "yay":
        install_yay()
    elif aur_helper == "paru":
        install_paru()
    else:
        if not shutil.which(aur_helper):
            raise RuntimeError(f"AUR helper '{aur_helper}' is not installed.")

    print(f"[*] Installing AUR packages via {aur_helper}: {', '.join(packages)}")
    for pkg in packages:
        try:
            run_command([aur_helper, "-S", "--noconfirm", "--needed", pkg], as_root=False)
        except RuntimeError as e:
            print(f"[!] Warning: Could not install AUR package '{pkg}': {e}")