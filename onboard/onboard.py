import argparse
import asyncio
import json
import os

import websockets

rov, websocket_uri = None, None


def main():
    # os.system('clear')
    print('onboard client starting')
    setup_from_args()
    rov.init()
    asyncio.run(client_handler())


def setup_from_args():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-p', '--physical', action='store_true',
                            help='run using physical instead of simulated hardware')
    arg_parser.add_argument('-w', '--websocket', default='localhost:8001',
                            help='websocket\'s ip and port, e.g. localhost:8001')
    args = arg_parser.parse_args()

    global rov, websocket_uri
    if args.physical:
        import physical.physical as rov
    else:
        import simulated.simulated as rov
    websocket_uri = f'ws://{args.websocket}'


# connect to surface station ---------------------------------------------------
async def client_handler():
    async for websocket in websockets.connect(websocket_uri):
        try:
            await asyncio.gather(
                consumer_handler(websocket),
                producer_handler(websocket)
            )
        except websockets.ConnectionClosed:
            print('onboard: websockets.ConnectionClosed - retrying...')
            await asyncio.sleep(1)
            continue


# incoming command handling (instructions for ROV) -----------------------------
async def consumer_handler(websocket):
    async for message in websocket:
        data = json.loads(message)
        match data['type']:
            case 'set_pin_pwms':
                for pin in data['pins']:
                    rov.set_pin_pwm(pin['number'], pin['value'])
                await rov.flush_pin_pwms()
            case _:
                print(f'Invalid type {data.type} for message: {message}')


# outgoing data handling (sensor readings) -------------------------------------
async def producer_handler(websocket):
    while True:
        await asyncio.gather(
            send_onboard_digest(websocket),
            asyncio.sleep(0.1)  # limit to 10 summaries per second
        )


# TODO: create hardware-agnostic sensor reading system
# currently requires hardcoding sensor pins, protocols, etc.
async def send_onboard_digest(websocket):
    await rov.poll_sensors()
    await websocket.send(json.dumps({
        'type': 'sensor_summary',
        'accelerometer': rov.accelerometer,
        'gyroscope': rov.gyroscope,
    }))


# start the rov! ---------------------------------------------------------------
if __name__ == "__main__":
    main()
