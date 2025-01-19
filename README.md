# vevor heater control
Vevor diesel heater control project

## why?
There is project for communication with chinnese heaters, but this broadly used protocol in cheap diesel heaters is unfortunately not used in Vevor ones. By date I needed to control the one I have in storage there was no serious work in this topic, so I started investigation by my own. 

## goal
Make component for ESPHome for full control of Vevor diesel heaters.

## current status of the project
There are two projects - one for reading data frames from Vevor heater, second project connected to Home assistant sending current status. 
Turning the heater on and off remotely will come soon.

## few things to know
The conroller sends every second command to main unit. Unit sends back current status.
Baudrate is 4.8 kbaud. 

## hardware
The bus is open drain. Basic voltage is cca 4V and very noisy (3.3 - 6V). Dont connect directly to any MCU without protection, there is risk that magic smoke will escape... 

## controller
Hardware seems to be very similar as described by [Ray Jones](https://gitlab.com/mrjones.id.au/bluetoothheater/-/blob/master/Documentation/V9%20-%20Hacking%20the%20Chinese%20Diesel%20Heater%20Communications%20Protocol.pdf?ref_type=heads)
Half duplex communication using NPN, PNP transistors and EN pin driving them. 
The CPU in Vevor controller is most likely 5V tolerant, unlike our ESP32. I created simple circuit for safe connection between Vevor bus and my Esp32.

##### connection to esp32
This is simple schematics how I connected my Esp32 to the bus.
![Connection Esp32 to vevor](docs/images/vevor_heater_esp32.PNG)

## Communication controller -> main unit
|byte   | certainty | values     | comment
| ---   | ---       | ---        | ---
|0:     |  100%     |0xAA        |identifier 0xAA
|1:     |  100%     |0x66        |device ID (controller 0x66, heater 0x77)
|2:     |  50%      |0x02        |command?
|3:     |  100%     |0x0B        |length field (0x0B for controller->heater, 0x33 for heater->controller)
|4:     |0%         |0x00        |unknown
|5:     |0%         |0x00        |unknown
|6:     |0%         |0x00        |unknown
|7:     |0%         |0x00        |unknown
|8:     |100%       |1-10        |power level [level]
|9:     |90%        |2, 6, 8     |requested state (0x02: off, 0x06: start, 0x08: running) [state]
|10:    |0%         |0x00        |unknown
|11:    |0%         |0x00        |unknown
|12:    |0%         |0x00        |unknown
|13:    |0%         |0x00        |unknown
|14:    |100%       |1-255       |checksum

## Communication main unit -> controller
|byte   | certainty | values     | comment
| ---   | ---       | ---        | ---
| 0:    | 100%      | 0xAA       |identifier 0xAA
| 1:    | 100%      | 0x77  devic| ID (controller 0x66, heater 0x77)
| 2:    | 50%       | 0x02       |command?
| 3:    | 100%      | 0x33  lengt| field (0x0B for controller->heater, 0x33 for heater->controller)
| 4:    | 80%       | 0-1        |all 1, last one 0 | heater enabled?
| 5:    | 99%       | 0x00-0x04  |state (0x00: off, 0x01: glow plug pre heat, 0x02: ignited, 0x03: stable combustion, 0x04: stoping, cooling) [state]
| 6:    | 100%      | 0x01-0x0A  |power level [level]
| 7:    | 0%        | 0x00       |unknown
| 8:    | 0%        | 0x00, 0x03 |0x03 if running, 0x00 if stopped (just last one is 0)
| 9:    | 0%        | 0x00, 0xFB |0xFB if running, 0x00 if stopped (just last one is 0)
| 10:   | 0%        | 0x00       |unknown
| 11:   | 99%       | 153-158    |input voltage [V * 10]
| 12:   | 0%        | 0x00       |unknown
| 13:   | 40%       | 0-12       |glow plug current [A]
| 14:   | 50%       | 0-1        |cooling down [0/1]
| 15:   | 30%       | 0-16       |Fan voltage? Some temperature? [V]
| 16-17:| 99%       | 480,1630   |heat exchanger temperature [°C * 100]
| 18:   | 0%        | 0x00       |unknown
| 19:   | 0%        | 0x00       |unknown
| 20-21:| 90%       | 0-325      |state duration [s]
| 22:   | 0%        | 0x00       |unknown
| 23:   | 90%       | 0-51       |pump frequency [Hz*10]
| 24:   | 25%       | 0-66       |glow plug voltage/current/temperature
| 25:   | 25%       | 0-86       |glow plug voltage/current/temperature
| 26:   | 25%       | 0-56       |glow plug voltage/current/temperature
| 27:   | 25%       | 0-12       |glow plug voltage/current/temperature
| 28-29 | 90%       | 0-3939     |fan speed [rpm]
| 30-45:| 0%        | 0x00       |unknown
| 46:   | 0%        | 35         |unknown constant
| 47:   | 0%        | 4          |unknown constant
| 48:   | 0%        | 17         |unknown constant
| 49:   | 0%        | 35         |unknown constant
| 50:   | 0%        | 0x00       |unknown
| 51:   | 0%        | 30, 40     |unknown
| 52-53 | 10%       | 0-420      |something glow plug related
| 54:   | 0%        | 0x00       |unknown
| 55:   | 100%      | 1-254      |checksum

