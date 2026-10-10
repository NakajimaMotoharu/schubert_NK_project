"""Capacity-safe cold working layer: original saved disk remains immutable backing.

This is a COW working checkpoint, not a standalone disaster-recovery backup.
Both original instance and older backing/snapshot stay intact, never reset/applied.
"""
import json
import os
import subprocess
from pg997_offline_preservation import DISK,VM,Q,ENV,digest,identity,idle,write_new

OUT=VM/'private/pg1000-cold-overlay-v1'
if __name__=='__main__':
    os.umask(0o077);idle();assert not OUT.exists();OUT.mkdir(mode=0o700)
    old=json.loads((VM/'private/pg997-offline-v2/begin.safe.json').read_bytes())
    source_id=identity(DISK);back=VM/'ubuntu-26.04-server-cloudimg-amd64.img';back_id=identity(back)
    assert old['sourceIdentity']==source_id and old['sourceSha256']==digest(DISK)
    assert old['backingIdentity']==back_id and old['backingSha256']==digest(back)
    layer=OUT/'active.qcow2'
    write_new(OUT/'begin.safe.json',{'run':'PG1000-cold-overlay-v1','sourceIdentity':source_id,
      'sourceSha256':old['sourceSha256'],'backingIdentity':back_id,'backingSha256':old['backingSha256'],
      'newWorkingDisk':str(layer),'originalDiskIsRetainedReadOnlyBacking':True,
      'standaloneBackup':False,'formalAccepted':False})
    with (OUT/'create.private.log').open('xb') as f:
        r=subprocess.run([str(Q),'create','-f','qcow2','-F','qcow2','-b',str(DISK),str(layer)],env=ENV,stdout=f,stderr=f)
    assert r.returncode==0
    with (OUT/'compare.private.log').open('xb') as f:
        c=subprocess.run([str(Q),'compare','-f','qcow2','-F','qcow2',str(DISK),str(layer)],env=ENV,stdout=f,stderr=f)
    assert c.returncode==0 and source_id==identity(DISK) and back_id==identity(back)
    info=json.loads(subprocess.check_output([str(Q),'info','--output=json',str(layer)],env=ENV))
    assert info['full-backing-filename']==str(DISK) and info['virtual-size']==40*1024**3
    write_new(OUT/'manifest.safe.json',{'run':'PG1000-cold-overlay-v1','actualExit':0,
      'createExit':r.returncode,'logicalCompareExit':c.returncode,'originalDiskUnchanged':True,
      'originalInternalSnapshotPreserved':True,'standaloneBackup':False,
      'workingDisk':str(layer),'workingDiskBeforeSha256':digest(layer),'workingDiskBytes':layer.stat().st_size,
      'sourceIdentity':source_id,'sourceSha256':old['sourceSha256'],'backingIdentity':back_id,
      'backingSha256':old['backingSha256'],'formalAccepted':False,'businessActions':0})
    print(json.dumps({'run':'PG1000-cold-overlay-v1','actualExit':0,'logicalCompareExit':0,
      'workingDiskBytes':layer.stat().st_size,'originalDiskUnchanged':True,'businessActions':0}))
