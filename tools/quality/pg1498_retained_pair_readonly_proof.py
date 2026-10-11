"""Current failed-before-stop exact Java/Ref read-only proof; no signal or authority replay."""
import ast
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import SSH,W
from pg1489_publication_recovery_sources import refs
from pg1493_publication_recovery_compile_v2 import remap

def payload():
    tree=ast.parse(remap(refs()));nodes=[]
    for n in tree.body:
        if isinstance(n,ast.Try):break
        if isinstance(n,ast.FunctionDef)and n.name in {'stop_one','save','kernel_scope'}:continue
        nodes.append(n)
    raw=ast.unparse(ast.Module(body=nodes,type_ignores=[])).replace('os.getppid()','92297').replace('os.getpid()','92323')
    return PRE+raw+'\n'+BODY

PRE=r'''
import sys,subprocess
q=subprocess.run(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',"begin read only;select pid from pg_stat_activity where usename='schubert_batch'and application_name='PG266-publication-recover';commit;"],capture_output=True,check=True)
assert len(q.stdout.splitlines())==1
sys.argv=['fixed-readonly-pair-proof','verify',q.stdout.decode().strip()]
'''

BODY=r'''
PAIR_SAVE=BASE/'pg1498-retained-publication-pair-proof-v1'
require(not os.path.lexists(PAIR_SAVE))
expected_args=EXPECTED_ARGS
frozen=FROZEN_HASHES
require(not any(SAVE.glob('*.stop-reserved.private'))and not any(SAVE.glob('*.stopped.private'))and not(SAVE/'complete.private').exists())
def process(pid,ticks,args):
 p=pathlib.Path('/proc')/str(pid);st=(p/'stat').read_text().rpartition(')')[2].split();require(int(st[19])==ticks)
 argv=(p/'cmdline').read_bytes();require(argv==b'\x00'.join(x.encode()for x in args)+b'\x00')
 status=dict(line.split(':',1)for line in(p/'status').read_text().splitlines()if ':'in line)
 require(status['Uid'].split()==status['Gid'].split()==['0']*4)
 fds={f.name:str(f.readlink())for f in(p/'fd').iterdir()}
 kids=sorted({int(x)for t in(p/'task').iterdir()for x in(t/'children').read_text().split()})
 return {'pid':pid,'ticks':ticks,'argvSha256':hashlib.sha256(argv).hexdigest(),'exe':str((p/'exe').readlink()),'cgroup':(p/'cgroup').read_text(),'fds':fds,'children':kids}
def pair():
 parent=process(92297,1431673,expected_args)
 child_path='/var/lib/pgpt-s1-preservation/pg1493-publication-only-tools-v2/pg1493_publication_recovery_refs.py'
 child=process(92323,CHILD_TICKS,['/usr/bin/python3','-B',child_path,'verify',str(BACKEND)])
 require(parent['exe']=='/opt/jdk-25.0.4/bin/java'and parent['children']==[92323]and child['children']==[])
 require(actor()['pid']==92297);peer_check()
 for name,digest in frozen.items():
  p=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1493-publication-only-tools-v2')/name;m=metadata(p)
  require(m[2:6]==[0,0,stat.S_IFREG|0o400,1]and hashlib.sha256(p.read_bytes()).hexdigest()==digest and metadata(p)==m)
 bus=dbus.SystemBus(private=True)
 try:
  daemon=dbus.Interface(bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus')
  names=[str(n)for n in daemon.ListNames()if str(n).startswith(':')and int(daemon.GetConnectionUnixProcessID(n))==92323]
  require(len(names)==1 and not any(str(n).startswith(':')and int(daemon.GetConnectionUnixProcessID(n))==92297 for n in daemon.ListNames()))
 finally:bus.close()
 parent['locks']=actor()['locks'];child['busNames']=names
 return {'parent':parent,'child':child,'backend':BACKEND}
first=snapshot();require(first==snapshot());validate_current(first);a=pair();b=pair();require(a==b)
PAIR_SAVE.mkdir(mode=0o700)
encoded=json.dumps({'pair':a,'current':first,'stopReservations0':True,'oldNormalCloseUnknown':True},sort_keys=True).encode()
with(PAIR_SAVE/'proof.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
fd=os.open(PAIR_SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'parentPid':92297,'childPid':92323,'sameActualMABackendAndSingleBus':True,'fullCurrentTwiceEqual':True,'proofSha256':hashlib.sha256(encoded).hexdigest(),'stopReservations0':True,'signals0':True,'formalAccepted':False}))
'''

def main():
    os.umask(0o077);out=W/'pg1498-retained-publication-pair-proof-v1';out.mkdir(mode=0o700)
    begin=json.loads((W/'pg1495-publication-recovery-once-v2/begin.safe.json').read_bytes())
    args=begin['command'];index=args.index('/opt/jdk-25.0.4/bin/java');expected=args[index:]
    fixed=json.loads((W/'pg1493-publication-recovery-frozen-v2.safe.json').read_bytes());assert fixed['actualExit']==0
    # Read exact child identity, then bind it into the independently verified full proof.
    r=subprocess.run(SSH+['sudo','-n','python3','-'],input=b"import pathlib;print(int(pathlib.Path('/proc/92323/stat').read_text().rpartition(')')[2].split()[19]))\n",capture_output=True,timeout=20)
    assert r.returncode==0 and r.stdout.strip().isdigit();ticks=int(r.stdout)
    raw='EXPECTED_ARGS='+repr(expected)+'\nFROZEN_HASHES='+repr(fixed['fileHashes'])+'\nCHILD_TICKS='+str(ticks)+'\n'+payload()
    (out/'payload.private.py').write_text(raw)
    r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw.encode(),capture_output=True,timeout=60)
    (out/'stderr.private.log').write_bytes(r.stderr)
    result={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'signals0':True,'formalAccepted':False}
    if r.returncode==0:result['guest']=json.loads(r.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(result));return r.returncode

if __name__=='__main__':raise SystemExit(main())
