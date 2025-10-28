import sys
import subprocess
import numpy as np

class VolumeController:
    def get_range(self):
        return (0, 100)

    def set_volume(self, level: int):
        raise NotImplementedError

    def get_volume(self) -> int:
        raise NotImplementedError

    def toggle_mute(self):
        raise NotImplementedError


class WindowsVolume(VolumeController):
    def __init__(self):
        from ctypes import POINTER, cast
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))

    def get_range(self):
        return (0, 100)

    def set_volume(self, level: int):
        level = int(np.clip(level, 0, 100))
        self.volume.SetMasterVolumeLevelScalar(level / 100.0, None)

    def get_volume(self) -> int:
        return int(round(self.volume.GetMasterVolumeLevelScalar() * 100))

    def toggle_mute(self):
        muted = self.volume.GetMute()
        self.volume.SetMute(0 if muted else 1, None)


class MacVolume(VolumeController):
    def set_volume(self, level: int):
        level = int(np.clip(level, 0, 100))
        subprocess.call(["osascript", "-e", f"set volume output volume {level}"])

    def get_volume(self) -> int:
        out = subprocess.check_output(["osascript", "-e", "output volume of (get volume settings)"])
        return int(out.decode().strip())

    def toggle_mute(self):
        out = subprocess.check_output(["osascript", "-e", "output muted of (get volume settings)"])
        muted = out.decode().strip().lower() == "true"
        subprocess.call(["osascript", "-e", f"set volume output muted {str(not muted).lower()}"])


class LinuxVolume(VolumeController):
    def set_volume(self, level: int):
        level = int(np.clip(level, 0, 100))
        subprocess.call(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{level}%"])

    def get_volume(self) -> int:
        try:
            out = subprocess.check_output(["pactl", "get-sink-volume", "@DEFAULT_SINK@"]).decode()
            perc = [int(tok.strip('%')) for tok in out.split() if tok.endswith('%')]
            return int(np.mean(perc)) if perc else 50
        except Exception:
            return 50

    def toggle_mute(self):
        subprocess.call(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"])


def get_volume_controller():
    if sys.platform.startswith("win"):
        return WindowsVolume()
    if sys.platform == "darwin":
        return MacVolume()
    return LinuxVolume()
