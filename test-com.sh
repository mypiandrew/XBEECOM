./setlocalxbeedest.py -p=ttyUSB1 -b="9600,8,N,1" -r="XBEECOM12345"
mbpoll -a 1 -b 9600 -P none -t 4 -r 1 -c 5 /dev/ttyUSB1 -1 -v -o 4
./setlocalxbeedest.py -p=ttyUSB1 -b="9600,8,N,1" -r="XBEECOM56789"
mbpoll -a 1 -b 9600 -P none -t 4 -r 1 -c 5 /dev/ttyUSB1 -1 -v -o 4
