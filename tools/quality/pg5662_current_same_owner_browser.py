"""One sameRoot0ea twelve-case Browser/guest-clock run; no old failed prefix imported."""
import json
import types
import pg5524_guest_clock_same_owner_browser as previous
import pg5048_current_same_owner_browser as guard_template
import pg5644_current_admission_image as admission
import pg5646_current_genuine_terminal as terminal
import pg5650_current_newday_whole_seal as seal
import pg5660_current_browser_ready as ready
from pg5045_current_browser_socks import owned_socks

SOURCE=admission.SOURCE
SLOT='pg5662-current-same-owner-browser-v1'


def receipt(slot):
    v=json.loads((admission.W/slot/'manifest.safe.json').read_bytes())
    if not(type(v.get('actualExit'))is int and v['actualExit']==0 and v.get('source')==SOURCE and type(v.get('result'))is dict):raise ValueError('actual same0ea phase receipt')
    return{**v['result'],'actualExit':v['actualExit'],'productionSource':v['source']}


def current_guard(raw):
    old='/opt/schubert-nk/releases/0.1.0-PG3976';new='/opt/schubert-nk/releases/0.1.0-PG5598'
    if raw.count(old)!=1 or new in raw:raise ValueError('one historical Browser authority boundary')
    return raw.replace(old,new,1)


def guard():
    ns={**vars(guard_template),'SOURCE':SOURCE,'admission':admission,'terminal':terminal,'seal':seal,'receipt':receipt,'current_guard':current_guard}
    return types.FunctionType(guard_template.guard.__code__,ns)()


def entry_source():
    raw=previous.entry_source()
    marker="previousFailedRunPreserved='pg5488-current-same-owner-browser-v1'"
    if raw.count(marker)!=1:raise ValueError('one legacy failed-effects metadata boundary')
    return raw.replace(marker,'legacyFailedPrefixImported=False',1)


def main():
    admission.authenticate_host();template=previous.previous.previous.previous.previous.previous
    ns={**vars(template),'SLOT':SLOT,'SOURCE':SOURCE,'ready':ready,'guard':guard,'owned_socks':owned_socks}
    exec(compile(entry_source(),'<new-only strict guest-clock0ea Browser>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
