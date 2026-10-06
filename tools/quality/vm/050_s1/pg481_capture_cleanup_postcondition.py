"""Read-only point-in-time cleanup proof before UI starts; full rows never leave Root."""
import hashlib,pathlib,subprocess,os
os.umask(0o077)
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private');R=pathlib.Path(__file__).parent
SSH=['ssh','-i',str(P/'vm-access'),'-p','22222','-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'ubuntu@127.0.0.1']
oracle=(R/'pg481_cleanup_postcondition.py').read_text()
PAYLOAD=r'''import ast,datetime,hashlib,json,os,pathlib,stat,subprocess
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54'
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg481-cleanup-postcondition');assert not root.exists()
def stopped_ui():
 for unit in ['schubert-nk-api.service','schubert-nk-web.service','caddy.service']:
  v=dict(r.split('=',1) for r in subprocess.check_output(['systemctl','show',unit,'--property=MainPID,ControlPID,Job'],text=True).splitlines());assert v=={'MainPID':'0','ControlPID':'0','Job':''}
stopped_ui()
base=pathlib.Path('/var/lib/pgpt-s1-preservation/pg478-newrun-preflight-v2');old=json.loads((base/'before.private.json').read_text());expected=json.loads((base/'cleanup-oracle.private.json').read_text())
sql="begin isolation level repeatable read read only;set local timezone='UTC';"
for table in old['rows']:sql+="select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb)) from (select to_jsonb(t) j from "+table+" t) q;"
sql+='commit;';raw=subprocess.check_output(['sudo','-n','-u','postgres','psql','-X','-q','-A','-t','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql],timeout=30);assert len(raw)<=33554432
new={}
for row in raw.splitlines():
 d=json.loads(row);assert d['table'] not in new;new[d['table']]=d['rows']
env={};exec(compile(ORACLE,'<independent public full-row oracle>','exec'),env);summary=env['evaluate'](old['rows'],new,expected);stopped_ui()
root.mkdir(mode=0o700)
data={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':'bab704707b8fd7e0dc7581c4489f0892236efe73','run':'49437eda-1681-43a9-883a-424eb55a6166','cutoff':'2026-10-06T06:28:43.734078Z','rows':new,'summary':summary,'wholeParentAccepted':False,'generatedNewRowsAccepted':False}
with (root/'full-rows.private.json').open('x') as f:os.fchmod(f.fileno(),0o600);json.dump(data,f,sort_keys=True);f.flush();os.fsync(f.fileno())
fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
print(json.dumps({'all24IndependentSurvivorsEqual':True,'old411BatchPreserved':summary['schubert.batch_runs']['oldPreserved'],'authDeleted':summary['schubert.auth_sessions']['deleted'],'httpDeleted':summary['schubert_web_session.web_http_sessions']['deleted'],'inboxDeleted':summary['schubert.request_inbox']['deleted'],'newGeneratedRowsAccepted':False,'parentAccepted':False,'privateSnapshotSHA256':hashlib.sha256((root/'full-rows.private.json').read_bytes()).hexdigest()}))
'''
log=W/'pg481-cleanup-postcondition-v1.private.log';assert not log.exists()
run=subprocess.run(SSH+['sudo -n python3 -B -'],input=('ORACLE='+repr(oracle)+'\n'+PAYLOAD).encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with log.open('xb') as f:f.write(run.stdout);f.write(run.stderr)
print(run.stdout.decode(),end='');print('PG481_CLEANUP_POSTCONDITION actual='+str(run.returncode)+' rawExported=false');raise SystemExit(run.returncode)
