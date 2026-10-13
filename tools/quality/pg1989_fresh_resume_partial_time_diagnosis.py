"""Independent partial inode/time predicate inventory; no namespace or reload changes."""
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,SSH
from pg1988_fresh_resume_retained_diagnosis import owner

SLOT='pg1989-fresh-resume-partial-time-diagnosis-v1'
PAYLOAD=r'''
import hashlib,json,os,pathlib,stat,time
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1984-fresh-resume-preparation-v1')
before=json.loads((root/'before.private.json').read_bytes());runtime=pathlib.Path('/run/systemd/system');directory=runtime/'schubert-nk-morning-controller.service.d';target=directory/'zz-pg1980-once-resume.conf'
def metadata(p):
 s=p.lstat();return [s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
old=before['runtime'][str(directory)]['metadata'];new=metadata(directory);file=metadata(target)
assert metadata(runtime)==before['runtime'][str(runtime)]['metadata']
assert {str(p)for p in runtime.rglob('*')}=={str(directory),str(target)}
assert new[:6]==old[:6]and new[6]>=old[6]and new[7]>=old[7]and new[8]>=old[8]
assert file[0]==old[0]and file[1]!=old[1]and file[2:6]==[0,0,stat.S_IFREG|0o644,1]
data=target.read_bytes();assert len(data)==file[6]and metadata(target)==file and not os.listxattr(target)
base=pathlib.Path('/etc/systemd/system/schubert-nk-morning-controller.service.d/pg477-native-coverage.conf').read_bytes();argv=[x[len(b'ExecStart='):]for x in base.splitlines()if x.startswith(b'ExecStart=')and x!=b'ExecStart='];assert len(argv)==1
literal=b'# SS343 6.13: explicit same-run fresh activation; retire after genuine terminal.\n[Service]\nExecStart=\nExecStart='+argv[0]+b' --resume 4148e3e8-f107-431a-ab27-d6e6d1f1772e\n'
assert data==literal
lower=(root/'before.private.json').stat().st_mtime_ns;now=time.time_ns()
print(json.dumps({'actualExit':0,'parentMetadataUnchanged':True,'directoryIdentityUnchanged':True,'directoryOwnTimesNondecreased':True,'directoryMetadata':new,'fileMetadata':file,'newFileLiteralByteSha256':hashlib.sha256(data).hexdigest(),'onlyExpectedNewFile':True,'durableBeforeKernelTimestampNs':lower,'fileMtimeFromDurableBeforeNs':file[7]-lower,'fileCtimeFromDurableBeforeNs':file[8]-lower,'directoryMtimeFromDurableBeforeNs':new[7]-lower,'directoryCtimeFromDurableBeforeNs':new[8]-lower,'allTimesNoFuture':all(t<=now for t in [file[7],file[8],new[7],new[8]]),'reloadReserved':(root/'daemon-reload-reserved.private').exists(),'currentStartsStopsReloadsSqlWrites0':True,'formalAccepted':False}))
'''


def main():
    os.umask(0o077);held=owner();out=W/SLOT;out.mkdir(mode=0o700)
    r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=PAYLOAD.encode(),capture_output=True,timeout=20);(out/'stderr.private.log').write_bytes(r.stderr)
    if owner()!=held:raise ValueError('same retained current owner required')
    result={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(PAYLOAD.encode()).hexdigest(),'formalAccepted':False}
    if not r.returncode:result.update(json.loads(r.stdout))
    (out/'manifest.safe.json').write_text(json.dumps(result,sort_keys=True));print(json.dumps(result));return r.returncode


if __name__=='__main__':raise SystemExit(main())
