import RPi.GPIO as GPIO
import datetime as dt


class LED:
    def __init__(self, pin):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(pin, GPIO.OUT)
        self._light = False
        self._pin = pin
        self._timer = dt.datetime.now()

    def switch(self):
        if (dt.datetime.now() - self._timer).total_seconds() >= 1:
            if self._light:
                self.set_low()
            else:
                self.set_high()

    def set_low(self):
        GPIO.output(self._pin, GPIO.LOW)
        self._light = False

    def set_high(self):
        GPIO.output(self._pin, GPIO.HIGH)
        self._light = True
