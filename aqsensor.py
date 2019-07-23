#!/usr/bin/env python3

import matplotlib as mpl
import numpy as np
import json
import requests
from requests.exceptions import HTTPError

import RPi.GPIO as GPIO
import time
import sys, getopt

class SensorLED:
	def __init__(self, red, green, blue, verbose = False):
		self.verbose = verbose
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
		self.setColour(colour)
		if self.verbose:
			print (value, colour)


class AQIndicator:
	def __init__(self, verbose = False):
		self.verbose = verbose
		self.sensor_id = 0
		self.sensor_ip = ''
		self.p1_sensor_led = SensorLED(14, 15, 18, self.verbose)
		self.p2_sensor_led = SensorLED(5, 6, 13, self.verbose)
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
		if self.verbose:
			print (self.url)
		try:
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
				self.p1_sensor_led.setColour(mpl.colors.to_rgb('pink'))
		
		except HTTPError as http_err:
			print('HTTP error occurred: ' + http_err)
			self.p1_sensor_led.setColour(mpl.colors.to_rgb('blue'))
		except Exception as err:
			print(err)
			self.p1_sensor_led.setColour(mpl.colors.to_rgb('blue'))
		
		time.sleep(update_frequency)

class AQIndicatorDirect(AQIndicator):
	def __init__(self, sensor_ip, verbose = False):
		super().__init__(verbose)
		self.direct = True
		self.sensor_ip = sensor_ip
		self.url = 'http://' + sensor_ip + '/data.json'

class AQIndicatorLuftdatenAPI(AQIndicator):
	def __init__(self, sensor_id, verbose = False):
		super().__init__(verbose)
		self.direct = False
		self.sensor_id = sensor_id
		self.url = 'http://api.luftdaten.info/v1/sensor/' + str(self.sensor_id) + '/'


def usage():
	print ('Usage: aqsensor.py [OPTIONS]\n\nOptions:\n-h --help\tShow this help text and exit\n-v --verbose\tShow diagnostic information whilst running\n-i <IP address>] --ip=<IP address>\tIP address of the sensor to get data directly from\n-s <ID> --id=<ID>\tthe Luftdaten ID of the sensor you wish to monitor\n-f <frequency> --frequency=<frequency>\tupdate frequency in milliseconds\n\nIf ID is specified then IP address is ignored.\nIf neither IP or ID are specified then the default ID is used.')

def main(argv):
	SENSOR_ID = 27319 # My sensor
	#SENSOR_ID = 28016 # high sensor in England
	#SENSOR_ID = 7239 # high sensor in Germany
	SENSOR_IP = '10.0.101.100'

	UPDATE_FREQUENCY = 60
	RUNNING = True
	DIRECT = False

	update_frequency = UPDATE_FREQUENCY
	sensor_id = SENSOR_ID
	sensor_ip = SENSOR_IP
	direct = DIRECT
	verbose = False
	try:
		opts, args = getopt.getopt(argv, 'hvi:s:f:', ['ip=', 'id=', 'frequency=', 'verbose'])
	except getopt.GetoptError:
		usage()
		sys.exit(2)

	for opt, arg in opts:
		if opt in ('-h', '--help'):
			usage()
			sys.exit()
		elif opt in ('-v', '--verbose'):
			verbose = True
		elif opt in ('-i', '--ip'):
			sensor_ip = arg
			direct = True
		elif opt in ('-s', '--id'):
			sensor_id = arg
			direct = False
		elif opt in ('-f', '--frequency'):
			try:
				update_frequency = int(arg)
			except:
				usage()
				sys.exit(2)

	if verbose == True:
		print('Update frequency: ' + str(update_frequency) + ' milliseconds')

	GPIO.setmode(GPIO.BCM)
	try:
		if direct:
			aq_indicator = AQIndicatorDirect(sensor_ip, verbose)
		else:
			aq_indicator = AQIndicatorLuftdatenAPI(sensor_id, verbose)

		aq_indicator.demoCycle()

		while RUNNING:
			aq_indicator.displayLevels(update_frequency)

	except KeyboardInterrupt:
		RUNNING = False

	finally:
		GPIO.cleanup()


if __name__ == "__main__":
	main(sys.argv[1:])
