"""Authenticated retained894v2 Java plus its exact helper only; preserve unknown close."""
import ast
from pathlib import Path
R=Path(__file__).resolve().parent
CHILD='''
def child():
 p=pathlib.Path('/proc/3833804');require(int((p/'stat').read_text().rpartition(')')[2].split()[19])==18972277)
 argv=(p/'cmdline').read_bytes();require(hashlib.sha256(argv).hexdigest()=='50eaf29d7c66330634ef3f2ccbcda4b3e2eb5f78e3e999e0aff0ef27cd816c52'and str((p/'exe').readlink())=='/usr/bin/python3.14')
 status=dict(l.split(':',1)for l in(p/'status').read_text().splitlines()if ':'in l)
 require(status['Uid'].split()==status['Gid'].split()==['0']*4 and status['PPid'].strip()in('3833775','1'))
 require(not {int(c)for t in(p/'task').iterdir()for c in(t/'children').read_text().split()})
 return {'pid':3833804,'ticks':18972277,'argvSha256':hashlib.sha256(argv).hexdigest(),'cgroup':(p/'cgroup').read_text(),'authority':{k:status[k].strip()for k in ('Uid','Gid','Groups','NoNewPrivs','CapInh','CapPrm','CapEff','CapBnd','CapAmb')}}
'''
STOP_CHILD='''
  if pathlib.Path('/proc/3833804').exists():
   require(child()==captured['helper']);fd=os.pidfd_open(3833804,0)
   try:
    require(child()==captured['helper']);private('helper-term-reserved.private.json',json.dumps(captured['helper'],sort_keys=True).encode())
    signal.pidfd_send_signal(fd,signal.SIGTERM,None,0);poll=select.poll();poll.register(fd,select.POLLIN);require(bool(poll.poll(15000)))
   finally:os.close(fd)
  deadline=time.monotonic()+15
  while pathlib.Path('/proc/3833804').exists()and time.monotonic()<deadline:time.sleep(.02)
  require(not pathlib.Path('/proc/3833804').exists())
'''
def source():
 raw=(R/'pg896_owned_handoff.py').read_text()
 for a,b in [('3832792','3833775'),('18878511','18972120'),('96e095662d125eaaae97b38a94010cdee4cfce7ca8ab0f0d8ab2aee14fab7e7e','4f29110487f84b514123eb9616ad4d890b8e62d7d89fd8818ce63ed25d7cbfa9'),('pg894-bootstrap-tools-v1','pg894-bootstrap-tools-v2'),('pg894-bootstrap-verify-v1','pg894-bootstrap-verify-v2'),('pg894-frozen-v1','pg894-frozen-v2'),('pg896-handoff-','pg899-handoff-')]:raw=raw.replace(a,b)
 old="require(not {int(c)for t in(p/'task').iterdir()for c in(t/'children').read_text().split()})";assert raw.count(old)==1
 raw=raw.replace(old,"require({int(c)for t in(p/'task').iterdir()for c in(t/'children').read_text().split()}=={3833804})")
 raw=raw.replace('def locks(owned):',CHILD+'\ndef locks(owned):')
 raw=raw.replace('captured=actor()',"captured={'java':actor(),'helper':child()}")
 raw=raw.replace('actor()==captured',"{'java':actor(),'helper':child()}==captured")
 marker="require(not pathlib.Path('/proc/3833775').exists());OWNED=False;"
 assert raw.count(marker)==1
 # Insert into the generated payload string, retaining its original indentation.
 raw=raw.replace(marker,"require(not pathlib.Path('/proc/3833775').exists())\n"+STOP_CHILD+"  OWNED=False;")
 ast.parse(raw);return raw
if __name__=='__main__':
 exec(compile(source(),'<899 exact retained cohort>','exec'),{'__file__':str(R/'pg899_bootstrap_owned_handoff.py'),'__name__':'__main__'})
