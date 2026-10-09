"""Exact before-publication UNKNOWN835v2 Java+Ref handoff; no current/epoch/Unit mutation."""
import ast
import inspect
from pg836_fixed_handoff import payload as previous
import pg784_stopped_baseline as transport
ACTOR=r'''def actor(pid,ticks):
 assert(pid,ticks)in((3413229,16968012),(3413338,16968640));p=pathlib.Path('/proc')/str(pid)
 assert int((p/'stat').read_text().rpartition(')')[2].split()[19])==ticks
 argv=(p/'cmdline').read_bytes();wanted='611b1cc6153d1c2f2ed11b08be57d3c702a499168d1a5bc2791a4edfaef67f90'if pid==3413229 else'db1959cce3081a349bc392d7e646d9be1f43d2f661ed2c4968b386c73c6871b0'
 assert hashlib.sha256(argv).hexdigest()==wanted
 assert str((p/'exe').readlink())==('/opt/jdk-25.0.4/bin/java'if pid==3413229 else'/usr/bin/python3.14')
 status=dict(s.split(':',1)for s in(p/'status').read_text().splitlines()if ':'in s)
 assert status['Uid'].split()==status['Gid'].split()==['0']*4
 authority={k:status[k].strip()for k in('Uid','Gid','Groups','NoNewPrivs','CapInh','CapPrm','CapEff','CapBnd','CapAmb','PPid')}
 if pid==3413338:assert authority['PPid']in('3413229','1');authority['PPid']='3413229'
 return {'pid':pid,'ticks':ticks,'argvSha256':hashlib.sha256(argv).hexdigest(),'cgroup':(p/'cgroup').read_text(),'authority':authority}
'''
def payload():
    raw=previous().replace('pg836-pre-freeze-handoff-v1','pg838-reference-handoff-v1').replace('pg835-pending-tools-v1','pg835-pending-tools-v2')
    raw=raw.replace("assert not os.path.lexists(base/'pg835-pending-codeonly')", "assert os.path.lexists(base/'pg835-pending-codeonly-v2')and not os.path.lexists(base/'pg835-pending-codeonly-v2/complete.private')and not os.path.lexists(base/'pg835-pending-codeonly-v2/refs-before.private.json')")
    a=raw.index('def actor(');b=raw.index('def resources(',a);raw=raw[:a]+ACTOR+raw[b:]
    raw=raw.replace('3412116','3413229').replace('16855351','16968012')
    raw=raw.replace(".splitlines()==[b'0',b'0']", ".splitlines()==([b'1',b'1']if expect_owned else[b'0',b'0'])")
    raw=raw.replace('owner=actor(3413229,16968012);resources(True);','owner=actor(3413229,16968012);actor(3413338,16968640);resources(True);')
    marker="assert not pathlib.Path('/proc/3413229').exists();resources(False);"
    assert raw.count(marker)==1
    raw=raw.replace(marker,"assert not pathlib.Path('/proc/3413229').exists()\n if pathlib.Path('/proc/3413338').exists():terminate(3413338,16968640,actor,reserve,lambda pid:os.pidfd_open(pid,0),lambda fd:signal.pidfd_send_signal(fd,signal.SIGTERM,None,0),wait,os.close)\n deadline=time.monotonic()+15\n while pathlib.Path('/proc/3413338').exists()and time.monotonic()<deadline:time.sleep(.02)\n assert not pathlib.Path('/proc/3413338').exists();resources(False);")
    raw=raw.replace('knownPreDatabaseOwnerGone=true','knownBeforePublicationJavaAndRefGone=true').replace("'ownedJavaGone':True","'ownedJavaAndRefGone':True")
    ast.parse(raw);return raw
if __name__=='__main__':
    raw=inspect.getsource(transport.main).replace('pg784-stopped-current-v1','pg838-reference-handoff-v1')
    context={**transport.__dict__,'PAYLOAD':payload()}
    exec(compile(raw,'<838 fixed actual reference scope>', 'exec'),context);context['main']()
