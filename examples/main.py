#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Main script
Do your stuff here, similar to the loop() function on Arduino
"""

from be_upy_blink import flash_led
from machine import Pin
from time import sleep


def loop():
    # set pin D4 as output (blue LED) and turn it off
    led_pin = Pin(4, Pin.OUT)
    led_pin.value(0)

    # loop forever
    while True:
        # flash LED 3 times, being each 1 second on and 3 seconds off
        # then sleep for 3 seconds and repeat
        flash_led(pin=led_pin, amount=3, on_time=1, off_time=2)
        sleep(3)


# MicroPython calls every function inside this file
loop()
