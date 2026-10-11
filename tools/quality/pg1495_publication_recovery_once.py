"""Once SSC266 exact current failed-publication cohort recovery; never replay on unknown.

Primitive/helper source and all tools immutable-qualified. New transport receipt
is not a successful old Root or resume grant. Independent full closing follows.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg1446_current_cold_stage import W,SSH
from pg1494_publication_recovery_stage import OUTNAME

def valid_receipt(data):
    return type(data)is bytes and data==(
        b'PG1292 STAGE PINNED_SIGNATURE_VERIFIED\n'
        b'PG1292 STAGE FULL_CANDIDATE_BOM_VERIFIED\n'
        b'PG1495_DONE publicationOnlyRecovered=true allScopesReturnedNormally=true originalRetiredOrAuthorityIssued=false\n')

def main():
    os.umask(0o077);out=W/'pg1495-publication-recovery-once-v2';out.mkdir(mode=0o700)
    frozen=json.loads((W/'pg1493-publication-recovery-frozen-v2.safe.json').read_bytes())
    stage=json.loads((W/OUTNAME/'manifest.safe.json').read_bytes())
    assert frozen['actualExit']==stage['actualExit']==0 and frozen['productionSource']=='769ddb15cd735c25fef581b5f9850ef9d0053c0f'
    assert stage['frozenOperatorSource']==frozen['operatorSource']
    tools='/var/lib/pgpt-s1-preservation/pg1493-publication-only-tools-v2'
    args=SSH+['sudo','-n','/opt/jdk-25.0.4/bin/java','--enable-native-access=ALL-UNNAMED',
        '-cp',tools+':'+tools+'/publication-only-helper.jar:/opt/schubert-nk/current/api/api.jar:/opt/schubert-nk/current/operations/batch.jar:/opt/schubert-nk/current/api/lib/*:/opt/schubert-nk/current/operations/lib/*',
        'Pg1493PublicationOnlyRecovery','recover']
    begin={'productionSource':frozen['productionSource'],'operatorSource':frozen['operatorSource'],
        'transportHead':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        'transportSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'hostPid':os.getpid(),'command':args,'oldRoot1456RemainsFailed':True,'rootRestartIssued':False,'formalAccepted':False,'requiresReattachNotRepeat':True}
    with(out/'begin.safe.json').open('x')as f:json.dump(begin,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    with(out/'recovery.private.log').open('xb')as f:r=subprocess.run(args,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
    log=(out/'recovery.private.log').read_bytes();success=r.returncode==0 and valid_receipt(log)
    manifest={'run':'PG1495-publication-recovery-once-v2','actualExit':0 if success else 1,'sshExit':r.returncode,'productionSource':frozen['productionSource'],'operatorSource':frozen['operatorSource'],'logSha256':hashlib.sha256(log).hexdigest(),'normalScopesReceipt':success,'oldRoot1456RemainsFailed':True,'rootRestartIssued':False,'formalAccepted':False,'independentFullClosingPending':True}
    with(out/'manifest.safe.json').open('x')as f:json.dump(manifest,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(manifest,sort_keys=True));return manifest['actualExit']

if __name__=='__main__':raise SystemExit(main())
