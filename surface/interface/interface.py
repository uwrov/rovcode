import pathlib
import subprocess
import websockets
import asyncio
import json

websocket = None

def notify_new_sensor_data():
    print(f'accelerometer: {core.accelerometer}, gyro: {core.gyroscope}')

def init(_core, _task):
    global core, task
    core, task = _core, _task

    uri = 'ws://localhost:8002'
    cwd = (pathlib.Path(__file__).parent / 'godot').resolve()
    subprocess.Popen(['godot', '--quiet', 'interface.tscn', '-u', uri], cwd=cwd,
                     stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


async def server_handler(_websocket):
    global websocket
    websocket = _websocket
    async for message in websocket:
        data = json.loads(str(message)[2:-1])
        result = json.dumps(data)
        core.translate_x = data['translate']


async def notify_sensor_update():
    if websocket == None:
        return
    await websocket.send(json.dumps({
        'accelerometer': core.accelerometer,
        'gyroscope': core.gyroscope
    }))
