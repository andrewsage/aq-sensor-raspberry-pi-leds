import matplotlib as mpl
import numpy as np
import json, requests

import RPi.GPIO as GPIO
import time

class SensorLED:
	def __init__(self, red, green, blue):
		GPIO.setup([red, green, blue], GPIO.OUT)
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

	def colourFader(self, mix = 0):
		c1 = np.array(mpl.colors.to_rgb(self.from_colour))
		c2 = np.array(mpl.colors.to_rgb(self.to_colour))
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
		colour = self.colourFader(min((value * scaling) / 100, 1))
		print (value, colour)
		self.setColour(colour)


class AQIndicator:
	def __init__(self):
		self.sensor_id = 0
		self.sensor_ip = ''
		self.p1_sensor_led = SensorLED(14, 15, 18)
		self.p2_sensor_led = SensorLED(5, 6, 13)
		self.direct = False # Is the reading direct from the sensor (True) or from the Luftdaten API (False)?
		self.url = ''

	# Test cycle through the colour range
	def demoCycle(self):
		for x in range(1, 101):
			colour = self.p1_sensor_led.colourFader(x / 100)
			self.p1_sensor_led.setColour(colour)
			colour = self.p2_sensor_led.colourFader(x / 100)
			self.p2_sensor_led.setColour(colour)
			time.sleep(0.025)

	def displayLevels(self, update_frequency):
		P1 = 0
		P2 = 0
		print (self.url)
		response = requests.get(self.url)
		if response.text:
			try:
				sensor_readings = json.loads(response.text)
				if self.direct:
					sensor = sensor_readings
				else:
					sensor = sensor_readings[-1]

				for sensor_data_value in sensor['sensordatavalues']:
					value  = sensor_data_value['value']
					value_type = sensor_data_value['value_type']
					if value_type in ['P1', 'SDS_P1']:
						P1 = float(value)
					if value_type in ['P2', 'SDS_P2']:
						P2 = float(value)

				self.p1_sensor_led.setValue(P1, 5)
				self.p2_sensor_led.setValue(P2, 10)

			except Exception as e:
				print (e)
				self.p1_sensor_led.setColour(mpl.colors.to_rgb('blue'))
		else:
			self.p1_sensor_led.setColour(mpl.colors.to_rgb('blue'))
		time.sleep(update_frequency)

class AQIndicatorDirect(AQIndicator):
	def __init__(self, sensor_ip):
		super().__init__()
		self.direct = True
		self.sensor_ip = sensor_ip
		self.url = 'http://' + sensor_ip + '/data.json'

class AQIndicatorLuftdatenAPI(AQIndicator):
	def __init__(self, sensor_id):
		super().__init__()
		self.direct = False
		self.sensor_id = sensor_id
		self.url = 'http://api.luftdaten.info/v1/sensor/' + str(self.sensor_id) + '/'

GPIO.setmode(GPIO.BCM)

SENSOR_ID = 27319 # My sensor
#SENSOR_ID = 28016 # high sensor in England
#SENSOR_ID = 7239 # high sensor in Germany
SENSOR_IP = '10.0.101.100'

UPDATE_FREQUENCY = 60
RUNNING = True
DIRECT = True

try:
	if DIRECT:
		aq_indicator = AQIndicatorDirect(SENSOR_IP)
	else:
		aq_indicator = AQIndicatorLuftdatenAPI(SENSOR_ID)
		
	aq_indicator.demoCycle()

	while RUNNING:
		aq_indicator.displayLevels(UPDATE_FREQUENCY)

except KeyboardInterrupt:
	RUNNING = False

finally:
	GPIO.cleanup()
