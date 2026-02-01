"""Generic ESP32 with 128x160 7735 display"""

from machine import Pin, SPI
import st7789

TFA = 0
BFA = 0

def config(rotation=0, buffer_size=0, options=0):
    return st7789.ST7789(
        SPI(1, baudrate=20000000, polarity=1, phase=1, sck=Pin(14), mosi=Pin(13)),
        128,
        160,
        reset=Pin(12, Pin.OUT),
        cs=Pin(26, Pin.OUT),
        dc=Pin(27, Pin.OUT),
        color_order=st7789.RGB,
        inversion=False,
        rotation=rotation,
        options=options,
        buffer_size=buffer_size)
