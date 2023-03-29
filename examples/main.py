#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""I2C EEPROM showcase"""

from eeprom import EEPROM
from machine import I2C, Pin

I2C_ADDR = 0x50

# define custom I2C interface, default is 'I2C(0)'
# check the docs of your device for further details and pin infos
i2c = I2C(0, scl=Pin(13), sda=Pin(12), freq=800000)
eeprom = EEPROM(addr=I2C_ADDR, at24x=32, i2c=i2c)   # AT24C32 on 0x50

# get LCD infos/properties
print("EEPROM is on I2C address 0x{0:02x}".format(eeprom.addr))
print("EEPROM has {} pages of {} bytes".format(eeprom.pages, eeprom.bpp))
print("EEPROM size is {} bytes ".format(eeprom.capacity))

# write 'micropython' to address 10
print("Save 'micropython' at address 10 ...")
eeprom.write(10, 'micropython')

# read 1 byte from address 4
print("Read 1 byte from address 4")
eeprom.read(4)

# read 10 byte from address 0
print("Read 10 byte from address 0")
eeprom.read(0, 10)

# write multiple pages, starting at address 25
# check bpp property of used EEPROM
# if 32 bytes are used, page 0 will contain "blablubf", page 1 will contain
# the remaining data "oobarbazquxquuxcorgegraultgraplywaldofredplughxyzzythud"
str_long = "blablubfoobarbazquxquuxcorgegraultgraplywaldofredplughxyzzythud"
print("Write '{}' to address 25".format(str_long))
eeprom.write(25, str_long)

# write a list of integers to the EEPROM, starting at address 64
int_list = [5, 17, 255, 9, 12, 7, 255]
print("Write list of integers to address 64: {}".format(int_list))
eeprom.write(64, int_list)

# update only changed values
# here 'm' -> 'M' and 'p' -> 'P', see example above
print("Update EEPROM with 'MicroPython' at address 10")
eeprom.write(10, 'MicroPython')

# update only changed values
# here 5 -> 7, 13 -> 13, 255 -> 244, see example above
int_list_updated = [7, 17, 255, 9, 13, 7, 244]
print("Update EEPROM with '{}' at address 64".format(int_list_updated))
eeprom.update(64, int_list_updated)
