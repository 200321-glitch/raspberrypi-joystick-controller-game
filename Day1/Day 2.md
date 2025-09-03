# Wiring Fixes & Joystick Data Capture

## Goals
- Fix the wiring of the MCP3008 and joysticks.
- Successfully retrieve joystick data.
- Create a working Python script to read X and Y values of both joysticks.

## What We Did
- Properly rewired MCP3008 with VCC, GND, CLK, DOUT, DIN, and CS connected to the Pi.
- Tested joystick inputs using `spidev` Python library.
- Successfully read analog values ranging from 0 to 1023 from both joysticks.

## Milestone Achieved
Joystick is now lit and working — we confirmed power delivery and accurate readings!

## Image refernces
![WhatsApp Image 2025-09-03 at 15 20 54_8828f957](https://github.com/user-attachments/assets/0eaeebea-cc83-4a13-affa-49d483baa4b7)



## Issues Encountered
At one point, the joystick showed a constant value (1023). We realized we had plugged the flex ribbon upside down. GPIO pin mapping confusion due to non-standard pin labeling on the GPIO Extension Board.


