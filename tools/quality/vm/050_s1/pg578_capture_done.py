"""Genuine new parent PID1 + durable originals, readonly ten metadata refs. No operation authority."""
import hashlib
import json
import os
import pathlib
import subprocess

R=pathlib.Path(__file__).resolve().parent
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
PAYLOAD=r'''
import ast,datetime,dbus,hashlib,importlib.util,json,os,pathlib,re,stat,subprocess
os.umask(0o077)
def require(value):
 if not value:raise ValueError('genuine new-parent readonly completion refused')
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441')
source='969d8ded10c0bf5841d9e3a5c531e922caf4a24a';run='b62b6984-ffc2-4c9d-aea9-e232d9d1ec9e'
fresh=pathlib.Path('/var/lib/pgpt-s1-preservation/pg573-fresh-parent-v2');raw=(fresh/'before.private.json').read_bytes();require(hashlib.sha256(raw).hexdigest()=='557ae9688c03162fe1962cd81d93eb9e4a70eb9acca998a02040afb96f0ec505');baseline=json.loads(raw)
issued=json.loads((fresh/'external-start-issued.private.json').read_bytes());require(issued['MainPID']=='909808'and issued['InvocationID']=='267003d6e12845dd8690cd9bd5afcad0'and issued['Job']=='76444'and issued['ExecMainStartTimestampMonotonic']=='57679957905')
pre=pathlib.Path('/var/lib/pgpt-s1-preservation/pg553-preflight-tools-v2/pg553_newrun_preflight.py');require(hashlib.sha256(pre.read_bytes()).hexdigest()=='e4cad29a26fb9592bc5cf6615fec79dc97ea6e73c05d8375a79b1767b7855423')
spec=importlib.util.spec_from_file_location('sealed_preflight',pre);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def strict(p,limit):
 s=p.lstat();require(stat.S_ISREG(s.st_mode)and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1 and not os.listxattr(p));raw=p.read_bytes();require(0<len(raw)<=limit and p.lstat()==s);return raw
anchor=pathlib.Path('/var/lib/schubert-nk/maintenance/runs')/(run+'.run');anchor_raw=strict(anchor,72);require(len(anchor_raw)==72)
lines=anchor_raw.decode('ascii').splitlines();require(len(lines)==3 and lines[:2]==['NKRUN1',run]);cutoff=lines[2]
require(re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z',cutoff)is not None)
require(datetime.datetime.fromisoformat(baseline['bounds']['lower'])<=datetime.datetime.fromisoformat(cutoff.replace('Z','+00:00'))<=datetime.datetime.fromisoformat(baseline['bounds']['upper']))
attempts=pathlib.Path('/var/lib/schubert-nk/maintenance/attempts');matches=[]
for p in attempts.glob('*.begin'):
 b=strict(p,109);parts=b.decode('ascii').splitlines()
 if len(parts)==4 and parts[:3]==['NKACT1',run,cutoff]:
  require(len(b)==109 and p.name==parts[3]+'.begin'and re.fullmatch('[0-9a-f-]{36}',parts[3])is not None);matches.append(parts[3])
require(len(matches)==1);activation=matches[0];done_path=attempts/(activation+'.done');done=strict(done_path,141)
receipt_tree=ast.parse(RECEIPT);definitions=[n for n in receipt_tree.body if isinstance(n,ast.FunctionDef)]
env={'datetime':datetime,'BOOT':'cc9ed8747f4f450ea1888de1e42c8441','INV':issued['InvocationID'],'JOB':issued['Job'],'START':int(issued['ExecMainStartTimestampMonotonic']),'RUN':run,'CUTOFF':cutoff,'ACT':activation}
exec(compile(ast.Module(body=definitions,type_ignores=[]),'<unchanged strict genuine PID1 oracle/new literal cohort>','exec'),env)
journal=m.command(['journalctl','--boot='+env['BOOT'],'_PID=1','UNIT=schubert-nk-morning-controller.service','INVOCATION_ID='+env['INV'],'-o','json','--no-pager']);pid1=[json.loads(l)for l in journal.splitlines()];summary=env['completed'](pid1,done)
require(not os.path.lexists('/var/lib/schubert-nk/maintenance/active')and not pathlib.Path('/proc/909808').exists())
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for u in m.UNITS:manager.RefUnit(u);refs.append(u)
 fields='Id,LoadState,ActiveState,SubState,Job,MainPID,ControlPID,InvocationID,Type,Restart,RemainAfterExit,Result,ExecMainCode,ExecMainStatus,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic,KillMode,SendSIGKILL'
 def show(u):
  v=dict(l.split('=',1)for l in m.command(['systemctl','show',u,'--property='+fields]).decode().splitlines());require(set(v)==set(fields.split(','))and v['Id']==u and v['LoadState']=='loaded');return v
 def snapshot():
  units={u:show(u)for u in m.UNITS};parent=units['schubert-nk-morning-controller.service'];require(parent['MainPID']==parent['ControlPID']=='0'and not parent['Job']and parent['ActiveState']=='inactive'and parent['SubState']=='dead')
  for u in ('schubert-nk-morning-controller.service','schubert-nk-bootstrap-admin.service'):
   for p in pathlib.Path('/sys/fs/cgroup/system.slice',u).glob('**/cgroup.procs'):require(not p.read_text().strip())
  q="begin isolation level repeatable read read only;set local timezone='UTC';";data={}
  for t in m.TABLES:q+="select json_build_object('table','"+t+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb))from(select to_jsonb(t)j from "+t+" t)q;"
  for line in m.command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q+'commit;']).splitlines():
   v=json.loads(line);require(v['table']not in data);data[v['table']]=v['rows']
  require(set(data)==set(m.TABLES))
  trees={k:m.tree(pathlib.Path(p))for k,p in [('startup','/run/schubert-nk/startup'),('originals','/var/lib/schubert-nk/maintenance'),('backup','/srv/schubert-nk/backup'),('transfer','/srv/schubert-nk/data/transfer'),('native','/run/schubert-nk/pt-coverage')]}
  release=pathlib.Path('/opt/schubert-nk/current');manifest=(release/'RELEASE-MANIFEST.json').read_bytes();require(str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG548'and hashlib.sha256(manifest).hexdigest()=='a224ea9cf421b06e7029b1f8845f2a7eb3d620b5ec2bdf90bfe64c731b99515b'and json.loads(manifest)['source']['commit']==source)
  return {'units':units,'rows':data,'trees':trees,'source':source,'manifestSha256':hashlib.sha256(manifest).hexdigest(),'pid1':pid1,'genuineCompletion':summary,'completionSha256':hashlib.sha256(done).hexdigest(),'run':run,'cutoff':cutoff,'activation':activation,'current':str(release.readlink()),'authority':False}
 after=snapshot();require(after==snapshot()and strict(anchor,72)==anchor_raw and strict(done_path,141)==done)
 root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg578-completed-readonly-v1');require(not os.path.lexists(root));root.mkdir(mode=0o700)
 with(root/'before.private.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(after,f,sort_keys=True);f.flush();os.fsync(f.fileno())
finally:
 for u in reversed(refs):manager.UnrefUnit(u)
 bus.close()
with(root/'complete.private').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(b'readonlyDiagnostic=true\ngenuineParentDone=true\nallNewMetadataScopesReturnedNormally=true\noperationAuthority=false\n');f.flush();os.fsync(f.fileno())
fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'run':'PG578-completed-readonly-v1','productionSource':source,'genuineCompletion':summary,'batchRun':run,'cutoff':cutoff,'activation':activation,'beforeSha256':hashlib.sha256((root/'before.private.json').read_bytes()).hexdigest(),'completeSha256':hashlib.sha256((root/'complete.private').read_bytes()).hexdigest(),'metadataScopesNormal':True,'operationAuthority':False,'wholeFormalAccepted':False}))
'''


