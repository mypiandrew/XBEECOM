#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, time, cmd, serial, binascii, argparse
from utilities import match, send, receive

class ArgParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

try:
    networkfile=open('network.conf','r')
    devicelist=networkfile.read()
    networklist='\r-------- Known Devices ----------\r\n' + devicelist + '\r\n\r\n'
    networkfile.close()
except:
    networklist="\r-------- Known Devices ----------\r\nNo Devices available, run network scanner to populate network.conf\r\n\r\n"


help_text = '''
### Change local XBEE's destination Address in transparent mode ###

Example:

./setlocalxbeedest.py -p=ttyS1 -b="9600,8,N,1" -r="XBEECOM1" –s
\r
\n
'''


parser = ArgParser(description='Set Destination XBEE address', epilog=(help_text + networklist), formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("-p", action='store', dest='port', help="Local XBEE serial port to connect to")
parser.add_argument("-b", action='store', dest='baud', help="Local XBEE baud, databits, parity, stopbits")
parser.add_argument("-r", action='store', dest='remote', help="Alphanumeric XBEE node name (NI)")
parser.add_argument("-s", action='store_true', dest='save', help="issue a WR to XBEE to write changes to flash")


# If there are no arguments
if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    sys.exit(1)

else:
	Dictionary = {}
	args = parser.parse_args()


        try:
	    with open("network.conf") as f:
	        	for line in f:
		        	(node, address) = line.strip().split('|')
		        	Dictionary.update({node:address})
        except:
            print "network.conf file not found, run network scanner"
            sys.exit(1)

	if args.remote not in Dictionary.keys():
		print "XBee module \"{0}\" not found in network.conf".format(args.remote)
		sys.exit(1)
	else:

		try:
			newDH = Dictionary[args.remote][:8]
			newDL = Dictionary[args.remote][8:16]

			ser = serial.Serial()
			ser.port 	 = '/dev/' + args.port
			ser.baudrate = args.baud.split(',')[0]
			ser.bytesize = match(args.baud.split(',')[1])
			ser.parity 	 = match(args.baud.split(',')[2])
			ser.stopbits = match(args.baud.split(',')[3])
			
			ser.close()
			ser.open()

			send(ser, '+++')
			receive(ser)

			send(ser, 'ATDH={0}\r'.format(newDH))
			receive(ser)

			send(ser, 'ATDL={0}\r'.format(newDL))
			receive(ser)

			if args.save:
				send(ser, 'ATWR\r')
				receive(ser)

			send(ser, 'ATCN\r')
			receive(ser)

			ser.close()
			
			print 'XBee Destination now Set {0} (DH={1}  DL={2})'.format(args.remote, newDH, newDL)
			
			
		except serial.SerialException as e:
			print 'Serial Exception:' + e
			sys.exit(1)








