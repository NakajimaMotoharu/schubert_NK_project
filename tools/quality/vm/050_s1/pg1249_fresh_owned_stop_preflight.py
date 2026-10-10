"""Reauthenticate complete physical source/seal immediately before owned stop."""
import inspect
import pg1222_completed_retirement_preflight as transport
from pg1246_fresh_completed_capture_v3 import payload as previous
from pg1247_fresh_owned_stop_sources import GUEST_BEFORE,BEFORE

def payload():
    s=previous().replace('fresh-completed-capture-v3','fresh-stop-preflight-v1')
    old='current=capture();require(current==capture());SAVE.mkdir(mode=0o700)'
    if s.count(old)!=1:raise ValueError('fixed full source preflight boundary required')
    join="sealed_current=pathlib.Path("+repr(GUEST_BEFORE)+").read_bytes();require(hashlib.sha256(sealed_current).hexdigest()=="+repr(BEFORE)+");require(current==json.loads(sealed_current))"
    s=s.replace(old,'current=capture();require(current==capture());'+join+';SAVE.mkdir(mode=0o700)')
    compile(s,'<actual complete source physical reauthentication>','exec');return s

def main():
    entry=inspect.getsource(transport.main).replace('pg1222-completed-retirement-preflight-v1','pg1249-fresh-stop-preflight-v1')
    env=dict(transport.__dict__);env['payload']=payload
    exec(compile(entry,'<new-only complete stop preflight>','exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
