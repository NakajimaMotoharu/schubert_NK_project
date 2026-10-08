"""Independent readonly seal of already completed PG570. No start/stop/restore."""
import datetime
import json
import os
import pathlib
import subprocess

W = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P = pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
PAYLOAD = r'''
import ast,datetime,hashlib,json,os,pathlib,re,stat,subprocess,sys,time
os.umask(0o077)
def require(v):
 if not v:raise ValueError('readonly Bootstrap final seal refused')
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441')
base=pathlib.Path('/var/lib/pgpt-s1-preservation')
raw=(base/'pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes()
require(hashlib.sha256(raw).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7')
parsed=ast.parse(raw);names={'command','metadata','strict','show','tree','configuration_fields','kernel'}
nodes=[n for n in parsed.body if isinstance(n,ast.FunctionDef)and n.name in names]
require(len(nodes)==len(names))
constants=[n for n in parsed.body if isinstance(n,ast.Assign)and all(isinstance(t,ast.Name)and t.id in {'UNITS','FIELDS'}for t in n.targets)]
require(len(constants)==2)
nodes=constants+nodes
exec(compile(ast.Module(body=nodes,type_ignores=[]),'<sealed readonly metadata>','exec'),globals())
proof=base/'pg570-bootstrap-existing-v1';verify=base/'pg570-bootstrap-verify-v1'
before=strict(proof/'before.private.json',0o600,33554432);after=strict(proof/'after.private.json',0o600,33554432)
require(hashlib.sha256(before).hexdigest()=='1d42516cf498d3ae58b5ba8a6253844676ed9162c588492f0cf78478a31ea2c6')
require(hashlib.sha256(after).hexdigest()=='8cd3195cc3a326ba4a2a84ba2cd5abe6e931bcd2131c2609c29983e9c85bd164')
b=json.loads(before);a=json.loads(after)
require(len(a['rows'])==24 and a['rows']==b['rows'])
require(strict(verify/'before.private.json',0o600,33554432)==strict(verify/'after.private.json',0o600,33554432))
for mode,root in [('verify',verify),('execute',proof)]:
 require(strict(root/'complete.private',0o600,4096)==('allNewScopesReturnedNormally=true\nall24DatabaseUnchanged=true\nmode='+mode+'\n').encode())
manifest=pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes()
require(hashlib.sha256(manifest).hexdigest()=='a224ea9cf421b06e7029b1f8845f2a7eb3d620b5ec2bdf90bfe64c731b99515b')
release=pathlib.Path('/opt/schubert-nk/current');require(str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG548')
data=json.loads(manifest);require(data['source']['commit']=='969d8ded10c0bf5841d9e3a5c531e922caf4a24a'and len(data['artifacts'])==187)
for entry in data['artifacts']:
 p=release/entry['path'];require(p.stat().st_size==entry['size']and hashlib.sha256(p.read_bytes()).hexdigest()==entry['sha256'])
command(['openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-in',str(release/'RELEASE-MANIFEST.json'),'-sigfile',str(base/'pg548-manifest.sig')],4096)
def snapshot():
 for u,v in a['units'].items():
  require(show(u,set(v))==v and v['MainPID']==v['ControlPID']=='0'and not v['Job']);kernel(u)
  require(show(u,configuration_fields())==a['configuration'][u])
 for name,path in [('startup','/run/schubert-nk/startup'),('originals','/var/lib/schubert-nk/maintenance'),('backup','/srv/schubert-nk/backup'),('native','/run/schubert-nk/pt-coverage'),('oldProofs','/var/lib/pgpt-s1-preservation/pg557-native-stop-v1'),('credentials','/etc/schubert-nk/credentials')]:require(tree(pathlib.Path(path))==a[name])
 q="begin isolation level repeatable read read only;set local timezone='UTC';";rows={}
 for t in a['rows']:
  require(re.fullmatch(r'schubert(?:_web_session)?\.[a-z_]+',t)is not None)
  q+="select json_build_object('table','"+t+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb))from(select to_jsonb(t)j from "+t+" t)q;"
 q+="select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;commit;"
 lines=command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q]).splitlines();require(len(lines)==26 and lines[-2:]==[b'0',b'0'])
 for line in lines[:-2]:
  v=json.loads(line);require(v['table']not in rows);rows[v['table']]=v['rows']
 require(rows==a['rows'])
 for n,path in {**{n:pathlib.Path('/run/schubert-nk')/n for n in ('backup-request','cleanup-request','expiry-request')},'runtime-parent':pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d')}.items():
  require({'metadata':metadata(path),'entries':sorted(p.name for p in path.iterdir()),'xattrs':os.listxattr(path)}==a['namespace'][n])
 require(not os.path.lexists('/run/systemd/system/schubert-nk-morning-controller.service.d/pg492-once-resume.conf'))
 for name in ('bootstrap-admin-username','bootstrap-admin-password'):require(not os.path.lexists('/etc/schubert-nk/credentials/'+name))
 require(not os.path.lexists('/run/credentials/schubert-nk-bootstrap-admin.service'))
 for name in ('maintenance.lock','startup-admission.lock'):
  s=(pathlib.Path('/run/schubert-nk')/name).lstat()
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   f=line.split()
   if len(f)>=8 and f[1]=='FLOCK':
    d=f[5].split(':');require((int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino))
snapshot();snapshot()
def hashes(root):return {p.name:{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}for p in root.iterdir()if p.is_file()and not p.name.endswith('.retired.private')}
print(json.dumps({'actualExit':0,'run':'PG572-bootstrap-final-v1','productionSource':data['source']['commit'],'whole187SignedArtifactBytesVerified':True,'unchangedSnapshots':2,'tables':24,'units':10,'allClientAdvisoryFlock0':True,'allUnitKernel0':True,'retiredTwoSourceAbsent':True,'runtimeCredentialsAbsent':True,'verifyBeforeAfterEqual':True,'originalsBackupNativeCredentialsUnchanged':True,'verifyProofs':hashes(verify),'executeProofs':hashes(proof),'startsStopsReloadsSqlWrites':0,'rawExported':False,'formalAccepted':False}))
'''


def main():
    os.umask(0o077)
    ssh = ['ssh', '-i', str(P / 'vm-access'), '-oBatchMode=yes', '-oIdentitiesOnly=yes',
           '-oStrictHostKeyChecking=yes', '-oUserKnownHostsFile=' + str(P / 'known_hosts'),
           '-p', '22222', 'ubuntu@127.0.0.1', 'sudo -n python3 -B -']
    for suffix in ('private.log', 'exit', 'safe.json'):
        assert not os.path.lexists(W / ('pg572-bootstrap-final-v2.' + suffix))
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    result = subprocess.run(ssh, input=PAYLOAD.encode(), capture_output=True, timeout=90)
    with (W / 'pg572-bootstrap-final-v2.private.log').open('xb') as f:
        f.write(result.stderr); f.flush(); os.fsync(f.fileno())
    with (W / 'pg572-bootstrap-final-v2.exit').open('x') as f:
        f.write(str(result.returncode) + '\n')
    if result.returncode == 0:
        safe = json.loads(result.stdout)
        safe.update(run='PG572-bootstrap-final-v2', startedUTC=started, completedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
        with (W / 'pg572-bootstrap-final-v2.safe.json').open('x') as f:
            json.dump(safe, f, sort_keys=True); f.flush(); os.fsync(f.fileno())
    print(json.dumps({'actualExit': result.returncode, 'rawExported': False}))
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
