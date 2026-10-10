"""New-only fresh Log oracle with explicit sealed schema and source authority."""
import inspect
import json
from pg1266_fresh_log_independent_capture import payload as previous
import pg1257_fresh_independent_terminal_post as transport
import pg1267_fresh_before_provenance as provenance


def payload(seals):
    s=previous(seals).replace('PG1266-fresh-independent-log-v1','PG1268-fresh-independent-log-v2').replace('pg1266-fresh-independent-log-v1','pg1268-fresh-independent-log-v2')
    old="old=json.loads(old_raw)['current'];require(old['source']==data['source']['commit'])"
    if s.count(old)!=1:raise ValueError('actual before provenance insertion refused')
    replacement="authority=types.ModuleType('explicit_before_provenance');exec(BEFORE_SOURCE,authority.__dict__);old=json.loads(old_raw)['current'];authority.verify(BEFORE_RECEIPT,old);require(BEFORE_RECEIPT['productionSource']==data['source']['commit'])"
    s='BEFORE_SOURCE='+repr(inspect.getsource(provenance))+'\nBEFORE_RECEIPT='+repr(before_receipt())+'\n'+s.replace(old,replacement)
    compile(s,'<complete actual qualified current Log v2>','exec');return s


def before_receipt():
    value=json.loads((transport.W/'pg1238-fresh-day-ordinary-before-v1.safe.json').read_bytes())
    names=['actualExit','productionSource','privateBeforeSha256','ordinaryNoargs','newJstDate']
    result={k:value[k] for k in names}
    snapshot={k:{} for k in provenance.FIELDS};snapshot['rows']={str(i):[] for i in range(24)}
    provenance.verify(result,snapshot)
    return result


def main():
    entry=inspect.getsource(transport.main).replace('pg1257-fresh-terminal-post-v1','pg1268-fresh-independent-log-v2')
    env=dict(transport.__dict__);env['payload']=payload
    exec(compile(entry,'<new-only explicit fresh Log actual transport>','exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
