"""Classify the three pinned MaintenanceRunFiles PMD statements without executing the owner."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess

D=Path('documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117')
E=Path('evidence/01_PT/018_NK-OPS-001/evidence')
TARGET='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/MaintenanceRunFiles.java'
DESIGN='documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md'
RULE='AvoidSynchronizedStatement'
AUDIT={
    149:('execute','scopeLock','Owns six nested directory references and callback lifetime through reverse releases. The outer monitor is held during I/O and callback.'),
    158:('perform','stateLock','Checks active ownership, inspects begin state and runs the supplied work before return. The same monitor prevents terminal state changing during borrowed work.'),
    164:('finish','stateLock','Performs real namespace verification, then marks the Session closed in finally. State lock is shared by work and terminal invalidation.'),
}


def git(*args):
    return subprocess.check_output(['git',*args],timeout=35)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def ref(path):
    return dict(path=str(path),sha256=digest(Path(path).read_bytes()))


def load(path):
    return json.loads(Path(path).read_bytes())


def main():
    start=load(next(D.glob('570_*')))
    v=start['values']
    core=v['productionCoreMain']
    assert git('rev-parse','HEAD').decode().strip()==v['source']
    pins=v['oracleReferences']
    assert all(ref(pin['path'])==pin for pin in pins)
    remaining,raw_receipt,reviewed,build,p004,earlier=(load(pin['path']) for pin in pins)
    assert build['sourceCore']==core and build['actualExit']==0 and p004['source']!=core
    assert len(remaining)==45 and earlier['index']==763 and earlier['newApplicable']==1
    assert earlier['warningStillOpen'] and earlier['nativeOriginalUnclassified']==34 and earlier['unrelatedRootUnclassified']==10
    current=git('show',f'{core}:{TARGET}')
    source_sha=digest(current)
    assert source_sha==raw_receipt['sourceInputs'][TARGET]==build['sourceInputs'][TARGET]
    p004_target=p004['nativeOrActualFileEvidence']['targets'][TARGET]['currentInputHashes'][0]
    assert p004_target['path']==TARGET and p004_target['currentSourceSha256']==source_sha
    assert digest(git('show',f"{p004['source']}:{TARGET}"))==source_sha
    assert current==Path(TARGET).read_bytes()
    source=current.decode().splitlines()
    current_items=[(i,line.strip()) for i,line in enumerate(source,1) if line.strip().startswith('synchronized (')]
    assert current_items==[(311,'synchronized (scopeLock) {'),(1098,'synchronized (stateLock) {'),
                          (1249,'synchronized (stateLock) {'),(1260,'synchronized (stateLock) {')]
    selected=[row for row in remaining if row['raw']['path']==TARGET]
    assert {row['rawFindingIndex'] for row in selected}==set(AUDIT)
    decisions=[]
    for row in selected:
        raw=row['raw']
        index=row['rawFindingIndex']
        method,lock,reason=AUDIT[index]
        line=int(raw['beginline'])
        assert row['sourceSha256']==source_sha and raw['method']==method and raw['rule']==RULE
        assert row['actualSourceLine']==source[line-1] and f'synchronized ({lock})' in source[line-1]
        decisions.append(dict(historicalIndex=index,rule=RULE,line=line,method=method,monitor=lock,
                              decision='APPLICABLE_OPEN_REQUIRES_SAME_OWNER_NATIVE_PROOF',reason=reason))
    companion,=[row for row in reviewed if row['path']==TARGET and row['rule']==RULE and row['method']=='invalidate']
    assert companion['line']==1260 and companion['decision']=='NOT_APPLICABLE_JAVA25_NONBLOCKING_MEMORY_ATOMICITY'
    assert companion['sourceSha256']==source_sha
    assert source[1259].strip()=='synchronized (stateLock) {' and source[1260].strip()=='open = false;'
    assert p004['requiredEnding'][0].startswith('Current native file open/held/terminal')
    physical={k:h for k,h in build['physicalClassHashes']['batch'].items() if '/MaintenanceRunFiles' in k}
    assert len(physical)==14
    main=git('rev-parse','origin/main').decode().strip()
    design=git('show',f'{main}:{DESIGN}').decode()
    assert any('MaintenanceRunFilesの6 root' in row and 'Session無効化の時点' in row for row in design.splitlines())
    effect={'historicalUnclassifiedTotal':45,'previousApplicableOpen':1,'newApplicableOpen':3,
            'unclassifiedAfterReviewedSubset':41,'unrelatedRootStillUnclassified':10}
    output=E/v['run']
    output.mkdir()
    value=dict(actualExit=0,toolSource=v['source'],sourceCore=core,source=ref(Path(TARGET)),startEvent=start['eventId'],
               binding=pins,previousExactRawWithoutReplay=True,decisions=decisions,effect=effect,physicalReceipt=physical,
               p004ReferenceSource=p004['source'],limitedSourceEqualityProven=True,
               preparationGuardExit1='P004-03 receipt has an older Core; verify the exact target SHA independently',
               sharedMonitorCompanion=dict(method='invalidate',oldIndex=companion['rawFindingIndex'],
                                           localStatementDecisionUnchanged=True,futureChangeCohort='perform/finish/invalidate'),
               design=dict(path=DESIGN,source=main,sha256=digest(design.encode())),nativeOperations=0,
               productTests=0,staticExecutions=0,coverageMeasured=0,finalP00403Accepted=False,formalUpdated=False,
               wholeF03Accepted=False,whole451Accepted=False,
               terminalAtUTC=datetime.now(timezone.utc).isoformat())
    with (output/'manifest.json').open('x') as f:
        json.dump(value,f,indent=2)
        f.write('\n')
    print(ref(output/'manifest.json'),effect)


if __name__=='__main__':
    main()
