"""Actual BUG1165 failed-phase pair proof, never signal/service authority.

QA047/SS343353; immutable frozen helper inputs + full same-source original
seal, every current FD/OFD, sole locks and actual DB socket peer. No hotpatch.
"""
import inspect
import json
import pg1722_bootstrap_db_owner_readonly_proof as previous
import pg1770_next_day_full_warning_seal as whole
import pg1766_next_day_independent_candidates as transport
from pg1446_current_cold_stage import W
from pg1772_warning_owned_stop_sources import SOURCE,TOOLS

SLOT='pg1777-warning-retained-pair-readonly-v1'

CHILD=r'''
def ref_child(parent):
 p=pathlib.Path('/proc/476116');s=(p/'stat').read_text().rpartition(')')[2].split()
 require(int(s[1])==476087 and int(s[19])==8492565)
 argv=(p/'cmdline').read_bytes();require(argv==b'/usr/bin/python3\0-B\0/var/lib/pgpt-s1-preservation/pg1772-warning-owned-stop-tools-v1/pg1772_native_refs.py\0stop\0'+b'476114\0')
 status=dict(l.split(':',1)for l in(p/'status').read_text().splitlines()if ':'in l)
 require(status['Uid'].split()==status['Gid'].split()==['0']*4)
 require(not {c for t in(p/'task').iterdir()for c in(t/'children').read_text().split()})
 fds={f.name:{'metadata':metadata9(f.stat()),'target':os.readlink(f)}for f in(p/'fd').iterdir()};require(set(fds)=={'0','1','2','3'})
 for n in ['0','1']:require(fds[n]['target'].startswith('pipe:[')and sum(v['target']==fds[n]['target']for v in parent['fds'].values())==1)
 require(fds['2']['target']=='/var/lib/pgpt-s1-preservation/pg1772-native-stop-v1/refs-prepare.private.log'and fds['3']['target'].startswith('socket:['))
 diagnostic=pathlib.Path(fds['2']['target']).read_bytes();require(b'PG1772_FRAME method=capture_data line=58' in diagnostic and b'PG1772_READBACK_UNKNOWN type=ValueError'in diagnostic)
 daemon=dbus.Interface(bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus')
 names=[]
 for n in daemon.ListNames():
  if not str(n).startswith(':'):continue
  try:pid=int(daemon.GetConnectionUnixProcessID(n))
  except dbus.DBusException:continue
  if pid==476116:names.append(str(n))
 require(len(names)==1)
 return {'pid':476116,'ticks':8492565,'ppid':476087,'argvSha256':hashlib.sha256(argv).hexdigest(),'fds':fds,'busNames':names,'diagnosticSha256':hashlib.sha256(diagnostic).hexdigest()}
'''


