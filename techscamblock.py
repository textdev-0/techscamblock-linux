import psutil, time, sys, ctypes, os, re, urllib.request, getpass, threading
from pathlib import Path
from plyer import notification
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal
from aboutremoteblock import show_scam_warning
from tray import setup_tray



APP_DIR      = os.path.dirname(os.path.abspath(sys.argv[0]))
CONFIG_PATH  = os.path.join(APP_DIR, "techscamblock.conf")



_DEFAULT_CFG = (
	"# TechScamBlock by the Raven Development Team\n"
	"# Unless you know what you are doing, you shouldn't modify this file.\n\n"
	"# ntfy.sh integration, to get mobile alerts\n"
	'NTFY_NOTIFICATION_ENDPOINT_URL = ""\n\n'
	"# Remote access tools that are allowed to run. Specify process name, "
	"# separated by a comma and a space (example1, example2, example3, ...)\n"
	'WHITELISTED_REMOTE_ACCESS_TOOLS = ""\n'
)



def _ensure_config() -> dict:
	if not os.path.exists(CONFIG_PATH):
		with open(CONFIG_PATH, "w", encoding="utf-8") as fh:
			fh.write(_DEFAULT_CFG)
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



_raw_white     = _cfg.get("WHITELISTED_REMOTE_ACCESS_TOOLS", "")
_whitelist_set = {m.group(0).lower() for m in re.finditer(r"[A-Za-z0-9_\-\.]+", _raw_white)}
_ALLOWED_SET   = _whitelist_set



class ScamNotifier(QObject):
	alert = pyqtSignal()



notifier = ScamNotifier()
info_window_open = False



def _handle_alert():
	global info_window_open
	show_scam_warning()
	info_window_open = False



notifier.alert.connect(_handle_alert)



