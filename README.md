# 🚀 Etherean - Configuration Wizards (Arch Edition)

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![OS: Arch Linux](https://img.shields.io/badge/OS-Arch%20Linux-blueviolet.svg?logo=arch-linux&logoColor=white)](https://archlinux.org)
[![Author: micky1028](https://img.shields.io/badge/Author-micky1028-orange.svg?logo=github)](https://github.com/micky1028)

The mission of **Etherean** is to break down the barriers of entry to the Linux world, eliminating terminal intimidation and hours spent on tedious post-installation setups. This repository contains the official interactive configuration tools designed to transform a clean Arch Linux installation into a fully featured, secure, and sleek system with just a single command.

This project is born from the intersection of Operating System development (OS Dev), automation, and Cybersecurity studies.

---

## 🌟 Project Philosophy

Many users avoid or abandon Arch Linux because they are intimidated by manual configuration, setting up multilib repositories, installing AUR helpers, configuring GPU drivers, or managing dependencies for gaming and productivity.

**Etherean** solves this problem by automating the entire post-installation workflow through interactive prompts and a modular setup wizard.

The project is **100% Open Source (GPL v3 License)** to guarantee complete transparency, security, and full code auditability by the community.

---

## 🛠️ What is Automated on Arch Linux?

* **Intelligent Repository Setup**: Silently configures and enables the `[multilib]` repository in `/etc/pacman.conf` for 32-bit applications and gaming compatibility.
* **AUR Helper Bootstrapping**: Automatically installs `base-devel`, `git`, and manages AUR helpers like `yay` or `paru`.
* **Hardware & Drivers**: Seamlessly handles selection and installation for NVIDIA, AMD, or Intel graphics drivers.
* **Gaming Ready**: One-click selection for `steam`, `lutris`, `heroic-games-launcher-bin`, and gaming runtimes.
* **Interactive Package Selection**: Choice-driven menus with an **"Install All" (A)** option across browsers, shells, programming tools, multimedia apps, utilities, and fonts.
* **System Maintenance & Reboots**: Handles initial database synchronization (`pacman -Sy`), checks for GitHub repo updates (`git pull`), performs a final full upgrade (`pacman -Syu`), and offers an automatic reboot prompt upon completion.

---

## 📂 Project Architecture

```text
ArchForEveryone-AFE-/
├── USETHISFIRST.sh       # Environment bootstrap script
├── main.py               # Main Python configuration wizard
├── settings.json         # Modular software & package mappings
└── modules/
    ├── core.py           # Execution commands & silent multilib handling
    ├── packages.py       # Pacman & AUR installation engines
    ├── dotfile.py        # Dotfile symlinking helper
    └── services.py       # Systemd service manager
```
USE THIS SCRIPT!:
```
git clone [https://github.com/micky1028/ArchForEveryone-AFE-.git](https://github.com/micky1028/ArchForEveryone-AFE-.git)
cd ArchForEveryone-AFE
chmod +x USETHISBEFORE.sh
./USETHISBEFORE.sh
```

and after use:
```
python3 main.py
```


