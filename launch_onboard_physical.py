import pathlib
import subprocess

# our ROV uses a raspberry pi (linux), so we don't need to have windows-specific workarounds for physical onboard launch

# TODO: make this live in a separate gitignored-file?
# TODO: investigate using raspberrypi.local instead of hardcoded IP addresses?
SURFACE_STATION_IP_ADDRESS = '10.19.2.241'

onboard_cwd = (pathlib.Path(__file__).parent / 'onboard').resolve()
onboard_proc = subprocess.Popen(['python3', 'onboard.py', '--physical',
                                '--websocket', f'{SURFACE_STATION_IP_ADDRESS}:8001'], cwd=onboard_cwd)

while True:
    pass
