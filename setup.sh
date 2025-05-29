#!/usr/bin/env bash

set -euo pipefail

USER="katchau"
DOTFILES_DIR="$HOME/.dotfiles"
OS_ID=""
OS_VERSION=""
SUDO="sudo"
LOG_FILE="$HOME/dotfiles_setup.log"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info()    { echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"; exit 1; }

detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS_ID="$ID"
    elif [ -f /etc/arch-release ]; then
        OS_ID="arch"
    else
        log_error "Sistema não suportado!"
    fi

    log_info "Detectado: $OS_ID"
}

install_aur_helpers() {
    log_info "Verificando AUR helpers..."

    if ! command -v yay &>/dev/null; then
        log_info "Instalando yay..."
        git clone https://aur.archlinux.org/yay.git /tmp/yay
        cd /tmp/yay && makepkg -si --noconfirm
    fi

    if ! command -v paru &>/dev/null; then
        log_info "Instalando paru..."
        git clone https://aur.archlinux.org/paru.git /tmp/paru
        cd /tmp/paru && makepkg -si --noconfirm
    fi
}

install_dependencies() {
    log_info "Instalando dependências..."

    case "$OS_ID" in
        arch|endeavouros|manjaro)
            $SUDO pacman -Sy --needed --noconfirm \
                python python-pip hyprland kitty waybar rofi swww \
                brightnessctl playerctl noto-fonts noto-fonts-emoji \
                otf-jetbrains-mono xdg-desktop-portal-hyprland \
                xdg-desktop-portal-gtk wl-clipboard grim slurp jq imagemagick \
                base-devel git || log_warn "Algumas dependências podem não ter sido instaladas"

            install_aur_helpers

            paru -S --needed --noconfirm nerd-fonts-jetbrains-mono || log_warn "Falha ao instalar Nerd Font via paru"

            python3 -m pip install --user pywal || log_warn "Falha ao instalar pywal"
            ;;

        debian|ubuntu|pop)
            $SUDO apt update
            $SUDO apt install -y \
                python3 python3-pip kitty rofi brightnessctl playerctl \
                fonts-noto-color-emoji fonts-jetbrains-mono jq imagemagick \
                wl-clipboard grim slurp meson build-essential git curl cmake \
                libgtk-3-dev libjsoncpp-dev libinput-dev libpulse-dev libdbusmenu-gtk3-dev cargo libwayland-dev || log_warn "Algumas dependências podem não ter sido instaladas"

            if ! command -v hyprland &>/dev/null; then
                log_warn "Hyprland não encontrado. Instalando via script..."
                curl -s https://raw.githubusercontent.com/hyprwm/Hyprland/main/install.sh | bash || log_warn "Falha ao instalar Hyprland"
            fi

            if ! command -v waybar &>/dev/null; then
                log_info "Compilando Waybar..."
                git clone https://github.com/Alexays/Waybar /tmp/waybar
                cd /tmp/waybar && meson build && ninja -C build
                $SUDO ninja -C build install
            fi

            if ! command -v swww &>/dev/null; then
                log_info "Compilando swww..."
                git clone https://github.com/Horus645/swww /tmp/swww
                cd /tmp/swww && cargo build --release
                $SUDO cp target/release/swww* /usr/local/bin/
            fi

            python3 -m pip install --user pywal || log_warn "Falha ao instalar pywal"
            ;;

        fedora)
            $SUDO dnf install -y \
                python3 python3-pip kitty rofi brightnessctl playerctl \
                google-noto-emoji-color-fonts jetbrains-mono-fonts jq ImageMagick \
                wl-clipboard grim slurp meson cmake git gcc make cargo || log_warn "Algumas dependências podem não ter sido instaladas"

            if ! command -v hyprland &>/dev/null; then
                $SUDO dnf copr enable -y solopasha/hyprland
                $SUDO dnf install -y hyprland || log_warn "Falha ao instalar Hyprland via COPR"
            fi

            if ! command -v waybar &>/dev/null; then
                $SUDO dnf install -y waybar || log_warn "Falha ao instalar Waybar"
            fi

            if ! command -v swww &>/dev/null; then
                log_info "Compilando swww..."
                git clone https://github.com/Horus645/swww /tmp/swww
                cd /tmp/swww && cargo build --release
                $SUDO cp target/release/swww* /usr/local/bin/
            fi

            python3 -m pip install --user pywal || log_warn "Falha ao instalar pywal"
            ;;

        *)
            log_error "Distribuição não suportada: $OS_ID"
            ;;
    esac
}

