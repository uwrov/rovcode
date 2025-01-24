import pathlib
import subprocess
import websockets
import asyncio
import json

class Interface():
    def __init__(self, _core: 'Core'):
        self.core = _core
        self.task = None
        self.websocket = None

        uri = 'ws://localhost:8002'
        cwd = (pathlib.Path(__file__).parent / 'godot').resolve()
        subprocess.Popen(['godot', '--quiet', 'interface.tscn', '-u', uri], cwd=cwd,
                         stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    def set_task(self, task: 'Task'):
        self.task = task


    def notify_new_sensor_data(self):
        print(f'accelerometer: {self.core.accelerometer}, gyro: {self.core.gyroscope}')

    async def server_handler(self, _websocket):
        self.websocket = _websocket
        async for message in self.websocket:
            data = json.loads(str(message)[2:-1])
            result = json.dumps(data)
            await self.core.consume_interface_websocket(data['translate'], data['translation'], data['rotation'], data['direct_motors'], data['servo_pwm'])


    async def notify_sensor_update(self):
        if self.websocket != None:
            await self.websocket.send(json.dumps({
                'accelerometer': self.core.accelerometer,
                'gyroscope': self.core.gyroscope
            }))
