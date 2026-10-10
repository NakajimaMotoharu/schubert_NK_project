"""Reauthenticate fresh current after old management recovery, no operations."""
import inspect
import pg1222_completed_retirement_preflight as transport
from pg1249_fresh_owned_stop_preflight import payload as previous

def payload():
    s=previous().replace('fresh-stop-preflight-v1','fresh-stop-preflight-v2')
    compile(s,'<actual recovered current complete preflight>','exec');return s

def main():
    entry=inspect.getsource(transport.main).replace('pg1222-completed-retirement-preflight-v1','pg1255-fresh-stop-preflight-v2')
    env=dict(transport.__dict__);env['payload']=payload
    exec(compile(entry,'<new-only recovered current preflight>','exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
