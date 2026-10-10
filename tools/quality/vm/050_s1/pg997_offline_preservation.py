"""Offline logical disk preservation with bounded space, before isolated boot.

The original qcow2/backing chain and internal snapshot are never modified.
A compressed overlay with retained backing is NOT claimed byte-identical qcow2.
"""
import datetime
import fcntl
import hashlib
import json
import os
import resource
import subprocess
from pathlib import Path

VM=Path('/home/mini/codex/project1/work/pgpt-vm')
Q=Path('/home/mini/codex/project1/work/toolchain/qemu/root/usr/bin/qemu-img')
OUT=VM/'private/pg997-offline-v2'
DISK=VM/'instance.qcow2'
ENV={**os.environ,'LD_LIBRARY_PATH':'/home/mini/codex/project1/work/toolchain/qemu/root/usr/lib/x86_64-linux-gnu'}

def identity(p):
    s=p.stat();return [s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns]

def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        while b:=f.read(8*1024*1024):h.update(b)
    return h.hexdigest()

def idle():
    names=subprocess.check_output(['ps','-eo','comm='],text=True).splitlines()
    assert not any(x.strip().startswith('qemu-system') for x in names)
    assert not subprocess.check_output(['ss','-H','-lnt','( sport = :22222 )'])
    r=subprocess.run(['lsof','-t',str(DISK)],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
    assert r.returncode==1 and r.stdout==b''

def file_limit():
    resource.setrlimit(resource.RLIMIT_FSIZE,(5*1024**3,5*1024**3))

def write_new(path, record):
    with path.open('x') as f:
        json.dump(record,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)

def qualified(convert_exit,compare_exit,before,after,back_before,back_after):
    return (type(convert_exit)is int and convert_exit==0 and type(compare_exit)is int and compare_exit==0
      and all(isinstance(v,list)and len(v)==5 and all(type(n)is int and n>=0 for n in v)
              for v in [before,after,back_before,back_after])
      and before==after and back_before==back_after)

def run_step(args,log,phase,preexec=None):
    try:
        with log.open('xb') as stream:
            return subprocess.run(args,env=ENV,stdout=stream,stderr=stream,preexec_fn=preexec)
    except Exception as failure:
        write_new(log.parent/'failure.safe.json',{'actualExit':1,'convertExit':None,'compareExit':None,
          'phase':phase,'exceptionType':type(failure).__name__,'partialAccepted':False,'businessActions':0})
        raise

def main():
    os.umask(0o077)
    with (VM/'private/pg997-boot-guard.lock').open('a') as guard:
        fcntl.flock(guard,fcntl.LOCK_EX|fcntl.LOCK_NB);idle()
        assert not OUT.exists()
        assert os.statvfs(VM).f_bavail*os.statvfs(VM).f_frsize>6*1024**3
        OUT.mkdir(mode=0o700)
        before=identity(DISK);back=VM/'ubuntu-26.04-server-cloudimg-amd64.img';back_id=identity(back)
        source_hash=digest(DISK);back_hash=digest(back)
        info=json.loads(subprocess.check_output([str(Q),'info','--output=json',str(DISK)],env=ENV))
        assert info['format']=='qcow2' and info['virtual-size']==40*1024**3 and not info['dirty-flag']
        assert info['full-backing-filename']==str(back)
        write_new(OUT/'begin.safe.json',{'run':'PG997-offline-v2','sourceIdentity':before,
          'sourceSha256':source_hash,'backingIdentity':back_id,'backingSha256':back_hash,
          'timeUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'hostPid':os.getpid(),
          'copyMode':'compressed overlay with retained immutable backing; original internal snapshots not removed',
          'convertExit':None,'compareExit':None,'formalAccepted':False})
        copy=OUT/'checkpoint-compressed.qcow2'
        r=run_step([str(Q),'convert','-c','-f','qcow2','-O','qcow2',
                 '-B',str(back),'-F','qcow2',str(DISK),str(copy)],
                 OUT/'convert.private.log','CONVERT',file_limit)
        write_new(OUT/'convert.safe.json',{'convertExit':r.returncode,'sourceIdentity':identity(DISK),
          'backingIdentity':identity(back),'partialBytes':copy.stat().st_size if copy.exists() else None})
        if r.returncode!=0:
            write_new(OUT/'failure.safe.json',{'actualExit':1,'convertExit':r.returncode,'compareExit':None,
              'phase':'CONVERT','sourceStable':before==identity(DISK),'backingStable':back_id==identity(back),
              'partialAccepted':False,'businessActions':0});raise RuntimeError('offline copy not qualified')
        c=run_step([str(Q),'compare','-f','qcow2','-F','qcow2',str(DISK),str(copy)],OUT/'compare.private.log','COMPARE')
        if not qualified(r.returncode,c.returncode,before,identity(DISK),back_id,identity(back)):
            write_new(OUT/'failure.safe.json',{'actualExit':1,'convertExit':r.returncode,'compareExit':c.returncode,
              'phase':'COMPARE','sourceStable':before==identity(DISK),'backingStable':back_id==identity(back),
              'partialAccepted':False,'businessActions':0});raise RuntimeError('offline compare not qualified')
        idle()
        result={'run':'PG997-offline-v2','timeUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'sourceIdentity':before,'sourceSha256':source_hash,'backingIdentity':back_id,'backingSha256':back_hash,
          'copySha256':digest(copy),'copyBytes':copy.stat().st_size,'virtualBytes':info['virtual-size'],
          'qemuImgCompareExit':c.returncode,'convertExit':r.returncode,'sourceUnchanged':True,
          'qcowByteIdentical':False,'logicalGuestBytesIdentical':True,'oldInternalSnapshotPreservedInOriginal':True,
          'businessActions':0,'oldRunRestored':False,'privateCopy':str(copy),'requiresBacking':True,'formalAccepted':False}
        write_new(OUT/'manifest.safe.json',result)
        print(json.dumps({k:result[k] for k in ['run','copyBytes','qemuImgCompareExit','sourceUnchanged','logicalGuestBytesIdentical','businessActions']}))

if __name__=='__main__':main()
