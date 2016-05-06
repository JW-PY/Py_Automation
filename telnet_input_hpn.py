import getpass
import telnetlib
import time, datetime
import os

#This script loops through the HOST dictionary that is loaded via the hosts.txt file, which must be in the same directory as the script.
#The hosts.txt file format is ip address one space and then device name i.e 10.1.1.1 switch1

#Verion 1.0

HOST = {}

username = ('admin')
enable = ('edsprivate')

filename = ('')

user_command = raw_input(b'Enter exec command please: ')
username = raw_input('Enter username: ')
password = raw_input('Enter password: ')


#This function loads all the devices into the dictionary
def load_hosts():
    with open("hosts.txt") as HostFile:
       for line in HostFile:
            (key, val) = line.split()
            HOST[(key)] = val

def make_directory():
    directory = '/Python27/my_scripts/telnet'

    #create the backup directort if it does not exist
    if not os.path.isdir(directory):
        print 'making dir'
        os.makedirs(directory)

    os.chdir(directory)
    print "Current working dir : %s" % os.getcwd()

    #Create the directory for the output files dd/mm/yyyy
    mydir = os.path.join(os.getcwd(), datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    os.makedirs(mydir)
    os.chdir(mydir)
	
	
#This function telnets to all devices in the HOST dictionary, gets the counters and wtites them to a file
def connect():
    for i in HOST:
       tn = telnetlib.Telnet(i, 23, 5)
       print 'Telneting to', i, HOST[i]
       tn.read_until(b"Username:")
       tn.write(username.encode('ascii') + b"\n")
       tn.read_until(b"Password:")
       tn.write(password.encode('ascii') + b"\n")
       print 'Entered login credentials'
       tn.write(b"screen-length disable\n")
       time.sleep(2)
       tn.write(user_command)
       tn.write("\r\n")
       time.sleep(3)
       tn.write(b"quit\n")
       f = open(str(HOST[i])+"-"+str(user_command)+".txt", 'w')
       f.write (tn.read_all().decode('ascii'))
       print 'Writing to file'
       f.close()
       tn.close()

	   
load_hosts()
make_directory()
connect()