def main():
    os.umask(0o077)
    assert (W/'pg574-observer-v1.exit').read_bytes()==b'0\n'
    assert (W/'pg575-chr-a01-native-v1.exit').read_bytes()==b'0\n'and(W/'pg576-client-v1.exit').read_bytes()==b'0\n'
    assert not os.path.lexists(W/'pg578-completed-readonly-v1.private.log')
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    result=subprocess.run(ssh,input=('RECEIPT='+repr((R/'pg556_parent_receipt.py').read_text())+'\n'+PAYLOAD).encode(),capture_output=True,timeout=90)
    with(W/'pg578-completed-readonly-v1.private.log').open('xb')as f:f.write(result.stderr);f.flush();os.fsync(f.fileno())
    with(W/'pg578-completed-readonly-v1.exit').open('x')as f:f.write(str(result.returncode)+'\n')
    if result.returncode==0:
        safe=json.loads(result.stdout)
        with(W/'pg578-completed-readonly-v1.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True)
        print(json.dumps(safe))
    else:print(json.dumps({'actualExit':result.returncode,'privateLogSha256':hashlib.sha256((W/'pg578-completed-readonly-v1.private.log').read_bytes()).hexdigest()}))
    raise SystemExit(result.returncode)


if __name__=='__main__':main()
