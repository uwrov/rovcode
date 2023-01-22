import pathlib
import subprocess
import time

surface_cwd = (pathlib.Path(__file__).parent / 'surface').resolve()
surface_proc = subprocess.Popen(['python3', 'surface.py'], cwd=surface_cwd)

onboard_cwd = (pathlib.Path(__file__).parent / 'onboard').resolve()
onboard_proc = subprocess.Popen(['python3', 'onboard.py'], cwd=onboard_cwd)

while True:
    pass