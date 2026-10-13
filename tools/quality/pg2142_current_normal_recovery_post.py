"""Independent exact all-asset post after current pair recovery; never replay place."""
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W, SSH
from pg2138_current_normal_pair_proof import PID, CHILD

SLOT='pg2142-current-normal-pair-recovery-post-v1'


def payload():
    path=W/'pg2130-current-normal-before-v1/payload.private.py'
    old=json.loads((path.parent/'manifest.safe.json').read_bytes());raw=path.read_text()
    if old['actualExit']!=0 or hashlib.sha256(raw.encode()).hexdigest()!=old['payloadSha256']:
        raise ValueError('qualified unchanged independent all-asset reader required')
    raw=raw[:raw.index("save=base/'pg2130-current-normal-before-v1'")]
    raw+=f"require(not pathlib.Path('/proc/{PID}').exists()and not pathlib.Path('/proc/{CHILD}').exists())\n"
    raw+="require(not pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG2126').exists()and not(base/'pg2126-manifest.sig').exists())\n"
    raw+="require(native==json.loads((base/'pg2130-current-normal-before-v1/native-before.private.json').read_bytes()))\n"
    raw+='''
save=base/'pg2142-current-normal-pair-recovery-post-v1';require(not os.path.lexists(save));save.mkdir(mode=0o700)
encoded=json.dumps({'after':after,'native':native},sort_keys=True).encode()
with(save/'after.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
for p in [save,save.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'postSha256':hashlib.sha256(encoded).hexdigest(),'all24And32And187Unchanged':True,'allTenKernelEmpty':True,'ownedActorsDBAdvisoryFlockGone':True,'allOriginalBackupAndNativeUnchanged':True,'candidateNotPlaced':True,'oldCloseUnknown':True,'signals0':True,'formalAccepted':False}))
'''
    from pyflakes.api import check
    if check(raw,'<current normal full recovery post>'):raise ValueError('whole actual namespace required')
    compile(raw,'<current normal full recovery post>','exec');return raw


def main():
    old=json.loads((W/'pg2140-current-normal-pair-owned-handoff-v1/manifest.safe.json').read_bytes())
    if old['actualExit']!=0 or old['queuedSameHostGateAcquired']is not True:raise ValueError('actual current pair handoff required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload().encode();(out/'payload.private.py').write_bytes(raw)
    r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw,capture_output=True,timeout=120)
    (out/'stderr.private.log').write_bytes(r.stderr)
    value={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'oldCloseUnknown':True,'formalAccepted':False}
    if not r.returncode:value['guest']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
