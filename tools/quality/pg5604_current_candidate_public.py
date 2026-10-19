"""Allowlisted actual host candidate and fresh deployed identity, never raw signature/key."""
import hashlib
import json
import os
from pg5598_current_signed_candidate import ROOT,W,SOURCE,OLD_SOURCE,OLD_BOM


def main():
    paths={'candidate':W/'pg5598-candidate-build-v1.safe.json','guest':W/'pg5602-current-vm-reauthentication-v1/manifest.safe.json'}
    hashes={k:hashlib.sha256(p.read_bytes()).hexdigest()for k,p in paths.items()}
    if hashes!={'candidate':'d1214e27276ffa7a368c593e36904fb39f48f5dac3d62a0fa54eafebf32491df','guest':'cc64c22320eb1f1c9c42d3bcb15d5ca106083bed6cee9185593c7fbbdf82023c'}:raise ValueError('exact original candidate/read-only results, no replay')
    candidate=json.loads(paths['candidate'].read_bytes());guest=json.loads(paths['guest'].read_bytes());observed=guest['result']
    if not(candidate['actualExit']==guest['actualExit']==0 and candidate['candidateSource']==guest['candidateSource']==SOURCE
      and candidate['priorSource']==guest['source']==observed['deployedSource']==OLD_SOURCE and observed['bomSha256']==OLD_BOM
      and candidate['manifestSha256']==guest['candidateBOM']and candidate['signatureVerified']and candidate['candidateNotDeployed']and observed['artifactsVerified']==187
      and observed['signatureVerifyExit']==0 and not guest['admissionAuthorityIssued']and guest['vmStateChangingActions']==0):raise ValueError('distinct signed candidate and deployed187 current, never placement permission')
    keys=('run','actualExit','candidateSource','operatorSource','priorSource','release','startedUTC','completedUTC','hostGateSha256','tests','suites','mainClasses',
      'changedClasses','semanticChangedClasses','debugOnlyChangedClasses','addedClasses','removedClasses','manifestSha256','artifacts','schema','sql','history','changedArtifactPaths',
      'signatureVerified','signatureSha256','helperSha256','guestMutations0','candidateNotDeployed','formalAccepted','signedBaseClassDelta','containerPhysicalProofs','deploymentAuthority','candidatePurpose')
    value={'actualExit':0,'source':SOURCE,'candidate':{k:candidate[k]for k in keys},'freshGuest':{k:observed[k]for k in('observedUTC','guestBoot','deployedSource','release','bomSha256','artifactsVerified','signatureVerifyExit','units')},
      'originalManifestSha256':hashes,'wholeReplayed':False,'signatureReissued':False,'vmStartStopActions':0,'oldNativeImported':False,'F03Accepted':False,'formalAccepted':False,'acceptedLeafDelta':0,'effortPercent':None,
      'signatureOrKeyBytesPublished':False,'dbOriginalBackupAndNativeFreshAuthenticationPending':True}
    out=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5604-current-candidate-v1';os.umask(0o077);out.mkdir()
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'candidateSource':SOURCE,'candidateBOM':candidate['manifestSha256'],'currentSource':OLD_SOURCE,'sha256':hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest(),'formalAccepted':False}))


if __name__=='__main__':main()
