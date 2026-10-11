"""Once new operator readonly profile; retain live ownership on unknown, never replay."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg1446_current_cold_stage import W,SSH


def main():
    os.umask(0o077);out=W/'pg1481-partial-original-profile-v1';out.mkdir(mode=0o700)
    compiled=json.loads((W/'pg1478-partial-profile-frozen-v1.safe.json').read_bytes())
    stage=json.loads((W/'pg1480-current-cold-stage-v1/manifest.safe.json').read_bytes())
    assert compiled['actualExit']==stage['actualExit']==0
    assert compiled['productionSource']=='769ddb15cd735c25fef581b5f9850ef9d0053c0f'
    args=SSH+['sudo','-n','/opt/jdk-25.0.4/bin/java','--enable-native-access=ALL-UNNAMED',
       '-cp','/var/lib/pgpt-s1-preservation/pg1478-partial-original-tools-v1:/opt/schubert-nk/current/api/api.jar:/opt/schubert-nk/current/operations/batch.jar:/opt/schubert-nk/current/api/lib/*:/opt/schubert-nk/current/operations/lib/*',
       'Pg1478PartialOriginalProfile','profile']
    with(out/'begin.safe.json').open('x')as f:
        json.dump({'operatorSource':compiled['operatorSource'],'productionSource':compiled['productionSource'],
           'hostPid':os.getpid(),'command':args,'businessMutations0':True,'stopIssued0':True,'formalAccepted':False},f,sort_keys=True);f.flush();os.fsync(f.fileno())
    with(out/'profile.private.log').open('xb')as f:
        result=subprocess.run(args,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
    log=(out/'profile.private.log').read_bytes()
    success=result.returncode==0 and log==b'PG1481_DONE readonlyProfile=true allScopesReturnedNormally=true originalRetiredOrAuthorityIssued=false\n'
    manifest={'run':'PG1481-partial-original-profile-v1','actualExit':0 if success else 1,
        'sshExit':result.returncode,'productionSource':compiled['productionSource'],
        'logSha256':hashlib.sha256(log).hexdigest(),'normalScopesAccepted':success,
        'businessMutations0':True,'ownedRecoveryAccepted':False,'formalAccepted':False,
        'profileTimingQualificationPending':True}
    with(out/'manifest.safe.json').open('x')as f:json.dump(manifest,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(manifest,sort_keys=True));return manifest['actualExit']


if __name__=='__main__':raise SystemExit(main())
