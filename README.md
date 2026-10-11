🚀 Etherean - Configuration Wizards (Arch Edition)

The mission of Etherean is to break down the barriers of entry to the Linux world, eliminating terminal intimidation and hours spent on tedious post-installation setups. This repository contains the official interactive configuration scripts designed to transform a clean Arch Linux installation into a fully featured, secure, and sleek system with just a single command.

This project is born from the intersection of Operating System development (OS Dev), automation, and Cybersecurity studies.
🌟 Project Philosophy

Many users abandon Arch Linux because they are intimidated by the command line or overwhelmed by the complexity of configuring multilib repositories, installing AUR helpers, setting up graphic drivers, or enabling 32-bit architectures for gaming.

Etherean solves this problem by automating the entire post-installation workflow through interactive scripts and modular configuration files that streamline everything smoothly.

The project is 100% Open Source (GPL v3 License) to guarantee complete transparency, security, and code auditability by the community.
🛠️ What is Automated on Arch Linux?

    Intelligent Repositories Setup: Automatically enables and configures the [multilib] repository in background silently for 32-bit application and gaming support.

    AUR Helper Bootstrapping: Automatically installs base development tools (base-devel, git) and bootstraps AUR support (yay / paru).

    Hardware & Drivers: Simplifies the detection and installation of GPU drivers (Nvidia, AMD, Intel) and system hardware utilities.

    Gaming Ready: Full support for steam, lutris, heroic-games-launcher-bin, and gaming dependencies.

    Productivity, Web & Shells: Lets you select your desktop environments, web browsers, shells, fonts, system utilities, and developer tools interactively.

    Terminal Aesthetics & Dotfiles: Symlinking and automatic environment setups for terminal customizations.

📂 Repository Structure

The project expands across the major families of the Linux ecosystem:

    🔹 Etherean_config.sh: Optimized script for Debian-based systems (Debian, Ubuntu, Linux Mint).

    🔸 Etherean_arch.sh / main.py: Variant for Arch-based systems (Arch Linux, EndeavourOS, CachyOS, Manjaro) with native AUR helper integration.

    🔻 Etherean_fedora.sh (Coming Soon): Variant for Fedora/RHEL-based systems utilizing DNF and RPM Fusion.

🚀 How to Run the Script (Arch Linux)

Open the terminal on your fresh Arch Linux installation and run these commands:
Bash

git clone https://github.com/micky1028/DebianForEveryone-DFE-.git
cd DebianForEveryone-DFE-

chmod +x USETHISFIRST.sh
./USETHISFIRST.sh

python3 main.py

👤 Author & Credits

    Author: micky1028 (GitHub)

    License: GPL v3 License
