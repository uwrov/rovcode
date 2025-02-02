import pathlib
import subprocess

# our ROV uses a raspberry pi (linux), so we don't need to have windows-specific workarounds for physical onboard launch

result = subprocess.run(['arp', '-n'], stdout=subprocess.PIPE)
output = result.stdout.decode('utf-8').splitlines()
for line in output:
    if 'eth0' in line:
        parts = line.split()
        SURFACE_STATION_IP_ADDRESS = parts[0]
        break

#SURFACE_STATION_IP_ADDRESS = '172.25.250.2'

onboard_cwd = (pathlib.Path(__file__).parent / 'onboard').resolve()
onboard_proc = subprocess.Popen(['python3', 'onboard.py', '--physical',
                                '--websocket', f'{SURFACE_STATION_IP_ADDRESS}:8001'], cwd=onboard_cwd)

while True:
    pass
