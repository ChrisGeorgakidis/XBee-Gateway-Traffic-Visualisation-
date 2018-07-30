# XBee-Gateway-Traffic-Visualisation-
## Overview
An XBee device is operating as a gateway and it will collect the data that are sent by other devices. Next it will parse the data and pass them through serial port. Then a GUI read the serial port communication and visualise the devices and the data that the specific one has sent.

## More Specific
The gateway will receive only data sent by other devices. This means that the gateway will operate as a receiver. When the gateway receives some data from a device, it has to store the address / id of the sender, in order to know all the devices that have sent data until now, and also the data that it received. It must keep the data that have sent by a device until a new data by the same device has received. After this the gateway passes the data and address / id through serial port. By doing that GUI will know all the information needed to visualise the traffic. The Gui will create a rectangle for each device that gateway has received data from. Inside each rectangle it will display the last data sent the gateway by this device.
