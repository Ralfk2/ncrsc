import pyrs.comms
import pyrs.rpc
import pyrs.msgs
import curses

# Message Definitions.
from pyrs.proto import core_pb2
from pyrs.proto import system_pb2


def print_status(sw, resp):
    sw.border(0)
    sw.addstr(1, 1, "Ncurses Retroshare Control Terminal v0.1")
    if resp.status.code == core_pb2.Status.SUCCESS:
        sw.move(2, 1); sw.clrtoeol()
        sw.addstr(2, 1, "Friends "+str(resp.no_connected)+" / "+str(resp.no_peers))
        sw.addstr(2, 25, "Network: "+get_status_string(resp.net_status))
        sw.move(3, 1); sw.clrtoeol()
        sw.addstr(3, 1, "Down: "+str(round(resp.bw_total.down,2)))
        sw.addstr(3, 25, "Up: "+str(round(resp.bw_total.up,2)))
    else:
        sw.addstr(2, 1, "code: "+str(resp.status.code))
    sw.refresh()
    
def request_status(rs):
    rp = system_pb2.RequestSystemStatus();
    msg_id = pyrs.msgs.constructMsgId(core_pb2.CORE, core_pb2.SYSTEM, system_pb2.MsgId_RequestSystemStatus, False);
    return rs.request(msg_id, rp)
    
def get_status_string(code):
    if code == system_pb2.ResponseSystemStatus.BAD_NATSYM: return "BAD: symmetric NAT"
    elif code == system_pb2.ResponseSystemStatus.BAD_NODHT_NAT: return "BAD: NAT no DHT"
    elif code == system_pb2.ResponseSystemStatus.BAD_OFFLINE: return "BAD: offline"
    elif code == system_pb2.ResponseSystemStatus.BAD_UNKNOWN: return "BAD: unknown"
    elif code == system_pb2.ResponseSystemStatus.WARNING_NATTED: return "Warning: natted"
    elif code == system_pb2.ResponseSystemStatus.WARNING_NODHT: return "Warning: no DHT"
    elif code == system_pb2.ResponseSystemStatus.WARNING_RESTART: return "Warning: restarted"
    elif code == system_pb2.ResponseSystemStatus.ADV_FORWARD: return "GOOD: forwarded port"
    elif code == system_pb2.ResponseSystemStatus.GOOD: return "GOOD"