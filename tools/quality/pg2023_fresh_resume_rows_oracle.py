"""Independent completed-run replay postconditions: retained rows, nine skips and protected warning."""
import ast
import datetime
import hashlib
import inspect
import json
import os
import subprocess
import pg1196_completed_rows_oracle as http
from pg1769_next_day_rows_oracle import http_validation_source,validate_http
from pg1196_completed_rows_oracle import require,identifier,instant,BATCH,LOG,SESSION,OUTBOX,STEPS
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg2015_completed_run_fresh_resume_once import SOURCE

SLOT='pg2023-fresh-resume-rows-oracle-v1'


def qualify(old,new,run,cutoff,lower,upper):
    require(type(old)is dict and type(new)is dict and set(old)==set(new)and len(old)==24)
    identifier(run);start,end=instant(lower),instant(upper);require(start<=end)
    added={}
    for table,before in old.items():
        now=new[table];require(type(before)is list and type(now)is list and all(type(r)is dict for r in [*before,*now]))
        seals=lambda rows:[json.dumps(r,sort_keys=True,separators=(',',':'))for r in rows]
        a,b=seals(before),seals(now);require(len(set(a))==len(a)and len(set(b))==len(b)and set(a)<=set(b))
        added[table]=[r for r,s in zip(now,b)if s not in set(a)]
        if table not in {BATCH,LOG,SESSION,OUTBOX}:require(not added[table])
    require({BATCH,LOG,SESSION,OUTBOX}<=set(old))
    batch=added[BATCH];require(len(batch)==10 and {r.get('step')for r in batch}==STEPS)
    day=instant(cutoff).astimezone(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat()
    for row in batch:
        historical=[r['attempt']for r in old[BATCH]if r['run_id']==run and r['step']==row['step']]
        require(historical and row['run_id']==run and row['business_date']==day and row['attempt']==max(historical)+1)
        require(all(type(row[k])is int and row[k]==0 for k in ['target_count','success_count','failure_count','byte_count']))
        require(start<=instant(row['started_at'])<=instant(row['ended_at'])<=end)
        if row['step']=='CLEAN_INBOX_OUTBOX':
            require(row['status']=='WARNING'and row['error_code']=='PROTECTED_RECORDS'and row['error_summary']=='protected records retained')
        else:
            require(row['status']=='SKIPPED'and row['error_code']=='ALREADY_SUCCESSFUL'and row['error_summary']=='step already successful for business date'and row['started_at']==row['ended_at'])
    # DDL V019 complete same-run progress is reused, not reset/re-inspected or deleted.
    progress=[r for r in old['schubert.inbox_inspection_progress']if r['run_id']==run]
    require(len(progress)==1 and progress[0]['protected_count']==4 and progress[0]['completed_at']is not None and instant(progress[0]['cutoff'])==instant(cutoff))
    result=validate_http(added,start,end)
    return {**result,'independentRowsQualified':True,'old24RowsRetained':True,'newSkippedSteps':9,'newProtectedWarningSteps':1,'sameRunProgressUnchanged':True,'wholeAccepted':False}


def oracle_source():
    raw=inspect.getsource(http);selected=[n for n in ast.parse(raw).body if isinstance(n,(ast.Import,ast.ImportFrom,ast.Assign))or isinstance(n,ast.FunctionDef)and n.name in {'require','instant','identifier','ciphertext','key_version'}]
    return '\n'.join(ast.get_source_segment(raw,n)for n in selected)+'\n'+http_validation_source()+inspect.getsource(qualify)


def payload():
    raw=oracle_source()+r'''
import hashlib,os,pathlib,subprocess
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='3d69f5af-6bac-46b1-a540-7591c4a79a0d')
base=pathlib.Path('/var/lib/pgpt-s1-preservation');br=(base/'pg2015-completed-run-fresh-resume-once-v1/before.private.json').read_bytes()
require(hashlib.sha256(br).hexdigest()=='fd6412f31de9af59219a0fe28f49ce0d073b074a7ff83ca3516a22e462568b83');before=json.loads(br)
done=(pathlib.Path('/var/lib/schubert-nk/maintenance/attempts')/'e31b627c-c0e2-4120-bd64-c0777479e800.done').read_text().splitlines()
require(len(done)==6 and done[:4]==['NKDONE1','4148e3e8-f107-431a-ab27-d6e6d1f1772e','2026-10-12T18:20:32.598894Z','e31b627c-c0e2-4120-bd64-c0777479e800']and done[5]in {'0','10'})
sql="begin isolation level repeatable read read only;set local timezone='UTC';set local statement_timeout='5s';"
for table in before['rows']:
 require(re.fullmatch(r'[a-z_]+\.[a-z_]+',table)is not None)
 sql+="select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb))from(select to_jsonb(t)j from "+table+' t)q;'
sql+='commit;'
r=subprocess.run(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk'],input=sql.encode(),capture_output=True,timeout=20);require(r.returncode==0 and 0<len(r.stdout)<=67108864)
now={}
for line in r.stdout.splitlines():
 v=json.loads(line);require(v['table']not in now);now[v['table']]=v['rows']
upper=datetime.datetime.now(datetime.timezone.utc).isoformat();result=qualify(before['rows'],now,done[1],done[2],'2026-10-13T01:15:32.188849+00:00',upper)
out=base/'pg2023-fresh-resume-rows-oracle-v1';os.umask(0o077);out.mkdir(mode=0o700)
with(out/'after.private.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump({'rows':now,'upper':upper,'result':result},f,sort_keys=True);f.flush();os.fsync(f.fileno())
fd=os.open(out,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({**result,'actualExit':0,'beforeSha256':hashlib.sha256(br).hexdigest(),'afterSha256':hashlib.sha256((out/'after.private.json').read_bytes()).hexdigest(),'startsStopsSqlWrites0':True,'privateOnly':True}))
'''
    from pyflakes.api import check
    if check(raw,'<actual independent completed-run full rows oracle>'):raise ValueError('all rows globals required')
    compile(raw,'<same current completed-run rows post>','exec');return raw


def main():
    os.umask(0o077)
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed row oracle required')
    terminal=json.loads((W/'pg2021-fresh-resume-terminal-receipt-v1/manifest.safe.json').read_bytes())
    if terminal['actualExit']!=0 or terminal['productionSource']!=SOURCE or terminal['normalUnit0or10']is not True:raise ValueError('current genuine terminal required')
    out=W/SLOT;out.mkdir(mode=0o700);raw=payload();(out/'payload.private.py').write_text(raw);started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=45)
    (out/'stderr.private.log').write_bytes(r.stderr);value={'actualExit':r.returncode,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'productionSource':SOURCE,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False}
    if not r.returncode:value.update(json.loads(r.stdout))
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
