import pyrs.comms
import pyrs.rpc
import pyrs.msgs
import curses

# Message Definitions.
from pyrs.proto import core_pb2
from pyrs.proto import peers_pb2
from pyrs.proto import system_pb2
from pyrs.proto import chat_pb2


def print_status(sw, resp):
    sw.addstr(1, 1, "Ncurses Retroshare Control Terminal v0.1")
    if resp.status.code == 3:
        sw.addstr(2, 1, "Friends "+str(resp.no_connected)+" / "+str(resp.no_peers))
        sw.addstr(2, 25, "Network: "+str(resp.net_status))
        sw.addstr(3, 1, "Down: "+str(round(resp.bw_total.down,2)))
        sw.addstr(3, 25, "Up: "+str(round(resp.bw_total.up,2)))
        sw.refresh()
    
def request_status(rs):
    rp = system_pb2.RequestSystemStatus();
    msg_id = pyrs.msgs.constructMsgId(core_pb2.CORE, core_pb2.CHAT, chat_pb2.MsgId_RequestRegisterEvents, False);
    return rs.request(msg_id, rp)