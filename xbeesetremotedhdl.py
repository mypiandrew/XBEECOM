#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, time, cmd, serial, binascii, argparse, os.path, re
from xbee.thread import DigiMesh
from utilities import bamatch, pamatch, stmatch, netdiscovery 


class ArgParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)




help_text = '''
\r\nReconfigure the DH/DL setting on a single remote unit and rebuild mesh routes

This program should be run with the host XBEE module in *Transparent* mode

The program sets up
- Looks up local XBEE SH/SL address
- Checks if target node name is known, if not asks to re-run discovery process
- Manually Sets DH/DL on target remote node 
- Runs local AG Command to setup mesh network with XBEEPI as central node,
  Uses invalid address by default to avoid overwriting DH/DL on other units
- Saves settings on remote COM units so return packet address retained over,
  power cycles


Example:
    
    Use default address FFFE for AG command
    ./xbeesetremotedhdl.py -p ttyUSB1 -b="9600,8,N,1" -r="XBEECOM12345" -s 

\r\n
'''


parser = ArgParser(description='Configure remote XBEE unit DH/DL setting', epilog=help_text, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("-p", action='store', dest='port', help="serial port to connect to", required=True)
parser.add_argument("-b", action='store', dest='baud', help="baud, databits, parity, stopbits", required=True)
parser.add_argument("-r", action='store', dest='remote', help="remote module node ID", required=True)
parser.add_argument("-a", action='store', dest='address',help="user supplied address for AG command" )
parser.add_argument("-s", action='store_true', dest='save', help="issue WR command to persist changes" )

# If there are no arguments
if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    sys.exit(1)
else:
    ## Start up ##
    args = parser.parse_args()
    ser   = serial.Serial('/dev/' + args.port, args.baud.split(',')[0])
    XBee  = DigiMesh(ser)
    DevList = {}
    ## Start up ##



    ## network.conf ##
    if not args.address:
        args.address = 'FFFE'

    if os.path.exists('network.conf'):
        with open("network.conf", 'r') as f:
            for line in f:
                (node, address) = line.strip().split('|')
                DevList.update({node:address})
    else:
        print("File network.conf does not exist, or is not in path.\n")
        print("Try scanning the network?")
        print("(Y/n)")
        answer = raw_input()
        if answer == 'Y' or answer == 'y':
            DevList = netdiscovery(XBee)
            print "\n"
        else: 
            print "Exiting."
            exit(1)

    if args.remote in DevList.keys():
        pass
    elif args.remote not in DevList.keys():
        print("\nError: Remote XBee Node ID not found in network.conf (DevList).\n Try scanning the network ?\n")
        print("(y/n)")
        answer = raw_input()
        if answer == 'Y' or answer == 'y':
            DevList = netdiscovery(XBee)
        else: 
            print "Exiting."
            exit(1)
    ## network.conf ##



    ## Commands
    print "\nGet SH/SL from Local XBEEPI unit :\n"
    print "ATSH"
    XBee.send(
                'at',
                frame_id='1',
                command='SH'
             )
    
    response = XBee.wait_read_frame()
    #print response
    if response['status'].encode("hex") == '00':
        SH = response['parameter'].encode("hex")
        print "OK (SH={0})".format(SH)
    
    time.sleep(0.5)

    print "ATSL"
    XBee.send(
                'at',
                frame_id='2',
                command='SL'
             )
    
    response = XBee.wait_read_frame()
    #print response
    if response['status'].encode("hex") == '00':
        SL = response['parameter'].encode("hex")
        print "OK (SL={0})".format(SL)
    else:
        print "Fail"
        print response
        exit(1)




    print "\nSet remote DH/DL to SH/SL:\n"
    print "Set remote DH"
    XBee.send(    'remote_at',
                dest_addr_long=binascii.unhexlify(DevList[args.remote]),
                frame_id='3',
                command='DH',
                parameter=binascii.unhexlify(SH)
             )
    
    response = XBee.wait_read_frame()
    if response['status'].encode("hex") == '00':
        print "OK"
    else:
        print "Fail"
        print response
        exit(1)

    time.sleep(0.5)

    print "Set remote DL"
    XBee.send(    'remote_at',
                dest_addr_long=binascii.unhexlify(DevList[args.remote]),
                frame_id='4',
                command='DL',
                parameter=binascii.unhexlify(SL)
             )
    response = XBee.wait_read_frame()
    if response['status'].encode("hex") == '00':
        print "OK"
    else:
        print "Fail"
        print response
        exit(1)

    time.sleep(0.5)


    print "\nAG Mesh building:\n"
    ## AG Command
    ##         - Builds mesh routes
    ##         - Configures remote DH/DL
    print "ATAG={0}".format(args.address)
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


    ## Apply changes ##
    print "Apply Changes on remote unit (ATAC)"
    XBee.send(  'remote_at',
                dest_addr_long=binascii.unhexlify(DevList[args.remote]),
                frame_id='7',
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

    if args.save:
        ## Persist changes ##
        print "Save Settings on remote unit (ATWR)"
        XBee.send(  'remote_at',
                    dest_addr_long=binascii.unhexlify(DevList[args.remote]),
                    frame_id='6',
                    command='WR'
                 )
        response = XBee.wait_read_frame()
        if response['status'].encode("hex") == '00':
            print "OK"
        else:
            print "Fail"
            print response
            exit(1)

        time.sleep(0.5)

    print "Sucessfully reconfigured remote module"
    print "\n"








