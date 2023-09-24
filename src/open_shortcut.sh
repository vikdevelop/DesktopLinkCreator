#!/usr/bin/bash
if flatpak list | grep firefox
then
		flatpak run org.mozilla.firefox --new-window $1
elif test -f /usr/bin/firefox
then
		firefox --new-window $1
elif flatpak list | grep Chrome
then
		flatpak run org.google.Chrome --new-window --app=$1
elif test -f /usr/bin/google-chrome
then
		google-chrome --new-window --app=$1
elif flatpak list | grep brave
then
		flatpak run com.brave.Browser --new-window --app=$1
elif test -f /usr/bin/brave-browser
then
		brave-browser --new-window --app=$1
elif flatpak list | grep Edge
then
		flatpak run com.microsoft.Edge --new-window --app=$1
elif test -f /usr/bin/edge
then
		edge --new-window --app=$1
fi
