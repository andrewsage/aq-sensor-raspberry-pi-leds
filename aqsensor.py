import matplotlib as mpl
import numpy as np
import json, requests

import RPi.GPIO as GPIO
import time

class SensorLED:
	def __init__(self, red, green, blue):
		GPIO.setup(red, GPIO.OUT)
		GPIO.setup(green, GPIO.OUT)
		GPIO.setup(blue, GPIO.OUT)
		# choosing a frequency for pwm
		Freq = 100
		self.RED = GPIO.PWM(red, Freq)
		self.GREEN = GPIO.PWM(green, Freq)
		self.BLUE = GPIO.PWM(blue, Freq)

		self.RED.start(50)
		self.GREEN.start(100)
		self.BLUE.start(50)
		self.from_colour = 'green'
		self.to_colour = 'red'
		self.value = 0

	def colourFader(self, c1, c2, mix = 0):
		c1 = np.array(mpl.colors.to_rgb(c1))
		c2 = np.array(mpl.colors.to_rgb(c2))
		return mpl.colors.to_rgb((1 - mix) * c1 + mix * c2)

	def setColour(self, colour):
		r = colour[0] * 100
		g = colour[1] * 100
		b = colour[2] * 100
		self.RED.ChangeDutyCycle(100 - r)
		self.GREEN.ChangeDutyCycle(100 - g)
		self.BLUE.ChangeDutyCycle(100 - b)

	def setValue(self, value, scaling):
		self.value = value
		colour = self.colourFader(self.from_colour, self.to_colour, min((value * scaling) / 100, 1))
		print (value, colour)
		self.setColour(colour)

class AQIndicator:
	def __init__(self, sensor_id):
		self.sensor_id = sensor_id
		self.p1_sensor_led = SensorLED(14, 15, 18)
		self.p2_sensor_led = SensorLED(5, 6, 13)

	# Test cycle through the colour range
	def demoCycle(self):
		for x in range(1, 101):
			colour = self.p1_sensor_led.colourFader('green', 'red', x / 100)
			self.p1_sensor_led.setColour(colour)
			time.sleep(0.025)

	def displayLevels(self, update_frequency):
		P1 = 0
		P2 = 0
		response = requests.get('http://api.luftdaten.info/v1/sensor/' + str(SENSOR_ID) + '/')
		if response.text:
			try:
				sensor_readings = json.loads(response.text)
				sensor = sensor_readings[-1]
				for sensor_data_value in sensor['sensordatavalues']:
					value  = sensor_data_value['value']
					value_type = sensor_data_value['value_type']
					if value_type == 'P1':
						P1 = float(value)
					if value_type == 'P2':
						P2 = float(value)

				self.p1_sensor_led.setValue(P1, 5)
				self.p2_sensor_led.setValue(P2, 10)

			except Exception as e:
				print (e)
				self.p1_sensor_led.setColour(mpl.colors.to_rgb('blue'))
		else:
			self.p1_sensor_led.setColour(mpl.colors.to_rgb('pink'))
		time.sleep(update_frequency)

GPIO.setmode(GPIO.BCM)

SENSOR_ID = 27319 # My sensor
#SENSOR_ID = 28016 # high sensor in England
#SENSOR_ID = 7239 # high sensor in Germany

UPDATE_FREQUENCY = 120
RUNNING = True

aq_indicator = AQIndicator(SENSOR_ID)
aq_indicator.demoCycle()

try:
	while RUNNING:
		aq_indicator.displayLevels(UPDATE_FREQUENCY)

except KeyboardInterrupt:
	RUNNING = False
	GPIO.cleanup()
