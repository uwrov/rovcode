import pathlib
import subprocess
import os


if os.name == 'posix':  # mac, linux, etc.
    surface_cwd = (pathlib.Path(__file__).parent / 'surface').resolve()
    surface_proc = subprocess.Popen(['python3', 'surface.py'], cwd=surface_cwd)
else:  # windows
    surface_cwd = (pathlib.Path(__file__).parent / 'surface').resolve()
    surface_proc = subprocess.Popen(
        ['python.exe', 'surface.py'], cwd=surface_cwd, shell=True)

while True:
    pass
