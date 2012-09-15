import pyrs.comms
import pyrs.rpc
import pyrs.msgs
import curses

# Message Definitions.
from pyrs.proto import core_pb2
from pyrs.proto import system_pb2
from pyrs.proto import files_pb2

class Menu(object):
    def __init__(self, nc_window, rs_rpc, parser, parent):
        #menu - structure
        self.title = "Downloads"
        self.cur_funct = self.print_active_downloads
        
        my,mx = nc_window.getmaxyx()
        self.__nc_window = curses.newwin(my-9, mx-4, 8, 2); self.__nc_window.border(0); self.__nc_window.idlok(1)
        self.my,self.mx = self.__nc_window.getmaxyx()
        self.__rs_rpc = rs_rpc
        self.__parser = parser
        self.parent = parent
        #self.chat_register_id = self.__rs_rpc.request(pyrs.msgs.constructMsgId(core_pb2.CORE, core_pb2.CHAT, chat_pb2.MsgId_RequestRegisterEvents, False), self.__rp)
    def tick(self):
        self.cur_funct()
    def end(self):
        return True
    def menu_key(self, c):
        return True
    def print_active_downloads(self):
        transfers = self.list_downloads()
        if transfers:
            self.__nc_window.erase()
            self.__nc_window.border(0)
            i=1
            for transfer in transfers:
                if i+2 < self.my:
                    self.__nc_window.addstr(1+i, 1, str(i)+": name: "+transfer.file.name.encode("utf-8"))
                    self.__nc_window.addstr(1+i, int(self.mx/3.)+5, "size: "+str(transfer.file.size/1024)+" kB")
                    self.__nc_window.addstr(1+i, int(self.mx/2.), str(round(transfer.fraction*100,2))+"% finished")
                    self.__nc_window.addstr(1+i, int(2*self.mx/3.), "rate: "+str(round(transfer.rate_kBs,2))+" kB/s")
                i+=1
            self.__nc_window.addstr(1, 1, "active Downloads ("+str(i)+"):")
        else:
            self.__nc_window.addstr(1, 1, "no active Downloads")
        self.__nc_window.refresh()
        
    def list_downloads(self):
        rp = files_pb2.RequestTransferList()
        rp.direction = files_pb2.DIRECTION_DOWNLOAD
        msg_id = pyrs.msgs.constructMsgId(core_pb2.CORE, core_pb2.FILES, files_pb2.MsgId_RequestTransferList, False);
        req_id = self.__rs_rpc.request(msg_id, rp)
        (msg_id, msg_body) = self.parent.rs_response(req_id)
        if msg_body :
            resp = self.__parser.construct(msg_id, msg_body)
            if resp.status.code == core_pb2.Status.SUCCESS:
                return  resp.transfers
            else : return False