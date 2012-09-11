#!/usr/bin/python2.7

import pyrs.comms
import pyrs.rpc
import pyrs.msgs
import curses
import sys
import time

#import ncrsc classes
import status

username='Ralfk'
password='test1234'
host='192.168.178.29'
port=7022
timeout = 0.5
debug_output = False

# Construct a Msg Parser.
parser = pyrs.msgs.RpcMsgs()

#init ncurses
stdscr = curses.initscr()
stdscr.border(0); stdscr.keypad(1); curses.cbreak(); curses.noecho()

#open connection
stdscr.addstr(2, 2, "connecting to server...")
stdscr.refresh()

comms = pyrs.comms.SSHcomms(username, password, host, port)
comms.connect()
rs = pyrs.rpc.RsRpc(comms);

stdscr.clear()
stdscr.border(0)
my,mx = stdscr.getmaxyx()
statuswin = curses.newwin(6, mx-4, 1, 2); statuswin.border(0)

stdscr.nodelay(1)
try:
    
    while stdscr.getch() == curses.ERR:     #loop till user presses some key
        status_req = status.request_status(rs)
        time.sleep(0.5)
        
        # Now iterate through all the responses.
        (msg_id, msg_body) = rs.response(status_req, timeout)
        if msg_body :
            resp = parser.construct(msg_id, msg_body)
            if resp :
                status.print_status(statuswin,resp)
except:  
   comms.close()  
   e = sys.exc_info()
   curses.endwin()
   print e

curses.nocbreak(); stdscr.keypad(0); curses.echo()   #leave terminal in "normal" mode
comms.close()
curses.endwin()