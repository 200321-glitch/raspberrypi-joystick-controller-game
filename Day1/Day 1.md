## Overview
Our team started the project by discussing potential game ideas that could be implemented using the Raspberry Pi and simple hardware components. We decided to build a joystick-controlled game using two analog joysticks connected through an MCP3008 ADC module.

## Goals
- Finalize project concept: Dual-joystick game controller using Raspberry Pi.
- Set up Raspberry Pi with required dependencies.
- Research how MCP3008 works for analog input.
- Connect joystick components for the first time.

## What We Did
- Installed required libraries: `spidev`, `RPi.GPIO`, and `Ursina`.
- Connected the MCP3008 ADC chip to the Raspberry Pi using jumper wires and a GPIO Extension Board.
- Tried testing joystick input using Python scripts.
- Faced initial confusion identifying correct GPIO pins – some pins like GPIO9, GPIO10, etc., were not available on our board.

## Issues Encountered
- We initially thought the joystick output could be read directly from the Pi, but later discovered we needed an analog-to-digital converter (MCP3008).
- Incorrect wiring attempts caused no signal detection.

## Image References

![WhatsApp Image 2025-09-03 at 15 21 19_ce783ab2](https://github.com/user-attachments/assets/c3bcbfe8-8645-46ee-8bc6-2bbb5b76b733)



Learning: MCP3008 is essential for reading analog signals since Raspberry Pi lacks analog input capabilities.
