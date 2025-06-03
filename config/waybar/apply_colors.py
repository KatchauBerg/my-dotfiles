#!/usr/bin/env python3
import os
import shutil
import subprocess
from pathlib import Path
import sys
import re

HOME = Path.home()
DOTFILES = HOME / ".dotfiles"
WAYBAR_CONFIG = HOME / ".config/waybar/config.jsonc"
WAYBAR_STYLE_TARGET = HOME / ".config/waybar/style.css"
LOG_FILE = HOME / ".cache/waybar_apply.log"

def log(message):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"{message}\n")

def apply_waybar_theme(theme_name):
    theme_css = DOTFILES / "themes" / theme_name / "waybar.css"

    if not theme_css.exists():
        log(f"[!] Arquivo de estilo não encontrado para o tema '{theme_name}': {theme_css}")
        print(f"Erro: Arquivo '{theme_css}' não existe.")
        return False

    # Copia o CSS para a style.css da Waybar
    shutil.copyfile(theme_css, WAYBAR_STYLE_TARGET)
    log(f"[+] Arquivo de estilo copiado: {theme_css} -> {WAYBAR_STYLE_TARGET}")

    # Garante que config.jsonc tenha o campo "style" apontando para style.css
    if WAYBAR_CONFIG.exists():
        with open(WAYBAR_CONFIG, "r") as f:
            config = f.read()

        new_config = re.sub(
            r'"style":\s*".*?"',
            f'"style": "{WAYBAR_STYLE_TARGET}"',
            config
        )

        with open(WAYBAR_CONFIG, "w") as f:
            f.write(new_config)

        log("[+] Caminho do estilo atualizado em config.jsonc")
    else:
        log("[!] config.jsonc da Waybar não encontrado")
    
    # Envia sinal para recarregar a Waybar
    subprocess.run(["pkill", "-SIGUSR2", "waybar"], check=False)
    log("[+] Sinal SIGUSR2 enviado para Waybar")
    return True

def main():
    if len(sys.argv) < 2:
        print("Uso: apply_colors.py <nome-do-tema>")
        log("Erro: Nenhum tema fornecido")
        sys.exit(1)

    theme = sys.argv[1]
    success = apply_waybar_theme(theme)
    if success:
        print(f"[OK] Tema da Waybar '{theme}' aplicado com sucesso.")
    else:
        print(f"[ERRO] Não foi possível aplicar o tema '{theme}'.")

if __name__ == "__main__":
    main()

