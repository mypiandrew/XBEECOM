#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, time, cmd, serial, binascii, argparse, os.path, re
from xbee.thread import DigiMesh, XBee
from utilities import netdiscovery

class ArgParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)




help_text = '''

This program should be run with the host XBEE module in *Transparent* mode

The program sets up
- Local Network ID (2513)
- Local Node Name (XBEEPI)
- Runs network discovery to map network nodes
- Runs local AG Command to setup mesh network with XBEEPI as central node,
  AG command overwrites DH/DL on remote units with matching address
- Saves settings on remote COM units so return packet address retained over 
  power cycles


Example:
    
    Use default address FFFF for AG command
    ./configurenetwork.py -p ttyUSB1 -b="9600,8,N,1"

    Use user supplied address for AG command
    ./configurenetwork.py -p ttyUSB1 -b="9600,8,N,1" -a 0013a200415f872e

\r\n
'''


parser = ArgParser(description='Configure XBEE-COM network', epilog=help_text, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("-p", action='store', dest='port', help="serial port to connect to", required=True)
parser.add_argument("-b", action='store', dest='baud', help="baud, databits, parity, stopbits", required=True)
parser.add_argument("-a", action='store', dest='address', help="user supplied address for AG command")

# If there are no arguments
if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    sys.exit(1)
else:
    
    args = parser.parse_args()

    DevList = {}

    if not args.address:
        args.address = 'FFFF'


    regex = re.compile("status\': \'..(00)\'")
    ser = serial.Serial('/dev/' + args.port, args.baud.split(',')[0])
    XBee = DigiMesh(ser)


    print "\nXBEE COM Configuration Utility v1.0\nRunning configuration steps...\n"

    ## Set local XBee PAN ID to 2513     ##
    print "Set Local Network ID (ATID=2513)"
    XBee.send(     'at',
                frame_id='1',
                command='ID',
                parameter=binascii.unhexlify('2513')
             )
    response = XBee.wait_read_frame()
        #print response
    if response['status'].encode("hex") == '00':
        print "OK"
    else:
        print "Fail"
        print response
        exit(1)


    time.sleep(0.5)


    ## Set Local XBee Node ID to XBEEPI ##
    print "Set Node Name to 'XBEEPI' (ATNI=XBEEPI)"
    XBee.send(    'at',
                frame_id='2',
                command='NI',
                parameter='XBEEPI'
             )
    response = XBee.wait_read_frame()
        #print response
    if response['status'].encode("hex") == '00':
        print "OK"
    else:
        print "Fail"
        print response
        exit(1)

    time.sleep(0.5)


    ## Apply changes to local XBee         ##
    print "Apply Settings (ATAC)"
    XBee.send(    'at',
                frame_id='3',
                command='AC'
             )
    response = XBee.wait_read_frame()
        #print response
    if response['status'].encode("hex") == '00':
        print "OK"
    else:
        print "Fail"
        print response
        exit(1)

    time.sleep(0.5)

    ## Apply changes to local XBee         ##
    print "Save Settings (ATWR)"
    XBee.send(    'at',
            frame_id='4',
            command='WR'
         )
    response = XBee.wait_read_frame()
    #print response
    if response['status'].encode("hex") == '00':
        print "OK"
    else:
        print "Fail"
        print response
        exit(1)

    time.sleep(0.5)


    # Now we've setup the network ID and local node ID scan the network to find remote units
    # We set the frame wait time out to 10seconds here to allow for a remote unit to respond
    DevList = netdiscovery(XBee)


    print "AG Mesh building:\n"
    print "ATAG={0}".format(args.address)
    ## AG Command
    ##         - Builds mesh routes
    ##         - Configures remote DH/DL
    XBee.send(  'at',
                frame_id='5',
                command='AG',
                parameter=binascii.unhexlify(args.address)
             )

    response = XBee.wait_read_frame()
    #print response
    if response['status'].encode("hex") == '00':
        print "OK\n"
    else:
        print "Fail"
        print response
        exit(1)

    time.sleep(0.5)

    ## For each remote module discovered (in network.conf) ##
    print "Persist changes on remote COM modules:\n"
    
    ## WR - persist changes for each COM module ##
    for node, address in DevList.items():
        if 'COM' in node:
            XBee.send(     'remote_at',
                        dest_addr_long=binascii.unhexlify(address),
                        frame_id='6',
                        command='WR'
                     )
            print "ATWR - {0}".format(address)
            tmp = re.search( regex, str(XBee.wait_read_frame()))
            if tmp.group(1) == '00':
                print "OK"
            else:
                print "Fail"
                exit(1)

            time.sleep(0.5)    
