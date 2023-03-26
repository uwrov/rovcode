import asyncio
import json
import os

import core.core as core
import interface.interface as interface
import task.task as task
import websockets


def main():
    print('surface server starting')
    core.init(interface, task)  # dirty hack to import sibling modules...
    interface.init(core, task)
    task.init(core, interface)
    print('serving')
    asyncio.run(serve())


# start the surface station and interface servers
# rov_server communicates with the actual ROV
# interface_server communicates with Godot interface running on surface station
# gather makes an infinite loop to keep communicating with ROV and interface
async def serve():
    rov_server = await websockets.serve(rov_server_handler, "", 8001)
    interface_server = await websockets.serve(interface.server_handler, "", 8002)
    await asyncio.gather(
        rov_server.wait_closed(),
        interface_server.wait_closed()
    )


# handles incoming ("consumer") and outgoing ("producer") communication with ROV
# see: https://websockets.readthedocs.io/en/stable/howto/patterns.html
async def rov_server_handler(websocket):
    await asyncio.gather(
        consume_incoming_data_from_rov(websocket),
        produce_outgoing_commands_to_rov(websocket)
    )


async def consume_incoming_data_from_rov(websocket):
    async for message in websocket:
        data = json.loads(message)
        if data['type'] == 'sensor_summary':
            await core.update_sensors(data)
        else:
            print(f'Invalid type {data.type} for message: {message}')


async def produce_outgoing_commands_to_rov(websocket):
    while True:
        await asyncio.gather(
            update_controls_and_send_to_rov(websocket),
            asyncio.sleep(0.1)  # limit to 10 summaries per second
        )


async def update_controls_and_send_to_rov(websocket):
    await core.update_controls()
    await websocket.send(json.dumps({
        'type': 'set_pin_pwms',
        'pins': core.pin_pwms
    }))


if __name__ == "__main__":
    main()
