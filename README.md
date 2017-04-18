# ILOCI
Imminent Loss of Control Identification as applied to a Lambada motorglider 

A project using machine learning and computationa thinking with Wolfram Mathematica on the Raspberry Pi 2 (RPi2)

Code is provided to operate on the Raspberry Pi Linux distribution Wheezy

The code enables the RPi2 to

1) Read 8 channels of signal conditioned sensor voltages from an MCP3008 chip using the Serial Parallel Interface SPI protocol via a Wolfram Mathlink C program interface, using C source code compiled and built using the Geany IDE, ML_spidev_mcp3008

2) Access the real time analog data within a Wolfram notebook or package started at RPi2 boot.

3) Analyze and classify the meaning of the sensor data using the Wolfram language function Classify, RunILOCIv0.9.nb

4) Communicate the interpretation of the data (Is loss of control imminent? What is the action required?) using a Bluetooth dongle to a RECEIVER (Rx RPi2) operating an OLED display.  The operation of the Bluetooth dongle and serial protocol is provided by a separate Mathlink C program interface, ML_System

5) Display and annunciate the interpreted action on the Rx RPi2 using a Wolfram notebook, SerialListenDisplay.nb, or an Adafruit SSD1306 OLED display physically connected via  SPI interface.

