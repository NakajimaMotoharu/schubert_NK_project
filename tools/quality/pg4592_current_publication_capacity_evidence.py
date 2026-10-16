"""Publish allowlisted real outcomes/hashes only; no rerun and no private images."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from pg1446_current_cold_stage import W

ROOT=Path(__file__).resolve().parents[2]
OUTPUT=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/output/PG4592'
INPUTS={
 'publication':'pg4544-activate-v1.safe.json',
 'post':'pg4552-failed-current-publication-post-v1/manifest.safe.json',
 'capacityBefore':'pg4570-capacity-current-before-v1/manifest.safe.json',
 'capacityGrow':'pg4572-capacity-online-grow-v1/manifest.safe.json',
 'capacityPost':'pg4574-capacity-current-after-v1/manifest.safe.json',
 'qualifiedTools':'pg4582-current-fresh-qualification-v1/manifest.safe.json',
 'observerStage':'pg4560-stage-v1.safe.json',
 'ordinaryRequest':'pg4576-current-fresh-noargs-once-v1/manifest.safe.json',
 'liveBinding':'pg4578-current-live-binding-v1/manifest.safe.json'}
SAFE={'actualExit','source','productionSource','candidateSource','candidateManifestSha256','BOM','sourceQualified','operatorSource',
 'startedUTC','completedUTC','observedUTC','payloadSha256','postSha256','firstFull11Sha256','sevenFinitePhasesVerified','all24And32Unchanged',
 'whole187SignedArtifactBytesVerified','allTenKernelEmpty','allClientAdvisoryFlock0','originalBackupNative58Preserved',
 'canonicalInvalidEpochApprovalCurrentAndOldLinkVerified','unitBytesInodesConfigurationUnchanged','newTenReferencesReturnedNormally',
 'unitExchangeAndReload','newSourceParentNotStarted','oldParent143DataOnly','oldNativeNotAppliedToNewSource','dbWrites','signalsOrStarts',
 'diskBytes','guestFreeBytes','geometrySha256','formalAccepted','hostSourceHashes','files','freshOnceSha256','staticFindings','productionPtAdded',
 'rootStartIssued','mode','automaticStartStop0','clientSuccessIsNotParentSuccess','oldRoot143Normal','originalBudgetSeconds',
 'clientExit','ordinaryNoargs','oldRunNotResumed','tenMetadataRefsNormalClose','binding','rootPid','rootTicks','rootArgvSha256','activeSha256',
 'startsStops0','rawExported','lanPayloadSha256','guestPayloadSha256','independentFullPostPending','sameBoot','nonRootPartitionsUnchanged',
 'rootStartUuidTypeUnchanged','guestFreeBytesAfter','noRebootCopyShrink','ownedLocksReleasedNormally','allTenUnitsKernelEmpty'}


def safe(value):
    result={key:value[key]for key in SAFE if key in value}
    for key in ['result','guest']:
        if key in value:result[key]=safe(value[key])
    return result


def main():
    rows={}
    for label,name in INPUTS.items():
        raw=(W/name).read_bytes();v=json.loads(raw)
        if type(v['actualExit'])is not int or v['actualExit']!=0:raise ValueError('original successful outcomes required; never rewrite failures')
        rows[label]={'privateEvidenceRelativePath':name,'sha256':hashlib.sha256(raw).hexdigest(),'safeOutcome':safe(v)}
    log=(W/'pg4582-current-fresh-qualification-v1/tests.private.log').read_bytes()
    count=re.search(rb'Ran (\d+) tests? in ',log)
    if count is None or b'\nOK\n'not in log or b'skipped'in log or b'FAILED'in log:raise ValueError('genuine original tests0 no skipped')
    os.umask(0o022);OUTPUT.mkdir(parents=True)
    (OUTPUT/'tool-tests.log').write_bytes(log)
    value={'programId':'NK-OPS-001','testIds':['PT-OPS-PUBLICATION-POST-NAMESPACE','PT-ENV-QMP-OWNER','PT-ENV-QMP-CHAIN','PT-ENV-ONLINE-CAPACITY','PT-OPS-FRESH964E-STATIC'],
      'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'branch':subprocess.check_output(['git','branch','--show-current'],text=True).strip(),
      'operatorCommit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'productionSource':'964e96e45bb588e7e75798b5adf425cbd9985427',
      'release':'PG4432','bom':'93807abdd4db24ad300b93d95d844ea21e64487dc5cf24b815c15db34305d3de',
      'commands':['pg4570_capacity_current_post.py before','pg4572_capacity_online_grow.py','pg4570_capacity_current_post.py after','pg4580_current_fresh_qualification.py','pg4560_current_same_peer_observer.py stage/watch','pg4576_current_fresh_noargs_once.py','pg4578_current_live_binding.py'],
      'selectedToolTests':int(count[1]),'toolTestsLogSha256':hashlib.sha256(log).hexdigest(),'outcomes':rows,'actualExit':0,
      'originalFailuresPreserved':['4564 host permission1','4566 chain-count1','4568 remote0/local sudo-PTY JSON1 recovered original','4546 original namespace1','4580 host static1 with24tools0'],
      'bugs':['BUG1367','BUG1368','BUG1369','BUG1370','BUG1371','BUG1372'],'horizontal':['YKT1133','YKT1134','YKT1135','YKT1136','YKT1137','YKT1138'],
      'formalTests':1964,'formalScopes':53,'formalAccepted':False,'effortCompletion':None,'qa051Final':'HELD',
      'oldSourceNativeImported':False,'rootRequestIsNotGenuineTerminal':True,'productionPtAdded':0,
      'unaccepted':['same Root genuine terminal/all24/seal','same-owner Browser/ownedstop/new-source native/CHR','F03/four100/451/trace/handoff'],
      'privacy':'Only explicit allowlisted outcomes/counts/SHA. No raw FD/DB/config/journal/credential/token/session/key images.'}
    raw=json.dumps(value,sort_keys=True,ensure_ascii=False,indent=2).encode()+b'\n';(OUTPUT/'manifest.json').write_bytes(raw)
    print(json.dumps({'actualExit':0,'manifest':str(OUTPUT/'manifest.json'),'sha256':hashlib.sha256(raw).hexdigest(),'selectedToolTests':int(count[1]),'formalAccepted':False}));return 0


if __name__=='__main__':raise SystemExit(main())
