"""Independent readonly seal after successful PG579, never reissues any stop."""
import hashlib
import json
import os
import pathlib
import subprocess

R=pathlib.Path(__file__).resolve().parent
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
PAYLOAD=r'''
import ast,datetime,dbus,hashlib,json,os,pathlib,re,stat,subprocess,sys,time
os.umask(0o077)
def require(value):
 if not value:raise ValueError('independent current terminal final refused')
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441')
base=pathlib.Path('/var/lib/pgpt-s1-preservation');root=base/'pg579-native-stop-v1'
def sealed(name,sha):
 p=root/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1);raw=p.read_bytes();require(p.lstat()==s and hashlib.sha256(raw).hexdigest()==sha);return raw
before=json.loads(sealed('before.private.json','3a302026f6fa536e745c627da360dc0fb9c3898941aff24a610319d80df1c232'));after=json.loads(sealed('after.private.json','cb5951e30fda2ef63f2691a24f302e46b8cffcff6c8345e69644672b9135eaf6'))
require(sealed('complete.private','8f31ba931b056ae9776855ac503403e9688eb34316873169eb20205aae3badae')==b'genuineParentDone=true\nallEightOwnedTerminal=true\nallNewScopesReturnedNormally=true\noriginalBackupStartupRowsPreserved=true\nstarts0=true\noldUnknownNormalized=false\n')
require(all(after[k]==before[k]for k in before if k not in ('units','configuration')))
raw=(base/'pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes();require(hashlib.sha256(raw).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7');parsed=ast.parse(raw)
names={'command','metadata','strict','show','tree','configuration_fields','kernel'}
constants=[n for n in parsed.body if isinstance(n,ast.Assign)and all(isinstance(t,ast.Name)and t.id in {'UNITS','FIELDS'}for t in n.targets)]
nodes=[n for n in parsed.body if isinstance(n,ast.FunctionDef)and n.name in names];require(len(constants)==2 and len(nodes)==7)
exec(compile(ast.Module(body=constants+nodes,type_ignores=[]),'<sealed terminal metadata>','exec'),globals())
for name,sha in HASHES.items():require(hashlib.sha256((base/'pg579-native-tools-v1'/name).read_bytes()).hexdigest()==sha)
receipt_rows=[json.loads(l)for l in sealed('parent.private.jsonl','f6a785436f14339073e98df92464afff240b087df3e93c316ccce47e351c3f58').splitlines()]
receipt=ast.parse(RECEIPT);defs=[n for n in receipt.body if isinstance(n,ast.FunctionDef)];assignments=[n for n in receipt.body if isinstance(n,ast.Assign)]
e={'datetime':datetime};exec(compile(ast.Module(body=assignments+defs,type_ignores=[]),'<strict current genuine parent>','exec'),e)
done_path=pathlib.Path('/var/lib/schubert-nk/maintenance/attempts/57f0e73d-d334-4882-9284-04246011da54.done');summary=e['completed'](receipt_rows,strict(done_path,0o600,141));require(summary['endMonotonicUs']==59234299969)
release=pathlib.Path('/opt/schubert-nk/current');manifest=(release/'RELEASE-MANIFEST.json').read_bytes()
require(str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG548'and hashlib.sha256(manifest).hexdigest()=='a224ea9cf421b06e7029b1f8845f2a7eb3d620b5ec2bdf90bfe64c731b99515b');data=json.loads(manifest)
require(data['source']['commit']=='969d8ded10c0bf5841d9e3a5c531e922caf4a24a'and len(data['artifacts'])==187)
for v in data['artifacts']:
 p=release/v['path'];require(p.stat().st_size==v['size']and hashlib.sha256(p.read_bytes()).hexdigest()==v['sha256'])
command(['openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-in',str(release/'RELEASE-MANIFEST.json'),'-sigfile',str(base/'pg548-manifest.sig')],4096)
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for u in UNITS:manager.RefUnit(u);refs.append(u)
 def snapshot():
  for u,v in after['units'].items():
   require(show(u,FIELDS)==v and v['MainPID']==v['ControlPID']=='0'and not v['Job']);kernel(u)
   require(show(u,configuration_fields())==after['configuration'][u])
  for k,p in [('startup','/run/schubert-nk/startup'),('originals','/var/lib/schubert-nk/maintenance'),('backup','/srv/schubert-nk/backup')]:require(tree(pathlib.Path(p))==after[k])
  require(not any(pathlib.Path('/proc',str(pid)).exists()for pid in (909808,1138681,1141157,1147348,950235)))
  q="begin isolation level repeatable read read only;set local timezone='UTC';";rows={}
  for t in after['rows']:
   require(re.fullmatch(r'schubert(?:_web_session)?\.[a-z_]+',t)is not None)
   q+="select json_build_object('table','"+t+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb))from(select to_jsonb(t)j from "+t+" t)q;"
  q+="select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;commit;"
  lines=command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q]).splitlines();require(len(lines)==26 and lines[-2:]==[b'0',b'0'])
  for line in lines[:-2]:
   v=json.loads(line);require(v['table']not in rows);rows[v['table']]=v['rows']
  require(rows==after['rows']and len(rows)==24)
  for name in ('maintenance.lock','startup-admission.lock'):
   s=(pathlib.Path('/run/schubert-nk')/name).lstat()
   for line in pathlib.Path('/proc/locks').read_text().splitlines():
    f=line.split()
    if len(f)>=8 and f[1]=='FLOCK':
     d=f[5].split(':');require((int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino))
  require(not os.path.lexists('/run/systemd/system/schubert-nk-morning-controller.service.d/pg492-once-resume.conf'))
  for name in ('backup-request','cleanup-request','expiry-request'):require(not list(pathlib.Path('/run/schubert-nk',name).iterdir()))
  return tree(pathlib.Path('/run/schubert-nk/pt-coverage'))
 native=snapshot();require(native==snapshot())
 proof={p.name:{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}for p in root.iterdir()if p.is_file()}
finally:
 for u in reversed(refs):manager.UnrefUnit(u)
 bus.close()
result={'actualExit':0,'run':'PG580-terminal-final-v1','productionSource':data['source']['commit'],'all24UnchangedTwice':True,'allTenUnitsKernelEmpty':True,'allActorGone':True,'allClientAdvisoryFlock0':True,'whole187SignedArtifactBytesVerified':True,'normalPG579NewScopesSealed':True,'normalNewMetadataScopes':True,'genuineCompletion':summary,'ownedExplicitStops':4,'eightTerminalReceipts':True,'nativeMetadataStableTwice':True,'nativePhysicalFiles':sum(p.endswith('.exec')for p in native),'proofHashes':proof,'toolHashes':HASHES,'startsStopsReloadsSqlWrites':0,'rawExported':False,'formalAccepted':False}
save=base/'pg580-terminal-final-v1';require(not os.path.lexists(save));save.mkdir(mode=0o700)
with(save/'result.safe.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
for p in (save,save.parent):
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps(result))
'''


