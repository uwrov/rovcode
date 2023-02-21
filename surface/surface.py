import asyncio
import json
import os

import core.core as core
import interface.interface as interface
import task.task as task
import websockets


def main():
    # os.system('clear')
    print('surface server starting')
    core.init(interface, task)  # dirty hack to import sibling modules...
    interface.init(core, task)
    task.init(core, interface)
    print('serving')
    asyncio.run(serve())


# start the surface station and interface servers ------------------------------
async def serve():
    rov_server = await websockets.serve(server_handler, "", 8001)
    interface_server = await websockets.serve(interface.server_handler, "", 8002)
    await asyncio.gather(
        rov_server.wait_closed(),
        interface_server.wait_closed()
    )


async def server_handler(websocket):
    await asyncio.gather(
        consumer_handler(websocket),
        producer_handler(websocket)
    )


# incoming data handling (sensor readings etc. from ROV) -----------------------
async def consumer_handler(websocket):
    async for message in websocket:
        data = json.loads(message)
        if data['type'] == 'sensor_summary':
            await core.update_sensors(data)
        else:
            print(f'Invalid type {data.type} for message: {message}')


# outgoing command handling (control outputs) ----------------------------------
async def producer_handler(websocket):
    while True:
        await asyncio.gather(
            send_control_digest(websocket),
            asyncio.sleep(0.1)  # limit to 10 summaries per second
        )


async def send_control_digest(websocket):
    await core.update_controls()
    await websocket.send(json.dumps({
        'type': 'set_pin_pwms',
        'pins': core.pin_pwms
    }))


# start the surface station! ---------------------------------------------------
if __name__ == "__main__":
    main()
