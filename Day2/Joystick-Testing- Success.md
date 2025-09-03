Day 2: Switching to PCF8591 & Joystick Data Capture

## Goals
- Solve the issue of Raspberry Pi not reading joystick analog signals properly.
- Remove unnecessary MCP3008 wiring.
- Add and configure the **PCF8591 ADC** to handle analog → digital conversion.
- Capture clean X/Y values for both joysticks.

## Key Change
We discovered that the **MCP3008 was not required** for our project. At one point, the joystick showed a constant value (1023).
Instead, the **PCF8591 (I²C Analog-to-Digital Converter)** provided a much simpler solution:  
- Fewer wires (just SDA + SCL for data).  
- Direct analog → digital conversion.  
- Stable, consistent joystick readings.  

By **removing the MCP3008** and wiring the joysticks through the **PCF8591**, our Raspberry Pi was finally able to read joystick input successfully. 

## Wiring

**Raspberry Pi → PCF8591**
- 3V3 → VCC  
- GND → GND  
- SDA (GPIO2) → SDA  
- SCL (GPIO3) → SCL  
- I²C Address: `0x48` (checked with `i2cdetect -y 1`)

**Joysticks → PCF8591**
- Joystick 1: X → AIN0, Y → AIN1  
- Joystick 2: X → AIN2, Y → AIN3  
- Both VCC → 3.3V, GND → GND  

> ✅ MCP3008 was completely removed.  
> ✅ PCF8591 is now the sole ADC in the system.

## What We Did
1. Enabled I²C and installed the required tools:
   ```bash
   sudo raspi-config nonint do_i2c 0
   sudo apt update && sudo apt install -y python3-smbus i2c-tools
   i2cdetect -y 1

## Image refernces

Before

![WhatsApp Image 2025-09-03 at 15 20 54_8828f957](https://github.com/user-attachments/assets/0eaeebea-cc83-4a13-affa-49d483baa4b7)





