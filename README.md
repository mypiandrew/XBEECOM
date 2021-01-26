# RF-COM XBEE Configuration Scripts

Python Scripts and documentation for RF-COM Units



## Programs

```configurenetwork.py``` 

This script performs the following steps:
- Set Local Network ID (2513)
- Set Local Node Name (XBEEPI)
- Runs network discovery to map network nodes
- Runs local AG Command to setup mesh network with XBEEPI as central node,
  AG command overwrites DH/DL on all remote units (or optionally just with matching DH+DL address)
- Saves settings on remote COM units so return packet address retained over 
  power cycles

```setlocalxbeebaud.py```

This script re-configures the local XBEE baud rate settings

```setlocalxbeedest.py```

This script sets the local XBEE's target/destination COM module 

```xbeesetremotebaud.py```

This script performs the following steps:
- Checks if target node name is known, if not asks to re-run discovery process
- Manually Sets BD/NB/SB settings on target remote node 
- Optionally Saves settings on remote COM units so return packet address retained over
  power cycles
- Applies changes

```xbeesetremotedhdl.py```

This script performs the following steps:
- Looks up local XBEE SH/SL address
- Checks if target node name is known, if not asks to re-run discovery process
- Manually Sets DH/DL on target remote node 
- Runs local AG Command to setup mesh network with XBEEPI as central node,
  Uses invalid address by default to avoid overwriting DH/DL on other units
- Saves settings on remote COM units so return packet address retained over,
  power cycles



## Installation


```
apt-get update && apt-get install python-serial python-setuptools
mkdir pythonxbee
cd pythonxbee
wget https://github.com/mypiandrew/python-xbee/archive/master.zip
unzip master.zip && cd python-xbee-master && python setup.py install
cd ../..
mkdir xbeecom
cd xbeecom
wget https://github.com/mypiandrew/XBEECOM/archive/master.zip
unzip master.zip && cd python-xbee-master
cd XBEECOM-master
chmod +x *.py
```


To do initial configuration first set local XBEE unit to API mode:
```
./setlocalxbeemode.py -p XBEE_SERIAL_PORT -b="9600,8,N,1" -a
```

Then run network configuration Script:
```
./configurenetwork.py -p XBEE_SERIAL_PORT -b="9600,8,N,1"
```

Finally set the local XBEE unit back to to TRANSPARENT mode:
```
./setlocalxbeemode.py -p XBEE_SERIAL_PORT -b="9600,8,N,1" -t
```

```XBEE_SERIAL_PORT``` is the serial port name that the local XBEE unit installed in the Pi Unit is connected to and will be typically one of ```ttyAMA0``` ```ttyS1``` or ```ttyUSB1``` depending on the hardware configuration, see main website page on relevant IO card for further details on this.


***Note : To avoid problems it is important to wait about 60 seconds after power up before doing performing any network activity (either scans or transmissions).***



## Example Use

```
root@raspberrypi:~/xbee/COM# ./setlocalxbeemode.py -p ttyUSB1 -b="9600,8,N,1" -a
+++
OK

RESULT=OK
ATAP=1
OK

RESULT=OK
ATAC
OK

RESULT=OK

** XBee Now Set to API Mode **


root@raspberrypi:~/xbee/COM#  ./configurenetwork.py -p ttyUSB1 -b="9600,8,N,1"

XBEE COM Configuration Utility v1.0
Running configuration steps...

Set Local Network ID (ATID=2513)
OK
Set Node Name to 'XBEEPI' (ATNI=XBEEPI)
OK
Apply Settings (ATAC)
OK
Save Settings (ATWR)
OK

Scanning network for remote modules...

XBEECOM12345 - 0013a200415d151e
XBEECOM56789 - 0013a20041725f5b

Scanning complete, populated 'network.conf' file.

AG Mesh building:

ATAG=FFFF
OK

Persist changes on remote COM modules:

ATWR - 0013a200415d151e
OK
ATWR - 0013a20041725f5b
OK
root@raspberrypi:~/xbee/COM# ./setlocalxbeemode.py -p ttyUSB1 -b="9600,8,N,1" -t
+++
OK

RESULT=OK
ATAP=0
OK

RESULT=OK
ATAC

** XBee Now Set to Transparent Mode **
root@raspberrypi:~/xbee/COM# ./setlocalxbeedest.py -p=ttyUSB1 -b="9600,8,N,1" -r="XBEECOM12345"
+++
OK

RESULT=OK
ATDH=0013a200
OK

RESULT=OK
ATDL=415d151e
OK

RESULT=OK
ATCN
OK

RESULT=OK
XBee Destination now Set XBEECOM12345 (DH=0013a200  DL=415d151e)
root@raspberrypi:~/xbee/COM# mbpoll -a 1 -b 9600 -P none -t 4 -r 1 -c 5 /dev/ttyUSB1 -1 -v -o 4
mbpoll 0.1-23 - FieldTalk(tm) Modbus(R) Master Simulator
Copyright (c) 2015 epsilonRT, All rights reserved.
This software is governed by the CeCILL license <http://www.cecill.info>

Opening /dev/ttyUSB1 at 9600 bauds (N, 8, 1)
Protocol configuration: Modbus RTU
Slave configuration...: address = [1]
                        start reference = 1, count = 5
Communication.........: /dev/ttyUSB1,       9600-8N1
                        t/o 4.00 s, poll rate 1000 ms
Data type.............: 16-bit register, output (holding) register table

-- Polling slave 1...
[01][03][00][00][00][05][85][C9]
Waiting for a confirmation...
<01><03><0A><00><0B><00><16><00><21><00><2C><00><37><1C><5F>
[1]:    11
[2]:    22
[3]:    33
[4]:    44
[5]:    55
```

For an example of how to set and switch between multiple end points and run a sample modbus data request see the example bash sript ```test-com.sh```



