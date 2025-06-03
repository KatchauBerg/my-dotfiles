#!/bin/bash
set -e

DOTFILES="$HOME/.dotfiles"

echo "Iniciando setup das dotfiles..."

# 1. Criar link simbólico para tema atual, se não existir
if [ ! -L "$DOTFILES/themes/current" ]; then
  ln -s "$DOTFILES/themes/catppuccin-mocha" "$DOTFILES/themes/current"
  echo "Link simbólico 'themes/current' criado para catppuccin-mocha"
else
  echo "Link simbólico 'themes/current' já existe"
fi

# 2. Tornar scripts executáveis
chmod +x "$DOTFILES/config/hypr/scripts/"*.py
chmod +x "$DOTFILES/bin/"*.py

# 3. Instalar dependências (exemplo para Arch Linux)
if command -v pacman &> /dev/null; then
  echo "Detectado Arch Linux, instalando dependências..."
  sudo pacman -Syu --needed python-gobject python-pywal
elif command -v apt &> /dev/null; then
  echo "Detectado Debian/Ubuntu, instalando dependências..."
  sudo apt update
  sudo apt install -y python3-gi python3-pywal
else
  echo "Sistema não detectado ou gerenciador de pacotes não suportado. Instale manualmente python3-gi e python3-pywal."
fi

echo "Setup finalizado. Para iniciar o gerenciador de temas GTK, rode:"
echo "$DOTFILES/bin/theme_manager_gtk3.py"

