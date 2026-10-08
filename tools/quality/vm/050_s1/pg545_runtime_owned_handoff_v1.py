"""SSC220: only the pinned PG543 tool pair; old UNKNOWN retained, no business action."""
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

PID=573159
CHILD=573188
BOOT='cc9ed874-7f4f-450e-a188-8de1e42c8441'
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg545-runtime-owned-handoff-v1')
EXPECTED={PID:(3787228,573157,'3884a575b13e0c6f347247c7fcb102e99128a4e5acf2572b69c46b6ab52b0ce2'),
          CHILD:(3787344,PID,'b3360a48a242b36cc73cf3df039824f40da49707478f9bda477b7001e335fe1e')}
LOCKS={'maintenance.lock':1997,'startup-admission.lock':1998}
phase='BOTH'


OLD=pathlib.Path('/var/lib/pgpt-s1-preservation/pg543-runtime-retirement-v2')
TOOLS=pathlib.Path('/var/lib/pgpt-s1-preservation/pg543-retirement-tools-v3')
PINS={"Pg543RuntimeRetirement$References.class":"cbfd73bbe7ffed2910344cce66f9864e014e8e3a094813fa91ab95fd7a995c8b","Pg543RuntimeRetirement.class":"a421a2ac79a6d9ea5c43cb6709318f8fd6d43bd5f7769e9c692b1f23a0a74342","pg542_current_contract.py":"32cdd48d0e68202340a796008310662b39845278dbe71d0cb4c3687d2fd9a312","pg543_retirement_contract.py":"cf5852442236c1d644ec7190ccb5b93bdebbe0c8d07f3ac6a712ee722a5abe8b","pg543_runtime_readback.py":"893d85907e3b40718c939e92fc778993697765172536741f1d213bd96dbbe1ac","pg543_runtime_retirement_refs.py":"aa04b0ddfdebe1e4afb15c9787c3add33ec7c1c4507557938c8f52c238f4179e"}
def authenticate_old(env):
    require({p.name for p in TOOLS.iterdir()}==set(PINS))
    for name,expected in PINS.items():
        p=TOOLS/name;require(hashlib.sha256(env['strict'](p,0o400,33554432)).hexdigest()==expected)
    oldpins={"runtime-before.private":"3992c3bcbe97066de238cb97678bb71537643bb598dd5b63a702b15d9e2e44e3","boundaries.private.json":"0e7fe76e884f918d936842d8bf887c03f816099a11a9a988d022720a13c43726","refs-prepare.private.log":"a8c3ee7da596b32f5d46a9dd149b485728fcff28633f42c1d00ef562af775120","before.private.json":"c34c058226c43e55b90ce3342a6b21cc74e6137a1a4084daaba7662ad04add59","retire-reserved.private.json":"7f00183f1e5902202a402138e59329e7abf0858a813b42d1da3ead87c99514a9"}
    require({p.name for p in OLD.iterdir()}==set(oldpins))
    for name,sha in oldpins.items():require(hashlib.sha256(env['strict'](OLD/name,0o600,33554432)).hexdigest()==sha)
    env['command'](['/usr/bin/openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-in','/opt/schubert-nk/releases/0.1.0-PG495/RELEASE-MANIFEST.json','-sigfile','/var/lib/pgpt-s1-preservation/pg495-manifest.sig'],4096)
def peer(env):
    identity="a.usename='schubert_batch' and a.application_name='PG543-runtime-retirement' and a.state='idle in transaction' and exists(select 1 from pg_locks l where l.pid=a.pid and l.locktype='advisory' and l.classid=0 and l.objid=71419602 and l.objsubid=1 and l.mode='ExclusiveLock' and l.granted)"
    q="select count(*)from pg_stat_activity where pid=573186;select count(*)from pg_stat_activity a where a.pid=573186 and a.datname='schubert_nk' and "+identity+";select count(*)from pg_stat_activity where datname='schubert_nk' and backend_type='client backend' and pid not in(573186,pg_backend_pid());select count(*)from pg_locks where locktype='advisory' and classid=0 and objid=71419602 and objsubid=1 and granted;select exists(select 1 from pg_roles where rolname='schubert_batch' and 'idle_in_transaction_session_timeout=60s'=any(rolconfig));"
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
    print('PG545_RUNTIME_'+('HANDOFF'if perform else'PREFLIGHT')+' fullRawUnchangedTwice=true sourcesUnchanged=true runtimePreserved=true businessActions0=true oldCloseUNKNOWN=true')


if __name__=='__main__':
    require(sys.argv[1:] in (['preflight'],['execute']))
    try:execute(sys.argv[1]=='execute')
    except Exception as failure:
        import traceback
        print('PG545_UNKNOWN type='+type(failure).__name__,flush=True)
        for frame in traceback.extract_tb(failure.__traceback__):
            if 'pg545_' in frame.filename:print('PG545_FRAME method='+frame.name+' line='+str(frame.lineno),flush=True)
        if (SAVE/'term-reserved.private.json').exists():
            while True:time.sleep(1)
        raise SystemExit(1)
