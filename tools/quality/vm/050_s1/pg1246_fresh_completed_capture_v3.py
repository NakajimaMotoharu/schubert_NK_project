"""New-only full32 capture with independent V012/V014 new-day progress joins."""
import inspect
import pg1222_completed_retirement_preflight as transport
from pg1245_fresh_completed_capture_v2 import payload as previous

def payload():
    s=previous().replace('fresh-completed-capture-v2','fresh-completed-capture-v3')
    old="rs=rows();summary=data.session_post(sealed['rows'],rs,data.instant('2026-10-10T20:03:22.718197Z'))"
    if s.count(old)!=1:raise ValueError('fixed new-day progress oracle insertion required')
    s=s.replace(old,old+"\n summary['independentProgress']=data.zero_progress_post(sealed['rows'],rs,data.instant('2026-10-10T20:03:22.718197Z'),'9f651096-aef9-4fba-90b0-a653e99f035a',datetime.datetime.now(datetime.timezone.utc))")
    compile(s,'<fresh complete new-day progress capture>','exec');return s

def main():
    entry=inspect.getsource(transport.main).replace('pg1222-completed-retirement-preflight-v1','pg1246-fresh-completed-capture-v3')
    env=dict(transport.__dict__);env['payload']=payload
    exec(compile(entry,'<new-only fresh progress fullcapture>','exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
