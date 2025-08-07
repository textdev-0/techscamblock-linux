import psutil
import socket
import signal
import os
import sys
import threading
import time
import re

#not the full main script because principle of least privs (or something) and also gui breaks in su
#daemon has su privs by default

# The daemon needs to read the config directly to know what to whitelist.
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
_raw_white = _cfg.get("WHITELISTED_REMOTE_ACCESS_TOOLS", "")
_whitelist_set = {m.group(0).lower() for m in re.finditer(r"[A-Za-z0-9_\-\.]+", _raw_white)}
_ALLOWED_SET = _whitelist_set

remote_access_processes = [
    # This list contains remote access tools commonly used in tech support scams.
    # It has been curated to avoid blocking standard Linux utilities.
    # It includes Windows executable names that might be run via Wine.
    "teamviewer",
    "anydesk",
    "rustdesk",
    "adservice",
    "LogMeIn",
    "LMIGuardianSvc",
    "GoToAssist",
    "SRServer",
    "GoTo.Resolve",
    "GoToResolve",
    "g2tray",
    "g2comm",
    "g2host",
    "g2svc",
    "g2vistahelper",
    "g2mainh",
    "g2fileh",
    "g2audioh",
    "g2printh",
    "GoToMyPCCrashHandler",
    "fleetdeck-agent",
    "fleetdeck-agent.msi",
    "fleetdeck-agent.mst",
    "fleetdeck",
    "fleetdeck_agent_svc",
    "SplashtopRemote",
    "SplashtopStreamer",
    "ZohoAssist",
    "zohosupport",
    "remote_assistance_host",
    "remote_assistance_host_uiaccess",
    "remote_open_url",
    "remote_security_key",
    "remote_webauthn",
    "remoting_desktop",
    "remoting_host",
    "remoting_native_messaging_host",
    "remoting_start_host",
    "chromeremotedesktophost.msi",
    "AteraAgent",
    "AgentPackage",
    "mstsc",
    "SupremoSystem",
    "Supremo",
    "SupremoHelper",
    "QuickAssist",
    "TiClientCore",
    "winvnc",
    "RemotePC",
    "RemotePCService",
    "IperiusRemote",
    "LiteManagerPro",
    "LiteManagerViewer",
    "ScreenConnect",
    "ClientService",
    "RUTServ",
    "RViewer",
    "DesktopNow",
    "presentationhost",
    "remcmdstub",
    "TakeControlTechConsole",
    "NableCommandPromptManager",
    "NableReactiveManagement",
    "BASupSrvc",
    "PME.Agent",
    "RequestHandlerAgent",
    "FileCacheServiceAgentSetup",
    "RequestHandlerAgentSetup",
    "Getscreen",
    "LiteManagerServer",
    "Radmin",
    "RDPClip",
    "Bomgar",
    "MeshAgent",
    "tacticalrmm",
    "SimpleService",
    "remoteaccesswinlauncher",
    "PCMonitorSrv",
    "PCMonitorManager",
    "nxexec",
    "nxservice",
    "NinjaRMM",
    "ngrok",
]
_REMOTE_SET = {p.lower() for p in remote_access_processes}

clients = []
clients_lock = threading.Lock()

#tell the gui that something bad happened
def notify_clients():
    with clients_lock:
        #loop over a copy of the list, so we can modify the original
        for client in list(clients):
            try:
                client.sendall(b"PROCESS_KILLED")
            except socket.error:
                #if the pipe is broken the client is gone
                clients.remove(client)

def monitor_processes():
    while True:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                name = (proc.info['name'] or "").lower()
                if name in _ALLOWED_SET:
                    continue

                #combine name and cmdline into one string for a bettercheck 2.0 (TM)
                full_check_string = name + ' ' + ' '.join([arg.lower() for arg in proc.info['cmdline'] or []])

                for p in _REMOTE_SET:
                    if p in full_check_string:
                        proc.kill()
                        # let the gui know we did a thing
                        notify_clients()
                        break # Found a match, move to the next process
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        time.sleep(1)

def cleanup_socket(signum, frame): #remove sock on shutdown
    try:
        os.remove(SOCKET_PATH)
    except OSError:
        pass
    sys.exit(0)

##########main logic

SOCKET_PATH = "/run/techscamblock.sock"

signal.signal(signal.SIGINT, cleanup_socket) #remove sock on nice shutdown/term
signal.signal(signal.SIGTERM, cleanup_socket)

if os.path.exists(SOCKET_PATH): #remove if already exists
    os.remove(SOCKET_PATH)

server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(SOCKET_PATH)
server.listen(5)
os.chmod(SOCKET_PATH, 0o666) #create socket with right perms

#boot up the actual scanner in the background
monitor_thread = threading.Thread(target=monitor_processes, daemon=True)
monitor_thread.start()

#main thread just wiats and listens for gui clients
while True:
    connection, client_address = server.accept()
    with clients_lock:
        clients.append(connection)
