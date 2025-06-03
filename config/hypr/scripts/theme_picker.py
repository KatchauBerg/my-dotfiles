#!/usr/bin/env python3

import sys
import os
import random
import shutil
import subprocess

HOME = os.path.expanduser("~")
DOTFILES = os.path.join(HOME, ".dotfiles")
THEMES_DIR = os.path.join(DOTFILES, "themes")

def apply_wallpaper(theme_name, wallpaper_name=None):
    theme_path = os.path.join(THEMES_DIR, theme_name)
    wallpapers_dir = os.path.join(theme_path, "wallpapers")

    wallpapers = []
    if os.path.isdir(wallpapers_dir):
        wallpapers = [f for f in os.listdir(wallpapers_dir)
                      if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    # fallback para wallpaper.png na pasta do tema
    if not wallpapers and os.path.isfile(os.path.join(theme_path, "wallpaper.png")):
        wallpapers = ["wallpaper.png"]

    if wallpaper_name:
        if wallpaper_name in wallpapers:
            chosen_wallpaper = wallpaper_name
        else:
            print(f"Wallpaper '{wallpaper_name}' não encontrado no tema '{theme_name}', usando aleatório.")
            chosen_wallpaper = random.choice(wallpapers) if wallpapers else None
    else:
        chosen_wallpaper = random.choice(wallpapers) if wallpapers else None

    if not chosen_wallpaper:
        print("Nenhum wallpaper encontrado para aplicar.")
        return False

    wallpaper_path = os.path.join(wallpapers_dir if os.path.isdir(wallpapers_dir) else theme_path, chosen_wallpaper)

    print(f"Aplicando wallpaper: {wallpaper_path}")

    # Aqui coloque seu comando real para aplicar o wallpaper
    # Exemplo com swww:
    # subprocess.run(["swww", "img", wallpaper_path], check=True)

    # Exemplo com swaybg:
    # subprocess.run(["swaybg", "-i", wallpaper_path, "-m", "fill"], check=True)

    # Se quiser testar só print, comente o comando abaixo
    # subprocess.run(["swww", "img", wallpaper_path], check=True)

    return True

def copy_if_exists(src, dst):
    if os.path.isfile(src):
        print(f"Copiando {os.path.basename(src)} para {dst}")
        shutil.copy(src, dst)
    else:
        print(f"Arquivo {src} não encontrado, pulando.")

def copy_dir_if_exists(src_dir, dst_dir):
    if os.path.isdir(src_dir):
        print(f"Copiando conteúdo de {src_dir} para {dst_dir}")
        # copia os arquivos dentro da pasta para destino (não a pasta em si)
        for item in os.listdir(src_dir):
            s = os.path.join(src_dir, item)
            d = os.path.join(dst_dir, item)
            if os.path.isfile(s):
                shutil.copy(s, d)
    else:
        print(f"Pasta {src_dir} não encontrada, pulando.")

def apply_neofetch_config(theme_path):
    neofetch_conf_src = os.path.join(theme_path, "config.conf")
    neofetch_conf_dst_dir = os.path.join(DOTFILES, "config", "neofetch")
    neofetch_conf_dst = os.path.join(neofetch_conf_dst_dir, "config.conf")
    neofetch_img_src = os.path.join(theme_path, "neofetch.png")
    neofetch_img_dst = os.path.join(neofetch_conf_dst_dir, "neofetch.png")

    os.makedirs(neofetch_conf_dst_dir, exist_ok=True)

    if os.path.isfile(neofetch_conf_src):
        print(f"Copiando config.conf do neofetch: {neofetch_conf_src}")
        shutil.copy(neofetch_conf_src, neofetch_conf_dst)
    else:
        print("Config.conf do neofetch não encontrado no tema.")

    if os.path.isfile(neofetch_img_src):
        print(f"Copiando imagem neofetch.png: {neofetch_img_src}")
        shutil.copy(neofetch_img_src, neofetch_img_dst)
    else:
        print("Imagem neofetch.png não encontrada no tema.")

def main():
    if len(sys.argv) < 2:
        print("Uso: theme_picker.py <tema> [wallpaper]")
        sys.exit(1)

    tema = sys.argv[1]
    wallpaper = sys.argv[2] if len(sys.argv) > 2 else None

    theme_path = os.path.join(THEMES_DIR, tema)
    if not os.path.isdir(theme_path):
        print(f"Tema '{tema}' não encontrado.")
        sys.exit(1)

    # Aplica wallpaper
    if not apply_wallpaper(tema, wallpaper):
        print("Falha ao aplicar wallpaper.")

    # Aplica configurações do kitty
    kitty_src = os.path.join(theme_path, "kitty.conf")
    kitty_dst_dir = os.path.expanduser("~/.config/kitty")
    os.makedirs(kitty_dst_dir, exist_ok=True)
    copy_if_exists(kitty_src, os.path.join(kitty_dst_dir, "kitty.conf"))

    # Aplica configurações do starship
    starship_src = os.path.join(theme_path, "starship.toml")
    starship_dst_dir = os.path.expanduser("~/.config")
    os.makedirs(starship_dst_dir, exist_ok=True)
    copy_if_exists(starship_src, os.path.join(starship_dst_dir, "starship.toml"))

    # Aplica configurações do waybar
    waybar_src_dir = os.path.join(theme_path, "waybar")
    waybar_dst_dir = os.path.expanduser("~/.config/waybar")
    os.makedirs(waybar_dst_dir, exist_ok=True)
    copy_dir_if_exists(waybar_src_dir, waybar_dst_dir)

    # Aplica configs do neofetch
    apply_neofetch_config(theme_path)

    print(f"\nTema '{tema}' aplicado com sucesso!")

if __name__ == "__main__":
    main()

