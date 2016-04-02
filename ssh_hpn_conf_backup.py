import paramiko
import time
import os, datetime



def disable_paging_hpn(remote_conn):
    #Disable paging on a HPN device

    remote_conn.send("screen-length disable\n")
    time.sleep(1)

    # Clear the buffer on the screen
    output = remote_conn.recv(1000)

    return output

def make_directory():
    directory = '/home/mininet/backups'

    #create the backup directort if it does not exist
    if not os.path.isdir(directory):
        print 'making dir'
        os.makedirs(directory)

    os.chdir(directory)
    print "Current working dir : %s" % os.getcwd()

    #Create the directory for the output files dd/mm/yyyy
    mydir = os.path.join(os.getcwd(), datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    os.makedirs(mydir)


if __name__ == '__main__':


    # Call the make directory funtion
    make_directory()

    # VARIABLES THAT NEED CHANGING
    ip = '192.168.56.20'
    username = 'admin'
    password = 'public'

    # Create instance of SSHClient object
    remote_conn_pre = paramiko.SSHClient()

    # Automatically add untrusted hosts (make sure okay for security policy in your environment)
    remote_conn_pre.set_missing_host_key_policy(
         paramiko.AutoAddPolicy())

    # initiate SSH connection
    remote_conn_pre.connect(ip, username=username, password=password, look_for_keys=False, allow_agent=False)
    print "SSH connection established to %s" % ip

    # Use invoke_shell to establish an 'interactive session'
    remote_conn = remote_conn_pre.invoke_shell()
    print "Interactive SSH session established"

    # Strip the initial router prompt
    output = remote_conn.recv(1000)

    # See what we have
    print output

    # Turn off paging
    disable_paging_hpn(remote_conn)

    # Now let's try to send the router a command
    remote_conn.send("\n")
    remote_conn.send("display interface brief\n")
    time.sleep(2)
    remote_conn.send("display cur\n")
    time.sleep(3)    # Wait for the command to complete

    output = remote_conn.recv(5000)
    print output
