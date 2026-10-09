"""Actual guest Python import closure before any Bootstrap owner/resource acquisition."""
import ast,datetime,hashlib,json,os,subprocess
from pathlib import Path
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
def payload(hashes):
 raw='''import hashlib,importlib,json,os,pathlib,stat,sys
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg894-bootstrap-tools-v2')
def validate():
 assert {p.name for p in root.iterdir()}==set(HASHES)|{'payload-sha256.json'}
 assert json.loads((root/'payload-sha256.json').read_bytes())==HASHES
 for name,digest in HASHES.items():
  p=root/name;s=p.lstat()
  assert stat.S_ISREG(s.st_mode)and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o400 and s.st_nlink==1
  assert hashlib.sha256(p.read_bytes()).hexdigest()==digest
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
validate();sys.path.insert(0,str(root));sys.dont_write_bytecode=True
modules=sorted(n[:-3]for n in HASHES if n.endswith('.py'))
for name in modules:importlib.import_module(name)
validate()
print(json.dumps({'actualExit':0,'modulesImported':modules,'resourceAcquisition0':True,'unitActions0':True,'sqlWrites0':True,'productionSource':'e01612fcd7f2752df5ae0836b78538fd5e87f120','formalAccepted':False}))
'''
 ast.parse(raw);return 'HASHES='+repr(hashes)+'\n'+raw
def main():
 os.umask(0o077);assert subprocess.check_output(['git','status','--porcelain'])==b''
 assert(W/'pg894-stage-v2.exit').read_bytes()==b'0\n'
 hashes=json.loads((W/'pg894-frozen-v2.safe.json').read_bytes())['fileHashes']
 base=W/'pg898-bootstrap-import-v1';assert not Path(str(base)+'.private.log').exists()
 ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
 start=datetime.datetime.now(datetime.timezone.utc);r=subprocess.run(ssh,input=payload(hashes).encode(),capture_output=True,timeout=30)
 with Path(str(base)+'.private.log').open('xb')as f:f.write(r.stderr);f.flush();os.fsync(f.fileno())
 with Path(str(base)+'.exit').open('x')as f:f.write(str(r.returncode)+'\n')
 safe={'actualExit':r.returncode,'startedUTC':start.isoformat(),'elapsedSeconds':(datetime.datetime.now(datetime.timezone.utc)-start).total_seconds(),'privateLogSha256':hashlib.sha256(r.stderr).hexdigest(),'formalAccepted':False}
 if r.returncode==0:safe.update(json.loads(r.stdout))
 with Path(str(base)+'.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True)
 print(json.dumps(safe));raise SystemExit(r.returncode)
if __name__=='__main__':main()
