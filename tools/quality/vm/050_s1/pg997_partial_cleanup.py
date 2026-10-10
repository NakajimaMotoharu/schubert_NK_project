"""Dispose only this turn's bounded failed copy after durable failure metadata.
Original disk/backing/internal snapshots and prior preservation are untouched.
"""
import json
import os
import sys
from pathlib import Path
from pg997_offline_preservation import DISK, VM, digest, identity, idle
OUT=VM/'private/pg997-offline-v1'

if __name__=='__main__':
    if len(sys.argv)==2:
        assert sys.argv[1]=='v2';OUT=VM/'private/pg997-offline-v2'
    os.umask(0o077);idle()
    copy=OUT/'checkpoint-compressed.qcow2';log=OUT/'convert.private.log'
    assert not (OUT/'manifest.safe.json').exists() and not (OUT/'cleanup.safe.json').exists()
    if len(sys.argv)==2:
        failure=json.loads((OUT/'failure.safe.json').read_bytes())
        begin=json.loads((OUT/'begin.safe.json').read_bytes())
        assert failure['convertExit']!=0 and failure['sourceStable'] and failure['backingStable']
        assert begin['sourceIdentity']==identity(DISK) and begin['sourceSha256']==digest(DISK)
    else:assert not (OUT/'failure.safe.json').exists()
    meta=identity(copy)
    assert meta[2]==5*1024**3 and copy.is_file() and not copy.is_symlink()
    disk_before=identity(DISK)
    record={'run':OUT.name,'actualPythonExit':1,'actualConvertExit':failure['convertExit'] if len(sys.argv)==2 else None,
      'missingConvertExitReason':'BUG1003 process-local returncode lost before durable failure record',
      'partialIdentity':meta,'partialSha256':digest(copy),'logSha256':digest(log),
      'formalAccepted':False,'logicalCopyAccepted':False,'originalDiskIdentityAtCleanup':disk_before,
      'removeReason':'Task-created incomplete copy at file limit; reproducible from preserved original/backing; recover storage without deleting old preservation',
      'oldArtifactsRemoved':0,'guestActions':0}
    with (OUT/('cleanup.safe.json' if len(sys.argv)==2 else 'failure.safe.json')).open('x') as f:json.dump(record,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    assert identity(copy)==meta and identity(DISK)==disk_before
    copy.unlink()
    fd=os.open(OUT,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
    print('PG997_FAILED_PARTIAL_ONLY_REMOVED bytes=5368709120 originalAndBackingPreserved=true failureLogMetadataRetained=true')
