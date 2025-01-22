import pigpio
import logging
import sys
import time
import serial
import busio
import board

import adafruit_bno055

class ROV:
    def __init__():
        self.pi = pigpio.pi("main", 8888)
        # uncomment if using I2C instead of UART
        # i2c = board.I2C()
        # bno = adafruit_bno055.BNO055_I2C(i2c)

        # UART setup
        uart = serial.Serial("/dev/serial0")
        self.bno = adafruit_bno055.BNO055_UART(uart)

    # number = GPIO number
    # value = PWM value
    def set_pin_pwm(number: int, value: int): 
        print(number, value)
        self.pi.set_servo_pulsewidth(number, value)


    # unnecessary for physical ROV
    async def flush_pin_pwms():
        pass


    # updates accelerometer and gyroscope values
    async def poll_sensors():
        # Gyroscope data (in degrees per second)
        # Accelerometer data (in meters per second squared)
        return self.bno.gyro, self.bno.acceleration
