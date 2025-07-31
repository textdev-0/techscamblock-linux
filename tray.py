import sys
import os
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QMessageBox
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtCore import QUrl, QTimer, QProcess



def get_resource_path(filename):
	base_dir = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
	return os.path.join(base_dir, filename)



def setup_tray(app, config_path):
	app.setQuitOnLastWindowClosed(False)
	icon = QIcon(get_resource_path("tray.png"))
	tray = QSystemTrayIcon(icon, app)
	menu = QMenu()
	info_action     = QAction("What is this?", app)
	settings_action = QAction("Settings",     app)
	exit_action     = QAction("Exit",         app)
	menu.addAction(info_action)
	menu.addAction(settings_action)
	menu.addAction(exit_action)
	tray.setContextMenu(menu)

	def open_link():
		url = "https://ravendevteam.org/remoteaccess"
		if sys.platform.startswith("win"):
			QProcess.startDetached("explorer.exe", [url])
		else:
			QDesktopServices.openUrl(QUrl(url))

	def open_settings():
		cfg = os.path.abspath(config_path)
		if sys.platform.startswith("win"):
			os.startfile(cfg)
		else:
			QDesktopServices.openUrl(QUrl.fromLocalFile(cfg))

	tray.activated.connect(lambda r: open_link() if r == QSystemTrayIcon.Trigger else None)
	info_action.triggered.connect(open_link)
	settings_action.triggered.connect(open_settings)

	def show_exit_dialog():
		dlg = QMessageBox()
		dlg.setWindowTitle("Confirm Exit")
		dlg.setText("This program protects your system from remote access scammers. Please only disable this if you know exactly what you're doing, and don't disable it if you are being told to by someone you don't completely trust.")
		dlg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
		ok_button = dlg.button(QMessageBox.Ok)
		ok_button.setEnabled(False)
		ok_button.setText("OK (5)")
		countdown = 5
		timer = QTimer(dlg)

		def update():
			nonlocal countdown
			if countdown > 0:
				ok_button.setText(f"OK ({countdown})")
				countdown -= 1
			else:
				timer.stop()
				ok_button.setText("OK")
				ok_button.setEnabled(True)

		timer.timeout.connect(update)
		timer.start(1000)
		if dlg.exec_() == QMessageBox.Ok:
			app.quit()

	exit_action.triggered.connect(show_exit_dialog)
	tray.show()
	return tray
