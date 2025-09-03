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
Joystick is now lit and working** — we confirmed power delivery and accurate readings!

## Image refernces
![WhatsApp Image 2025-09-03 at 15 21 19_ce783ab2](https://github.com/user-attachments/assets/09981495-1186-4700-bdc5-30dd03b6ff3c)



## Issues Encountered
At one point, the joystick showed a constant value (1023). We realized we had plugged the flex ribbon upside down. GPIO pin mapping confusion due to non-standard pin labeling on the GPIO Extension Board.


