"""Seal real Root13 WARNING data/manager failure and current owned resources.

SS341/343/353 SSC278 BUG1162; PT-OPS-WARN1770. This is not whole acceptance.
No success-only historical receipt/row oracle is imported as current evidence.
"""
import ast
import inspect
from pg1702_new_source_completed_seal import payload as old_payload
import pg1766_next_day_independent_candidates as transport
from pg1765_warning_terminal_capture_v2 import payload as capture_payload
from pg1769_next_day_rows_oracle import oracle_source
from pg1762_next_day_done_receipt import EXPECTED,OLD

SLOT='pg1770-next-day-full-warning-seal-v1'


def warning_completion(rows,done):
    import datetime
    if type(rows)is not list or not rows:raise ValueError('actual failure journal required')
    for r in rows:
        if not all(r.get(k)==v for k,v in {'_BOOT_ID':EXPECTED['boot'],'_PID':'1','_UID':'0','_COMM':'systemd','UNIT':'schubert-nk-morning-controller.service','INVOCATION_ID':EXPECTED['invocation']}.items()):raise ValueError('actual Root failure generation required')
        if type(r.get('__MONOTONIC_TIMESTAMP'))is not str or not r['__MONOTONIC_TIMESTAMP'].isdecimal()or not EXPECTED['start']<=int(r['__MONOTONIC_TIMESTAMP'])<=EXPECTED['start']+1800000000:raise ValueError('original budget required')
    jobs=[r for r in rows if r.get('MESSAGE_ID')=='be02cf6855d2428ba40df7e9d022f03d'and r.get('JOB_ID')==EXPECTED['job']and r.get('JOB_TYPE')=='start'and r.get('JOB_RESULT')=='failed']
    failures=[r for r in rows if r.get('MESSAGE_ID')=='98e322203f7a4ed290d09fe03c09fe15'and r.get('EXIT_CODE')=='exited'and r.get('EXIT_STATUS')=='10']
    if len(jobs)!=1 or len(failures)!=1:raise ValueError('exact retained failure facts required')
    fields=done.decode('ascii').splitlines()
    if len(fields)!=6 or fields[:4]!=['NKDONE1',EXPECTED['run'],EXPECTED['cutoff'],EXPECTED['activation']]or fields[5]!='10':raise ValueError('exact warning original required')
    ended=datetime.datetime.fromisoformat(fields[4].replace('Z','+00:00'))
    stamp=jobs[0].get('__REALTIME_TIMESTAMP')
    if type(stamp)is not str or not stamp.isdecimal():raise ValueError('actual PID1 time required')
    real=datetime.datetime.fromtimestamp(int(stamp)/1000000,datetime.timezone.utc)
    if ended.tzinfo is None or not datetime.datetime.fromisoformat(EXPECTED['cutoff'].replace('Z','+00:00'))<=ended<=real or (real-ended).total_seconds()>60:raise ValueError('same completion time required')
    end=int(jobs[0]['__MONOTONIC_TIMESTAMP'])
    return {'genuinePid1Failure':True,'genuinePid1StartDone':False,'genuineRootDone':True,'completionOutcome':'WARNING','managerFailureRetained':True,'sameRunActivationCutoff':True,'endMonotonicUs':end,'elapsedSeconds':(end-EXPECTED['start'])/1000000,'wholeAccepted':False}


def replace_constant(raw,name,new):
    nodes=[n for n in ast.parse(raw).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id==name for t in n.targets)]
    if len(nodes)!=1:raise ValueError('one explicit constant boundary required')
    old=ast.get_source_segment(raw,nodes[0]);return raw.replace(old,name+'='+repr(new),1)


def guard():
    raw=capture_payload();marker="out=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1765-warning-terminal-capture-v2')"
    if raw.count(marker)!=1:raise ValueError('one readonly capture stop point required')
    raw=raw[:raw.index(marker)]+"\nrows=json.loads(project(journal))\n"+inspect.getsource(warning_completion)+"\nresult=warning_completion(rows,done)\n"
    return raw


def payload():
    raw=old_payload();raw=replace_constant(raw,'GUARD',guard())
    model=oracle_source().replace('def qualify(before,now,oracle,run,cutoff,upper):','def qualify_new(before,now,oracle,run,cutoff,upper):')
    model+=r'''
import hashlib,pathlib
oracle_raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1768-next-day-inbox-oracle-v1/oracle.private.json').read_bytes()
require(hashlib.sha256(oracle_raw).hexdigest()=='a1f2ff92e014509b67dfb727f41fe5165b75d18f271ee90a68b8f7518aefe030')
EXPECTED_ORACLE=json.loads(oracle_raw)
def qualify(old,new,cutoff,done,upper):
 require(cutoff==EXPECTED_ORACLE['cutoff']and instant(cutoff)<=instant(done)<=instant(upper))
 return qualify_new(old,new,EXPECTED_ORACLE,'4148e3e8-f107-431a-ab27-d6e6d1f1772e',cutoff,upper)
'''
    raw=replace_constant(raw,'ORACLE',model)
    schema="{'backup','configuration','extraDurable','originals','pid1','rows','runtime','startup','unitFilesActual','units'}"
    if raw.count(schema)!=1:raise ValueError('actual original schema point required')
    raw=raw.replace(schema,"{'backup','configuration','extraDurable','investigationBusinessDay','native','originals','pid1','rows','runtime','startup','unitFilesActual','units'}")
    for a,b in [('pg1702-new-source-completed-seal-v1',SLOT),('pg1699-new-current-ordinary-once-v1/before.private.json','pg1759-next-day-ordinary-once-v1/before.private.json'),('ef9ddffcf813c6e4f4b8bb6379c30e5e0d87503a4abaf46859976a32fa8bfecb','a919274268cfd66a4478f83cfeff52c1bfc3fb12323209133218bdc72d01c23e')]+[(OLD[k],EXPECTED[k])for k in ('run','cutoff','activation')]:
        if a not in raw:raise ValueError('actual full join boundary required')
        raw=raw.replace(a,b)
    from pyflakes.api import check
    if check(raw,'<actual warning full seal>'):raise ValueError('all emitted globals required')
    compile(raw,'<actual warning full seal>','exec');return raw


def main():
    raw=inspect.getsource(transport.main).replace('pg1766-next-day-independent-candidates-v1',SLOT)
    ns={**transport.__dict__,'payload':payload};exec(compile(raw,'<fixed full warning seal transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
