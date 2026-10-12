"""Actual safe manifests + immutable start-source reconciliation, no raw export."""
import datetime
import hashlib
import json
from pathlib import Path
import platform
import subprocess
from pg1446_current_cold_stage import W

ROOT=Path(__file__).resolve().parents[2]


def main():
    observations=[]
    for slot,test in [('pg1813-current-warning-pair-once-handoff-v1','PT-OPS-PG1813-ONCE001'),('pg1814-current-pair-independent-full-post-v1','PT-OPS-PG1814-POST001')]:
        raw=(W/slot/'manifest.safe.json').read_bytes();v=json.loads(raw)
        if v['actualExit']!=0:raise ValueError('actual success required')
        allowed=['actualExit','normalRefThenJavaTermOnce','managementPeerAdvisoryMA0','liveDaemonPeersPreserved','all24Config32Signed187OriginalBackupNativeUnchanged','newObserverReferencesReturnedNormally','oldCloseUnknown','serviceStartsStops0','afterSha256','allOriginalWholeSnapshotUnchanged','recoveredPairAbsent','managementPeersAdvisoryMA0','currentFourOwnedLive','tables','configurationFields','signedArtifacts','privateBeforeSha256','normalMetadataReferences']
        observations.append({'TestID':test,'slot':slot,'actualExit':0,'manifestSha256':hashlib.sha256(raw).hexdigest(),'payloadSha256':v['payloadSha256'],'queuedSameHostGateAcquired':v.get('queuedSameHostGateAcquired'),'guest':{k:v['guest'][k]for k in allowed if k in v['guest']}})
    paths={'requested':'pg1802-stop-v1.requested','frozen':'pg1801-frozen-v1.safe.json','result':'pg1802-stop-v1.safe.json'}
    records={k:json.loads((W/p).read_bytes())for k,p in paths.items()}
    started=records['requested']['operatorSource'];frozen=records['frozen']['operatorSource']
    if started!=frozen or records['result']['actualExit']!=143:raise ValueError('actual immutable failure source reconciliation required')
    result={'createdUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'collectorCommit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'operatorCommit':'17796771438519e9d8c2a9774366ced6aace23cf','branch':'dev-foundation','productionSource':'2741c4546afad6c1e8b6efbd53dfb58144edf7bb','hostPython':platform.python_version(),'JDK':'25.0.4','observations':observations,'oldStopSourceReconciliation':{'actualStartedSource':started,'frozenSource':frozen,'mislabelledCompletionOperator':records['result']['operatorSource'],'actualExit':143,'oldNormalClose':'UNKNOWN','rawNotRewritten':True,'manifests':{k:{'path':p,'sha256':hashlib.sha256((W/p).read_bytes()).hexdigest()}for k,p in paths.items()}},'independentUniqueTests':10,'relatedBUG':['BUG-1172','BUG-1173','BUG-1174','BUG-1175'],'relatedSSC':['SSC-281'],'nativeCoverage':'NOT_QUALIFIED','wholeAccepted':False,'formalAccepted':False,'secretsExported':False}
    target=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/output/700_manifest.json'
    with target.open('x')as f:json.dump(result,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'path':str(target.relative_to(ROOT)),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'formalAccepted':False}))


if __name__=='__main__':main()
