#!/usr/bin/python
# Written for Python 2.7
# Version 1.1

# This program provides to functions. The 1st is to clear the port statistics on all HP switches loaded into the HOST.txt file.
# the 2nd is to collect the port statstics from all HP switches loaded into the HOST.txt file and then write the results to a file.
# Its best to do the port clearing weeks ahead of the port collection to account for staff being on leave.

import paramiko
import time
import os, datetime

#This function loads all the devices into the dictionary
def load_hosts():
    with open("hosts.txt") as HostFile:
       for line in HostFile:
            (key, val) = line.split()
            HOST[(key)] = val


def disable_paging_hpn(remote_conn):
    #Disable paging on a HPN device

    remote_conn.send("screen-length disable\n")
    time.sleep(1)

    # Clear the buffer on the screen
    output = remote_conn.recv(1000)

    return output

def make_directory(folder):
    directory = str("/automation/" + folder)
    #create the backup directory if it does not exist
    if not os.path.isdir(directory):
        print 'making dir'
        os.makedirs(directory)
    os.chdir(directory)
    print "Current working dir : %s" % os.getcwd()
    #Create the directory for the output files dd/mm/yyyy
    mydir = os.path.join(os.getcwd(), datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    os.makedirs(mydir)
    os.chdir(mydir)


def free_ports(i):
    Fa = 0
    Gi = 0
    a = ('\n')
    # This function loops over the output to calculate the ports with 0 input
    for line in open('%s.txt' % HOST[i], 'r'):
        if line.startswith('G'):
            Gi = Gi + 1
        if line.startswith('F'):
            Fa = Fa + 1
    print HOST[i], 'has', Gi, 'free Gigabit Ethernet ports'
    print HOST[i], 'has', Fa, 'free Fast Ethernet ports'
    GiStatement = HOST[i], 'has', Gi, 'free Gigabit Ethernet ports'
    FaStatement = HOST[i], 'has', Fa, 'free Fast Ethernet ports'
    GiStatement = str(GiStatement)
    GiStatement = ''.join(GiStatement)
    FaStatement = str(FaStatement)
    FaStatement = ''.join(FaStatement)
    with open("free_ports.txt", "a") as myfile:
        myfile.write (GiStatement+'\n')
        myfile.write (FaStatement+'\n')
        myfile.write (a)
        myfile.close()

def free_port_clean_comma():
    a = ('\n')
    f1 = open('free_ports.txt', 'r')
    f2 = open('free_ports_comma.txt', 'a')
    for line in f1:
       f2.write(line.replace(',', ''))
    f1.close()
    f2.close()

def free_port_clean_quotes():
    a = ('\n')
    f1 = open('free_ports_comma.txt', 'r')
    f2 = open('free_ports_quotes.txt', 'a')
    for line in f1:
       f2.write(line.replace("'", ''))
    f1.close()
    f2.close()	

def free_port_clean_brackets():
    a = ('\n')
    f1 = open('free_ports_quotes.txt', 'r')
    f2 = open('free_ports_brackets.txt', 'a')
    for line in f1:
       f2.write(line[1:-2])
       f2.write(a)
    f1.close()
    f2.close()

def ssh_exception(i,e):
    a = ('\n')
    print HOST[i], 'had the following error', e
    ExceptFile = open('failures.txt', 'a')
    message = (HOST[i], 'had the following error', e)
    message = str(message)
    ExceptFile.write (message)
    ExceptFile.write (a)
    ExceptFile.close()
	
def app_close():
    print '''

   
 Finished !
   
    '''
    close = raw_input (' Press x and enter to close: ')   
 
def collect_port_data(HOST):
    # Call the make directory funtion
    make_directory('free_ports')
    for i in HOST:
        # Create instance of SSHClient object
        remote_conn_pre = paramiko.SSHClient()

        # Automatically add untrusted hosts (make sure okay for security policy in your environment)
        remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # initiate SSH connection
        print " "
        print "Attempting connection to %s" % i
        try:
            remote_conn_pre.connect(i, username=username, password=password, look_for_keys=False, allow_agent=False)
            print "SSH connection established to %s" % i
		
            # Use invoke_shell to establish an 'interactive session'
            remote_conn = remote_conn_pre.invoke_shell()
            print "Interactive SSH session established"

            # Strip the initial router prompt
            output = remote_conn.recv(1000)

            # See what we have
            print output

            # Turn off paging by calling paging function
            disable_paging_hpn(remote_conn)

            # Send commands to the device
            remote_conn.send("\n")
            remote_conn.send("display counters inbound interface | include    0                  0                  0         0\n")
            time.sleep(2)    # Wait for the command to complete
            output = remote_conn.recv(5000)
            print output
            #Write to a file with the name of the switch
            f = open('%s.txt' %HOST[i], 'w')
            f.write (output.decode('ascii'))
            f.close()
            # Call the free ports function
            free_ports(i)

            print ' '
            print '######################################################'
            print ' '
        except (paramiko.ssh_exception.BadHostKeyException, paramiko.ssh_exception.AuthenticationException, paramiko.ssh_exception.SSHException, paramiko.ssh_exception.socket.error) as e:
            ssh_exception(i,e)
		   
    #Remove remove the commas, quotes, and parentheses from the free ports file. 
    try:
        free_port_clean_comma()
        free_port_clean_quotes()
        free_port_clean_brackets()
        # Clean up the redundant files
        filename1 = 'free_ports_brackets.txt'
        filename2 = 'free_ports.txt'
        os.system ("copy %s %s" % (filename1, filename2))
        os.remove ('free_ports_comma.txt')
        os.remove ('free_ports_quotes.txt')
        os.remove ('free_ports_brackets.txt')
    except IOError:
        print "*********************************************************"	
        print "Failed cleanup due to exceptions check failures.txt file"
        print "*********************************************************"

def clear_ports(HOST):
    # Call the make directory funtion
    make_directory('clear_ports')
    for i in HOST:
        # Create instance of SSHClient object
        remote_conn_pre = paramiko.SSHClient()

        # Automatically add untrusted hosts (make sure okay for security policy in your environment)
        remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # initiate SSH connection
        print " "
        print "Attempting connection to %s" % i
        try:
            remote_conn_pre.connect(i, username=username, password=password, look_for_keys=False, allow_agent=False)
            print "SSH connection established to %s" % i
		
            # Use invoke_shell to establish an 'interactive session'
            remote_conn = remote_conn_pre.invoke_shell()
            print "Interactive SSH session established"

            # Strip the initial router prompt
            output = remote_conn.recv(1000)

            # See what we have
            print output

            # Turn off paging by calling paging function
            disable_paging_hpn(remote_conn)

            # Send commands to the device
            remote_conn.send("\n")
            remote_conn.send("reset counters interface\n")
            time.sleep(2)    # Wait for the command to complete
            output = remote_conn.recv(5000)
            print output
            #Write to a file with the name of the switch
            f = open('%s.txt' %HOST[i], 'w')
            f.write (output.decode('ascii'))
            f.close()
            #Record failure of clearing of counters in a file
            for line in open('%s.txt' % HOST[i], 'r'):
                if line.startswith('Permission denied.'):
                    f = open('failures.txt', 'a')
                    message = (HOST[i], 'Device reported: Permission denied after reset counters command was executed')
                    message = str(message)
                    f.write (message)
                    f.write (a)
                    f.close()
                else:
				    continue
            #Record successful clearing of counters in a file
            with open("Successful connections.txt", "a") as myfile:
               comment = ('Successful ssh connection to', HOST[i],'and command sent to terminal')
               comment = str(comment)
               myfile.write (comment+'\n')
               myfile.close()
            print ' '
            print '######################################################'
            print ' '
        except (paramiko.ssh_exception.BadHostKeyException, paramiko.ssh_exception.AuthenticationException, paramiko.ssh_exception.SSHException, paramiko.ssh_exception.socket.error) as e:
            ssh_exception(i,e)

if __name__ == '__main__':

    # List of devices to iterate over
    HOST = {}
    a = ('\n')
	#load all the devices into the HOST dictionary
    load_hosts()
	
    # Collect credentials
    print '''
	
	
	
 HPN Comware 5 free port tool
 
 All results are stored in the folder named automation
 
 
 
    '''
    username = raw_input(b' Enter username: ')
    password = raw_input(' Enter password: ')
    print ""  
    print ""
    print ''' 
	
 1 - Clear port statistics
 2 - Find number of free ports
 3 - Exit
 
    '''
    choice = raw_input(b'Enter selection number: ')
    choice = int(choice)
    if choice == 1:	
        clear_ports(HOST)
        app_close()
    elif  choice == 2:
        collect_port_data(HOST)
        app_close()
    elif choice == 3:
        print ' '	
        print "Bye"
        time.sleep(1)
    else:
        print 'Incorrect selection'
        time.sleep(1)
