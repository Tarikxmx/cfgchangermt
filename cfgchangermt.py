import sys, paramiko, re, time, datetime, os, select, configparser

channel_data = bytes()
buf = ''
prompt = False

cfg = configparser.ConfigParser()
cfg.read('config.ini')

if len(sys.argv) < 3:
    print('''\nToo few arguments. Usage: client_update_mt.py <config_section> <ip_list> ''')
    #config = sys.argv[1]
    #cmd = cfg[config]['COMMAND']
    #print(cmd)
    exit()

config = sys.argv[1]
ip_list = sys.argv[2]
user = cfg[config]['LOGIN']
password = cfg[config]['PASSWORD']
port = cfg[config]['PORT']
cmd = cfg[config]['COMMAND']
cmd = cmd.strip("\"")
#to = cfg['config]']['TIMEOUT']
timeout = 5

##########################################################################
def file_len(ip_list):
    with open(ip_list) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def debug(content):
    print(content)
    time_now = datetime.datetime.now().strftime("%H:%M:%S")
    file = ip_list.strip('.txt')
    file = file + '_' + cfg[config]['DEBUG_FILE']
    log_file = open(file, 'a')
    log_buf = ''
    log_buf = 'log: ' +time_now+ ' : '+content + '\n'
    log_file.write(log_buf)
    log_file.close

def log_error(address, content):
    print(address, content)
    time_now = datetime.datetime.now().strftime("%H:%M:%S")
    file = ip_list.strip('.txt')
    file = file + '_' + cfg[config]['ERROR_FILE']
    log_file = open(file, 'a')
    log_buf = ''
    log_buf = 'log: ' +time_now+ ' : '+address + ' : '+content + '\n'
    log_file.write(log_buf)
    log_file.close

############################################################################    
print(ip_list)
ip_count = file_len(ip_list) #todo: check len, if 0 then exit
file_in = open(ip_list, 'r')
for i, line in enumerate(file_in):
    try:
        quit_loop = False
        buf_ip = line
        ip = buf_ip.strip( '\n' )

        debug('############################################\n')
        debug(ip)
        #print('############################################\n')
        print('ip_address: ', ip)
        
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, port=port, username=user, password=password, timeout=5)
        
        #print("logged in\n")
        debug("logged in\n")
        
        channel = client.invoke_shell()
        channel_data = bytes()
        while quit_loop == False: #todo: fix that unecessery loop condition
            r,w,e = select.select([channel], [], [], timeout)
            if channel in r:
                channel_data += channel.recv(9999)
                buf = channel_data.decode('utf-8')
                if buf.endswith('] > ') == True:
                    debug('We found prompt, sending cmd')
                    channel.send(cmd+'\r\n')
                    time.sleep(2)
                    channel_data = bytes()
                    channel.send('quit\r\n')
                    quit_loop = True
                    break     
        percent = i / ip_count * 100
        print("---------------- done:  ", int(percent), "% -----------------")

    except paramiko.ssh_exception.AuthenticationException as ssherr:
        debug(str(ssherr))
        #print (ssherr)
        client.close()
    except paramiko.ssh_exception.SSHException as ssherr:
        debug(str(ssherr))
        #print (ssherr)
        client.close()
    except paramiko.ssh_exception.socket.error as ssherr:
        debug(str(ssherr))
        #print (ssherr)
        client.close()
    except paramiko.ssh_exception.BadHostKeyException as ssherr:
        debug(str(ssherr))
        #print (ssherr)
        client.close()
    finally:
        client.close()
#print ("done")
debug("done")
	
	
	
	
