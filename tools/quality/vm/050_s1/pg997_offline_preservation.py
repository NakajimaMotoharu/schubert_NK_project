"""Offline logical disk preservation with bounded space, before isolated boot.

The original qcow2/backing chain and internal snapshot are never modified.
A compressed standalone logical copy is NOT claimed byte-identical qcow2.
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
OUT=VM/'private/pg997-offline-v1'
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
        copy=OUT/'checkpoint-compressed.qcow2'
        with (OUT/'convert.private.log').open('xb') as log:
            r=subprocess.run([str(Q),'convert','-c','-f','qcow2','-O','qcow2',str(DISK),str(copy)],
                 env=ENV,stdout=log,stderr=log,preexec_fn=file_limit)
        assert r.returncode==0
        with (OUT/'compare.private.log').open('xb') as log:
            c=subprocess.run([str(Q),'compare','-f','qcow2','-F','qcow2',str(DISK),str(copy)],env=ENV,stdout=log,stderr=log)
        assert c.returncode==0 and before==identity(DISK) and back_id==identity(back)
        idle()
        result={'run':'PG997-offline-v1','timeUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'sourceIdentity':before,'sourceSha256':source_hash,'backingIdentity':back_id,'backingSha256':back_hash,
          'copySha256':digest(copy),'copyBytes':copy.stat().st_size,'virtualBytes':info['virtual-size'],
          'qemuImgCompareExit':c.returncode,'convertExit':r.returncode,'sourceUnchanged':True,
          'qcowByteIdentical':False,'logicalGuestBytesIdentical':True,'oldInternalSnapshotPreservedInOriginal':True,
          'businessActions':0,'oldRunRestored':False,'privateCopy':str(copy),'formalAccepted':False}
        with (OUT/'manifest.safe.json').open('x') as f:
            json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
        print(json.dumps({k:result[k] for k in ['run','copyBytes','qemuImgCompareExit','sourceUnchanged','logicalGuestBytesIdentical','businessActions']}))

if __name__=='__main__':main()
