#!/usr/bin/env python3
import os
import subprocess
import sys
import json
import hashlib
from pathlib import Path
from threading import Thread
import time
import random
import logging

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path.home() / 'theme_picker.log'),
        logging.StreamHandler()
    ]
)

# Configurações
HOME = Path.home()
DOTFILES_DIR = HOME / ".dotfiles"
THEMES_DIR = DOTFILES_DIR / "themes"
WALLPAPER_DIR = DOTFILES_DIR / "swww/wallpapers"
DEFAULT_WALLPAPER = WALLPAPER_DIR / "default.jpg"

# Garante diretórios existem
THEMES_DIR.mkdir(parents=True, exist_ok=True)
WALLPAPER_DIR.mkdir(parents=True, exist_ok=True)

class ThemeManager:
    def __init__(self):
        self.verify_themes()
        self.create_default_theme()

    def verify_themes(self):
        """Verifica se há temas disponíveis"""
        if not any(THEMES_DIR.iterdir()):
            logging.warning("Nenhum tema encontrado! Criando tema padrão...")
            self.create_default_theme()

    def create_default_theme(self):
        """Cria tema padrão se necessário"""
        default_theme = THEMES_DIR / "default"
        default_theme.mkdir(exist_ok=True)
        
        # Cria wallpaper padrão se não existir
        default_wp = default_theme / "default.jpg"
        if not default_wp.exists():
            if not DEFAULT_WALLPAPER.exists():
                subprocess.run([
                    "convert", "-size", "1920x1080", "xc:#2563eb", 
                    str(DEFAULT_WALLPAPER)
                ])
            default_wp.symlink_to(DEFAULT_WALLPAPER)
        
        logging.info(f"Tema padrão criado: {default_theme}")

    def get_available_themes(self):
        """Retorna lista de temas disponíveis"""
        return [d.name for d in THEMES_DIR.iterdir() if d.is_dir()]

    def select_theme_interactive(self):
        """Seleciona tema usando Rofi"""
        themes = self.get_available_themes()
        if not themes:
            logging.error("Nenhum tema disponível!")
            return None
            
        rofi_cmd = ["rofi", "-dmenu", "-p", "Selecione um tema"]
        proc = subprocess.run(
            rofi_cmd, 
            input="\n".join(themes).encode(), 
            capture_output=True
        )
        
        if proc.returncode == 0:
            return proc.stdout.decode().strip()
        return None

    def find_wallpapers(self, theme_name):
        """Encontra wallpapers em um tema"""
        theme_path = THEMES_DIR / theme_name
        image_exts = [".jpg", ".jpeg", ".png", ".webp", ".gif"]
        wallpapers = []
        
        # Busca por arquivos de imagem
        for file in theme_path.iterdir():
            if file.suffix.lower() in image_exts:
                wallpapers.append(file)
        
        return wallpapers

    def apply_theme(self, theme_name):
        """Aplica o tema selecionado"""
        theme_path = THEMES_DIR / theme_name
        wallpapers = self.find_wallpapers(theme_name)
        
        if not wallpapers:
            logging.error(f"Nenhum wallpaper encontrado para o tema: {theme_name}")
            wallpapers = [DEFAULT_WALLPAPER]
        
        wallpaper = random.choice(wallpapers)
        logging.info(f"Aplicando wallpaper: {wallpaper}")
        
        # Aplica wallpaper
        subprocess.run([
            "swww", "img", str(wallpaper),
            "--transition-type", "grow",
            "--transition-duration", "1"
        ])

        # Aplica cores com wal
        subprocess.run(["wal", "-i", str(wallpaper), "-n"])
        
        # Aplica Waybar se houver CSS personalizado no tema
        waybar_theme_css = theme_path / "waybar.css"
        waybar_target_css = HOME / ".config/waybar/style.css"
        if waybar_theme_css.exists():
            try:
                subprocess.run(["cp", str(waybar_theme_css), str(waybar_target_css)], check=True)
                logging.info(f"Waybar CSS do tema '{theme_name}' aplicado.")
            except Exception as e:
                logging.error(f"Erro ao aplicar CSS da Waybar: {e}")
        else:
            logging.info(f"Tema '{theme_name}' não tem CSS para a Waybar.")

        # Reinicia o waybar
        subprocess.run(["pkill", "-9", "waybar"], check=False)
        subprocess.Popen(
            ["waybar"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )

        # Atualiza Kitty (se tiver script)
        self.update_apps(skip_waybar=True)

    def update_apps(self, skip_waybar=False):
        """Atualiza Kitty e opcionalmente Waybar"""
        scripts = {
            "kitty": DOTFILES_DIR / "kitty/apply_colors.py"
        }
        if not skip_waybar:
            scripts["waybar"] = DOTFILES_DIR / "waybar/apply_colors.py"

        for app, script in scripts.items():
            if script.exists():
                subprocess.run(["python3", str(script)])
                logging.info(f"{app.capitalize()} atualizado")
            else:
                logging.warning(f"Script não encontrado: {script}")

    def run(self):
        """Executa o fluxo principal"""
        if theme := self.select_theme_interactive():
            self.apply_theme(theme)
        else:
            logging.info("Nenhum tema selecionado")

if __name__ == "__main__":
    manager = ThemeManager()
    manager.run()

