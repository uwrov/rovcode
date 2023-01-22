import random

accelerometer, gyroscope = None, None
translate_x = 0.0

pin_pwms = None

def init(_interface, _task):
    global interface, task
    interface, task = _interface, _task


async def update_sensors(summary_data):
    global accelerometer, gyroscope
    accelerometer = summary_data['accelerometer']
    gyroscope = summary_data['gyroscope']
    await interface.notify_sensor_update()


async def update_controls():
    global pin_pwms
    pin_pwms = [
        {
            'number': 10,
            'value': 1500 + round(translate_x * 200),
        },
        # {
        #     'number': 11,
        #     'value': 1650 + random.randint(-5, 5),
        # }
    ]
