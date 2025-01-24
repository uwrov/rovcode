import pathlib
import subprocess
import websockets
import asyncio
import json

class Interface():
    def __init__(_core, _task):
        self.core, self.task = _core, _task
        self.websocket = None

        uri = 'ws://localhost:8002'
        cwd = (pathlib.Path(__file__).parent / 'godot').resolve()
        subprocess.Popen(['godot', '--quiet', 'interface.tscn', '-u', uri], cwd=cwd,
                         stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    def notify_new_sensor_data():
        print(f'accelerometer: {self.core.accelerometer}, gyro: {self.core.gyroscope}')

    async def server_handler(_websocket):
        self.websocket = _websocket
        async for message in self.websocket:
            data = json.loads(str(message)[2:-1])
            result = json.dumps(data)
            core.consume_interface_websocket(data['translate'], data['translation'], data['rotation'], data['direct_motors'], data['servo_pwm'])


    async def notify_sensor_update():
        if self.websocket != None:
            await self.websocket.send(json.dumps({
                'accelerometer': self.core.accelerometer,
                'gyroscope': self.core.gyroscope
            }))
