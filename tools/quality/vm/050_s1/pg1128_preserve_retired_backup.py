"""Read-only original QCOW backing export of one legitimately retired bundle.

No VM/device/DB/current-backup changes; exactly five old entries pinned by PG1106.
Raw dump/config/credential contents stay private outside Git/model output.
"""
import datetime
import hashlib
import json
import os
import stat
import subprocess
from pathlib import Path
from dissect.hypervisor.disk.qcow2 import QCow2
from dissect.volume.disk import Disk
from dissect.extfs.extfs import ExtFS

P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
BASE=Path('/home/mini/codex/project1/work/pgpt-vm/instance.qcow2')
BACKING=Path('/home/mini/codex/project1/work/pgpt-vm/ubuntu-26.04-server-cloudimg-amd64.img')
OUT=P/'pg1128-retired-backup-v1'
OLD='/srv/schubert-nk/backup/20261009-063333-601297d0-a8ba-47da-852b-0ffeae409965'
NAMES={'MANIFEST.json','schubert_nk.dump','config.tar','credentials.tar.age'}


def identity(path):
    s=path.stat()
    return[s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns]


def main():
    if OUT.exists():raise ValueError('existing private preservation kept')
    certified=json.loads((P/'pg1000-cold-overlay-v1/manifest.safe.json').read_bytes())
    before=(identity(BASE),identity(BACKING))
    if before!=(certified['sourceIdentity'],certified['backingIdentity']):
        raise ValueError('unchanged certified backing identities required')
    script=r'''
import pathlib,json,hashlib
p=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/after.private.json')
raw=p.read_bytes()
if hashlib.sha256(raw).hexdigest()!='044dcfac0913fcdeabb0bc2706c526adeebfcf08140d284153a0c829c46aaafd':raise ValueError('fixed before refused')
old='/srv/schubert-nk/backup/20261009-063333-601297d0-a8ba-47da-852b-0ffeae409965'
d=json.loads(raw)['snapshot']['durable']['backup']
v={k:x for k,x in d.items()if k==old or k.startswith(old+'/')}
if len(v)!=5:raise ValueError('exact retired bundle required')
print(json.dumps(v))
'''
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes',
         '-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),
         '-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    result=subprocess.run(ssh,input=script.encode(),capture_output=True,timeout=15)
    if result.returncode!=0:raise ValueError('private before metadata unavailable')
    expected=json.loads(result.stdout)
    if set(expected)!={OLD}|{OLD+'/'+x for x in NAMES}:
        raise ValueError('retired entry closure refused')
    # Explicit rb backing handles avoid 3.21's absolute-name auto-resolution
    # limitation. The original packages are unchanged, all streams read-only.
    backing=QCow2(BACKING)
    image=QCow2(BASE,backing_file=backing.open())
    if image.fh.mode!='rb' or backing.fh.mode!='rb':
        raise ValueError('read-only disk handles required')
    disk=Disk(image.open())
    matches=[]
    for part in disk.partitions:
        try:fs=ExtFS(part.open());fs.get(OLD)
        except Exception:continue # Non-root GPT partitions are not extfs/this path.
        matches.append((part,fs))
    if len(matches)!=1:raise ValueError('unique preserved root filesystem required')
    partition,fs=matches[0]
    os.umask(0o077);OUT.mkdir(mode=0o700);dest=OUT/'bundle';dest.mkdir(mode=0o700)
    records={}
    for name in sorted(expected):
        node=fs.get(name);wanted=expected[name]['metadata'];inode=node.inode
        observed=[node.inum,inode.i_uid,inode.i_gid,inode.i_mode,inode.i_links_count,node.size,node.mtime_ns,node.ctime_ns]
        if observed!=wanted[1:] or node.xattr:
            raise ValueError('retired original inode metadata refused')
        if name==OLD:
            if not stat.S_ISDIR(inode.i_mode):raise ValueError('retired directory required')
            continue
        if not stat.S_ISREG(inode.i_mode)or node.size>128*1024*1024:
            raise ValueError('bounded retired regular artifact required')
        target=dest/Path(name).name
        h=hashlib.sha256();size=0
        with node.open()as source,target.open('xb')as sink:
            while True:
                block=source.read(131072)
                if not block:break
                sink.write(block);h.update(block);size+=len(block)
            sink.flush();os.fsync(sink.fileno())
        if size!=wanted[6]or h.hexdigest()!=expected[name]['sha256']:
            raise ValueError('retired artifact digest refused')
        records[Path(name).name]=dict(size=size,sha256=h.hexdigest(),originalMetadata=wanted,
                                     privateMode=oct(stat.S_IMODE(target.stat().st_mode)))
    if before!=(identity(BASE),identity(BACKING)):
        raise ValueError('original backing changed during read-only export')
    image.fh.close();backing.fh.close()
    manifest=dict(run='PG1128-retired-backup-v1',scope='PRIVATE_PRESERVATION_ONLY',
                  completedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  originalPath=OLD,rootPartition=partition.number,rootOffset=partition.offset,
                  sourceIdentity=before[0],backingIdentity=before[1],
                  certifiedSourceSha256=certified['sourceSha256'],
                  certifiedBackingSha256=certified['backingSha256'],
                  sourceShaRehashed=False,sourceIdentityUnchanged=True,
                  packagesManifestSha256=hashlib.sha256(Path('/home/mini/codex/project1/work/toolchain/dissect-backup-readonly-20261010/manifest.json').read_bytes()).hexdigest(),
                  files=records,currentBackupVmDbModified=False,
                  rawOutsideGit=True,formalAccepted=False)
    with(OUT/'manifest.private.json').open('x')as f:json.dump(manifest,f,indent=2);f.flush();os.fsync(f.fileno())
    for directory in [dest,OUT]:
        fd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
    print(json.dumps({'actualExit':0,'run':manifest['run'],'filesPreserved':len(records),
                      'bytesPreserved':sum(x['size']for x in records.values()),
                      'manifestSha256':hashlib.sha256((OUT/'manifest.private.json').read_bytes()).hexdigest(),
                      'originalInodeMetadataAndHashesVerified':True,'sourceIdentityUnchanged':True,
                      'currentBackupVmDbModified0':True,'rawOutsideGit':True,'formalAccepted':False}))


if __name__=='__main__':main()
