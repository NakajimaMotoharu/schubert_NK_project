"""Whitelist-only public receipts. No raw DB/FD/native/authentication state."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
from pg1446_current_cold_stage import W
from pg3520_outbox_owned_sources_v2 import SOURCE, BOM

ROOT=Path(__file__).resolve().parents[2]
PUBLIC=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3534-current-root-owned-native-v1'
COMMON={'actualExit','productionSource','operatorSource','payloadSha256','startedUTC','completedUTC','formalAccepted'}
RECEIPTS={
 'terminal':('pg3472-outbox-current-terminal-v1/manifest.safe.json',{'genuineParentDone','genuineRootDone','genuinePid1StartDone','newActivationSameRunCutoff','completionCode','completionOutcome','normalUnit0or10','currentManagerGc','managerExitCodeObserved','elapsedSeconds','wholeAccepted'}),
 'all24':('pg3474-outbox-current-rows-v1/manifest.safe.json',{'beforeSha256','afterSha256','independentOracleSha256','expectedSessionDeleted','expectedOutboxDeleted','expectedInboxProtected','expectedInboxDeleted','newAnonymousHttpLogs','newAnonymousSessions','newSentOutbox','logOutboxOneToOne','newDaySteps','independentRowsQualified','wholeAccepted'}),
 'seal':('pg3476-outbox-current-full-seal-v1/manifest.safe.json',{'tables','configurationFields','signedArtifacts','currentFourOwnedLive','sqlOracleQualified','businessFullOraclePending','backupManifestRetentionOraclePending','privateBeforeSha256'}),
 'fresh39':('pg3506-signed-current-full-proof-v2/manifest.safe.json',set()),
 'recovery':('pg3510-signed-current-handoff-v1/manifest.safe.json',{'oldCloseUnknown','forceUnlock'}),
 'independentRecoveryPost':('pg3512-signed-current-recovery-post-v1/manifest.safe.json',{'oldExit','oldCloseUnknown'}),
 'hostABI':('pg3522-frozen-v1.safe.json',{'genuineParentBeforeSha256','guestMutations0'}),
 'normalStop':('pg3524-stop-v1.safe.json',{'operatorSourceUnchanged','sourceQualified','action','privateLogSha256','oldFailedNormalized','starts0'}),
 'normalStopPost':('pg3526-outbox-owned-post-v2/manifest.safe.json',{'all24UnchangedTwice','allTenUnitsKernelEmpty','allActorGone','allClientAdvisoryFlock0','whole187SignedArtifactBytesVerified','normalCurrentOwnedStopScopesSealed','ownedExplicitStops','eightTerminalReceipts','nativeMetadataStableTwice','nativePhysicalFiles','startsStopsReloadsSqlWrites'}),
 'nativeCatalog':('pg3530-outbox-current-native-catalog-v1/manifest.safe.json',{'oldSource22CopiesPreserved','oldSourceNativeImported','oldNativeImported','backupPid1GenerationVerified','inspectorPid1GenerationVerified','currentRootOriginalBudgetPreserved','guestWritesStartsStops0'}),
 'nativeQualification':('pg3532-outbox-current-native-qualified-v3/manifest.safe.json',{'manifestSha256'}),
}


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    inputs={};outputs={}
    for name,(relative,fields)in RECEIPTS.items():
        raw=(W/relative).read_bytes();v=json.loads(raw)
        if type(v['actualExit'])is not int or v['actualExit']!=0 or v.get('productionSource',SOURCE)!=SOURCE:
            raise ValueError('genuine same-source receipt required: '+name)
        outputs[name]={k:x for k,x in v.items()if k in COMMON|fields}
        inputs[name]={'privateLogicalSlot':relative,'sha256':sha(raw)}
    native=json.loads((W/RECEIPTS['nativeQualification'][0]).read_bytes())['result']
    if native['productionSource']!=SOURCE or native['classByteMismatch']!=0 or native['oldNativeImported']is not False:
        raise ValueError('current native only and mismatch0 required')
    outputs['nativeQualification']['technical']={k:native[k]for k in ['currentNativeStreams','validatedNativePoints','classByteMismatch','qualified3412Tests','oldNativeImported','coverage100','gain','moduleCounters','xmlHashes']}
    outputs['nativeQualification']['remaining']={k:sum(x[k]['missed']for x in native['moduleCounters'].values())for k in ['LINE','METHOD','CLASS','BRANCH']}
    artifact=W/'pg3483-char-output-preserved-v1/artifacts/CHR-A01.json'
    baseline=ROOT/'program/characterization/baseline/current/artifacts/CHR-A01.json'
    raw=artifact.read_bytes();actual=json.loads(raw);expected=json.loads(baseline.read_bytes())
    if (sha(raw)!='3f4ed53954d6c3652d8265adde23004d79dd51fec9e16eb1db79255abd059558'
            or actual.keys()!=expected.keys()or {k for k in actual if actual[k]!=expected[k]}!={'title'}
            or actual['title']!='schubert NK - ログイン'):
        raise ValueError('explicit approved title-only redacted DOM required')
    PUBLIC.mkdir(parents=True)
    (PUBLIC/'CHR-A01.json').write_bytes(raw)
    for name,v in outputs.items():
        with(PUBLIC/(name+'.json')).open('x')as f:json.dump(v,f,sort_keys=True,indent=2);f.write('\n')
    files={p.name:sha(p.read_bytes())for p in PUBLIC.iterdir()if p.is_file()}
    manifest={'actualExit':0,'productionSource':SOURCE,'BOM':BOM,'operatorHead':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
              'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'inputs':inputs,'files':files,
              'testIds':['PT-OPS-3472-001','PT-OPS-3474-001','PT-OPS-3476-001','PT-OPS-3482-001','PT-OPS-3506-001','PT-OPS-3510-001','PT-OPS-3512-001','PT-OPS-3520-001','PT-OPS-3522-001','PT-OPS-3524-001','PT-OPS-3526-001','PT-OPS-3530-001','PT-OPS-3532-001'],
              'CHR-A01':{'actualExit':0,'artifactSha256':sha(raw),'baselineSha256':sha(baseline.read_bytes()),'approvedDIF':['DIF-001'],'QA':'QA-045','onlyTitleDiff':True,'otherCHRNotRun':True},
              'oldStop143UnknownPreserved':True,'rawDB_FD_Native_Session_CredentialExported':False,
              'formalTests':1964,'formalScopes':53,'individualAccepted':17,'individualTotal':190,'effortCompletionRate':None,
              'fullCharacterizationGate':False,'QA051final':'HELD','global100':False,'formalAccepted':False}
    with(PUBLIC/'manifest.json').open('x')as f:json.dump(manifest,f,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'actualExit':0,'publicManifest':str((PUBLIC/'manifest.json').relative_to(ROOT)),
                      'sha256':sha((PUBLIC/'manifest.json').read_bytes()),'safeFiles':len(files),'formalUpdated':False}))
    return 0


if __name__=='__main__':raise SystemExit(main())
