"""SSC219: only the pinned PG543 tool pair; old UNKNOWN retained, no business action."""
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

PID=571379
CHILD=571408
BOOT='cc9ed874-7f4f-450e-a188-8de1e42c8441'
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg544-runtime-owned-handoff-v1')
EXPECTED={PID:(3670527,571377,'f46ba13d3123ce2dc770a48183351a81d262a143c9d667802ad1fd680cb4a7bd'),
          CHILD:(3670640,PID,'9fff6140014fb039d6b3d21efb5e4964bdc3d65ee9a40ba0e35193534474cffc')}
LOCKS={'maintenance.lock':1997,'startup-admission.lock':1998}
phase='BOTH'


OLD=pathlib.Path('/var/lib/pgpt-s1-preservation/pg543-runtime-readonly-v1')
TOOLS=pathlib.Path('/var/lib/pgpt-s1-preservation/pg543-retirement-tools-v2')
PINS={"Pg543RuntimeRetirement$References.class":"cbfd73bbe7ffed2910344cce66f9864e014e8e3a094813fa91ab95fd7a995c8b","Pg543RuntimeRetirement.class":"8c3910d1eb1d182bf9e858ee9bd2d0e26ccbd81c86ec8e8565dfe7669c60e476","pg542_current_contract.py":"32cdd48d0e68202340a796008310662b39845278dbe71d0cb4c3687d2fd9a312","pg543_retirement_contract.py":"2cf70aa895cd1c14d153d671c8f4921ad212ac6ce5e3ac155fd214d6f8beb963","pg543_runtime_readback.py":"769b08106726464165e0251f0dba80b0bde41311b31e5bcf3ce340b70109768b","pg543_runtime_retirement_refs.py":"beb3efab1e80f28a516f60e5e287fdd02e25db587998796ba9377b92ff8cef4d"}
def authenticate_old(env):
    require({p.name for p in TOOLS.iterdir()}==set(PINS))
    for name,expected in PINS.items():
        p=TOOLS/name;require(hashlib.sha256(env['strict'](p,0o400,33554432)).hexdigest()==expected)
    require({p.name for p in OLD.iterdir()}=={'refs-prepare.private.log'})
    require(hashlib.sha256(env['strict'](OLD/'refs-prepare.private.log',0o600,4096)).hexdigest()=='801010d902a17c87eb5eb664e2ffe556731bf92ec066582783169c01b0891376')
    env['command'](['/usr/bin/openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-in','/opt/schubert-nk/releases/0.1.0-PG495/RELEASE-MANIFEST.json','-sigfile','/var/lib/pgpt-s1-preservation/pg495-manifest.sig'],4096)
def peer(env):
    identity="a.usename='schubert_batch' and a.application_name='PG543-runtime-retirement' and a.state='idle in transaction' and exists(select 1 from pg_locks l where l.pid=a.pid and l.locktype='advisory' and l.classid=0 and l.objid=71419602 and l.objsubid=1 and l.mode='ExclusiveLock' and l.granted)"
    q="select count(*)from pg_stat_activity where pid=571406;select count(*)from pg_stat_activity a where a.pid=571406 and a.datname='schubert_nk' and "+identity+";select count(*)from pg_stat_activity where datname='schubert_nk' and backend_type='client backend' and pid not in(571406,pg_backend_pid());select count(*)from pg_locks where locktype='advisory' and classid=0 and objid=71419602 and objsubid=1 and granted;select exists(select 1 from pg_roles where rolname='schubert_batch' and 'idle_in_transaction_session_timeout=60s'=any(rolconfig));"
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
    env,baseline,snapshot,*_=load(owner)
    authenticate_old(env)
    bus=dbus.SystemBus(private=True)
    manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
    refs=[]
    for unit in env['UNITS']:manager.RefUnit(unit);refs.append(unit)
    peer(env);before=snapshot();require(before==baseline and before==snapshot());peer(env)
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
    print('PG544_BOOTSTRAP_'+('HANDOFF'if perform else'PREFLIGHT')+' fullRawUnchangedTwice=true sourcesUnchanged=true runtimePreserved=true businessActions0=true oldCloseUNKNOWN=true')


if __name__=='__main__':
    require(sys.argv[1:] in (['preflight'],['execute']))
    try:execute(sys.argv[1]=='execute')
    except Exception as failure:
        import traceback
        print('PG544_UNKNOWN type='+type(failure).__name__,flush=True)
        for frame in traceback.extract_tb(failure.__traceback__):
            if 'pg544_' in frame.filename:print('PG544_FRAME method='+frame.name+' line='+str(frame.lineno),flush=True)
        if (SAVE/'term-reserved.private.json').exists():
            while True:time.sleep(1)
        raise SystemExit(1)
