"""Publish bounded genuine six-case typed boundary results, never promote a failed whole."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[2]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
PUBLIC=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3684-typed-inode-boundary-v1'


def main():
    failed=json.loads((W/'pg3680-typed-inode-related-v1/manifest.safe.json').read_bytes())
    raw=(W/'pg3682-typed-inode-corrected-v1/manifest.safe.json').read_bytes();actual=json.loads(raw);r=actual['result']
    before=(W/'pg3678-numeric-conditional-before-v1/manifest.safe.json').read_bytes();b=json.loads(before)
    if not(failed['actualExit']==1 and b['actualExit']==actual['actualExit']==r['actualExit']==r['mavenExit']==0 and b['independentBeforeReproduced']and r['tests']==6 and r['suites']==1 and r['mainClasses']==568 and r['allMainResourcesDebugSameBytes']and r['FESFlakyNotRun']==0):raise ValueError('actual six only, original failed33 retained')
    c=r['modules']['batch']['checkedAttributesCounters']
    if not(c['BRANCH']=={'missed':0,'covered':46}and c['LINE']=={'missed':0,'covered':23}and c['METHOD']=={'missed':0,'covered':1}):raise ValueError('whole boundary counters required')
    path='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/RootServiceExecutableAdmissionTest.java'
    tested=subprocess.check_output(['git','show',r['sourceSnapshot']+':'+path],cwd=ROOT)
    if tested!=(ROOT/path).read_bytes():raise ValueError('actual current Test bytes')
    out={k:r[k]for k in ['actualExit','mavenExit','productionSource','sourceSnapshot','sourceArchiveSha256','startUTC','endUTC','tests','suites','mainClasses','staticSelectedModules','FESFlakyNotRun','allMainResourcesDebugSameBytes','logSha256','serverManifestSha256','modules','vmActions']}
    out.update(run='PG3684-typed-inode-boundary-v1',testIds=['PT-ROOTELF-3678-001','PT-ROOTELF-3678-002','PT-ROOTELF-3678-003'],beforeSha256=hashlib.sha256(before).hexdigest(),actualPrivateReceiptSha256=hashlib.sha256(raw).hexdigest(),originalFailed33ActualExit=1,originalSuccessful27NotReplayed=True,testPath=path,testSha256=hashlib.sha256(tested).hexdigest(),fullIntegrationPending=True,nativeQualificationOfNewTestSnapshotPending=True,newWholeTestTotal=None,F03Accepted=False,formalAccepted=False,acceptedLeafDelta=0,BUG='BUG1312',YKT='YKT1078')
    PUBLIC.mkdir()
    with(PUBLIC/'manifest.json').open('x')as f:json.dump(out,f,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'actualExit':0,'manifestSha256':hashlib.sha256((PUBLIC/'manifest.json').read_bytes()).hexdigest(),'checkedAttributes':c,'formalUpdated':False}));return 0


if __name__=='__main__':raise SystemExit(main())
