import pathlib
import subprocess
import os

SURFACE_STATION_IP_ADDRESS = '10.19.2.241'

if os.name == 'posix':  # mac, linux, etc.
    # surface_cwd = (pathlib.Path(__file__).parent / 'surface').resolve()
    # surface_proc = subprocess.Popen(['python3', 'surface.py'], cwd=surface_cwd)

    onboard_cwd = (pathlib.Path(__file__).parent / 'onboard').resolve()
    onboard_proc = subprocess.Popen(['python3', 'onboard.py',
                                     '--websocket', f'{SURFACE_STATION_IP_ADDRESS}:8001'], cwd=onboard_cwd)
else:  # windows
    # surface_cwd = (pathlib.Path(__file__).parent / 'surface').resolve()
    # surface_proc = subprocess.Popen(
    #     ['python.exe', 'surface.py'], cwd=surface_cwd, shell=True)

    onboard_cwd = (pathlib.Path(__file__).parent / 'onboard').resolve()
    onboard_proc = subprocess.Popen(['python.exe', 'onboard.py',
                                     '--websocket', f'{SURFACE_STATION_IP_ADDRESS}:8001'], cwd=onboard_cwd, shell=True)

while True:
    pass
