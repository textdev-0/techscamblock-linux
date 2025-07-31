import sys
from PyQt5.QtWidgets import QApplication, QMessageBox, QWidget
from PyQt5.QtCore import Qt, QTimer, QSharedMemory
from PyQt5.QtGui import QPainter, QColor



_ACTIVE_POPUPS = []



class FullScreenOverlay(QWidget):
    def __init__(self, geometry, parent=None):
        super().__init__(parent)
        self.setGeometry(geometry)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.X11BypassWindowManagerHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QColor(0, 0, 0, 150))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())



shared_memory = QSharedMemory("ScamWarningPopup")



def is_already_running():
    if shared_memory.attach():
        return True
    shared_memory.create(1)
    return False



def show_scam_warning():
    sm = QSharedMemory("ScamWarningPopup")
    if sm.attach() or not sm.create(1):
        return
    app = QApplication.instance()
    created = False
    if app is None:
        app = QApplication(sys.argv)
        created = True
    overlays = [FullScreenOverlay(screen.geometry()) for screen in app.screens()]
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle("Likely Scam Prevented")
    msg.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
    body_text = """
    <b>A real tech support agent will NEVER ask for access to your device. You should only ever give access to your device if you know exactly what you are doing, and you completely trust the person.</b><br><br>
    
    There was an attempt to run a remote access tool on your device. <b>The remote access tool was stopped, so your system is safe</b>.<br><br>

    A remote access tool allows somebody else to access your computer. They can see your screen, read your files, and download malicious files.<br><br>

    If somebody is on the phone with you or is messaging you trying to get you to run one of these tools, <b>hang up or stop messaging them immediately</b>, and get help from somebody you know and trust like a family member or your bank.<br><br>

    For more information, visit:<br>
    <a href='https://ravendevteam.org/remoteaccess'>https://ravendevteam.org/remoteaccess</a>
    """
    msg.setText(body_text)
    msg.setTextFormat(Qt.RichText)
    msg.setStyleSheet("QLabel { font-size: 16px; line-height: 1.6; }")
    ok_button = msg.addButton("OK (5)", QMessageBox.AcceptRole)
    ok_button.setEnabled(False)
    countdown = 5
    
    def update_button():
        nonlocal countdown
        if countdown > 0:
            ok_button.setText(f"OK ({countdown})")
            countdown -= 1
        else:
            timer.stop()
            ok_button.setText("OK")
            ok_button.setEnabled(True)

    timer = QTimer(msg)
    timer.timeout.connect(update_button)
    timer.start(1000)
    update_button()

    def close_overlays():
        for overlay in overlays:
            overlay.close()
        sm.detach()
        if msg in _ACTIVE_POPUPS:
            _ACTIVE_POPUPS.remove(msg)
        
    msg.buttonClicked.connect(close_overlays)
    msg.finished.connect(close_overlays)
    msg.setWindowFlag(Qt.WindowCloseButtonHint, False)
    msg.show()
    _ACTIVE_POPUPS.append(msg)
    if created:
        app.exec_()



if __name__ == "__main__":
    show_scam_warning()