def main():
    os.umask(0o077)
    assert (W/'pg579-native-stop-v1.exit').read_bytes()==b'0\n'
    assert not os.path.lexists(W/'pg580-terminal-final-v1.private.log')
    classes=W/'pg579-native-tools-v1';files={n:classes/n for n in ('Pg579NativeStop.class','Pg579NativeStop$References.class')}
    for n in ('pg579_native_refs.py','pg579_native_owned_stop.py','pg526_term_witness.py','pg526_native_term_witness.py','pg579_parent_receipt.py','pg579_durable.py'):files[n]=R/n
    hashes={n:hashlib.sha256(p.read_bytes()).hexdigest()for n,p in files.items()}
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    prefix='HASHES='+repr(hashes)+'\nRECEIPT='+repr((R/'pg579_parent_receipt.py').read_text())+'\n'
    result=subprocess.run(ssh,input=(prefix+PAYLOAD).encode(),capture_output=True,timeout=90)
    with(W/'pg580-terminal-final-v1.private.log').open('xb')as f:f.write(result.stderr);f.flush();os.fsync(f.fileno())
    with(W/'pg580-terminal-final-v1.exit').open('x')as f:f.write(str(result.returncode)+'\n')
    if result.returncode==0:
        safe=json.loads(result.stdout)
        with(W/'pg580-terminal-final-v1.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True)
    print(json.dumps({'actualExit':result.returncode,'rawExported':False,'privateLogSha256':hashlib.sha256((W/'pg580-terminal-final-v1.private.log').read_bytes()).hexdigest()}));raise SystemExit(result.returncode)


if __name__=='__main__':main()
