#!/bin/bash
# Monitora mudanças no wallpaper via swww (ou outro gerenciador)
swww query || swww init

# Quando o wallpaper mudar, extrai cores e aplica
swww img "$WALLPAPER_DIR"/* --transition-type any --transition-fps 60 | while read -r event; do
    if [[ $event == *"changed"* ]]; then
        WALLPAPER_PATH=$(echo "$event" | awk '{print $2}')
        wal -i "$WALLPAPER_PATH" -n                           # Gera esquema de cores
        apply-colors-to-kitty                                 # Aplica no terminal
        apply-colors-to-waybar                                # Atualiza a Waybar
    fi
done
