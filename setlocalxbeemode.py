#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, time, cmd, serial, binascii, argparse
from utilities import match, send, receive

class ArgParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

help_text = '''
### Set local XBEE operating mode ###


Example :

   Set to API mode :
   ./setlocalxbeemode.py -p ttyUSB1 -b="9600,8,N,1" -a
   
   Set to Transparent mode :
   ./setlocalxbeemode.py -p ttyUSB1 -b="9600,8,N,1" -t

   ****************************************************
   ** NOTE: -a and -t are mutually exclusive options **
   ****************************************************

\r\n\r\n
'''

parser = ArgParser(description='Set local XBEE operating mode', epilog=help_text, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("-p", action='store', dest='port', help="serial port to connect to")
parser.add_argument("-b", action='store', dest='baud', help="baud, databits, parity, stopbits")
parser.add_argument("-t", action='store_true', dest='trans', help="set XBEE to Transparent mode (AP=0)")
parser.add_argument("-a", action='store_true', dest='api', help="set XBEE to API mode (AP=1)")
parser.add_argument("-s", action='store_true', dest='save', help="issue a WR to make changes permanent")

# If there are no arguments
if len(sys.argv)==1:
    print "\r\n"
    parser.print_help(sys.stderr)
    sys.exit(1)

else:
	args = parser.parse_args()
	try:
		ser = serial.Serial()
		ser.port         = '/dev/' + args.port
		ser.baudrate = args.baud.split(',')[0]
		ser.bytesize = match(args.baud.split(',')[1])
		ser.parity       = match(args.baud.split(',')[2])
		ser.stopbits = match(args.baud.split(',')[3])

		ser.close()
		ser.open()

		if args.trans:
                        send(ser, '+++')
                        receive(ser)
			send(ser, 'ATAP=0\r')
			receive(ser)
			if args.save:
			    send(ser, 'ATWR\r')
			    receive(ser)
			send(ser, 'ATAC\r')
			print '\r\n** XBee Now Set to Transparent Mode **\r\n\r\n'
		
		if args.api:
                        send(ser, '+++')
                        receive(ser)
			send(ser, 'ATAP=1\r')
			receive(ser)
			if args.save:
				send(ser, 'ATWR\r')
				receive(ser)
			send(ser, 'ATAC\r')
			receive(ser)				
			print '\r\n** XBee Now Set to API Mode **\r\n\r\n'	
			
		ser.close()

	except serial.SerialException as e:
		print 'Serial Exception:' + e
                sys.exit(1)
