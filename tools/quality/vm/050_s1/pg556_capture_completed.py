"""Readonly same-source DONE snapshot for subsequent owned-stop binding; no operation authority."""
import hashlib,os,pathlib,subprocess
os.umask(0o077)
R=pathlib.Path(__file__).resolve().parent;W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
assert (W/'pg554-parent-observer-v1.exit').read_bytes()==b'0\n'
assert (W/'pg555-preui-v1.exit').read_bytes()==b'0\n'
ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1']
payload=r'''
import datetime,dbus,hashlib,importlib.util,json,os,pathlib,stat,subprocess
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
env={};exec(compile(RECEIPT,'<independent genuine parent>','exec'),env)
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg556-completed-readonly-v2');assert not root.exists()
pre=pathlib.Path('/var/lib/pgpt-s1-preservation/pg553-preflight-tools-v2/pg553_newrun_preflight.py')
spec=importlib.util.spec_from_file_location('sealed_preflight',pre);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
current=pathlib.Path('/opt/schubert-nk/current');raw=(current/'RELEASE-MANIFEST.json').read_bytes();assert current.readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG548') and hashlib.sha256(raw).hexdigest()==m.DIGEST and json.loads(raw)['source']['commit']==m.SOURCE
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for u in m.UNITS:manager.RefUnit(u);refs.append(u)
 fields='Id,LoadState,ActiveState,SubState,Job,MainPID,ControlPID,InvocationID,Type,Restart,RemainAfterExit,Result,ExecMainCode,ExecMainStatus,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic,KillMode,SendSIGKILL'
 def show(u):
  out=m.command(['/usr/bin/systemctl','show',u,'--property='+fields]);value=dict(s.split('=',1)for s in out.decode().splitlines());assert set(value)==set(fields.split(','))and value['Id']==u and value['LoadState']=='loaded';return value
 journal=m.command(['/usr/bin/journalctl','--boot='+env['BOOT'],'_PID=1','UNIT=schubert-nk-morning-controller.service','INVOCATION_ID='+env['INV'],'-o','json','--no-pager'])
 rows=[json.loads(s)for s in journal.splitlines()];done=pathlib.Path('/var/lib/schubert-nk/maintenance/attempts',env['ACT']+'.done').read_bytes();summary=env['completed'](rows,done)
 assert not pathlib.Path('/var/lib/schubert-nk/maintenance/active').exists()and not pathlib.Path('/proc/581443').exists()
 def snapshot():
  units={u:show(u)for u in m.UNITS};parent=units['schubert-nk-morning-controller.service'];assert parent['MainPID']==parent['ControlPID']=='0'and not parent['Job']and parent['ActiveState']=='inactive'and parent['SubState']=='dead'
  for u in ['schubert-nk-morning-controller.service','schubert-nk-bootstrap-admin.service']:
   for p in pathlib.Path('/sys/fs/cgroup/system.slice',u).glob('**/cgroup.procs'):assert not p.read_text().strip()
  data={};q="begin isolation level repeatable read read only;set local timezone='UTC';"
  for t in m.TABLES:q+="select json_build_object('table','"+t+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb))from(select to_jsonb(t)j from "+t+" t)q;"
  for line in m.command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q+'commit;']).splitlines():
   v=json.loads(line);assert v['table']not in data;data[v['table']]=v['rows']
  assert set(data)==set(m.TABLES)
  trees={k:m.tree(pathlib.Path(p))for k,p in {'startup':'/run/schubert-nk/startup','originals':'/var/lib/schubert-nk/maintenance','backup':'/srv/schubert-nk/backup','transfer':'/srv/schubert-nk/data/transfer'}.items()}
  return {'units':units,'rows':data,'trees':trees,'current':str(current.readlink()),'pid1':rows,'completionSha256':hashlib.sha256(done).hexdigest(),'source':m.SOURCE,'manifestSha256':m.DIGEST,'genuineCompletion':summary}
 before=snapshot();assert before==snapshot()
 preui=json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg555-preui-v1/full-rows.private.json').read_bytes());assert preui['source']==m.SOURCE and preui['run']==env['RUN']and preui['cutoff']==env['CUTOFF']
 survivor_env={};exec(compile(SURVIVORS,'<strict independent old column preservation>','exec'),survivor_env)
 before['appendOnlyRowsObservedNotAccepted']=survivor_env['survivors_preserved'](preui['rows'],before['rows'])
 before['preuiSurvivorsPreserved']=True;before['newGeneratedRowsAccepted']=False;before['authority']=False
 root.mkdir(mode=0o700)
 with(root/'before.private.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(before,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 for p in(root,root.parent):
  fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
finally:
 for u in reversed(refs):manager.UnrefUnit(u)
 bus.close()
with(root/'complete.private').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(b'readonlyDiagnostic=true\ngenuineParentDone=true\nallNewMetadataScopesReturnedNormally=true\noperationAuthority=false\n');f.flush();os.fsync(f.fileno())
fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
print(json.dumps({'genuineCompletion':summary,'sameSource':True,'preuiSurvivorsPreserved':True,'newGeneratedRowsAccepted':False,'metadataScopesNormal':True,'operationAuthority':False,'snapshotSha256':hashlib.sha256((root/'before.private.json').read_bytes()).hexdigest(),'completeSha256':hashlib.sha256((root/'complete.private').read_bytes()).hexdigest()}))
'''
log=W/'pg556-completed-readonly-v2.private.log';assert not log.exists()
with log.open('xb')as f:
 result=subprocess.run(ssh+['sudo -n python3 -B -'],input=('RECEIPT='+repr((R/'pg556_parent_receipt.py').read_text())+'\nSURVIVORS='+repr((R/'pg556_survivors.py').read_text())+'\n'+payload).encode(),stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
with(W/'pg556-completed-readonly-v2.exit').open('x')as f:f.write(str(result.returncode)+'\n')
print('PG556_COMPLETED_READONLY actualExit='+str(result.returncode)+' privateLogSha256='+hashlib.sha256(log.read_bytes()).hexdigest());raise SystemExit(result.returncode)
