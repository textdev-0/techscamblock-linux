import sys, os, re, urllib.request, getpass, threading, socket, time
from plyer import notification
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal
from aboutremoteblock import show_scam_warning
from tray import setup_tray

CONFIG_PATH = "/etc/techscamblock/techscamblock.conf"
_DEFAULT_CFG = """# TechScamBlock by the Raven Development Team
# Unless you know what you are doing, you shouldn't modify this file.

# ntfy.sh integration, to get mobile alerts
NTFY_NOTIFICATION_ENDPOINT_URL = ""

# Remote access tools that are allowed to run. Specify process name, # separated by a comma and a space (example1, example2, example3, ...)
WHITELISTED_REMOTE_ACCESS_TOOLS = ""
"""

def _ensure_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        try:
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            with open(CONFIG_PATH, "w", encoding="utf-8") as fh:
                fh.write(_DEFAULT_CFG)
        except OSError:
            return {"NTFY_NOTIFICATION_ENDPOINT_URL": "", "WHITELISTED_REMOTE_ACCESS_TOOLS": ""}

    cfg = {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = map(str.strip, line.split("=", 1))
            if v.startswith('"') and v.endswith('"'):
                v = v[1:-1]
            cfg[k] = v
    return cfg

_cfg = _ensure_config()

_raw_ntfy = _cfg.get("NTFY_NOTIFICATION_ENDPOINT_URL", "").strip()
if _raw_ntfy:
    if _raw_ntfy.startswith("http://"):
        _raw_ntfy = "https://" + _raw_ntfy[7:]
    _ntfy_url = _raw_ntfy if _raw_ntfy.startswith("https://ntfy.sh/") else ""
else:
    _ntfy_url = ""

def _send_ntfy(msg: str):
    if not _ntfy_url:
        return
    try:
        req = urllib.request.Request(
            _ntfy_url,
            data=msg.encode("utf-8"),
            method="POST",
            headers={"Title": "TechScamBlock Alert"}
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass

class ScamNotifier(QObject):
    alert = pyqtSignal()

notifier = ScamNotifier()
info_window_open = False

def _handle_alert():
    global info_window_open
    if not info_window_open:
        info_window_open = True
        username = getpass.getuser()
        notification.notify(
            title="Remote Access Attempt Prevented",
            message="An attempt to remotely access your device was prevented.",
            timeout=5
        )
        _send_ntfy(f"TechScamBlock: A remote access tool was blocked on {username}'s device.")
        show_scam_warning()
        info_window_open = False

notifier.alert.connect(_handle_alert)

SOCKET_PATH = "/run/techscamblock.sock"

def listen_for_daemon():
    while True:
        try:
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.connect(SOCKET_PATH)
            while True:
                data = client.recv(1024)
                if data == b"PROCESS_KILLED":
                    notifier.alert.emit()
                if not data:
                    break #daemon disconnected
        except (socket.error, FileNotFoundError):
            #daemon isnt running or socket is missing, should wait and retry
            time.sleep(5)
        finally:
            client.close()

if __name__ == "__main__":
    app = QApplication.instance() or QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    tray = setup_tray(app, CONFIG_PATH)
    #start listening for daemon notifs in bg thread
    listener_thread = threading.Thread(target=listen_for_daemon, daemon=True)
    listener_thread.start()
    app.exec_()
