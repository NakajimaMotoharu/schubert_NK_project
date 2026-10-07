"""SSC216: only the pinned PG535 tool pair; old UNKNOWN retained, no business action."""
import hashlib
import json
import os
import pathlib
import signal
import stat
import sys
import time
import dbus
from pg536_bootstrap_readback import load, require

PID=567192
CHILD=567221
BOOT='cc9ed874-7f4f-450e-a188-8de1e42c8441'
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg536-bootstrap-owned-handoff-v1')
EXPECTED={PID:(2871934,567190,'4cc659cb2ca0264e69829c81b0cd9a40d46db1b4d05cb302e491eb9e72423ee4'),
          CHILD:(2872058,PID,'bf970c5edc115d47659136f86e4f008cd77a3eca541fc8a74455efe84ed2a48b')}
LOCKS={'maintenance.lock':1997,'startup-admission.lock':1998}
phase='BOTH'


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
    env,snapshot=load(owner)
    bus=dbus.SystemBus(private=True)
    manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
    refs=[]
    for unit in env['UNITS']:manager.RefUnit(unit);refs.append(unit)
    before=snapshot();require(before==snapshot())
    if perform:
        parentfd=os.pidfd_open(PID);childfd=os.pidfd_open(CHILD);owner()
        SAVE.mkdir(mode=0o700);save('before.private.json',before)
        save('term-reserved.private.json',{'child':CHILD,'java':PID,'onePairOnly':True,'oldCloseUNKNOWN':True})
        owner();signal.pidfd_send_signal(childfd,signal.SIGTERM);os.close(childfd);wait_gone(CHILD)
        phase='JAVA_ONLY';owner();require(before==snapshot())
        signal.pidfd_send_signal(parentfd,signal.SIGTERM);os.close(parentfd);wait_gone(PID)
        phase='NONE';owner();require(before==snapshot() and before==snapshot())
        save('after.private.json',snapshot())
    for unit in reversed(refs):manager.UnrefUnit(unit)
    bus.close()
    if perform:
        save('complete.private.json',{'fixedChildThenJavaTERM':True,'fullRawUnchangedTwice':True,
             'allNewReferencesNormallyClosed':True,'peerAdvisoryFlock0':True,'oldCloseUNKNOWN':True,
             'sourcesUnchanged':True,'businessActions0':True})
    print('PG536_BOOTSTRAP_'+('HANDOFF'if perform else'PREFLIGHT')+' fullRawUnchangedTwice=true sourcesUnchanged=true normal20Preserved=true businessActions0=true oldCloseUNKNOWN=true')


if __name__=='__main__':
    require(sys.argv[1:] in (['preflight'],['execute']))
    try:execute(sys.argv[1]=='execute')
    except Exception as failure:
        import traceback
        print('PG536_UNKNOWN type='+type(failure).__name__,flush=True)
        for frame in traceback.extract_tb(failure.__traceback__):
            if 'pg536_' in frame.filename:print('PG536_FRAME method='+frame.name+' line='+str(frame.lineno),flush=True)
        if (SAVE/'term-reserved.private.json').exists():
            while True:time.sleep(1)
        raise SystemExit(1)