remote_access_processes = [
    # TeamViewer
    "TeamViewer.exe",
    "TeamViewer_Setup.exe",
    "TeamViewer_Service.exe",
    "TeamViewer_Desktop.exe",
    "TeamViewer_Host.exe",

    # AnyDesk
    "AnyDesk.exe",
    "adservice.exe",

    # LogMeIn (and GoToAssist)
    "LogMeIn.exe",
    "LogMeInRescue.exe",
    "LMIGuardianSvc.exe",
    "GoToAssist.exe",
    "SRServer.exe",
    "GoToResolveUnattended.exe",
    "GoToResolveUnattendedUpdater.exe",
    "GoToResolveUnattendedUI.exe",
    "GoToResolveTools64.exe",
    "GoToResolveUi.exe",
    "GoToResolveService.exe",
    "GoToResolveProcessChecker.exe",
    "GoToResolveCrashHandler.exe",
    "GoToResolveLoggerProcess.exe",
    "GoTo.Resolve.Antivirus.App.exe",
    "GoTo.Resolve.PatchManagement.Client.exe",
    "GoTo.Resolve.Alerts.Monitor.App.exe",
    "GoToResolve.exe",

    # GoToMyPC Remote Desktop
    "g2tray.exe",
    "g2comm.exe",
    "g2host.exe",
    "g2svc.exe",
    "g2vistahelper.exe",
    "g2mainh.exe",
    "g2fileh.exe",
    "g2audioh.exe",
    "g2printh.exe",
    "GoToMyPCCrashHandler.exe",

    # FleetDeck Remote Desktop
    "fleetdeck-agent.exe",
    "fleetdeck-agent.msi",
    "fleetdeck-agent.mst",
    "fleetdeck.exe",
    "fleetdeck_agent_svc.exe",

    # Splashtop Remote Desktop
    "SplashtopRemote.exe",
    "SplashtopStreamer.exe",

    # VNC Connect (RealVNC)
    "vncserver.exe",
    "vncviewer.exe",

    # Zoho Assist
    "ZohoAssist.exe",
    "zohosupport.exe",

    # Chrome Remote Desktop
    "remote_assistance_host.exe",
    "remote_assistance_host_uiaccess.exe",
    "remote_open_url.exe",
    "remote_security_key.exe",
    "remote_webauthn.exe",
    "remoting_desktop.exe",
    "remoting_host.exe",
    "remoting_native_messaging_host.exe",
    "remoting_start_host.exe",
    "chromeremotedesktophost.msi",

    # Atera Remote Desktop
    "AteraAgent.exe",
    "AgentPackageNetworkDiscoveryWG.exe",
    "AgentPackageAgentInformation.exe",
    "AgentPackageSTRemote.exe",
    "AgentPackageFileExplorer.exe",
    "AgentPackageMonitoring.exe",
    "AgentPackageRuntimeInstaller.exe",

    # Microsoft Remote Desktop (RDP)
    "mstsc.exe",

    # Supremo Remote Desktop
    "SupremoSystem.exe",
    "Supremo.exe",
    "SupremoHelper.exe",

    # Quick Assist (Windows built-in)
    "QuickAssist.exe",

    # FixMeIT Remote Desktop
    "TiClientCore.exe",

    # UltraVNC Remote Desktop
    "winvnc.exe",
    "vncviewer.exe",

    # RemotePC Remote Desktop
    "RemotePC.exe",
    "RemotePCService.exe",

    # Iperius Remote
    "IperiusRemote.exe",

    # LiteManager Remote Desktop
    "LiteManagerPro.exe",
    "LiteManagerViewer.exe",

    # ConnectWise (ScreenConnect)
    "ScreenConnect.WindowsClient.exe",
    "ScreenConnect.BackstageShell.exe",
    "ScreenConnect.ClientService.exe",
    "ScreenConnect.Service.exe",
    "ClientService.exe",

    # Remote Utilities
    "RUTServ.exe",
    "RViewer.exe",

    # DesktopNow (NCH Software)
    "DesktopNow.exe",

    # NetSupport Manager
    "presentationhost.exe",
    "remcmdstub.exe",

    # N-Able Remote Desktop
    "TakeControlTechConsole",
    "NableCommandPromptManager32.exe",
    "NableCommandPromptManager64.exe",
    "NableReactiveManagement.exe",
    "BASupSrvc.exe",
    "BASupSrvcCnfg.exe",
    "PME.Agent.exe",
    "RequestHandlerAgent.exe",
    "FileCacheServiceAgentSetup.exe",
    "RequestHandlerAgentSetup.exe",

    # ngrok Tunnel
    "ngrok.exe",

    # Getscreen Remote Desktop
    "Getscreen.exe",

    # Additional Various Remote Desktop Utilities:
    "LiteManagerServer.exe",
    "Radmin.exe",
    "RDPClip.exe",
    "Bomgar.exe",
    "RDPWrap.exe",
    "tailscale.exe",
    "tailscaled.exe",
    "MeshAgent.exe",
    "tacticalrmm.exe",
    "SimpleService.exe",
    "remoteaccesswinlauncher.exe",
    "rustdesk.exe",
    "PCMonitorSrv.exe",
    "PCMonitorManager.exe",
    "nxexec.exe",
    "nxplayer.exe",
    "nxservice.exe",
    "nxservice64.exe",
    "NinjaRMMAgentPatcher.exe",
    "ninjarmm-cli.exe",
    "NinjaRMMAgent.exe",
    "MeshAgent.exe",
]



_REMOTE_SET = {p.lower() for p in remote_access_processes}



def is_admin():
	try:
		return ctypes.windll.shell32.IsUserAnAdmin() != 0
	except Exception:
		return False



def run_as_admin():
	try:
		ctypes.windll.shell32.ShellExecuteW(
			None, "runas", sys.executable, " ".join(sys.argv), None, 1
		)
		sys.exit()
	except Exception:
		sys.exit()



def launch_info_window():
	global info_window_open
	if not info_window_open:
		info_window_open = True
		notifier.alert.emit()



def monitor_processes():
	username = getpass.getuser()
	notified = set()
	while True:
		for proc in psutil.process_iter(['pid', 'name']):
			try:
				name_raw = proc.info['name'] or ""
				name = name_raw.lower()
				if name in _ALLOWED_SET:
					continue
				if name in _REMOTE_SET and name not in notified:
					proc.kill()
					notified.add(name)
					notification.notify(
						title="Remote Access Attempt Prevented",
						message="An attempt to remotely access your device was prevented.",
						timeout=5
					)
					_send_ntfy(
						f"TechScamBlock: {name_raw} was ran and blocked on {username}'s device."
					)
					launch_info_window()
			except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
				pass
		time.sleep(1)



if __name__ == "__main__":
	if not is_admin():
		run_as_admin()
	else:
		app = QApplication.instance() or QApplication(sys.argv)
		app.setQuitOnLastWindowClosed(False)
		tray = setup_tray(app, CONFIG_PATH)
		threading.Thread(target=monitor_processes, daemon=True).start()
		app.exec_()