create_symlinks() {
    log_info "Criando links simbólicos..."

    declare -A config_map=(
        ["hypr"]=".config/hypr"
        ["kitty"]=".config/kitty"
        ["waybar"]=".config/waybar"
        ["swww"]=".config/swww"
    )

    for src in "${!config_map[@]}"; do
        target_dir="$HOME/${config_map[$src]}"
        src_path="$DOTFILES_DIR/$src"

        mkdir -p "$(dirname "$target_dir")"

        if [ -L "$target_dir" ]; then
            rm -f "$target_dir"
        elif [ -d "$target_dir" ]; then
            mv "$target_dir" "${target_dir}.bak"
            log_warn "Backup de $target_dir criado"
        fi

        ln -sf "$src_path" "$target_dir"
    done

    mkdir -p "$HOME/.local/bin"
    find "$DOTFILES_DIR/scripts" -type f -executable -print0 | while IFS= read -r -d $'\0' script; do
        ln -sf "$script" "$HOME/.local/bin/$(basename "$script")"
    done
}

setup_directories() {
    log_info "Configurando diretórios e permissões..."

    mkdir -p \
        "$HOME/.cache/theme_cache" \
        "$HOME/.cache/wal" \
        "$DOTFILES_DIR/swww/wallpapers" \
        "$DOTFILES_DIR/themes" \
        "$HOME/.local/bin"

    chmod -R +x "$DOTFILES_DIR/hypr/scripts"/*.py 2>/dev/null || true
    chmod +x "$DOTFILES_DIR/kitty/apply_colors.py" 2>/dev/null || true
    chmod +x "$DOTFILES_DIR/waybar/apply_colors.py" 2>/dev/null || true

    if [ ! -f "$DOTFILES_DIR/swww/wallpapers/default.jpg" ]; then
        convert -size 1920x1080 xc:black "$DOTFILES_DIR/swww/wallpapers/default.jpg"
    fi
}

post_install() {
    log_info "Executando configurações finais..."

    if ! grep -q "XDG_CURRENT_DESKTOP=Hyprland" "$HOME/.bashrc"; then
        {
            echo -e "\n# Configuração para Hyprland"
            echo "export XDG_CURRENT_DESKTOP=Hyprland"
            echo "export QT_QPA_PLATFORM=wayland"
            echo "export MOZ_ENABLE_WAYLAND=1"
        } >> "$HOME/.bashrc"
    fi

    if ! pgrep swww-daemon >/dev/null 2>&1; then
        swww init || log_warn "Falha ao iniciar swww"
    fi

    if [ ! -d "$DOTFILES_DIR/themes/default" ]; then
        mkdir -p "$DOTFILES_DIR/themes/default"
        cp "$DOTFILES_DIR/swww/wallpapers/default.jpg" "$DOTFILES_DIR/themes/default/wallpaper.jpg"
    fi
}

main() {
    echo -e "\n${GREEN}=== Iniciando configuração do dotfiles ===${NC}"
    echo "Log detalhado: $LOG_FILE"

    detect_os
    install_dependencies
    create_symlinks
    setup_directories
    post_install

    echo -e "\n${GREEN}=== Configuração concluída com sucesso! ===${NC}"
    echo "Próximos passos:"
    echo "1. Reinicie sua sessão (logout/login)"
    echo "2. Execute 'hyprctl reload' para carregar as configurações"
    echo "3. Use Super+T para abrir o theme picker (se configurado)"
}

main

