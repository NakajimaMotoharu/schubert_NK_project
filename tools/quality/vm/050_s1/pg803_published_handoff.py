"""Fixed published-current UNKNOWN799-v2 handoff, no replay publication/start/DB mutation."""
import ast
import inspect
import pg784_stopped_baseline as transport
from pg782_owned_handoff import terminate
from pg801_guard_handoff import PAYLOAD as before_guard

def payload():
 raw=before_guard.replace('pg801-guard-handoff-v1','pg803-published-handoff-v1').replace('pg799-pending-tools-v1','pg799-pending-tools-v2').replace('0.1.0-PG750','0.1.0-PG796')
 raw=raw.replace("assert not os.path.lexists(base/'pg799-pending-codeonly')","assert os.path.lexists(base/'pg799-pending-codeonly-v2')and not os.path.lexists(base/'pg799-pending-codeonly-v2/complete.private')")
 start=raw.index('def actor(');end=raw.index('def resources(',start)
 raw=raw[:start]+r'''def actor(pid,ticks):
 assert(pid,ticks)in((3112993,15339690),(3113102,15340179));p=pathlib.Path('/proc')/str(pid)
 assert int((p/'stat').read_text().rpartition(')')[2].split()[19])==ticks
 argv=(p/'cmdline').read_bytes();a=argv.split(b'\0')
 if pid==3112993:
  assert str((p/'exe').readlink())=='/opt/jdk-25.0.4/bin/java'and a[-4:]==[b'Pg799PendingDeployment',b'102cdf1d365ab321f74b523237590eee764ae858',b'c48af3ada5e2f00b1704f65fdb4625d6220bed29b6cecbbd23d7354cf708880d',b'']
 else:assert a[:3]==[b'/usr/bin/python3',b'-B',b'/var/lib/pgpt-s1-preservation/pg799-pending-tools-v2/pg799_pending_refs.py']and a[-3:]==[b'102cdf1d365ab321f74b523237590eee764ae858',b'c48af3ada5e2f00b1704f65fdb4625d6220bed29b6cecbbd23d7354cf708880d',b'']
 status=dict(s.split(':',1)for s in(p/'status').read_text().splitlines()if ':'in s)
 assert status['Uid'].split()==status['Gid'].split()==['0']*4
 authority={k:status[k].strip()for k in('Uid','Gid','Groups','NoNewPrivs','CapInh','CapPrm','CapEff','CapBnd','CapAmb','PPid')}
 if pid==3113102:assert authority['PPid']in('3112993','1');authority['PPid']='3112993'
 return {'pid':pid,'ticks':ticks,'argvSha256':hashlib.sha256(argv).hexdigest(),'cgroup':(p/'cgroup').read_text(),'authority':authority}
'''+raw[end:]
 raw=raw.replace("'3112232'","'3112993'")
 raw=raw.replace("assert h.command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q]).splitlines()==[b'0',b'0']", "assert h.command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q]).splitlines()==([b'1',b'1']if expect_owned else[b'0',b'0'])")
 raw=raw.replace('owner=actor(3112232,15308543);resources(True);before=h.snapshot();assert before==h.snapshot()==h.baseline()[\'capturedSnapshot\']', "import pg799_pending_refs as publication\n old=json.loads((base/'pg799-pending-codeonly-v2/refs-before.private.json').read_bytes())\n owner=actor(3112993,15339690);actor(3113102,15340179);resources(True);before=h.snapshot();assert before==h.snapshot()\n assert before['rows']==old['rows']and before['configuration']==old['configuration']and publication.approval_only(old['trees'],before['trees'])\n assert pathlib.Path('/etc/schubert-nk/release-approval/current').read_bytes()==publication.NEW_APPROVAL\n assert pathlib.Path('/run/schubert-nk/startup/epoch.current').read_bytes()==(base/'pg799-pending-codeonly-v2/old-epoch.private').read_bytes()")
 raw=raw.replace('terminate(3112232,15308543,','terminate(3112993,15339690,').replace("pathlib.Path('/proc/3112232')","pathlib.Path('/proc/3112993')")
 marker='assert not pathlib.Path(\'/proc/3112993\').exists();resources(False);'
 assert raw.count(marker)==1
 raw=raw.replace(marker,"assert not pathlib.Path('/proc/3112993').exists()\n if pathlib.Path('/proc/3113102').exists():terminate(3113102,15340179,actor,reserve,lambda pid:os.pidfd_open(pid,0),lambda fd:signal.pidfd_send_signal(fd,signal.SIGTERM,None,0),wait,os.close)\n deadline=time.monotonic()+15\n while pathlib.Path('/proc/3113102').exists()and time.monotonic()<deadline:time.sleep(.02)\n assert not pathlib.Path('/proc/3113102').exists();resources(False);")
 raw=raw.replace('knownPreDatabaseOwnerGone=true','knownPublishedCurrentOwnerAndRefGone=true').replace("'ownedJavaGone':True","'ownedJavaAndRefGone':True")
 return inspect.getsource(terminate)+'\n'+raw

if __name__=='__main__':
 ast.parse(payload());raw=inspect.getsource(transport.main).replace('pg784-stopped-current-v1','pg803-published-handoff-v1');context={**transport.__dict__,'PAYLOAD':payload()}
 exec(compile(raw,'<803 published known owner handoff>', 'exec'),context);context['main']()
