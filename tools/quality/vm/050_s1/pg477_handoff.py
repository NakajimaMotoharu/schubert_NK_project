"""BUG764/SSC191: fixed already-stopped cohort; no service signal/start/namespace change.
Old Java TERM is interruption, never normal-close or old-tool success. Root-private proofs.
"""
import hashlib,json,os,pathlib,select,signal,stat,subprocess,sys,time
import dbus
sys.path.insert(0,'/var/lib/pgpt-s1-preservation/pg475-native-tools-v1')
from pg466_term_witness import FIELDS,unique
ROOT=pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-handoff')
PID=3409258;TICKS=21847391
BOOT='e07aa706-1acd-4e65-b309-d7f330f79d54'
CLASS='d9805f0f14bc1d916a815691733281635acbbcf54c7a0f1e02899910b8f7b75b'
ALL=['caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service','schubert-nk-morning-controller.service','schubert-nk-bootstrap-admin.service']
CP="/var/lib/pgpt-s1-preservation/pg477-handoff-tools-v1:/var/lib/pgpt-s1-preservation/pg475-readback-tools-v1:/var/lib/pgpt-s1-preservation/pg474-readback-tools-v1:/var/lib/pgpt-s1-preservation/pg473-readback-tools-v1:/var/lib/pgpt-s1-preservation/pg471-readback-tools-v3:/var/lib/pgpt-s1-preservation/pg471-completed-tools-v2:/var/lib/pgpt-s1-preservation/pg469-current-tools-v3:/var/lib/pgpt-s1-preservation/pg468-recovery-tools-v4:/var/lib/pgpt-s1-preservation/pg468-recovery-tools-v2:/var/lib/pgpt-s1-preservation/pg466-tool-v3:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v2:/var/lib/pgpt-s1-preservation/pg464-completed-readback-v7:/var/lib/pgpt-s1-preservation/pg464-code-tools-v2:/var/lib/pgpt-s1-preservation/pg461-known30-tool-v3:/var/lib/pgpt-s1-preservation/pg456-applied-tools-v7:/opt/schubert-nk/releases/0.1.0-PG475/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG475/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG475/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG475/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar"
def require(b):
    if not b:raise ValueError('fixed handoff refused')
def command(args,timeout=5,limit=4194304):
    result=subprocess.run(args,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=timeout)
    require(result.returncode==0 and len(result.stdout)<=limit);return result.stdout
def save(name,data):
    require('/' not in name);p=ROOT/name
    with p.open('xb') as f:os.fchmod(f.fileno(),0o600);f.write(data);f.flush();os.fsync(f.fileno())
def show(unit):
    require(unit in ALL);raw=command(['/usr/bin/systemctl','show',unit,'--property='+','.join(sorted(FIELDS))]).decode('ascii');values={}
    for line in raw.splitlines():
        k,v=line.split('=',1);require(k not in values);values[k]=v
    require(set(values)==FIELDS and values['Id']==unit and values['LoadState']=='loaded');return values
def tick(pid):return int((pathlib.Path('/proc')/str(pid)/'stat').read_text().rpartition(')')[2].split()[19])
def empty_kernel(unit):
    c=pathlib.Path('/sys/fs/cgroup/system.slice')/unit
    if c.exists():
        for p in [c,*[x for x in c.rglob('*') if x.is_dir()]]:
            require(not (p/'cgroup.procs').read_text().strip() and 'populated 0\n' in (p/'cgroup.events').read_text())
