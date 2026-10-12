"""Independent new-day 24-table postcondition; never manager/owner acceptance.

SS331/324/341 + V010-014; PT-OPS-DAY1769. Before selectors and authenticated
UPW proof are separately sealed by1768. Readonly consistent actual image only.
"""
import ast
import inspect
import json
import pg1196_completed_rows_oracle as http
from pg1196_completed_rows_oracle import require,instant,BATCH,LOG,SESSION,OUTBOX,STEPS
from pg1762_next_day_done_receipt import EXPECTED
from pg1766_next_day_independent_candidates import main as previous_main
import pg1766_next_day_independent_candidates as transport


def delta(old,new,keys,ids):
    require(type(old)is list and type(new)is list and type(ids)is list)
    seals=lambda rows:[json.dumps(r,sort_keys=True,separators=(',',':'))for r in rows]
    a,b=seals(old),seals(new);require(len(set(a))==len(a)and len(set(b))==len(b))
    deleted=[r for r,s in zip(old,a)if s not in set(b)]
    require(sorted(str(r[keys])for r in deleted)==sorted(ids))
    added=[r for r,s in zip(new,b)if s not in set(a)]
    return added


def qualify(before,now,oracle,run,cutoff,upper):
    require(set(before)==set(now)and len(before)==24)
    start,end=instant(cutoff),instant(upper);require(start<end)
    expected=oracle['expected'];inbox=oracle['expectedInbox'];removed={}
    for table in before:
        name=table.split('.')[-1]
        ids=expected.get(table,expected.get(name,[]))
        key='id'
        if name=='request_inbox':ids=inbox['deleted'];key='message_id'
        elif name in {'inbox_inspection_progress','log_cleanup_progress'}:key='run_id'
        elif name=='web_receipt_references':key='receipt_id'
        elif name=='login_ip_attempts':key='client_address'
        removed[table]=(key,ids)
    added={table:delta(rows,now[table],*removed[table])for table,rows in before.items()}
    allowed={BATCH,LOG,SESSION,OUTBOX,'schubert.inbox_inspection_progress','schubert.log_cleanup_progress'}
    require(all(not rows for table,rows in added.items()if table not in allowed))
    batch=added[BATCH];require(len(batch)==10 and {r['step']for r in batch}==STEPS)
    session_count=sum(len(expected[k])for k in ['auth_sessions','login_ip_attempts','web_http_sessions'])
    outbox_count=sum(len(expected[k])for k in ['schubert.mq_outbox',OUTBOX])
    targets={'CLEAN_SESSION':session_count,'CLEAN_INBOX_OUTBOX':outbox_count+len(expected['inbox_scan_candidates'])}
    successes={'CLEAN_SESSION':session_count,'CLEAN_INBOX_OUTBOX':outbox_count+len(inbox['deleted'])}
    require(all(not expected[k]for k in ['notifications','questions','app_logs','batch_runs','schubert.inbox_inspection_progress','schubert.log_cleanup_progress','web_receipt_references']))
    protected=len(inbox['protected'])
    for r in batch:
        require(r['run_id']==run and r['business_date']=='2026-10-13')
        require(start<=instant(r['started_at'])<=instant(r['ended_at'])<=end and type(r['attempt'])is int and r['attempt']==1)
        require(all(type(r[k])is int for k in ['target_count','success_count','failure_count','byte_count'])and r['failure_count']==0)
        if r['step']in {'BACKUP_DB','BACKUP_CONFIG'}:
            target=1 if r['step']=='BACKUP_DB'else 2
            require(r['status']=='SUCCESS'and r['target_count']==r['success_count']==target and r['byte_count']>0 and r['error_code']is r['error_summary']is None)
        else:
            require(r['byte_count']==0 and r['target_count']==targets.get(r['step'],0)and r['success_count']==successes.get(r['step'],0))
            if r['step']=='CLEAN_INBOX_OUTBOX'and protected:
                require(r['status']=='WARNING'and r['error_code']=='PROTECTED_RECORDS'and r['error_summary']=='protected records retained')
            else:require(r['status']=='SUCCESS'and r['error_code']is r['error_summary']is None)
    progress=added['schubert.inbox_inspection_progress'];require(len(progress)==1);p=progress[0]
    require(p['run_id']==run and instant(p['cutoff'])==start and start<=instant(p['completed_at'])<=end)
    require(p['inspected_count']==len(expected['inbox_scan_candidates'])and p['deleted_count']==len(inbox['deleted'])and p['protected_count']==protected)
    require(p['after_message_id']==max(expected['inbox_scan_candidates'],default=None))
    logs=added['schubert.log_cleanup_progress'];require(len(logs)==1);p=logs[0]
    require(p['run_id']==run and instant(p['cutoff'])==start and start<=instant(p['completed_at'])<=end)
    require(p['target_count']==p['deleted_count']==p['skipped_count']==0 and p['after_logged_at']is p['after_id']is None)
    result=validate_http(added,start,end)
    return {**result,'newDaySteps':10,'expectedSessionDeleted':session_count,'expectedOutboxDeleted':outbox_count,'expectedInboxDeleted':len(inbox['deleted']),'expectedInboxProtected':protected,'independentRowsQualified':True,'wholeAccepted':False}


