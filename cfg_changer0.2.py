import sys, paramiko, re, time, datetime, threading, os, select

#hostname = "172.17.80.9"
user = "back1up"
password = "12345azxqc"
port = "10022"
adresy = "test.txt"
cmd = "/ip service set ssh port=10022\r\n/tool graphing set store-every=5min\r\ntool graphing interface add interface=all\r\n \
        /system clock set time-zone-name=Europe/Warsaw\r\n system ntp client set enabled=yes primary-ntp=172.16.11.2 secondary-ntp=172.16.11.11\r\n"
channel_data = bytes()
buf = ''
licznik = int()
prompt = False
timeout = 5

##########################################################################
def file_len(adresy):
    with open(adresy) as f:
        for i, l in enumerate(f):
            pass
    return i + 1
def debug(content):
    print(content)
    czas_teraz = datetime.datetime.now().strftime("%H:%M:%S")
    log_file = open('cfg_changer_run.txt', 'a')
    log_buf = ''
    log_buf = 'log: ' +czas_teraz+ ' : '+content + '\n'
    log_file.write(log_buf)
    log_file.close

def log_error(address, content):
    print(address, content)
    czas_teraz = datetime.datetime.now().strftime("%H:%M:%S")
    log_file = open('cfg_changer_errors.txt', 'a')
    log_buf = ''
    log_buf = 'log: ' +czas_teraz+ ' : '+address + ' : '+content + '\n'
    log_file.write(log_buf)
    log_file.close
    
##########################################################################
class run_thread(threading.Thread):
    def __init__(self, wartosc_z, wartosc_w, counter):
        threading.Thread.__init__(self)
        self.wartosc_z = wartosc_z
        self.wartosc_w = wartosc_w
        self.counter = counter
        #self.content = content
    def run(self):
        content = zaloguj_do_mt_rob_telnet(self.wartosc_z, self.wartosc_w)
        #debug("%s zakonczony %s" % (self.counter, result))
        debug(self.counter, self.wartosc_w, content)
############################################################################    
licznik_adresow = file_len(adresy)
file_in = open(adresy, 'r')
for i, line in enumerate(file_in):
    try:
        licznik = 0
        wyjdz = False
        buf_adr = line
        adr = buf_adr.strip( '\n' )

        debug('############################################\n')
        debug(adr)
        #print('############################################\n')
        print('adres: ', adr)
        
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(adr, port=port, username=user, password=password, timeout=10)
        
        #print("logged in\n")
        debug("logged in\n")
        
        channel = client.invoke_shell()
        channel_data = bytes()
        while wyjdz == False:
            r,w,e = select.select([channel], [], [], timeout)
            if channel in r:
                channel_data += channel.recv(9999)
                buf = channel_data.decode('utf-8')
                #print('buf: ', buf)
                if buf.endswith('] > ') == True:
                    debug('jest prompt, wysylamy cmd')
                    channel.send(cmd)
                    channel_data = bytes()
                    channel.send('quit\r\n')
                    continue
                if buf.find('quit\r\n') != -1:
                    debug('odebralismy quit')
                    channel_data = bytes()
                    wyjdz = True
                    break     
        procent = i / licznik_adresow * 100
        print("---------------- wykonano:  ", int(procent), "% -----------------")

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
	
	
	
	