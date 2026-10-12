"""New readonly full-seal equality before fixed owned stop; no success claim."""
import inspect
import pg1770_next_day_full_warning_seal as seal
from pg1772_warning_owned_stop_sources import context

SLOT='pg1775-warning-stop-preflight-v1'


def payload():
    return seal.payload().replace(seal.SLOT,SLOT)


def main():
    before,_,_,_=context()
    raw=inspect.getsource(seal.transport.main).replace('pg1766-next-day-independent-candidates-v1',SLOT)
    old='    print(json.dumps(result));return r.returncode'
    if raw.count(old)!=1:raise ValueError('one actual preflight result boundary required')
    raw=raw.replace(old,"""    if r.returncode==0:
        guest=result['guest']
        if guest['privateBeforeSha256']!=BEFORE:raise ValueError('full current owned seal changed')
        with(W/'pg1775-warning-stop-preflight-v1.safe.json').open('x')as f:json.dump(guest,f,sort_keys=True);f.flush();os.fsync(f.fileno())
"""+old)
    ns={**seal.transport.__dict__,'payload':payload,'BEFORE':before}
    exec(compile(raw,'<fresh identical warning stop seal>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
