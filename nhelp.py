import pyrs.comms
import pyrs.rpc
import pyrs.msgs
import curses

# Message Definitions.
from pyrs.proto import core_pb2
from pyrs.proto import system_pb2
from pyrs.proto import files_pb2

class Menu(object):
    def __init__(self, nc_window, parent):
        #menu - structure
        self.title = "Help"
        
        my,mx = nc_window.getmaxyx()
        self.__nc_window = curses.newwin(my-9, mx-4, 8, 2); self.__nc_window.border(0); self.__nc_window.idlok(1)
        self.my,self.mx = self.__nc_window.getmaxyx()
        self.parent = parent
        self.scroll = 0
        self.printed = False
        #self.chat_register_id = self.__rs_rpc.request(pyrs.msgs.constructMsgId(core_pb2.CORE, core_pb2.CHAT, chat_pb2.MsgId_RequestRegisterEvents, False), self.__rp)
    def tick(self, update=False):
        if self.printed: return True
        self.__nc_window.erase()
        self.__nc_window.border(0)
        self.__nc_window.addstr(1, 1, "Help", curses.A_BOLD)
        help_list = ["", "you can switch between your tabs with the arrow keys and/or with the key as written above", ""]
        i = 2
        for child in self.parent.children:
            help_list.append(" Function "+child[0].title)
            i += 2
            for s in child[0].get_help():
                help_list.append(s)
                i += 1
            help_list.append("")
        if self.scroll > 0 and i+2-self.scroll < self.my:
                self.scroll -= self.my-(i+2-self.scroll)
                if self.scroll < 0: self.scroll = 0
        i = 0
        for s in help_list:
            if i > self.scroll and i+2-self.scroll < self.my:
                self.__nc_window.addstr(1+i-self.scroll, 1, s)
            i += 1
        self.__nc_window.addstr(1, 6, str(self.scroll)+"/"+str(len(help_list)))
        self.__nc_window.refresh()
        self.printed = True
        return True
    def end(self):
        self.printed = False
        return True
    def menu_key(self, c):
        if c == ord('r'): self.printed = False
        elif c == curses.KEY_DOWN:
            self.scroll += 5
            self.printed = False
        elif c == curses.KEY_UP:
            self.scroll -= 5
            self.printed = False
            if self.scroll < 0: self.scroll = 0
        return True
    def get_help(self):
        help_list = ["   move up/down with your arrow keys", "   refresh the page with 'r'"]
        return help_list