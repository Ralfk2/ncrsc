import pyrs.comms
import pyrs.rpc
import pyrs.msgs
import curses

# Message Definitions.
from pyrs.proto import core_pb2
from pyrs.proto import system_pb2
from pyrs.proto import chat_pb2

class Menu(object):
    def __init__(self, nc_window, rs_rpc, parser, parent):
        #menu - structure
        self.title = "Chat"
        self.cur_funct = self.print_lobbies
        
        my,mx = nc_window.getmaxyx()
        self.__nc_window = curses.newwin(my-9, mx-4, 8, 2); self.__nc_window.border(0); self.__nc_window.idlok(1)
        self.my,self.mx = self.__nc_window.getmaxyx()
        self.__rs_rpc = rs_rpc
        self.__parser = parser
        self.__rp = chat_pb2.RequestChatLobbies()
        self.__rp.lobby_set = chat_pb2.RequestChatLobbies.LOBBYSET_ALL
        self.parent = parent
        self.lobbies = False
        #self.chat_register_id = self.__rs_rpc.request(pyrs.msgs.constructMsgId(core_pb2.CORE, core_pb2.CHAT, chat_pb2.MsgId_RequestRegisterEvents, False), self.__rp)
    def tick(self, update=False):
        self.cur_funct(update)
    def blubb(self):
        msg_id = pyrs.msgs.constructMsgId(core_pb2.CORE, core_pb2.CHAT, chat_pb2.MsgId_RequestRegisterEvents, False);
        #msg_id = pyrs.msgs.constructMsgId(core_pb2.CORE, core_pb2.CHAT, chat_pb2.MsgId_EventChatMessage, True);
        chat_register_id = self.__rs_rpc.request(msg_id, self.__rp)
        (msg_id, msg_body) = self.parent.rs_response(chat_register_id)
        if msg_body :
            resp = self.__parser.construct(msg_id, msg_body)
            if resp.status.code == core_pb2.Status.SUCCESS and (msg_id == self.__chatEvent_msgid):
                self.print_lobby(resp)
    def end(self):
        return True
    def menu_key(self, c):
        if c >= ord('0') and c <= ord('9'): self.enter_leave_lobby(c)
        elif c == ord('n'): self.change_name()
        return True
    def add_message_to_lobby(self,resp):
        pass
    def print_lobby(self, resp):
        self.__nc_window.erase()
        self.__nc_window.border(0)
        self.__nc_window.addstr(1, 1, resp.msg.msg)
    def list_lobbies(self):
        msg_id = pyrs.msgs.constructMsgId(core_pb2.CORE, core_pb2.CHAT, chat_pb2.MsgId_RequestChatLobbies, False);
        chat_req_id = self.__rs_rpc.request(msg_id, self.__rp)
        (msg_id, msg_body) = self.parent.rs_response(chat_req_id)
        if msg_body :
            resp = self.__parser.construct(msg_id, msg_body)
            if resp.status.code == core_pb2.Status.SUCCESS:
                return  resp.lobbies
            else : return False

    def print_lobbies(self, update=False):
        if update: self.lobbies = self.list_lobbies()
        if self.lobbies:
            self.__nc_window.erase()
            self.__nc_window.border(0)
            self.__nc_window.addstr(1, 1, "Public lobbies:")
            i=0
            for lobby in self.lobbies:
                if i+3 < self.my:
                    atr = curses.A_NORMAL
                    if lobby.lobby_state == chat_pb2.ChatLobbyInfo.LOBBYSTATE_JOINED : atr = curses.A_BOLD
                    self.__nc_window.addstr(2+i, 1, str(i)+": name: "+lobby.lobby_name.encode("utf-8"), atr)
                    self.__nc_window.addstr(2+i, int(self.mx/3.), "#"+str(lobby.no_peers), atr)
                    self.__nc_window.addstr(2+i, int(self.mx/3.)+4, "topic: "+lobby.lobby_topic.encode("utf-8"), atr)
                    i+=1
            self.__nc_window.refresh()  
    def enter_leave_lobby(self, c):         #at the moment one can only join lobbies 0-9
        self.__nc_window.addstr(min(12,self.my)-1, 1, str(c))
        lobbies = self.list_lobbies()
        if lobbies:
            i=ord('0')
            for lobby in lobbies:
                if c == i:
                    rp = chat_pb2.RequestJoinOrLeaveLobby();
                    rp.lobby_id = lobby.lobby_id;
                    if lobby.lobby_state == chat_pb2.ChatLobbyInfo.LOBBYSTATE_JOINED :
                        rp.action = chat_pb2.RequestJoinOrLeaveLobby.LEAVE_OR_DENY;
                    else :
                        rp.action = chat_pb2.RequestJoinOrLeaveLobby.JOIN_OR_ACCEPT;
                    msg_id = pyrs.msgs.constructMsgId(core_pb2.CORE, core_pb2.CHAT, chat_pb2.MsgId_RequestJoinOrLeaveLobby, False);
                    reg_id = self.__rs_rpc.request(msg_id, rp)
                    (msg_id, msg_body) = self.parent.rs_response(reg_id)
                    if msg_body :
                        resp = self.__parser.construct(msg_id, msg_body)
                        if resp.status.code == core_pb2.Status.SUCCESS:
                            if lobby.lobby_state == chat_pb2.ChatLobbyInfo.LOBBYSTATE_JOINED :
                                self.__nc_window.addstr(min(12,self.my), 1, "You left "+lobby.lobby_name.encode("utf-8"))
                            else:
                                self.__nc_window.addstr(min(12,self.my), 1, "You entered "+lobby.lobby_name.encode("utf-8"))
                            self.__nc_window.refresh()  
                            return True
                        return False
                    return False
                i+=1
        self.__nc_window.addstr(min(12,self.my), 1, "The lobby you chose doesn't exist.")
        return False
        
    def change_name(self):
        self.__nc_window.nodelay(0)
        self.__nc_window.erase()
        self.__nc_window.border(0)
        curses.echo()  
        self.__nc_window.addstr(1, 1, "Enter you new name and press Enter or enter nothing and press Enter to cancel:")
        name = self.__nc_window.getstr(2,1)
        self.__nc_window.nodelay(1)
        curses.noecho()  
        if len(name) > 0:
            rp = chat_pb2.RequestSetLobbyNickname()
            rp.nickname = name
            
            msg_id = pyrs.msgs.constructMsgId(core_pb2.CORE, core_pb2.CHAT, chat_pb2.MsgId_RequestSetLobbyNickname, False);
            req_id = self.__rs_rpc.request(msg_id, rp)
            (msg_id, msg_body) = self.parent.rs_response(req_id)
            if msg_body :
                resp = self.__parser.construct(msg_id, msg_body)
                return resp.status.code == core_pb2.Status.SUCCESS
            return False
        return True
    def get_help(self):
        help_list = ["   enter/leave lobbies by pressing the number in front of them (0-9)", "   press 'n' to change your name (does not work yet)"]
        return help_list