def http_validation_source():
    body=inspect.getsource(http.after);body=body[body.index('    logs,events,sessions='):body.index('    return ')]
    return 'def validate_http(added,start,end):\n'+body+"    return {'newAnonymousHttpLogs':len(logs),'newAnonymousSessions':len(sessions),'newSentOutbox':len(events),'logOutboxOneToOne':True}\n"


def validate_http(added,start,end):
    env=dict(http.__dict__)
    exec(compile(http_validation_source(),'<independent HTTP structural oracle>','exec'),env)
    return env['validate_http'](added,start,end)


def oracle_source():
    raw=inspect.getsource(http)
    nodes=ast.parse(raw).body
    selected=[n for n in nodes if isinstance(n,(ast.Import,ast.ImportFrom))or isinstance(n,ast.Assign)or isinstance(n,ast.FunctionDef)and n.name in {'require','instant','identifier','ciphertext','key_version'}]
    source='\n'.join(ast.get_source_segment(raw,n)for n in selected)+'\n'
    source+=http_validation_source()
    source+=inspect.getsource(delta)+'\n'+inspect.getsource(qualify)
    return source


def payload():
    raw=oracle_source()+'\nRUN='+repr(EXPECTED['run'])+'\nCUT='+repr(EXPECTED['cutoff'])+'\n'
    raw+=r'''
import hashlib,os,pathlib,subprocess
require(os.geteuid()==0)
base=pathlib.Path('/var/lib/pgpt-s1-preservation')
br=(base/'pg1759-next-day-ordinary-once-v1/before.private.json').read_bytes();require(hashlib.sha256(br).hexdigest()=='a919274268cfd66a4478f83cfeff52c1bfc3fb12323209133218bdc72d01c23e');before=json.loads(br)
oraw=(base/'pg1768-next-day-inbox-oracle-v1/oracle.private.json').read_bytes();require(hashlib.sha256(oraw).hexdigest()=='a1f2ff92e014509b67dfb727f41fe5165b75d18f271ee90a68b8f7518aefe030');oracle=json.loads(oraw)
require(oracle['beforeSha256']==hashlib.sha256(br).hexdigest()and oracle['cutoff']==CUT)
sql="begin isolation level repeatable read read only;set local timezone='UTC';"
for table in before['rows']:
 require(re.fullmatch(r'[a-z_]+\.[a-z_]+',table)is not None)
 sql+="select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb))from(select to_jsonb(t)j from "+table+' t)q;'
sql+='commit;'
r=subprocess.run(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk'],input=sql.encode(),capture_output=True,timeout=20);require(r.returncode==0 and 0<len(r.stdout)<=67108864)
now={}
for line in r.stdout.splitlines():
 v=json.loads(line);require(v['table']not in now);now[v['table']]=v['rows']
upper=datetime.datetime.now(datetime.timezone.utc).isoformat()
result=qualify(before['rows'],now,oracle,RUN,CUT,upper)
out=base/'pg1769-next-day-rows-oracle-v1';os.umask(0o077);out.mkdir(mode=0o700)
with(out/'after.private.json').open('x')as f:json.dump({'rows':now,'upper':upper,'result':result},f,sort_keys=True);f.flush();os.fsync(f.fileno())
fd=os.open(out,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
print(json.dumps({**result,'beforeSha256':hashlib.sha256(br).hexdigest(),'independentOracleSha256':hashlib.sha256(oraw).hexdigest(),'afterSha256':hashlib.sha256((out/'after.private.json').read_bytes()).hexdigest(),'actualExit':0,'startsStopsSqlWrites':0,'privateOnly':True}))
'''
    from pyflakes.api import check
    if check(raw,'<new-day full rows independent oracle>'):raise ValueError('emitted dependency failure')
    compile(raw,'<new-day rows oracle>','exec');return raw


def main():
    raw=inspect.getsource(previous_main).replace('pg1766-next-day-independent-candidates-v1','pg1769-next-day-rows-oracle-v1')
    ns={**transport.__dict__,'payload':payload};exec(compile(raw,'<new-day readonly rows transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
