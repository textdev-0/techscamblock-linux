@echo off
nuitka --onefile --standalone --enable-plugin=pyqt5 --remove-output --windows-icon-from-ico=ICON.ico --include-data-files=tray.png=tray.png --windows-console-mode=disable --windows-uac-admin --output-dir=dist --follow-imports techscamblock.py
pause