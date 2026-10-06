"""BUG788 independent read-only day/run SQL oracle; diagnosis success is NOT route acceptance."""
import os,pathlib,subprocess
os.umask(0o077)
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
SSH=['ssh','-i',str(P/'vm-access'),'-p','22222','-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'ubuntu@127.0.0.1']
payload=r'''import json,subprocess,pathlib,hashlib
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54'
p=pathlib.Path('/var/lib/pgpt-s1-preservation/pg487-parent-failure-v1/snapshot.private.json');assert hashlib.sha256(p.read_bytes()).hexdigest()=='5c2108ca88f39b2a68c374b2314b569be0dbb844016bce1861801eb1b379ca87'
q="""begin isolation level repeatable read read only;set local timezone='UTC';
select json_build_object('step',s.step,'current_skip',
 (select count(*) from schubert.batch_runs c where c.run_id='91a748b4-1abe-484c-9682-44f46429b324' and c.business_date=date '2026-10-06' and c.step=s.step and c.status='SKIPPED' and c.error_code='ALREADY_SUCCESSFUL' and c.error_summary='step already successful for business date' and c.target_count=0 and c.success_count=0 and c.failure_count=0 and c.byte_count=0 and c.started_at=c.ended_at),
 'same_run_success',(select count(*) from schubert.batch_runs r where r.run_id='91a748b4-1abe-484c-9682-44f46429b324' and r.business_date=date '2026-10-06' and r.step=s.step and r.status='SUCCESS'),
 'other_run_success',(select count(*) from schubert.batch_runs r where r.run_id<>'91a748b4-1abe-484c-9682-44f46429b324' and r.business_date=date '2026-10-06' and r.step=s.step and r.status='SUCCESS' and r.ended_at<=timestamptz '2026-10-06T12:06:14.564793Z'))
from (values ('CLEAN_NOTIFICATION'),('CLEAN_QUESTION'),('CLEAN_SESSION'),('CLEAN_INBOX_OUTBOX'),('CLEAN_LOG'),('CLEAN_BATCH_RUN'),('CLEAN_TRANSFER')) s(step);commit;"""
raw=subprocess.check_output(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q]);rows=[json.loads(l) for l in raw.splitlines()]
assert len(rows)==7 and len({r['step'] for r in rows})==7 and all(r['current_skip']==r['other_run_success']==1 and r['same_run_success']==0 for r in rows)
print(json.dumps({'independentSqlActualExit0':True,'currentSevenCanonicalSkips':True,'earlierSameDayOtherRunSuccesses':7,'sameRunSuccesses':0,'requirementRouteFailed':True,'exactLostThrowTraceClaimed':False,'source':'2e017b4063960bfb5f2483f10510d1a6a3391a9f','BUG':'BUG-788','SS':['SS331-8.3','SS341','SS343'],'starts0':True,'updates0':True,'privateSnapshotSha256':hashlib.sha256(p.read_bytes()).hexdigest()}))
'''
r=subprocess.run(SSH+['sudo -n python3 -B -'],input=payload.encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with (W/'pg487-reference-sql-diagnosis-v1.private.log').open('xb') as f:f.write(r.stdout);f.write(r.stderr)
with (W/'pg487-reference-sql-diagnosis-v1.exit').open('x') as f:f.write(str(r.returncode)+'\n')
if r.returncode==0:print(r.stdout.decode(),end='')
else:print('PG487_SQL_DIAGNOSIS_REFUSED actual='+str(r.returncode)+' logsPrivate=true')
raise SystemExit(r.returncode)
