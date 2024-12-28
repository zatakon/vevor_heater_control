# vevor_heater_control
Vevor diesel heater control project

## why?
There is project for communication with chinnese heaters, but this broadly used protocol in cheap diesel heaters is unfortunately not used in Vevor ones. By date I needed to control the one I have in storage there was no serious work in this topic, so I started investigation by my own. 

## goal
Make component for ESPHome for full control of Vevor diesel heaters.

## first impressions
The conroller send every second command to main unit. If received the main unit answers with status. Probably after timeout in commands from controller main unit shuts down. 
Baudrate is 4.8 kbaud. 

## hardware
The bus is open drain. Basic voltage is cca 4V and very noisy (3.3 - 6V). Dont connect directly to any MCU without protection, there is risk that magic smoke will escape... 

## controller
Hardware seems to be very similar as described by [Ray Jones](https://gitlab.com/mrjones.id.au/bluetoothheater/-/blob/master/Documentation/V9%20-%20Hacking%20the%20Chinese%20Diesel%20Heater%20Communications%20Protocol.pdf?ref_type=heads)
Half duplex communication using NPN, PNP transistors and EN pin driving them. 




