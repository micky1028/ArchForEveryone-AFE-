"""Turns the wizard's choices into an ordered install plan and runs it.

Order and rules mirror main.py, so the terminal UI and the plain CLI behave the same:
  * drivers and desktop environments always go through pacman
  * everything else ending in "-bin" goes through the AUR helper
  * the final full upgrade comes last
"""
from modules.core import run_command, enable_multilib
from modules.packages import install_pacman_packages, install_aur_packages
from modules.services import enable_service

# Same spelling as settings.json ("desktop_enviroments").
FORCE_PACMAN = ("drivers", "desktop_enviroments")

LABELS = {
    "drivers": "GPU driver",
    "desktop_enviroments": "desktop environment",
    "browsers": "web browser",
}


def is_aur(key, pkg):
    return key not in FORCE_PACMAN and pkg.endswith("-bin")


def _pretty(key):
    return LABELS.get(key, key.replace("_", " "))


def build_plan(settings, selection):
    """Return [(label, kind, payload)] in execution order."""
    plan = [
        ("Enabling the multilib repository", "multilib", None),
        ("Synchronizing package databases", "sync", None),
    ]
    if settings.get("pacman_packages"):
        plan.append(("Installing base pacman packages", "pacman", list(settings["pacman_packages"])))
    if settings.get("aur_packages"):
        plan.append(("Installing base AUR packages", "aur", list(settings["aur_packages"])))

    for key, choice in selection.items():
        pkgs = [choice] if isinstance(choice, str) else list(choice or [])
        pacman = [p for p in pkgs if not is_aur(key, p)]
        aur = [p for p in pkgs if is_aur(key, p)]
        if pacman:
            plan.append((f"Installing {_pretty(key)}", "pacman", pacman))
        if aur:
            plan.append((f"Installing {_pretty(key)} (AUR)", "aur", aur))

    for srv in settings.get("services", []):
        plan.append((f"Enabling service {srv}", "service", srv))

    plan.append(("Performing final system upgrade", "upgrade", None))
    return plan


def describe(kind, payload):
    """Commands a step would run (used by --dry-run)."""
    if kind == "multilib":
        return ["uncomment [multilib] in /etc/pacman.conf"]
    if kind == "sync":
        return ["pacman -Sy --noconfirm"]
    if kind == "pacman":
        return [f"pacman -S --noconfirm --needed {p}" for p in payload]
    if kind == "aur":
        return ["(install yay first if missing)"] + [f"yay -S --noconfirm --needed {p}" for p in payload]
    if kind == "service":
        return [f"systemctl enable --now {payload}"]
    if kind == "upgrade":
        return ["pacman -Syu --noconfirm"]
    return []


def execute(plan, dry_run=False):
    """Run the plan in the normal terminal. Returns the labels of steps that failed."""
    failures = []
    for label, kind, payload in plan:
        print(f"\n[*] {label}...")
        if dry_run:
            for line in describe(kind, payload):
                print(f"    $ {line}")
            continue
        try:
            if kind == "multilib":
                enable_multilib()
            elif kind == "sync":
                run_command(["pacman", "-Sy", "--noconfirm"], as_root=True)
            elif kind == "pacman":
                install_pacman_packages(payload)
            elif kind == "aur":
                install_aur_packages(payload)
            elif kind == "service":
                enable_service(payload)
            elif kind == "upgrade":
                run_command(["pacman", "-Syu", "--noconfirm"], as_root=True)
        except Exception as e:  # keep going, report at the end
            print(f"[!] Warning: {label} failed: {e}")
            failures.append(label)
    return failures