def payload():
    frozen=json.loads((W/'pg1773-frozen-v1.safe.json').read_bytes())
    if frozen['actualExit']!=0 or frozen['productionSource']!=SOURCE:raise ValueError('frozen current ABI required')
    cp='/var/lib/pgpt-s1-preservation/'+TOOLS+':/opt/schubert-nk/releases/0.1.0-PG1638/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG1638/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG1638/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG1638/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
    argv=['/opt/jdk-25.0.4/bin/java','--enable-native-access=ALL-UNNAMED','-cp',cp,'Pg1772NativeStop','stop']
    actor=previous.ACTOR.replace('actor()', 'recovery_actor()')
    actor="def metadata9(s):return tuple(getattr(s,k)for k in ['st_dev','st_ino','st_uid','st_gid','st_mode','st_nlink','st_size','st_mtime_ns','st_ctime_ns'])\n"+actor
    for a,b in [('383695','476087'),('7281859','8492401'),('383693','476085'),('len(fds)==99','len(fds)==101'),('require(not children)','require(children=={476116})'),("'PG1719-bootstrap-guard'","'PG998-native-stop'")]:
        if a not in actor:raise ValueError('explicit actual pair binding boundary required')
        actor=actor.replace(a,b)
    raw=whole.payload()
    node=next(n for n in __import__('ast').parse(raw).body if isinstance(n,__import__('ast').Try)and any(isinstance(t,__import__('ast').Assign)and any(isinstance(x,__import__('ast').Name)and x.id=='current'for x in t.targets)for t in n.body))
    # Retain the original normal finally/unref/close boundary. No user slot operation.
    old=__import__('ast').get_source_segment(raw,node)
    body=r'''
try:
 for unit in UNITS:manager.LoadUnit(unit);manager.RefUnit(unit);refs.append(unit)
 current=capture()
 baseline_raw=(BASE/'pg1770-next-day-full-warning-seal-v1/before.private.json').read_bytes()
 require(hashlib.sha256(baseline_raw).hexdigest()=='b8ce2d5610f625bd6c2d27be466e843fc09fa239a7f779c8cb4711d718fb8ef9')
 require(current==json.loads(baseline_raw))
 for name,h in FROZEN.items():
  p=BASE/'pg1772-warning-owned-stop-tools-v1'/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and hashlib.sha256(p.read_bytes()).hexdigest()==h)
 failure=BASE/'pg1772-native-stop-v1';require({p.name for p in failure.iterdir()}=={'refs-prepare.private.log'})
 parent=recovery_actor();require(parent==recovery_actor());child=ref_child(parent);require(child==ref_child(parent));locks=[owned_lock(n)for n in ['maintenance.lock','startup-admission.lock']];peer=same_peer();require(peer==same_peer())
 require(parent==recovery_actor()and child==ref_child(parent))
 SAVE.mkdir(mode=0o700)
 value={'parent':parent,'child':child,'locks':locks,'peer':peer,'fullCurrent':current,'stopReservations0':True,'serviceStops0':True,'oldCloseUnknown':True,'source':SOURCE,'frozenHashes':FROZEN}
 with(SAVE/'proof.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(json.dumps(value,sort_keys=True).encode());f.flush();os.fsync(f.fileno())
finally:
 for unit in reversed(refs):manager.UnrefUnit(unit)
 bus.close()
'''
    raw=raw.replace(old,body)
    raw=raw[:raw.index("fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)")]+r'''
fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'productionSource':SOURCE,'proofSha256':hashlib.sha256((SAVE/'proof.private.json').read_bytes()).hexdigest(),'parentPid':476087,'parentTicks':8492401,'parentFdCount':101,'childPid':476116,'childTicks':8492565,'childFdCount':4,'samePeer':True,'backendPid':peer['activity']['pid'],'ownedLocks':2,'all24Config32Signed187AndOriginalBackupUnchanged':True,'stopReservations0':True,'serviceStops0':True,'signals0':True,'oldCloseUnknown':True,'observerRefsReturnedNormally':True,'formalAccepted':False}))
'''
    marker='bus=dbus.SystemBus(private=True);manager='
    at=raw.index(marker)
    raw=raw[:at]+actor+'\n'+CHILD+'\n'+raw[at:]
    raw=raw.replace('pg1770-next-day-full-warning-seal-v1',SLOT,1)
    raw='EXPECTED_ARGV='+repr(b'\0'.join(v.encode()for v in argv)+b'\0')+'\nFROZEN='+repr(frozen['fileHashes'])+'\n'+raw
    from pyflakes.api import check
    if check(raw,'<actual current retained pair proof>'):raise ValueError('all emitted globals required')
    compile(raw,'<fixed retained pair proof>','exec');return raw


def main():
    # Existing host exclusion remains with the failed1774. This is only its
    # diagnosed readonly observation, not a second manager/ordinary actor.
    raw=inspect.getsource(transport.main).replace('pg1766-next-day-independent-candidates-v1',SLOT)
    old="    with management_gate(P/'current-management-critical.lock'):\n        r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=90)"
    if raw.count(old)!=1:raise ValueError('one diagnosed readonly exclusion boundary required')
    raw=raw.replace(old,"    r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=90)")
    ns={**transport.__dict__,'payload':payload};exec(compile(raw,'<readonly failed-phase proof transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
