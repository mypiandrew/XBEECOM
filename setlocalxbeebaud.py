#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, time, cmd, serial, binascii, argparse
from utilities import match, bamatch, pamatch, stmatch, send, receive

class ArgParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

help_text = '''
### Change Local XBEE baud rate settings ###

Example

   ./setlocalxbeebaud.py  -p ttyUSB1 -o="9600,8,N,1" -n="19200,8,N,1" 
\r\n\r\n

'''

parser = ArgParser(description='Change Local XBEE Serial Port Config', epilog=help_text, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("-p", action='store', dest='port', help="serial port to connect to")
parser.add_argument("-o", action='store', dest='oldbaud', help="oldbaud, databits, parity, stopbits")
parser.add_argument("-n", action='store', dest='newbaud', help="newbaud, databits, parity, stopbits")
parser.add_argument("-s", action='store_true', dest='save', help="issue a WR to make changes permanent")
parser.add_argument("-a", action='store_true', dest='api', help="Assume device is in API mode rather than Transparent")


# If there are no arguments
if len(sys.argv)==1:
    print "\r\n"
    parser.print_help(sys.stderr)
    sys.exit(1)

else:
	args = parser.parse_args()

	try:
                print "Reconfiguring XBEE Serial settings..."
		ser = serial.Serial()
		ser.port 	 = '/dev/' + args.port
		ser.baudrate = args.oldbaud.split(',')[0]
		ser.bytesize = match(args.oldbaud.split(',')[1])
		ser.parity 	 = match(args.oldbaud.split(',')[2])
		ser.stopbits = match(args.oldbaud.split(',')[3])
		
		ser.close()
		ser.open()

                if args.api != True:
                    send(ser, '+++')
		    receive(ser)
		
		send(ser, 'ATBD={0}\r'.format(bamatch(args.newbaud.split(',')[0])))
		receive(ser)
		
		send(ser, 'ATNB={0}\r'.format(pamatch(args.newbaud.split(',')[2])))
		receive(ser)
		
		send(ser, 'ATSB={0}\r'.format(stmatch(args.newbaud.split(',')[3])))
		receive(ser)


		if args.save:
			send(ser, 'ATWR\r')
			receive(ser)

		send(ser, 'ATCN\r')
		ser.close()

		print 'XBEE Serial setting finished, now set to {0}'.format(args.newbaud)
		
		
	except serial.SerialException as e:
		print 'Serial Exception:' + e
		sys.exit(1)








