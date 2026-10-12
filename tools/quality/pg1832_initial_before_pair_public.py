"""Whitelisted actual recovery/post hashes; no private before/DB/session copied."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
from pg1446_current_cold_stage import W

ROOT=Path(__file__).resolve().parents[2]


def main():
    observations=[]
    for slot,test in [('pg1823-identity-stop-pair-once-handoff-v1','PT-OPS-PG1823-ONCE001'),('pg1824-initial-before-pair-independent-full-post-v1','PT-OPS-PG1824-POST001')]:
        raw=(W/slot/'manifest.safe.json').read_bytes();value=json.loads(raw)
        if value['actualExit']!=0:raise ValueError('actual success required')
        guest=value['guest'];allowed=['actualExit','normalRefThenJavaTermOnce','managementPeerAdvisoryMA0','liveDaemonPeersPreserved','all24Config32Signed187OriginalBackupNativeUnchanged','newObserverReferencesReturnedNormally','oldCloseUnknown','serviceStartsStops0','afterSha256','allOriginalWholeSnapshotUnchanged','recoveredPairAbsent','managementPeersAdvisoryMA0','currentFourOwnedLive','tables','configurationFields','signedArtifacts','privateBeforeSha256','normalMetadataReferences']
        observations.append({'TestID':test,'slot':slot,'actualExit':0,'manifestSha256':hashlib.sha256(raw).hexdigest(),'payloadSha256':value['payloadSha256'],'queuedSameHostGateAcquired':value.get('queuedSameHostGateAcquired'),'guest':{k:guest[k]for k in allowed if k in guest}})
    old=W/'pg1816-stop-v1.safe.json';failure=json.loads(old.read_bytes())
    if failure['actualExit']!=143 or failure['operatorSource']!='c5e20130e93c88636f737370ee85c53fffec47b2'or failure['sourceQualified']is not False:raise ValueError('old actual failure and captured source required')
    result={'createdUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'branch':'dev-foundation','collectorCommit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'operatorCommit':'fabcf1c20f44e0ec1aee20882b733ef367b1ff22','productionSource':'2741c4546afad6c1e8b6efbd53dfb58144edf7bb','observations':observations,'oldStop':{'actualExit':143,'oldNormalClose':'UNKNOWN','operatorSource':failure['operatorSource'],'completedObservedHead':failure['completedObservedHead'],'sourceQualified':False,'manifestSha256':hashlib.sha256(old.read_bytes()).hexdigest()},'relatedBUG':['BUG-1177'],'relatedSSC':['SSC-282'],'independentSourceSchemaTests':2,'newEntryTests':4,'nativeCoverage':'NOT_QUALIFIED','formalAccepted':False,'wholeLeafAcceptedDelta':0,'rawPrivateExported':False}
    target=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/output/704_manifest.json'
    with target.open('x')as f:json.dump(result,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'path':str(target.relative_to(ROOT)),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'formalAccepted':False}))


if __name__=='__main__':main()
