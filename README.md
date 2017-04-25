# ILOCI
Imminent Loss of Control Identification as applied to a Lambada motorglider 

A project using machine learning and computational thinking with Wolfram Mathematica on the Raspberry Pi 2 (RPi2)

Code is provided to operate on the Raspberry Pi Linux distribution Wheezy

The code enables the RPi2 to

1) Read 8 channels of signal conditioned sensor voltages from an MCP3008 chip using the Serial Parallel Interface SPI protocol via a Wolfram Mathlink C program interface, using C source code compiled and built using the Geany IDE, ML_spidev_mcp3008

2) Access the real time analog data within a Wolfram notebook or package started at RPi2 boot.

3) Analyze and classify the meaning of the sensor data using the Wolfram language function Classify, RunILOCIv0.9.nb

4) Communicate the interpretation of the data (Is loss of control imminent? What is the action required?) using a Bluetooth dongle to a RECEIVER (Rx RPi2) operating an OLED display.  The operation of the Bluetooth dongle and serial protocol is provided by a separate Mathlink C program interface, ML_System

5) Display and annunciate the interpreted action on the Rx RPi2 using a Wolfram notebook, SerialListenDisplay.nb, or an Adafruit SSD1306 OLED display physically connected via  SPI interface.

The two zip files now contain software for the sender and receiver respectively.
The sender contains RunILOCIv0.9Sim.nb and the receiver contains SerialListenDisplay.nb so that the two RPi2's can be setup to exchange simulated data without the analog mcp3008 chip and board attached to the sender.  The bluetooth adapters were purchased from Amazon, Kinivo BTD-400 Bluetooth 4.0 USB Adapter for Windows 10 / 8.1 / 8 / 7 / Vista

4/24/2017  For testing the classifier without the MCP3008 SPI interface, a test flight data file 2016_6_25_28.dat is provided.  

Use the notebook ILOCITrainingVerificationSets-Test7.nb to create the ILOCITest7Classifier.m classifier file with the data file.

The data file can be played back to the RECEIVER, over Bluetooth, using the SENDER notebook ReRunILOCIv0.9.nb.  

Script file RunILOCIv0.9.m is loaded by the startwolfram init.d script at boot up of the RPi2, and has comments and changes to allow execution for simulation. It has functionality illustrated in the notebook RunILOCIv0.9.nb

Files 8channels*.m are SENDER scripts used by startwolfram init.d script to only record flight data, but not to analyze with Classify, or send to the RECEIVER

Notebooks 8channels*.nb illustrate the development of their respectively named scripts.