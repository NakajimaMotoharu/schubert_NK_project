"""SSC271 exact current runtime holder proof. Read-only, no reload/start/signal."""
import ast
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import SSH,W
from pg1559_pending_runtime_sources import refs,TOOLS
from pg1560_pending_runtime_compile import valid_frozen
import pg1498_retained_pair_readonly_proof as original

PID=105206
TICKS=3041121
CHILD=105232
CHILD_TICKS=3041209
SLOT='pg1564-retained-runtime-pair-proof-v1'

VALIDATE=r'''
runtime_changed=True
def validate_current(value):
 actual=dict(value);runtime=actual.pop('oneTimeRuntime')
 root=pathlib.Path('/run/systemd/system');directory=root/writer.UNIT;target=directory/writer.NAME
 require(set(runtime)=={str(root),str(directory),str(target)})
 require(runtime[str(root)]['metadata'][2:6]==[0,0,stat.S_IFDIR|0o755,3])
 require(runtime[str(directory)]['metadata'][2:6]==[0,0,stat.S_IFDIR|0o755,2])
 expected=writer.fixed_dropin(pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1544/systemd/schubert-nk-morning-controller.service').read_bytes(),pathlib.Path('/etc/systemd/system/schubert-nk-morning-controller.service.d/pg477-native-coverage.conf').read_bytes())
 require(writer.NAME=='zz-pg1160-once-resume.conf'and writer.RUN_ID=='15700a87-9117-4f63-a0ff-768dd604d0f1')
 require(runtime[str(target)]['metadata'][2:7]==[0,0,stat.S_IFREG|0o644,1,len(expected)]and runtime[str(target)]['sha256']==hashlib.sha256(expected).hexdigest())
 flags=os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC
 opened=[]
 try:
  for path in [root,directory,target]:
   fd=os.open(path,flags);opened.append(fd);s=os.fstat(fd)
   m=[s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
   require(m==runtime[str(path)]['metadata']and not os.listxattr(fd))
   if path==target:require(os.pread(fd,4097,0)==expected and os.pread(fd,1,len(expected))==b'')
   require(metadata(path)==m)
 finally:
  for fd in reversed(opened):os.close(fd)
 require(command(['findmnt','-n','-o','FSTYPE','--target',str(root)],4096).strip()==b'tmpfs')
 for unit,config in actual['configuration'].items():configuration_permitted(unit,config)
 actual['configuration']=profile_expected['configuration'];require(actual==profile_expected)
 for unit in UNITS:kernel_empty(unit)
'''

def payload():
    nodes=[]
    for node in ast.parse(refs()).body:
        if isinstance(node,ast.Try):break
        nodes.append(node)
    raw=ast.unparse(ast.Module(body=nodes,type_ignores=[])).replace('os.getppid()',str(PID)).replace('os.getpid()',str(CHILD))
    pre=original.PRE.replace('PG266-publication-recover','PG271-runtime-once')
    body=original.BODY
    for a,b in [('pg1498-retained-publication-pair-proof-v1',SLOT),('92297',str(PID)),('1431673',str(TICKS)),('92323',str(CHILD)),('pg1493-publication-only-tools-v2',TOOLS),('pg1493_publication_recovery_refs.py','pg1559_pending_runtime_refs.py')]:body=body.replace(a,b)
    return "import sys\nsys.path.insert(0,'/var/lib/pgpt-s1-preservation/"+TOOLS+"')\n"+pre+raw+'\n'+VALIDATE+'\n'+body

def main():
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700)
    begin=json.loads((W/'pg1562-pending-runtime-v1/begin.safe.json').read_bytes());args=begin['command'];expected=args[args.index('/opt/jdk-25.0.4/bin/java'):]
    fixed=json.loads((W/'pg1560-pending-runtime-frozen-v2.safe.json').read_bytes())
    if not valid_frozen(fixed)or fixed['operatorSource']!='72e34dbd833fcc845c2700d3af111d0b9876b161':raise ValueError('actual still-owned frozen source required')
    raw='EXPECTED_ARGS='+repr(expected)+'\nFROZEN_HASHES='+repr(fixed['fileHashes'])+'\nCHILD_TICKS='+str(CHILD_TICKS)+'\n'+payload();compile(raw,'<current runtime holder readonly proof>','exec')
    (out/'payload.private.py').write_text(raw)
    result=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw.encode(),capture_output=True,timeout=90)
    (out/'stderr.private.log').write_bytes(result.stderr)
    safe={'actualExit':result.returncode,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'signals0':True,'formalAccepted':False}
    if result.returncode==0:safe['guest']=json.loads(result.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(safe));return result.returncode

if __name__=='__main__':raise SystemExit(main())
