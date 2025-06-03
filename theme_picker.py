#!/usr/bin/env python3

import os
import subprocess
import sys
from pathlib import Path

DOTFILES = Path.home() / ".dotfiles"
THEMES_DIR = DOTFILES / "themes"
WAYBAR_STYLE = Path.home() / ".config/waybar/style.css"
STARSHIP_CONFIG = Path.home() / ".config/starship.toml"
NEOFETCH_CUSTOM = Path.home() / ".config/neofetch/custom.txt"
NEOFETCH_CONFIG = Path.home() / ".config/neofetch/config.conf"

def get_available_themes():
    return sorted([d.name for d in THEMES_DIR.iterdir() if d.is_dir()])

def choose_theme(themes):
    try:
        result = subprocess.run(
            ["rofi", "-dmenu", "-p", "Escolha um tema:"],
            input="\n".join(themes),
            text=True,
            capture_output=True
        )
        return result.stdout.strip()
    except FileNotFoundError:
        print("❌ Rofi não encontrado.")
        sys.exit(1)

def apply_theme(theme):
    theme_path = THEMES_DIR / theme
    if not theme_path.exists():
        notify(f"Tema '{theme}' não encontrado!", error=True)
        sys.exit(1)

    # Wallpaper
    subprocess.run([
        "swww", "img", str(theme_path / "wallpaper.jpg"),
        "--transition-type", "any",
        "--transition-fps", "60",
        "--transition-duration", "0.7"
    ])

    # Waybar
    (theme_path / "waybar.css").replace(WAYBAR_STYLE)

    # Starship
    (theme_path / "starship.toml").replace(STARSHIP_CONFIG)

    # Neofetch
    os.makedirs(NEOFETCH_CUSTOM.parent, exist_ok=True)
    (theme_path / "neofetch.txt").replace(NEOFETCH_CUSTOM)

    # Atualizar config do neofetch
    if NEOFETCH_CONFIG.exists():
        with open(NEOFETCH_CONFIG, "r") as f:
            lines = f.readlines()
        with open(NEOFETCH_CONFIG, "w") as f:
            for line in lines:
                if line.startswith("image_source="):
                    f.write(f'image_source="{NEOFETCH_CUSTOM}"\n')
                else:
                    f.write(line)

    # Reinicia Waybar
    subprocess.run(["pkill", "waybar"])
    subprocess.Popen(["waybar"])

    notify(f"Tema '{theme}' aplicado com sucesso!")

def notify(message, error=False):
    icon = "dialog-error" if error else "preferences-desktop-theme"
    subprocess.run(["notify-send", "-i", icon, message])

if __name__ == "__main__":
    themes = get_available_themes()
    if not themes:
        notify("Nenhum tema encontrado!", error=True)
        sys.exit(1)

    selected = choose_theme(themes)
    if selected:
        apply_theme(selected)