def holder():
    require(tick(PID)==TICKS)
    p=pathlib.Path('/proc')/str(PID);argv=(p/'cmdline').read_bytes().split(b'\0');require(argv[-3:]==[b'Pg477StoppedDeployment',b'verify',b''])
    require(argv[0]==b'/opt/jdk-25.0.4/bin/java' and len(argv)==7 and argv[1]==b'--enable-native-access=ALL-UNNAMED' and argv[2]==b'-cp')
    require(hashlib.sha256(pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-stopped-tools-v1/Pg477StoppedDeployment.class').read_bytes()).hexdigest()==CLASS)
    locks={};fd_targets={}
    for fd in (p/'fd').iterdir():
        try:target=str(fd.readlink())
        except FileNotFoundError:continue
        fd_targets[fd.name]=target
    raw=pathlib.Path('/proc/locks').read_text().splitlines()
    for name in ('maintenance.lock','startup-admission.lock'):
        target=pathlib.Path('/run/schubert-nk')/name;st=target.stat();require(st.st_uid==st.st_gid==0 and stat.S_IMODE(st.st_mode)==0o600 and st.st_nlink==1)
        require(str(target) in fd_targets.values());identity=(os.major(st.st_dev),os.minor(st.st_dev),st.st_ino)
        matches=[]
        for line in raw:
            fields=line.split()
            if len(fields)>=8 and fields[1:5]==['FLOCK','ADVISORY','WRITE',str(PID)]:
                device=fields[5].split(':')
                if len(device)==3 and (int(device[0],16),int(device[1],16),int(device[2]))==identity:matches.append(line)
        require(len(matches)==1);locks[name]=list(identity)
    # A logical JDBC object is not a proof of a live server session/advisory lease.
    database=command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-A','-t','-d','schubert_nk','-c',"select pid,usename,state,client_port from pg_catalog.pg_stat_activity where usename in ('schubert_batch','schubert_migration') order by pid"]).decode('ascii')
    return {'pid':PID,'startTicks':TICKS,'boot':BOOT,'classSha256':CLASS,'locks':locks,'observedOldDatabaseSessions':database,'oldCloseUnknown':True}
def all_terminal():
    first={unit:show(unit) for unit in ALL}
    for unit,v in first.items():
        require(v['MainPID']==v['ControlPID']=='0' and not v['Job'] and v['ActiveState'] in ('inactive','failed'));empty_kernel(unit)
    require(first=={unit:show(unit) for unit in ALL});return first

def readback(mode,label):
    p=ROOT/(label+'.private.log')
    with p.open('xb') as f:
        os.fchmod(f.fileno(),0o600)
        result=subprocess.run(['/opt/jdk-25.0.4/bin/java','--enable-native-access=ALL-UNNAMED','-cp',CP,'Pg477HandoffReadback',mode],stdin=subprocess.DEVNULL,stdout=f,stderr=f,timeout=90)
        f.flush();os.fsync(f.fileno())
    require(result.returncode==0 and p.stat().st_size<=1048576 and b'PG477_HANDOFF_READBACK allReadOnlyScopesReturnedNormally=true' in p.read_bytes())
def no_sessions():
    value=command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-A','-t','-d','schubert_nk','-c',"select count(*) from pg_catalog.pg_stat_activity where usename in ('schubert_batch','schubert_migration')"]).strip()
    require(value==b'0')
def interrupt_owned(original,states):
    readback('snapshot','before-term');no_sessions()
    require(holder()==original and all_terminal()==states)
    fd=os.pidfd_open(PID,0)
    try:
        require(holder()==original);save('term-request.private',json.dumps(original,sort_keys=True).encode())
        signal.pidfd_send_signal(fd,signal.SIGTERM,None,0)
        poll=select.poll();poll.register(fd,select.POLLIN);require(poll.poll(15000))
    finally:os.close(fd)
    end=time.monotonic()+15
    while (pathlib.Path('/proc')/str(PID)).exists() and time.monotonic()<end:time.sleep(.01)
    require(not (pathlib.Path('/proc')/str(PID)).exists())
    require(not any(line.split()[4:5]==[str(PID)] for line in pathlib.Path('/proc/locks').read_text().splitlines()))
    no_sessions();require(all_terminal()==states);readback('verify','after-term');no_sessions();require(all_terminal()==states)
    save('interrupted.private',b'interrupted=true\nexpectedExit143=true\noldCloseUnknown=true\noldActivated=false\noldPhysicalHolderAbsent=true\nnewOwnershipNotYetAcquired=true\n')

def main():
    require(os.geteuid()==0 and sys.argv[1:]==['terminate'])
    require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
    require(pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG475'))
    require(not ROOT.exists());ROOT.mkdir(mode=0o700)
    for target in ['timers.target','paths.target']:
        require(command(['/usr/bin/systemctl','show',target,'--property=LoadState']).strip()==b'LoadState=masked')
    original=holder();require(not original['observedOldDatabaseSessions'].strip())
    # No owned child remains: REF_RELEASED transport was followed by actual child exit0.
    children=(pathlib.Path('/proc')/str(PID)/'task'/str(PID)/'children').read_text().strip();require(not children)
    proof=json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-stopped-tools-v1/refs-verify-before.private.json').read_text(),object_pairs_hook=unique)
    bus=dbus.SystemBus(private=True)
    manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
    refs=[]
    try:
        for unit in ALL:manager.RefUnit(unit);refs.append(unit)
        states=all_terminal();require(states==proof['stopped'])
        save('holder-before.private.json',json.dumps(original,sort_keys=True).encode())
        save('unit-before.private.json',json.dumps(states,sort_keys=True).encode())
        interrupt_owned(original,states)
        for unit in reversed(refs):manager.UnrefUnit(unit)
        bus.close()
        print('PG477_HANDOFF oldToolInterrupted=true oldCloseNotInferred=true allTenStoppedPreserved=true currentUnchanged=true newOwnershipRequired=true',flush=True)
    except Exception:
        print('PG477_HANDOFF_UNKNOWN newStartIsolated=true senderRetained=true',file=sys.stderr,flush=True)
        while True:time.sleep(1)
if __name__=='__main__':main()
