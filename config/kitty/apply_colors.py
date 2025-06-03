#!/usr/bin/env python3
import os
import json
import subprocess
from pathlib import Path
import hashlib
import shutil

HOME = Path.home()
WAL_COLORS = HOME / ".cache/wal/colors.json"
KITTY_CONF = HOME / ".config/kitty/colors.conf"
KITTY_MAIN_CONF = HOME / ".config/kitty/kitty.conf"
CACHE_FILE = HOME / ".cache/kitty_colors.cache"

def main():
    # Verifica cache
    current_hash = hashlib.md5(WAL_COLORS.read_bytes()).hexdigest() if WAL_COLORS.exists() else ""
    
    if CACHE_FILE.exists():
        with open(CACHE_FILE, 'r') as f:
            cache_data = json.load(f)
            if cache_data.get('hash') == current_hash:
                return
    
    # Gera nova configuração
    if not WAL_COLORS.exists():
        return
    
    with open(WAL_COLORS) as f:
        colors = json.load(f)
    
    conf = f"""
# Arquivo gerado automaticamente - NÃO EDITAR MANUALMENTE
foreground {colors['special']['foreground']}
background {colors['special']['background']}
color0 {colors['colors']['color0']}
color1 {colors['colors']['color1']}
color2 {colors['colors']['color2']}
color3 {colors['colors']['color3']}
color4 {colors['colors']['color4']}
color5 {colors['colors']['color5']}
color6 {colors['colors']['color6']}
color7 {colors['colors']['color7']}
"""
    
    # Escreve o arquivo de cores
    KITTY_CONF.write_text(conf)
    
    # Atualiza a configuração principal para incluir colors.conf
    if not KITTY_MAIN_CONF.exists():
        KITTY_MAIN_CONF.write_text("include colors.conf\n")
    else:
        with open(KITTY_MAIN_CONF, 'r+') as f:
            content = f.read()
            if "include colors.conf" not in content:
                f.seek(0, 0)
                f.write("include colors.conf\n" + content)
    
    # Atualiza cache
    with open(CACHE_FILE, 'w') as f:
        json.dump({'hash': current_hash}, f)
    
    # Força recarregamento em todas as instâncias
    subprocess.run(["pkill", "-USR1", "kitty"], stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    main()
