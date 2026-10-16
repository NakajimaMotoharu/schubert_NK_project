"""Publish only explicit safe hashes/counts and typed outcomes, never raw private images."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from pg1446_current_cold_stage import W
from pg4514_metadata_only_recover import complete

ROOT=Path(__file__).resolve().parents[2]
OUTPUT=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/output/PG4518'
INPUTS={
 'fullRead':'pg4482-bound-configuration-pair-read-v1/manifest.safe.json',
 'failedProof':'pg4492-inspect-pair-tools-v1-proof/manifest.safe.json',
 'pairProof':'pg4492-inspect-pair-tools-v2-proof/manifest.safe.json',
 'failedRecovery':'pg4494-inspect-pair-recover-v2/manifest.safe.json',
 'postRead':'pg4504-post-retainer-full-read-v1/manifest.safe.json',
 'metadataProof':'pg4512-metadata-only-tools-v1-proof/manifest.safe.json',
 'recovery':'pg4514-metadata-only-recover-v1/manifest.safe.json',
 'setCompile':'pg4500-frozen-v1.safe.json'}
SAFE={'actualExit','source','BOM','boot','observedUTC','mode','signalsIssued','childSignalsIssued','oldScopesNormal','newTenRefsNormalClose',
 'oldPostReplayed','unitOperationsIssued','formalAccepted','allOldProcessesAndResourcesGone','proofSha256','candidatePlaced',
 'firstPairSha256','secondPairSha256','firstDataSha256','secondDataSha256','firstConfigSha256','secondConfigSha256','all19UnitFieldsAnd32SettingsPreserved',
 'allCurrentOriginalDataPreserved','allFullPairDescriptorsEqualTwice','ownerSha256','ownerSecondSha256','terminalSha256','terminalSecondSha256','dataSha256','configurationSha256','identitySha256',
 'independentPostCompleted0','allNewPostScopesNormal','retainerScopeNormal','operationsIssued',
 'newMARDDBTenRefNormalClose','independentFailedDoneRecoveryPost','oldParentNormal','all24OriginalBackupNativeUnitConfigUnchanged','parent143StillFailed','beforeSha256','afterSha256',
 'signalStartStopReloadDbWrites','ordinaryPoolsFreshSocketMatched','nativeQualificationPending','completeGraphQualified','productionSource','candidateSource','candidateManifestSha256',
 'currentCompileJarSource','failedCurrentDataBeforeSha256','historicalGenericToolSource','operatorSource','bundleSha256','guestMutations0','startedUTC','completedUTC'}


def safe_value(value):
    result={k:v for k,v in value.items()if k in SAFE}
    if 'result'in value:result['result']=safe_value(value['result'])
    if 'independentPost'in value:result['independentPost']=safe_value(value['independentPost'])
    for key in ['originalInspectActualExit','originalRecoveryActualExit']:
        if key in value:result[key]=value[key]
    if 'fileHashes'in value:result['frozenPhysicalFiles']=len(value['fileHashes'])
    return result


def main():
    rows={}
    for label,path in INPUTS.items():
        raw=(W/path).read_bytes();v=json.loads(raw)
        rows[label]={'privateEvidenceRelativePath':path,'sha256':hashlib.sha256(raw).hexdigest(),'safeOutcome':safe_value(v)}
        expected=1 if label=='failedProof'else 255 if label=='failedRecovery'else 0
        if type(v['actualExit'])is not int or v['actualExit']!=expected:raise ValueError('actual original outcome, never normalize')
        if label=='recovery':complete(v['result'])
    os.umask(0o022);OUTPUT.mkdir(parents=True)
    names=['pg4480_complete_inspect_pair_read_test','pg4482_bound_configuration_pair_read_test','pg4488_inspect_pair_contract_test','pg4490_inspect_pair_handoff_sources_test',
      'pg4494_inspect_pair_recover_test','pg4510_metadata_only_handoff_sources_test','pg4514_metadata_only_recover_test','pg4498_set_typed_unused_sources_test','pg4516_set_typed_unused_dispatch_test']
    command=['python3','-B','-m','unittest',*names];r=subprocess.run(command,cwd=ROOT,capture_output=True)
    log=r.stdout+r.stderr;(OUTPUT/'tool-tests.log').write_bytes(log)
    if r.returncode!=0 or b'\nOK\n'not in log or b'skipped'in log or b'FAILED'in log:raise ValueError('all related tool tests must complete0, no skip')
    count=re.search(rb'Ran (\d+) tests? in ',log)
    if count is None:raise ValueError('actual test count required')
    manifest={'programId':'NK-OPS-001','testIds':['PT-OPS-INSPECT-PAIR-IMAGE','PT-OPS-INSPECT-PAIR-HANDOFF','PT-OPS-INSPECT-POST-HANDOFF','PT-OPS-SET-FIELDS'],
      'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'branch':subprocess.check_output(['git','branch','--show-current'],text=True).strip(),
      'evidenceOperatorHead':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'productionCandidateSource':'964e96e45bb588e7e75798b5adf425cbd9985427',
      'deployedSource':'7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e','formalTests':1964,'formalScopes':53,'effortCompletion':None,'formalAccepted':False,
      'command':command,'actualExit':r.returncode,'selectedToolTests':int(count[1]),'toolTestsLogSha256':hashlib.sha256(log).hexdigest(),'outcomes':rows,
      'bugs':['BUG1363','BUG1364','BUG1365','BUG1366'],'horizontal':['YKT1129','YKT1130','YKT1131','YKT1132'],'design':['SSC296','SSC297','SSC298'],
      'oldUnknownAndFailedParentsNormalized':False,'newCandidatePlaced':False,'currentMainNativeCreditImported':False,
      'publicContentPolicy':'Explicit safe outcome allowlist only; no raw FD/config/DB/journal/credential/token/session/key images; full private SHA references preserved',
      'unaccepted':['newv5 actual inspect/unused placement','candidate RO/publication','new normal Root/native/Browser/CHR/F03/four100/451/trace/handoff','QA051 final']}
    raw=json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2).encode()+b'\n';(OUTPUT/'manifest.json').write_bytes(raw)
    print(json.dumps({'actualExit':0,'manifest':str(OUTPUT/'manifest.json'),'sha256':hashlib.sha256(raw).hexdigest(),'selectedToolTests':int(count[1]),'formalAccepted':False}));return 0


if __name__=='__main__':raise SystemExit(main())
