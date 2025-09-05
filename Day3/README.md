Build a simple two-player game on Raspberry Pi using the Ursina game engine where each player controls a cube to collect “apples” within a time limit. The focus was on:

Reading two analog joysticks via a single PCF8591 ADC (I²C).
Clean input handling inside a Python virtual environment.
A minimal, fun gameplay loop with a scoreboard and restart flow

Hardware

Raspberry Pi (Python 3)
PCF8591 (I²C, 8-bit) — used
MCP3008 (SPI) — not used
Two analog joysticks (X/Y axes)
Jumper wires, breadboard

Software

Python virtual environment (to avoid PEP 668 issues)
Ursina (game engine)
smbus2 for I²C within the venv
I²C enabled via raspi-config; device detected at 0x48
We fixed environment errors by using a venv and installing smbus2 (instead of system smbus).

We did not use the MCP3008 (MCP board). Instead, we successfully read both joysticks using a single PCF8591 over I²C.
