import pathlib
import subprocess
import time

# surface_cwd = (pathlib.Path(__file__).parent / 'surface').resolve()
# surface_proc = subprocess.Popen(['python.exe', 'surface.py'], cwd=surface_cwd, shell=True)

onboard_cwd = (pathlib.Path(__file__).parent / 'onboard').resolve()
onboard_proc = subprocess.Popen(['python.exe', 'onboard.py', '--websocket', '10.19.2.241:8001'], cwd=onboard_cwd, shell=True) #'--websocket', '10.19.2.241:8001'

while True:
    pass
