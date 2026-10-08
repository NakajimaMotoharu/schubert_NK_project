"""SSC222: only PG549 v4 pre-SAVE fixed pair; old UNKNOWN and all raw retained."""
import hashlib
import json
import os
import pathlib
import signal
import stat
import sys
import time
import dbus
from pg543_runtime_readback import load, require
from pg543_retirement_contract import old_peer_state

PID=576780
CHILD=576809
BOOT='cc9ed874-7f4f-450e-a188-8de1e42c8441'
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg551-completed-ref-handoff-v1')
EXPECTED={PID:(4161990,576778,'3be3de301dcbd99e087eae25622d42718f1d167ae96db6cbb353c592342aedcc'),CHILD:(4162106,PID,'48093440b74bdf9b4ed0808a61d6526904a468331bb422b5e2844aa79d660e73')}
LOCKS={'maintenance.lock':1997,'startup-admission.lock':1998}
phase='BOTH'


OLD=pathlib.Path('/var/lib/pgpt-s1-preservation/pg543-runtime-retirement-v2')
TOOLS=pathlib.Path('/var/lib/pgpt-s1-preservation/pg549-completed-tools-v4')
PINS={"Pg549CompletedDeployment.class":"167486794e2c1b33bf72de9762fbbc471bbafe041b15d357f14a87ed9739fa0e","Pg549CompletedDeployment$References.class":"798cf7f2bcfc8f20c40da0b1ebae2240b7a678c24b9555231ad8653cbf5432bb","pg542_current_contract.py":"32cdd48d0e68202340a796008310662b39845278dbe71d0cb4c3687d2fd9a312","pg543_retirement_contract.py":"c2b3fe88ce6934eb5ced5254b7ea9d1f40c931a58eb58098adc0e90e7abc6176","pg543_runtime_readback.py":"1b2be1929d4b886dd8513fc8771315641031e79708375cd3defdc079db9277da","pg549_completed_refs.py":"9b4bfd3225e7e5883110f76c2ff4e64a1ad1f7c6df463d3ff9be8f8f0a051177","pg549_completed_contract.py":"98cbf95ab403ebe30d6d6fb8f04403759c38cbbc81bf4a6e2665b80cc06d177e"}
def authenticate_old(env):
    require({p.name for p in TOOLS.iterdir()}==set(PINS))
    for name,expected in PINS.items():require(hashlib.sha256(env['strict'](TOOLS/name,0o400,33554432)).hexdigest()==expected)
    proof=pathlib.Path('/var/lib/pgpt-s1-preservation/pg549-completed-verify-v4')
    require({p.name for p in proof.iterdir()}=={'refs-prepare.private.log'} and hashlib.sha256(env['strict'](proof/'refs-prepare.private.log',0o600,33554432)).hexdigest()=='8d8b373a0d1ebc4b92c17aae1f2132ee5f25db62907c87162c499bc5f7448da8')
    for release,digest in [('PG495','f6992c4de95477594987d2f10def06110d0c28cb6d4fd063da47bd0bab7e7d44'),('PG548','a224ea9cf421b06e7029b1f8845f2a7eb3d620b5ec2bdf90bfe64c731b99515b')]:
        r=pathlib.Path('/opt/schubert-nk/releases/0.1.0-'+release);raw=(r/'RELEASE-MANIFEST.json').read_bytes()
        require(hashlib.sha256(raw).hexdigest()==digest)
        data=json.loads(raw);require(len(data['artifacts'])==187 and data['versions']['schema']=='028')
        for a in data['artifacts']:
            p=r/a['path'];metadata=env['metadata'](p);require(metadata[2:4]==[0,986] and metadata[5]==1 and metadata[6]==a['size'] and hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256'] and metadata==env['metadata'](p))
        env['command'](['/usr/bin/openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-in',str(r/'RELEASE-MANIFEST.json'),'-sigfile','/var/lib/pgpt-s1-preservation/'+release.lower()+'-manifest.sig'],4096)

def peer(env):
    identity="a.usename='schubert_batch' and a.application_name='PG549-completed-codeonly' and a.state='idle in transaction' and exists(select 1 from pg_locks l where l.pid=a.pid and l.locktype='advisory' and l.classid=0 and l.objid=71419602 and l.objsubid=1 and l.mode='ExclusiveLock' and l.granted)"
    q="select count(*)from pg_stat_activity where pid=576807;select count(*)from pg_stat_activity a where a.pid=576807 and a.datname='schubert_nk' and "+identity+";select count(*)from pg_stat_activity where datname='schubert_nk' and backend_type='client backend' and pid not in(576807,pg_backend_pid());select count(*)from pg_locks where locktype='advisory' and classid=0 and objid=71419602 and objsubid=1 and granted;select exists(select 1 from pg_roles where rolname='schubert_batch' and 'idle_in_transaction_session_timeout=60s'=any(rolconfig));"
    actual=env['command'](['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q],4096).splitlines()
    require(len(actual)==5 and actual[4]in(b't',b'f'))
    return old_peer_state(actual[:4],phase=='NONE',actual[4]==b't')

def process(pid):
    p=pathlib.Path('/proc',str(pid))
    a=(p/'stat').read_text().rpartition(')')[2].split()
    value={'pid':pid,'ticks':int(a[19]),'parent':int(a[1]),
           'argv':hashlib.sha256((p/'cmdline').read_bytes()).hexdigest(),
           'uid':(p/'status').read_text().split('Uid:')[1].splitlines()[0].split(),
           'children':{int(c) for t in (p/'task').iterdir() for c in (t/'children').read_text().split()}}
    require(value['ticks']==int((p/'stat').read_text().rpartition(')')[2].split()[19]))
    return value


def identity(value,pid,ticks,argv,parent):
    return (isinstance(value,dict) and set(value)=={'pid','ticks','argv','uid','parent','children'}
            and type(value['pid']) is int and value['pid']==pid
            and type(value['ticks']) is int and value['ticks']==ticks
            and type(value['parent']) is int and value['parent']==parent
            and value['argv']==argv and value['uid']==['0']*4
            and isinstance(value['children'],set) and all(type(c) is int and c>1 for c in value['children']))


def owner():
    require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
    if phase!='NONE':
        r=process(PID);ticks,parent,argv=EXPECTED[PID]
        require(identity(r,PID,ticks,argv,parent) and r['children']==({CHILD} if phase=='BOTH' else set()))
        if phase=='BOTH':
            c=process(CHILD);ticks,parent,argv=EXPECTED[CHILD]
            require(identity(c,CHILD,ticks,argv,parent) and not c['children'])
        else:require(not pathlib.Path('/proc',str(CHILD)).exists())
        targets={str(fd.readlink()) for fd in pathlib.Path('/proc',str(PID),'fd').iterdir()}
    else:
        require(not any(pathlib.Path('/proc',str(p)).exists() for p in EXPECTED))
        targets=set()
    raw=pathlib.Path('/proc/locks').read_text().splitlines()
    for name,inode in LOCKS.items():
        p=pathlib.Path('/run/schubert-nk')/name;s=p.lstat()
        require((os.major(s.st_dev),os.minor(s.st_dev),s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size)==(0,28,inode,0,0,stat.S_IFREG|0o600,1,0))
        hits=[]
        for line in raw:
            f=line.split()
            if len(f)>=8 and f[1]=='FLOCK':
                dev=f[5].split(':')
                if tuple(int(x,16)for x in dev[:2])+(int(dev[2]),)==(0,28,inode):hits.append(f)
        if phase=='NONE':require(not hits)
        else:require(str(p) in targets and len(hits)==1 and hits[0][1:5]==['FLOCK','ADVISORY','WRITE',str(PID)])
    return BOOT,PID,CHILD


def save(name,value):
    with (SAVE/name).open('x')as f:
        os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    os.fsync(fd);os.close(fd)


def wait_gone(pid):
    deadline=time.monotonic()+15
    while pathlib.Path('/proc',str(pid)).exists() and time.monotonic()<deadline:time.sleep(.01)
    require(not pathlib.Path('/proc',str(pid)).exists())


def execute(perform):
    global phase
    require(os.geteuid()==0 and type(perform)is bool and not SAVE.exists())
    os.umask(0o077)
    old_boundary=json.loads((OLD/'boundaries.private.json').read_bytes())
    env,baseline,snapshot,*_=load(owner,post=True,caddy_before=old_boundary['caddyExecStartPre'])
    authenticate_old(env)
    bus=dbus.SystemBus(private=True)
    manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
    refs=[]
    for unit in env['UNITS']:manager.RefUnit(unit);refs.append(unit)
    peer(env);before=snapshot();require(all(before[k]==baseline[k]for k in before if k not in('configuration','runtime')) and before['runtime']is None and before==snapshot());peer(env)
    if perform:
        parentfd=os.pidfd_open(PID);childfd=os.pidfd_open(CHILD);owner()
        SAVE.mkdir(mode=0o700);save('before.private.json',before)
        save('term-reserved.private.json',{'child':CHILD,'java':PID,'onePairOnly':True,'oldCloseUNKNOWN':True})
        owner();signal.pidfd_send_signal(childfd,signal.SIGTERM);os.close(childfd);wait_gone(CHILD)
        phase='JAVA_ONLY';owner();peer(env);require(before==snapshot())
        signal.pidfd_send_signal(parentfd,signal.SIGTERM);os.close(parentfd);wait_gone(PID)
        phase='NONE';owner();peer(env);require(before==snapshot() and before==snapshot())
        save('after.private.json',snapshot())
    for unit in reversed(refs):manager.UnrefUnit(unit)
    bus.close()
    if perform:
        save('complete.private.json',{'fixedChildThenJavaTERM':True,'fullRawUnchangedTwice':True,
             'allNewReferencesNormallyClosed':True,'peerAdvisoryFlock0':True,'oldCloseUNKNOWN':True,
             'sourcesUnchanged':True,'businessActions0':True})
    print('PG551_RUNTIME_'+('HANDOFF'if perform else'PREFLIGHT')+' fullRawUnchangedTwice=true sourcesUnchanged=true runtimePreserved=true businessActions0=true oldCloseUNKNOWN=true')


if __name__=='__main__':
    require(sys.argv[1:] in (['preflight'],['execute']))
    try:execute(sys.argv[1]=='execute')
    except Exception as failure:
        import traceback
        print('PG551_UNKNOWN type='+type(failure).__name__,flush=True)
        for frame in traceback.extract_tb(failure.__traceback__):
            if 'pg551_' in frame.filename:print('PG551_FRAME method='+frame.name+' line='+str(frame.lineno),flush=True)
        if (SAVE/'term-reserved.private.json').exists():
            while True:time.sleep(1)
        raise SystemExit(1)
