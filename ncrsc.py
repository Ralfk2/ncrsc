#!/usr/bin/python2.7

import pyrs.comms
import pyrs.rpc
import pyrs.msgs
import curses
import sys
import time

#import ncrsc classes
import status
import nhelp
import download
import upload
import chat

# Message Definitions.
from pyrs.proto import core_pb2
from pyrs.proto import system_pb2
from pyrs.proto import chat_pb2

import pyrs.test.auth

auth = pyrs.test.auth.Auth()

class MAIN(object):
    def __init__(self, stdscr, comms):
        # Construct a Msg Parser.
        self.TIMEOUT = 0.5
        self.parser = pyrs.msgs.RpcMsgs()
        self.rs = pyrs.rpc.RsRpc(comms)
        self.stdscr = stdscr
        self.comms = comms
        self.t = time.time()
        self.my,self.mx = self.stdscr.getmaxyx()
        self.statuswin = curses.newwin(7, self.mx-4, 1, 2); self.statuswin.border(0)
        self.statuswin.refresh()
        self.chatEvent_msgid = pyrs.msgs.constructMsgId(core_pb2.CORE, core_pb2.CHAT, chat_pb2.MsgId_EventChatMessage, True);
        
        #construct children
        self.children = []
        self.children.append([nhelp.Menu(self.stdscr, self), curses.KEY_F1]) #help menu
        self.children.append([download.Menu(self.stdscr, self.rs, self.parser, self), curses.KEY_F2]) #download menu
        self.children.append([upload.Menu(self.stdscr, self.rs, self.parser, self), curses.KEY_F3]) #upload menu
        self.children.append([chat.Menu(self.stdscr, self.rs, self.parser, self), curses.KEY_F4]) #chat menu
        #set active_child to help menu
        self.active_child = self.children[0]
        self.build_menu()
    def tick(self):
        loop = True
        while loop:
            t=time.time()
            while t-time.time() > -0.2:
                c = stdscr.getch()
                if c == ord('q'): 
                    loop = False
                    break               #exit while
                elif self.menu_key(c):
                    self.active_child[0].menu_key(c)
                
            if self.t-time.time() < -0.5 : 
                status_req = status.request_status(self.rs)
                
                # Now iterate through all the responses.
                (msg_id, msg_body) = self.rs.response(status_req, self.TIMEOUT)
                if msg_body :
                    resp = self.parser.construct(msg_id, msg_body)
                    if resp :
                        status.print_status(self.statuswin,resp)
                self.active_child[0].tick(True)
                self.t = time.time()
            else:
                self.active_child[0].tick()
            #if c >= ord('0') and c <= ord('9'): self.chat.enter_leave_lobby(c)
            #elif c == ord('n'): self.chat.change_name()
    def rs_response(self, req, i=0):
        resp = self.rs.response(req, self.TIMEOUT)
        if resp == None:
            time.sleep(5)
            if i == 20: return resp                 # ther server did probably die
            return self.rs_response(req, i+1)
        return resp
    def menu_key(self, c):
        i = 0
        for child in self.children:
            if c == child[1]:
                self.active_child[0].end()
                self.active_child = child
                self.build_menu()
                return False
            elif child[1] == self.active_child[1]:
                if c == curses.KEY_LEFT and i > 0:
                    self.active_child[0].end()
                    self.active_child = self.children[i-1]
                    self.build_menu()
                    return False
                elif c == curses.KEY_RIGHT and i+1 < len(self.children):
                    self.active_child[0].end()
                    self.active_child = self.children[i+1]
                    self.build_menu()
                    return False
            i += 1
        return True
    def build_menu(self):
        self.statuswin.addstr(4, 1, "")  #set cursor position
        for child in self.children:
            atr = curses.A_NORMAL
            if child[1] == self.active_child[1]: atr = curses.A_BOLD
            self.statuswin.addstr(self.get_key_string(child[1])+": "+child[0].title+" ", atr)
        self.statuswin.addstr("q: exit")
        self.statuswin.refresh()
    def get_key_string(self, c):
        if c == curses.KEY_F1: return "F1"
        elif c == curses.KEY_F2: return "F2"
        elif c == curses.KEY_F3: return "F3"
        elif c == curses.KEY_F4: return "F4"
        elif c == curses.KEY_F5: return "F5"
        elif c == curses.KEY_F6: return "F6"
        elif c == curses.KEY_F7: return "F7"
        elif c == curses.KEY_F8: return "F8"
        elif c == curses.KEY_F9: return "F9"
        else: return "unknown"

#init ncurses
stdscr = curses.initscr()
stdscr.border(0); stdscr.keypad(1); curses.cbreak(); curses.noecho()

#open connection
stdscr.addstr(2, 2, "connecting to server...")
stdscr.refresh()

comms = pyrs.comms.SSHcomms(auth.user, auth.pwd, auth.host, auth.port)
comms.connect()

stdscr.clear()
stdscr.border(0)
stdscr.nodelay(1)
main = MAIN(stdscr, comms)

try:
    main.tick()

except:  
   e = sys.exc_info()
   stdscr.addstr(20, 2, str(e))
   time.sleep(1.5)
   curses.nocbreak(); stdscr.keypad(0); curses.echo()
   curses.endwin()
   print e
   import pdb; pdb.post_mortem(e[2])
   comms.close()  

curses.nocbreak(); stdscr.keypad(0); curses.echo()   #leave terminal in "normal" mode
comms.close()
curses.endwin()