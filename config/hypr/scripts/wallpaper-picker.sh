#!/bin/bash
WALLPAPER_DIR="$HOME/.dotfiles/swww/wallpaper"
WALLPAPER=$(ls "$WALLPAPER_DIR" | rofi -dmenu -p "Escolha um wallpaper")

if [ -n "$WALLPAPER" ]; then
    swww img "$WALLPAPER_DIR/$WALLPAPER" --transition-type wipe
fi
