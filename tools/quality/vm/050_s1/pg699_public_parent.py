"""Whitelisted current parent/stop/native results, no raw JaCoCo session/DB/secret."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

R=Path(__file__).resolve().parent;T=R.parents[3]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
D=T/'evidence/01_PT/018_NK-OPS-001/evidence/PG690-current-native-public-v1'
SOURCE='9bd50536f692610036a0ed8b83e0a8b35fe2a66f'


def main():
    os.umask(0o077);assert not subprocess.check_output(['git','status','--porcelain'],cwd=T)
    assert not D.exists();D.mkdir();files={}
    names=('pg689-backup-preserve-v1','pg690-prepare-v1','pg690-start-v1','pg692-retention-post-v1',
           'pg693-completed-readonly-v1','pg694-chr-a01-native-v1','pg696-native-stop-v1','pg697-terminal-final-v1')
    allowed=('run','actualExit','operatorSource','productionSource','startedUTC','completedUTC','endedUTC',
             'elapsedSeconds','beforeSha256','completeSha256','snapshotSha256','privateLogSha256',
             'priorFiles','priorEligibleBundles','priorProtectedNames','privateArchiveSha256','privateArchiveBytes',
             'rawExported','serverMutations','prepared','starts0','clientExit','clientSuccessIsNotParentSuccess',
             'MainPID','InvocationID','Job','ExecMainStartTimestampMonotonic','oldRowsPreserved',
             'newBackupSuccess','newOtherSkipped','retentionDeleted','eligibleAfter','protectedPreserved',
             'remainingOldBackupBytesUnchanged','runId','cutoff','actualDumpList0','newFileSecurity',
             'sameParentGeneration','genuineCompletion','batchRun','activation','metadataScopesNormal',
             'operationAuthority','wholeFormalAccepted','parentEndedUTC','harnessClassesSha256',
             'baselineSha256','sameCapturedParentApiWebCaddyBeforeAfter','sharedCurrentDriver',
             'approvedDIF001TitleOnly','otherCasesNotRun','fullGate','rawCookieTokenExported','oldCloseNotInferred',
             'productionPT0','all24UnchangedTwice','allTenUnitsKernelEmpty','allActorGone','allClientAdvisoryFlock0',
             'whole187SignedArtifactBytesVerified','normalNewMetadataScopes','ownedExplicitStops',
             'eightTerminalReceipts','nativeMetadataStableTwice','nativePhysicalFiles','startsStopsReloadsSqlWrites',
             'formalAccepted')
    for name in names:
        raw=(W/(name+'.safe.json')).read_bytes();v=json.loads(raw)
        assert v.get('actualExit',v.get('clientExit'))==0
        safe={k:v[k]for k in allowed if k in v};safe['privateReceiptSha256']=hashlib.sha256(raw).hexdigest()
        content=(json.dumps(safe,indent=2)+'\n').encode()
        with(D/(name+'.safe.json')).open('xb')as f:f.write(content)
        files[name+'.safe.json']=hashlib.sha256(content).hexdigest()
    raw=(W/'pg698-current-eight-native-v1/manifest.safe.json').read_bytes();v=json.loads(raw)
    assert v['actualExit']==0 and v['productionSource']==SOURCE and v['currentNativeStreams']==8
    safe={k:v[k]for k in ('run','actualExit','productionSource','operatorSource','recordedUTC',
                         'frozenHostManifestSha256','hostExecHashes','currentNativeStreams',
                         'historicalNativeNotImported','gain','coverage100','formalAccepted','rawExported')}
    for name in ('hostOnlyCounters','moduleCounters'):
        safe[name]={}
        for module,values in v[name].items():
            assert values['classByteMismatch']==0
            safe[name][module]={k:values[k]for k in ('LINE','METHOD','CLASS','BRANCH')}
            for count in safe[name][module].values():
                assert set(count)=={'missed','covered'}and all(type(x)is int and x>=0 for x in count.values())
    safe['privateReceiptSha256']=hashlib.sha256(raw).hexdigest()
    content=(json.dumps(safe,indent=2)+'\n').encode()
    with(D/'pg698.safe.json').open('xb')as f:f.write(content)
    files['pg698.safe.json']=hashlib.sha256(content).hexdigest()
    manifest={'run':'PG690-current-native-public-v1','source':SOURCE,'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip(),
              'branch':'dev-foundation','os':'Linux host/Ubuntu26.04 guest','jdk':'25.0.4',
              'tools':{'jacoco':'0.8.15','asm':'9.10.1','postgresql':'18.6','artemis':'2.56.0'},
              'specs':['558','559','560','561','562','563','564','565'],
              'testIds':['BACK689001','FRESH690001..004','RET692001..002','DONE693001..002','A01-694001..002','STOP696001..003','POST697001..002','NATIVE698001..002'],
              'ssc':['SSC-233'],'files':files,'rawSessionsCookiesTokensCredentialsDBBackupsExported':False,
              'formalAccepted':False,'coverage100':False,'pgptComplete':False}
    with(D/'manifest.json').open('x')as f:json.dump(manifest,f,indent=2);f.write('\n')
    print(json.dumps({'safeReceipts':len(files),'manifestSha256':hashlib.sha256((D/'manifest.json').read_bytes()).hexdigest(),'formalAccepted':False}))


if __name__=='__main__':main()
