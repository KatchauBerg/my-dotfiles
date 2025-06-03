#!/usr/bin/env python3

import gi
import subprocess
import os

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject, Gio

HOME = os.path.expanduser("~")
DOTFILES = os.path.join(HOME, ".dotfiles")
THEMES_DIR = os.path.join(DOTFILES, "themes")
THEME_PICKER_SCRIPT = os.path.join(DOTFILES, "config", "hypr", "scripts", "theme_picker.py")

class ThemeManager(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Theme Manager")
        self.set_border_width(10)
        self.set_default_size(300, 500)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(vbox)

        # Lista de temas
        self.liststore = Gtk.ListStore(str)
        self.treeview = Gtk.TreeView(model=self.liststore)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Temas disponíveis", renderer, text=0)
        self.treeview.append_column(column)
        self.treeview.get_selection().connect("changed", self.on_selection_changed)
        vbox.pack_start(self.treeview, True, True, 0)

        # ComboBox para selecionar wallpaper
        self.wallpaper_combo = Gtk.ComboBoxText()
        self.wallpaper_combo.append_text("Aleatório")
        self.wallpaper_combo.set_active(0)
        vbox.pack_start(Gtk.Label(label="Wallpaper:"), False, False, 0)
        vbox.pack_start(self.wallpaper_combo, False, False, 0)

        # Status
        self.status_label = Gtk.Label(label="Selecione um tema")
        vbox.pack_start(self.status_label, False, False, 0)

        # Botão aplicar
        self.apply_button = Gtk.Button(label="Aplicar tema")
        self.apply_button.set_sensitive(False)
        self.apply_button.connect("clicked", self.on_apply_clicked)
        vbox.pack_start(self.apply_button, False, False, 0)

        self.selected_theme = None

        self.file_monitor = Gio.File.new_for_path(THEMES_DIR).monitor_directory(Gio.FileMonitorFlags.NONE, None)
        self.file_monitor.connect("changed", self.on_themes_dir_changed)

        self.load_themes()

    def load_themes(self):
        self.liststore.clear()
        if not os.path.isdir(THEMES_DIR):
            self.status_label.set_text("Pasta de temas não encontrada!")
            return
        temas = sorted([
            d for d in os.listdir(THEMES_DIR)
            if os.path.isdir(os.path.join(THEMES_DIR, d))
            and not d.startswith(".") and d != "current"
        ])
        for tema in temas:
            self.liststore.append([tema])
        self.selected_theme = None
        self.apply_button.set_sensitive(False)
        self.status_label.set_text("Selecione um tema")

    def load_wallpapers_for_theme(self, theme_name):
        self.wallpaper_combo.remove_all()
        self.wallpaper_combo.append_text("Aleatório")
        self.wallpaper_combo.set_active(0)

        wallpapers_dir = os.path.join(THEMES_DIR, theme_name, "wallpapers")
        fallback = os.path.join(THEMES_DIR, theme_name, "wallpaper.png")

        wallpapers = []

        if os.path.isdir(wallpapers_dir):
            wallpapers = [
                f for f in os.listdir(wallpapers_dir)
                if f.lower().endswith((".png", ".jpg", ".jpeg"))
            ]

        if not wallpapers and os.path.isfile(fallback):
            wallpapers = ["wallpaper.png"]

        for wp in sorted(wallpapers):
            self.wallpaper_combo.append_text(wp)

    def on_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            self.selected_theme = model[treeiter][0]
            self.status_label.set_text(f"Tema selecionado: {self.selected_theme}")
            self.apply_button.set_sensitive(True)
            self.load_wallpapers_for_theme(self.selected_theme)
        else:
            self.selected_theme = None
            self.status_label.set_text("Selecione um tema")
            self.apply_button.set_sensitive(False)

    def on_apply_clicked(self, button):
        if not self.selected_theme:
            return

        wallpaper = self.wallpaper_combo.get_active_text()
        wallpaper_arg = wallpaper if wallpaper != "Aleatório" else None

        try:
            args = ["python3", THEME_PICKER_SCRIPT, self.selected_theme]
            if wallpaper_arg:
                args.append(wallpaper_arg)

            result = subprocess.run(
                args, capture_output=True, text=True, check=True
            )
            self.status_label.set_text(f"✅ Tema '{self.selected_theme}' aplicado com sucesso!")
        except subprocess.CalledProcessError as e:
            err = e.stderr or e.stdout
            self.status_label.set_text(f"❌ Erro ao aplicar tema:\n{err}")

    def on_themes_dir_changed(self, monitor, file, other_file, event_type):
        if event_type in (
            Gio.FileMonitorEvent.CREATED,
            Gio.FileMonitorEvent.DELETED,
            Gio.FileMonitorEvent.MOVED_IN,
            Gio.FileMonitorEvent.MOVED_OUT
        ):
            GObject.idle_add(self.load_themes)

def main():
    win = ThemeManager()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()

