# Examples

Usage examples of this `micropython-eeprom` library

---------------

## General

An example of all implemented functionalities can be found at the
[MicroPython EEPROM examples folder][ref-micropython-eeprom-examples]

## Setup EEPROM

```python
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
```

## Read data

```python
# read 1 byte from address 4
eeprom.read(4)

# read 10 byte from address 7
eeprom.read(7, 10)
```

## Write data

```python
# write 'micropython' to address 10
eeprom.write(10, 'micropython')

# write multiple pages, starting at address 25
# check bpp property of used EEPROM
# if 32 bytes are used, page 0 will contain "blablubf", page 1 will contain
# the remaining data "oobarbazquxquuxcorgegraultgraplywaldofredplughxyzzythud"
eeprom.write(25, 'blablubfoobarbazquxquuxcorgegraultgraplywaldofredplughxyzzythud')

# write a list of integers to the EEPROM, starting at address 64
eeprom.write(64, [5, 17, 255, 9, 12, 7, 255])
```

## Update data

```python
# update only changed values, here 'm' -> 'M' and 'p' -> 'P', see write example
eeprom.write(10, 'MicroPython')

# update only changed values, here 5 -> 7, 13 -> 13, 255 -> 244, see write example
eeprom.update(64, [7, 17, 255, 9, 13, 7, 244])
```
