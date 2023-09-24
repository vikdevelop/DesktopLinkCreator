#!/usr/bin/python3
import sys
import os
import locale
from pathlib import Path
import json
import glob
import gi
import webbrowser
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib

p_lang = locale.getlocale()[0]
r_lang = p_lang[:-3]

try:
    locale = open(f"/app/translations/{r_lang}.json")
except:
    locale = open("/app/translations/en.json")

_ = json.load(locale)

if not os.path.exists(f"{Path.home()}/.local/bin/open_shortcut.sh"):
    os.system("cp /app/open_shortcut.sh ~/.local/bin/open_shortcut.sh && chmod +x ~/.local/bin/open_shortcut.sh")

class Dialog_set(Adw.MessageDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(transient_for=app.get_active_window(), **kwargs)
        self.set_heading(_["remove_shortcuts"])
        self.set_body_use_markup(True)

        # Box for appending widgets
        self.setdBox = Gtk.ListBox.new()
        self.setdBox.set_selection_mode(mode=Gtk.SelectionMode.NONE)
        self.setdBox.get_style_context().add_class(class_name='boxed-list')
        self.set_extra_child(self.setdBox)
        self.add_response('cancel', _["cancel"])
        
        os.chdir(f"{Path.home()}/.local/share/applications")
        
        if glob.glob(f"*.dlc.desktop") == []:
            self.set_body(_["remove_shortcuts_desc"])
        else:
            get_dir_content = glob.glob(f"*.dlc.desktop")
            actions = Gtk.StringList.new(strings=get_dir_content)
            
            self.import_row = Adw.ComboRow.new()
            self.import_row.set_use_markup(True)
            self.import_row.set_use_underline(True)
            self.import_row.set_title("")
            self.import_row.set_title_lines(2)
            self.import_row.set_subtitle_lines(4)
            self.import_row.set_model(model=actions)
            self.setdBox.append(child=self.import_row)
            self.add_response('ok', _["remove"])
        
        self.set_response_appearance('ok', Adw.ResponseAppearance.DESTRUCTIVE)
        self.connect('response', self.dialog_response)
        
        self.show()
        
    def dialog_response(self, dialog, response):
        sel_item = self.import_row.get_selected_item()
        if response == 'ok':
            os.popen(f'rm {sel_item.get_string()}')

class BTWindow(Gtk.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title("Desktop Link Creator")
        self.headerbar = Gtk.HeaderBar.new()
        self.set_titlebar(titlebar=self.headerbar)
        self.application = kwargs.get('application')
        self.connect("close-request", self.on_close)
        
        self.set_size_request(455, 600)
        
        self.settings = Gio.Settings.new_with_path("io.github.vikdevelop.DesktopLinkCreator", "/io/github/vikdevelop/DesktopLinkCreator/")
        
        (width, height) = self.settings["window-size"]
        self.set_default_size(width, height)
        
        if self.settings["maximized"]:
            self.maximize()
        
        # App menu
        self.menu_button_model = Gio.Menu()
        self.menu_button_model.append(_["remove_shortcuts"], "app.set-installed")
        self.menu_button_model.append(_["about_app"], 'app.about')
        self.menu_button = Gtk.MenuButton.new()
        self.menu_button.set_icon_name(icon_name='open-menu-symbolic')
        self.menu_button.set_menu_model(menu_model=self.menu_button_model)
        self.headerbar.pack_end(child=self.menu_button)
        
        # Create button
        self.translateButton = Gtk.Button.new()
        self.tr_button_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 5)
        self.tr_button_box.append(Gtk.Image.new_from_icon_name( \
            'document-new-symbolic'))
        self.tr_button_box.append(Gtk.Label.new(_["create"]))
        self.translateButton.set_child(self.tr_button_box)
        self.translateButton.set_can_focus(True)
        self.translateButton.add_css_class('suggested-action')
        self.translateButton.connect("clicked", self.create_desktop)
        self.headerbar.pack_start(self.translateButton)
        
        # Toast
        self.toast_overlay = Adw.ToastOverlay.new()
        self.toast_overlay.set_margin_top(margin=1)
        self.toast_overlay.set_margin_end(margin=1)
        self.toast_overlay.set_margin_bottom(margin=1)
        self.toast_overlay.set_margin_start(margin=1)

        # Set Adw.ToastOverlay() as a primary child
        self.set_child(self.toast_overlay)
        
        # primary Gtk.Box
        self.binaryBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.binaryBox.set_halign(Gtk.Align.CENTER)
        self.binaryBox.set_valign(Gtk.Align.CENTER)
        self.binaryBox.set_margin_start(15)
        self.binaryBox.set_margin_end(15)
        self.toast_overlay.set_child(self.binaryBox)

        # Widget showing icon of desktop file
        self.iconImage = Gtk.Image.new()
        self.iconImage.set_from_icon_name("io.github.vikdevelop.DesktopLinkCreator")
        self.iconImage.set_pixel_size(128)
        self.binaryBox.append(self.iconImage)

        # Widget showing name of desktop file
        self.nameLabel = Gtk.Label.new()
        self.binaryBox.append(self.nameLabel)

        # Widget showing description of desktop file
        self.urlLabel = Gtk.Label.new()
        self.binaryBox.append(self.urlLabel)
        
        # List Box for entries 
        self.entryBox = Gtk.ListBox.new()
        self.entryBox.set_selection_mode(mode=Gtk.SelectionMode.NONE)
        self.entryBox.add_css_class(css_class='boxed-list')
        self.binaryBox.append(self.entryBox)
        
        # Name entry
        self.nameEntry = Adw.EntryRow.new()
        self.nameEntry.set_title(_["name"])
        self.nameEntry.connect('changed', self.on_nameEntry_changed)
        self.entryBox.append(self.nameEntry)
        
        # URL entry
        self.urlEntry = Adw.EntryRow()
        self.urlEntry.set_title(_["url_adress"])
        self.urlEntry.connect('changed', self.on_urlEntry_changed)
        self.entryBox.append(self.urlEntry)
        
        # Icon button
        self.icon_button = Gtk.Button.new_from_icon_name("document-open-symbolic")
        self.icon_button.add_css_class('flat')
        self.icon_button.set_tooltip_text(_["select_icon"])
        self.icon_button.connect('clicked', self.open_icon_chooser)
        
        # Icon entry
        self.iconEntry = Adw.EntryRow()
        self.iconEntry.set_title(_["icon"])
        self.iconEntry.set_editable(False)
        self.iconEntry.add_suffix(self.icon_button)
        self.entryBox.append(self.iconEntry)

    # Get text from nameEntry for using in Gtk.nameLabel
    def on_nameEntry_changed(self, nameEntry):
        self.nameLabel.set_markup(f"<big><b>{self.nameEntry.get_text()}</b></big>")

    # Get text from urlEntry for using in Gtk.urlLabel
    def on_urlEntry_changed(self, urlEntry):
        self.urlLabel.set_markup(f"{self.urlEntry.get_text()}")
        
    # Open folder chooser
    def open_icon_chooser(self, w):
        def apply_selected(source, res, data):
            try:
                file = source.open_finish(res)
            except:
                return
            self.folder_pb = file.get_path()
            self.iconEntry.set_text(self.folder_pb)
            self.iconImage.set_from_file(self.folder_pb)
        
        self.icon_chooser = Gtk.FileDialog.new()
        self.icon_chooser.set_modal(True)
        self.icon_chooser.set_title(_["select_icon"])
        
        self.png_filter = Gtk.FileFilter.new()
        self.png_filter.set_name("PNG")
        self.png_filter.add_pattern('*.png')
        self.jpg_filter = Gtk.FileFilter.new()
        self.jpg_filter.set_name("JPEG")
        self.jpg_filter.add_pattern('*.jpeg')
        self.svg_filter = Gtk.FileFilter.new()
        self.svg_filter.set_name("SVG")
        self.svg_filter.add_pattern('*.svg')
        self.file_filter_list = Gio.ListStore.new(Gtk.FileFilter);
        self.file_filter_list.append(self.png_filter)
        self.file_filter_list.append(self.jpg_filter)
        self.file_filter_list.append(self.svg_filter)
        
        self.icon_chooser.set_filters(self.file_filter_list)
        self.icon_chooser.open(self, None, apply_selected, None)
        
    # Create desktop file
    def create_desktop(self, w):
        if self.nameEntry.get_text() == "":
            self.err_toast()
        elif self.urlEntry.get_text() == "":
            self.err_toast()
        elif self.iconEntry.get_text() == "":
            self.err_toast()
        else:
            name_with_spaces = self.nameEntry.get_text()
            name_without_spaces = name_with_spaces.replace(" ", "_")
            with open(f"{Path.home()}/.local/share/applications/{name_without_spaces}.dlc.desktop", "w") as d:
                d.write(f'[Desktop Entry]\nName={self.nameEntry.get_text()}\nType=Application\nURL={self.urlEntry.get_text()}\nExec={Path.home()}/.local/bin/open_shortcut.sh {self.urlEntry.get_text()}\nIcon={self.iconEntry.get_text()}')
            self.toast_done = Adw.Toast.new(title=_["desktop_created_status"])
            self.toast_overlay.add_toast(self.toast_done)

    # Show error toast if entry is empty
    def err_toast(self):
        self.blankToast = Adw.Toast.new(title=_["entry_blank"])
        self.toast_overlay.add_toast(self.blankToast)

    # Action after closing application
    def on_close(self, widget, *args):
        (width, height) = self.get_default_size()
        self.settings["window-size"] = (width, height)
        self.settings["maximized"] = self.is_maximized()
        
class BTApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.create_action('about', self.on_about_action, ["F1"])
        self.create_action('set-installed', self.on_set_installed)
        self.connect('activate', self.on_activate)
        
    def on_about_action(self, action, param):
        dialog = Adw.AboutWindow(transient_for=app.get_active_window())
        dialog.set_application_name("Desktop Link Creator")
        dialog.set_developer_name("vikdevelop")
        if r_lang == 'en':
            print("")
        else:
            dialog.set_translator_credits(_["translator_credits"])
        dialog.set_license_type(Gtk.License(Gtk.License.GPL_3_0))
        dialog.set_website("https://github.com/vikdevelop/DesktopLinkCreator")
        dialog.set_issue_url("https://github.com/vikdevelop/DesktopLinkCreator/issues")
        dialog.set_copyright("© 2023 vikdevelop")
        dialog.set_developers(["vikdevelop https://github.com/vikdevelop"])
        version = "1.0"
        icon = "io.github.vikdevelop.DesktopLinkCreator"
        dialog.set_version(version)
        dialog.set_application_icon(icon)
        dialog.show()
        
    def on_set_installed(self, action, param):
        self.dialog = Dialog_set(self)
    
    def create_action(self, name, callback, shortcuts=None):
        action = Gio.SimpleAction.new(name, None)
        action.connect('activate', callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f'app.{name}', shortcuts)
    
    def on_activate(self, app):
        self.win = BTWindow(application=app)
        self.win.present()
app = BTApp()
app.run(sys.argv)
