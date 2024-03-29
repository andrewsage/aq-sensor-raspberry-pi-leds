# AQ Sensor Raspberry Pi LEDs
Raspberry Pi project that shows the health levels of PM2.5 and PM10 sensor readings from a [Luftdaten](https://luftdaten.info) air quality sensor.

This project was developed to make use of sensors setup as part of the [Air Quality Aberdeen](https://www.airaberdeen.org) project.

![photo of built project](images/rpi2+built.png)


When running the LEDs indicate as follows:

* Left - the PM10 level over a range of 0 to 20 with the colour going from green to red.
* Right - the PM2.5 level over a range of 0 to 10 with the colour going from green to red.

If the Raspberry Pi is unable to connect to the Luftdaten API then the right LED will go blue.

When it starts up, just as a diagnostics test, the left LED will cycle from green to red.

## Hardware requirements
Raspberry Pi (has been tested on Raspberry Pi 2B+ and 3B+)

* 2 x RGB LED anode
* 2 x 100 ohm resistors
* 4 x 150 ohm resistors
* Breadboard
* 6 x female - male jumper wires

![breadboard diagram for Raspberry Pi AQ Sensor LEDs](images/aq-sensor-rpi-leds_bb.png)

## Software requirements
matplotlib is used to create the colour gradients. If it is not installed then install it using the following:

`sudo pip3 install matplotlib`

## Configuration

Change the following in the code:

* `DIRECT` to `True` to get data directly from sensor, `False` to get data from Luftdaten API.
* `SENSOR_IP` to the IP address of the sensor - used when getting data directly from the sensor.
* `SENSOR_ID` to the Luftdaten ID of the sensor you wish to monitor - used when getting data from Luftdaten API.
* `UPDATE_FREQUENCY` to the number of milliseconds between requests to the Luftdaten API.


## Running

```
sudo python3 aqsensor.py
```

```
Usage: aqsensor.py [OPTIONS]

Options:
-h --help	Show this help text and exit
-v --verbose	Show diagnostic information whilst running
-i <IP address>] --ip=<IP address>	IP address of the sensor to get data directly from
-s <ID> --id=<ID>	the Luftdaten ID of the sensor you wish to monitor
-f <frequency> --frequency=<frequency>	update frequency in milliseconds

If ID is specified then IP address is ignored.
If neither IP or ID are specified then the default ID is used.
```

Or it can be run in the background by setting the permission of the file to allow execution:

```
chmod +x aqsensor.py
```

To start it running (and be able to close the terminal and leave it running):

```
nohup ./aqsensor.py &
```

To stop it running in the background:

```
ps ax | grep aqsensor.py
kill PID
```

