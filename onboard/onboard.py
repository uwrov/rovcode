import argparse
import asyncio
import json
import os

import websockets
from websockets.client import ClientConnection

def main():
    print('onboard client starting')
    rov, websocket_uri = setup_using_command_line_args()
    asyncio.run(client_handler(websocket_uri, rov))


# allows file to be run with arguments
# includes default websocket if none specified 
def setup_using_command_line_args():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-p', '--physical', action='store_true',
                            help='run using physical instead of simulated hardware')
    arg_parser.add_argument('-w', '--websocket', default='localhost:8001',
                            help='websocket\'s ip and port, e.g. localhost:8001')
    args = arg_parser.parse_args()

    if args.physical:
        from physical.physical import ROV
    else:
        from simulated.simulated import ROV

    rov = ROV()
    websocket_uri = f'ws://{args.websocket}'
    
    return rov, websocket_uri


# connect to surface station
async def client_handler(websocket_uri: str, rov: 'ROV'):
    async for websocket in websockets.connect(websocket_uri):
        try:
            await asyncio.gather(
                consumer_handler(websocket, rov),
                producer_handler(websocket, rov)
            )
        except websockets.ConnectionClosed:
            print('onboard: websockets.ConnectionClosed - retrying...')
            await asyncio.sleep(1)
            continue


# incoming command handling (instructions for ROV)
async def consumer_handler(websocket: ClientConnection, rov: 'ROV'):
    async for message in websocket:
        data = json.loads(message)
        if data['type'] == 'set_pin_pwms':
            for pin in data['pins']:
                rov.set_pin_pwm(pin['number'], pin['value'])
            await rov.flush_pin_pwms()
        else:
            print(f'Invalid type {data.type} for message: {message}')


# outgoing data handling (sensor readings)
async def producer_handler(websocket: ClientConnection, rov: 'ROV'):
    while True:
        await asyncio.gather(
            send_onboard_digest(websocket, rov),
            asyncio.sleep(0.1)  # limit to 10 summaries per second
        )


# TODO: create hardware-agnostic sensor reading system
# currently requires hardcoding sensor pins, protocols, etc.
async def send_onboard_digest(websocket: ClientConnection, rov: 'ROV'):
    gyro, accel = await rov.poll_sensors()
    await websocket.send(json.dumps({
        'type': 'sensor_summary',
        'accelerometer': accel,
        'gyroscope': gyro,
    }))


if __name__ == "__main__":
    main()
