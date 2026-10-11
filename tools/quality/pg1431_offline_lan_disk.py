"""Retain original chain; compare new-only standalone guest bytes before LAN copy.

No VM start, snapshot application, RAM restore, original mutation or DB action.
"""
import datetime
import fcntl
import json
import os
from pathlib import Path
import resource
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent/'vm/050_s1'))
from pg997_offline_preservation import VM, Q, ENV, digest, identity, idle, write_new
from pg998_metrics import append
from lan_server import copy, run

OUT=VM/'private/pg1431-lan-standalone-v1'
ACTIVE=VM/'private/pg1000-cold-overlay-v1/active.qcow2'
REMOTE='/home/mini/schubert-nk-pgpt/vm/pg1431'


def limited():
    resource.setrlimit(resource.RLIMIT_FSIZE,(45*1024**3,45*1024**3))


def main():
    os.umask(0o077)
    with (VM/'private/pg997-boot-guard.lock').open('a') as guard:
        fcntl.flock(guard,fcntl.LOCK_EX|fcntl.LOCK_NB)
        idle()
        assert os.statvfs(VM).f_bavail*os.statvfs(VM).f_frsize > 55*1024**3
        assert subprocess.run(['lsof','-t',str(ACTIVE)],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL).returncode==1
        info=json.loads(subprocess.check_output([str(Q),'info','--output=json','--backing-chain',str(ACTIVE)],env=ENV))
        assert len(info)==3 and all(v['format']=='qcow2' and not v.get('dirty-flag',True)
                                  and not v['format-specific']['data'].get('corrupt',False) for v in info)
        assert info[0]['virtual-size']==40*1024**3
        paths=[Path(v['filename']) for v in info]
        assert paths==[ACTIVE,VM/'instance.qcow2',VM/'ubuntu-26.04-server-cloudimg-amd64.img']
        OUT.mkdir(mode=0o700)
        before={str(p):{'identity':identity(p),'sha256':digest(p)} for p in paths}
        write_new(OUT/'begin.safe.json',{'sourceChain':before,'run':'PG1431-lan-standalone-v1',
            'timeUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'vmBootIssued':False,
            'snapshotApplied':False,'ramStateRestored':False,'originalsRetained':True})
        destination=OUT/'guest.qcow2'
        with (OUT/'convert.private.log').open('xb') as log:
            result=subprocess.run([str(Q),'convert','-f','qcow2','-O','qcow2','-S','4k',str(ACTIVE),str(destination)],
                                  env=ENV,stdout=log,stderr=log,preexec_fn=limited)
        assert result.returncode==0
        with (OUT/'compare.private.log').open('xb') as log:
            comparison=subprocess.run([str(Q),'compare','-f','qcow2','-F','qcow2',str(ACTIVE),str(destination)],
                                      env=ENV,stdout=log,stderr=log)
        assert comparison.returncode==0
        assert before=={str(p):{'identity':identity(p),'sha256':digest(p)} for p in paths}
        idle()
        image=json.loads(subprocess.check_output([str(Q),'info','--output=json',str(destination)],env=ENV))
        assert 'backing-filename' not in image and not image['dirty-flag'] and not image.get('snapshots')
        disk_hash=digest(destination)
        write_new(OUT/'offline-qualified.safe.json',{'actualExit':0,'convertExit':0,'logicalCompareExit':0,
            'sourceStable':True,'guestSha256':disk_hash,'guestBytes':destination.stat().st_size,
            'originalInternalSnapshotPreserved':True,'newImageHasNoRamSnapshot':True,'formalAccepted':False})
        code,_=run("python3 -c \"import os;from pathlib import Path;p=Path('"+REMOTE+
                   "');assert not p.exists();v=os.statvfs('/');assert v.f_bavail*v.f_frsize>125*1024**3;p.mkdir(parents=True,mode=0o700);os.chmod(p.parent,0o700)\"")
        assert code==0
        code,_=copy(str(destination),REMOTE+'/guest.qcow2')
        assert code==0
        code,output=run('sha256sum '+REMOTE+'/guest.qcow2')
        assert code==0 and output.split()[0]==disk_hash
        assert before=={str(p):{'identity':identity(p),'sha256':digest(p)} for p in paths}
        idle()
        write_new(OUT/'manifest.safe.json',{'run':'PG1431-lan-standalone-v1','actualExit':0,
            'convertExit':0,'logicalCompareExit':0,'guestSha256':disk_hash,
            'guestBytes':destination.stat().st_size,'sourceChain':before,'sourceStable':True,
            'remoteDisk':REMOTE+'/guest.qcow2','remoteExactHash':True,'vmBootIssued':False,
            'oldIntentRetired':False,'oldToolNormalClose':False,'coldReauthenticationPending':True,
            'formalAccepted':False})
        print(json.dumps({'run':'PG1431','actualExit':0,'guestSha256':disk_hash,
                          'guestBytes':destination.stat().st_size,'vmBootIssued':False}))


if __name__=='__main__':
    main()
