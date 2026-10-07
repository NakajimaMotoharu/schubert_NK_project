"""Current same-parent pre-UI full-column readonly proof. Never start/stop or complete parent."""
import os,pathlib,subprocess,hashlib
os.umask(0o077)
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
SSH=['ssh','-i',str(P/'vm-access'),'-p','22222','-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'ubuntu@127.0.0.1']
PAYLOAD=r'''import datetime,hashlib,json,os,pathlib,subprocess
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg522-preui-rows-v1');assert not root.exists()
def manager(unit):return dict(l.split('=',1)for l in subprocess.check_output(['systemctl','show',unit,'--property=MainPID,ControlPID,Job,InvocationID,ActiveState,SubState,Result,ExecMainCode,ExecMainStatus'],text=True).splitlines())
def preui():
 p=manager('schubert-nk-morning-controller.service');assert p['MainPID']=='320189' and p['InvocationID']=='8f4514e19fd94c429f2587af71edb53a' and p['ActiveState']=='activating' and p['Job']=='26968'
 for u in ['schubert-nk-api.service','schubert-nk-web.service','caddy.service']:
  v=manager(u);assert v['MainPID']==v['ControlPID']=='0' and v['Job']==''
 for u,inv in [('schubert-nk-cleanup.service','4e71eb986ac348d4b6cefe80a9f62148'),('schubert-nk-expiry-cleanup.service','cb7377c817fd41b098bd885d43daa37b')]:
  v=manager(u);assert v['InvocationID']==inv and v['Result']=='success' and v['ExecMainCode']=='1' and v['ExecMainStatus']=='0' and v['MainPID']==v['ControlPID']=='0' and v['Job']==''
 return p
before=preui();raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg521-runtime-resume-v2/after.private.json').read_bytes();assert hashlib.sha256(raw).hexdigest()=='f72d6c82d7ab352e415b3d9547ec83cf5c3a0a9d80a77a1d795720e8f9f8991e';old=json.loads(raw)['rows'];assert len(old)==24 and len(old['schubert.batch_runs'])==452
q="begin isolation level repeatable read read only;set local timezone='UTC';"
for t in old:q+="select json_build_object('table','"+t+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb)) from (select to_jsonb(t) j from "+t+" t) q;"
q+='commit;';data={}
for line in subprocess.check_output(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q],timeout=30).splitlines():
 v=json.loads(line);assert v['table'] not in data;data[v['table']]=v['rows']
assert set(data)==set(old) and all(data[t]==old[t]for t in old if t!='schubert.batch_runs')
assert all(r in data['schubert.batch_runs']for r in old['schubert.batch_runs'])
added=[r for r in data['schubert.batch_runs']if r not in old['schubert.batch_runs']]
steps={'BACKUP_DB','BACKUP_CONFIG','CLEAN_INBOX_OUTBOX','CLEAN_LOG','CLEAN_NOTIFICATION','CLEAN_QUESTION','CLEAN_SESSION','CLEAN_TRANSFER','CLEAN_BATCH_RUN','CLEAN_EXPIRY'}
assert len(added)==10 and {r['step']for r in added}==steps
dates={r['business_date']for r in old['schubert.batch_runs']if r['run_id']=='91a748b4-1abe-484c-9682-44f46429b324'};assert len(dates)==1
assert all(r['run_id']=='91a748b4-1abe-484c-9682-44f46429b324' and r['business_date']in dates and r['status']=='SKIPPED' and all(r[k]==0 for k in ['target_count','success_count','failure_count','byte_count']) and r['error_code']=='ALREADY_SUCCESSFUL' and r['error_summary']=='step already successful for business date' and r['started_at']is not None and r['ended_at']is not None and r['started_at']<=r['ended_at'] for r in added)
assert preui()==before
root.mkdir(mode=0o700)
with(root/'full-rows.private.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rows':data,'parent':before,'parentAccepted':False},f,sort_keys=True);f.flush();os.fsync(f.fileno())
fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'sameCurrentParent':True,'old452AllColumnsPreserved':True,'newTenExactApprovedSKIP':True,'other23TablesAllColumnsUnchanged':True,'normalCurrentCleanupExpiry0':True,'uiNotStartedAtCapture':True,'parentAccepted':False,'privateSnapshotSha256':hashlib.sha256((root/'full-rows.private.json').read_bytes()).hexdigest(),'rawExported':False}))
'''
log=W/'pg522-preui-rows-v1.private.log';assert not log.exists()
r=subprocess.run(SSH+['sudo -n python3 -B -'],input=PAYLOAD.encode(),capture_output=True)
with log.open('xb')as f:f.write(r.stdout);f.write(r.stderr);f.flush();os.fsync(f.fileno())
print(r.stdout.decode(),end='');print('PG522_PREUI_ROWS actual='+str(r.returncode)+' privateLogSha256='+hashlib.sha256(log.read_bytes()).hexdigest());raise SystemExit(r.returncode)
