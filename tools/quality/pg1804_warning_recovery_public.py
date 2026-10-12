"""Whitelisted safe counts/hashes only; never copy private evidence."""
import datetime
import hashlib
import json
import platform
from pathlib import Path
import subprocess
from pg1446_current_cold_stage import W
from pg1796_warning_fresh_pair_once_handoff import SLOT as RECOVERY_SLOT
from pg1798_warning_recovery_independent_post import SLOT as POST_SLOT

ROOT=Path(__file__).resolve().parents[2]


def main():
    observations=[]
    for slot in [RECOVERY_SLOT,POST_SLOT]:
        path=W/slot/'manifest.safe.json';raw=path.read_bytes();value=json.loads(raw)
        if value['actualExit']!=0:raise ValueError('actual result required')
        guest=value['guest']
        keys=['actualExit','allOriginalWholeSnapshotUnchanged','recoveredPairAbsent','managementPeersAdvisoryMA0','managementPeerAdvisoryMA0','currentFourOwnedLive','tables','configurationFields','signedArtifacts','privateBeforeSha256','normalMetadataReferences','newObserverReferencesReturnedNormally','normalRefThenJavaTermOnce','liveDaemonPeersPreserved','all24Config32Signed187OriginalBackupNativeUnchanged','oldCloseUnknown','serviceStartsStops0','afterSha256']
        observations.append({'TestID':'PT-OPS-PG1796-REC001'if '1796'in slot else 'PT-OPS-PG1798-POST001','slot':slot,'actualExit':value['actualExit'],'manifestSha256':hashlib.sha256(raw).hexdigest(),'payloadSha256':value['payloadSha256'],'guest':{k:guest[k]for k in keys if k in guest}})
    result={'createdUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'branch':'dev-foundation','collectorCommit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'operatorCommit':'8c37abcee33b392a73e91ff20379fa64b35add0f','productionSource':'2741c4546afad6c1e8b6efbd53dfb58144edf7bb','environment':{'OS':'Ubuntu26.04.1/x86-64','JDK':'25.0.4','PythonHost':platform.python_version(),'PostgreSQL':'18.6','Artemis':'2.56.0','Maven':'3.9.12'},'observations':observations,'relatedBUG':['BUG-1165','BUG-1166','BUG-1167','BUG-1168','BUG-1169','BUG-1170','BUG-1171'],'relatedSSC':['SSC-279','SSC-280'],'coverage':'limited independent guard tests; Java native/full unchanged','formalAccepted':False,'rawPrivateCopied':False,'oldUnknownNormalized':False}
    target=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/output/695_manifest.json'
    with target.open('x')as f:json.dump(result,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'publicPath':str(target.relative_to(ROOT)),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'formalAccepted':False}))


if __name__=='__main__':main()
