import os
import shutil
import subprocess

def get_distro_info():
    distro = {"id": "unknown", "name": "Unknown Linux"}
    try:
        with open("/etc/os-release", "r") as f:
            for line in f:
                if line.startswith("ID="):
                    distro["id"] = line.strip().split("=")[1].strip('"').lower()
                elif line.startswith("NAME="):
                    distro["name"] = line.strip().split("=")[1].strip('"')
    except FileNotFoundError:
        pass
    return distro
def enable_multilib():
    conf_path = "/etc/pacman.conf"
    if not os.path.exists(conf_path):
        return

    try:
        with open(conf_path, "r") as f:
            lines = f.readlines()

        new_lines = []
        multilib_section_found = False
        modified = False

        for line in lines:
            stripped = line.strip()
            if stripped == "#[multilib]":
                line = "[multilib]\n"
                multilib_section_found = True
                modified = True
            elif stripped == "[multilib]":
                multilib_section_found = True
            
            if multilib_section_found and "#Include = /etc/pacman.d/mirrorlist" in line:
                line = line.lstrip("#")
                multilib_section_found = False
                modified = True

            new_lines.append(line)

        if not any("[multilib]" in l for l in new_lines):
            new_lines.append("\n[multilib]\nInclude = /etc/pacman.d/mirrorlist\n")
            modified = True

        # Scrive le modifiche solo se è stato effettivamente modificato qualcosa
        if modified:
            import tempfile
            with tempfile.NamedTemporaryFile("w", delete=False) as tmp:
                tmp.writelines(new_lines)
                tmp_path = tmp.name

            # Esegue la copia silenziosamente (senza stampe)
            subprocess.run(["cp", tmp_path, conf_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            os.unlink(tmp_path)
    except Exception:
        pass  # Ignora eventuali errori silenziosamente
    
def check_environment():
    is_root = os.geteuid() == 0
    has_sudo = shutil.which("sudo") is not None
    return {"is_root": is_root, "has_sudo": has_sudo}

def run_command(cmd, as_root=False):
    env = check_environment()
    if as_root and not env["is_root"]:
        if env["has_sudo"]:
            cmd = ["sudo"] + cmd
        else:
            raise PermissionError("Root privileges required but sudo is not available.")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)} with exit code {result.returncode}")
    return True