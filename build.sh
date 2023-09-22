#!/usr/bin/bash
echo "Downloading depency runtime and SDK"
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
flatpak install --system runtime/org.gnome.Platform/x86_64/44 runtime/org.gnome.Sdk/x86_64/44 -y
echo "Building app with Flatpak builder"
git clone https://github.com/vikdevelop/DesktopLinkCreator /tmp/DesktopLinkCreator
cd /tmp/DesktopLinkCreator
flatpak-builder build *.yaml --install --user
cd
rm -rf /tmp/DesktopLinkCreator
echo "DesktopLinkCreator has been installed successfully! Try run the app from desktop or terminal command 'flatpak run io.github.vikdevelop.DesktopLinkCreator'"
