"""Same actual296 four owners and unchanged12 cases; owned current SOCKS generation required."""
import json
import types
import pg5048_current_same_owner_browser as previous
import pg5476_current_admission_image as admission
import pg5478_current_genuine_terminal as terminal
import pg5482_current_newday_whole_seal as seal
import pg5486_current_browser_ready as ready
from pg5045_current_browser_socks import owned_socks

SLOT='pg5488-current-same-owner-browser-v1'
SOURCE=admission.SOURCE


def receipt(slot):
    v=json.loads((admission.W/slot/'manifest.safe.json').read_bytes())
    if not(type(v.get('actualExit'))is int and v['actualExit']==0 and v.get('source')==SOURCE and type(v.get('result'))is dict):
        raise ValueError('actual same296 phase receipt')
    return{**v['result'],'actualExit':v['actualExit'],'productionSource':v['source']}


def current_guard(raw):
    old='/opt/schubert-nk/releases/0.1.0-PG3976';new='/opt/schubert-nk/releases/0.1.0-PG5430'
    if raw.count(old)!=1 or new in raw:raise ValueError('one exact historical Browser release authority')
    return raw.replace(old,new,1)


def guard():
    ns={**vars(previous),'SOURCE':SOURCE,'admission':admission,'terminal':terminal,'seal':seal,
        'receipt':receipt,'current_guard':current_guard}
    return types.FunctionType(previous.guard.__code__,ns)()


def main():
    ns={**vars(previous),'SOURCE':SOURCE,'SLOT':SLOT,'admission':admission,'ready':ready,'guard':guard,'owned_socks':owned_socks}
    return types.FunctionType(previous.main.__code__,ns)()


if __name__=='__main__':raise SystemExit(main())
