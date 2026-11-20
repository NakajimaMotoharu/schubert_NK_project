"""Bind the current short-target evidence to the previously accepted planning denominator."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess


OPS = Path('evidence/01_PT/018_NK-OPS-001/evidence')
PMO = Path('documents/400_PGPT/470_PMO')
REVIEW = Path('../PMO/hourly-monitor/更新判断-20261207/更新判定基準.json')
RUN = 'PG41164-wbs66-short-current-core-proof-delta-v1'


def pin(path):
    return dict(path=str(path), sha256=sha256(path.read_bytes()).hexdigest())


def read(path):
    return json.loads(path.read_bytes())


def evidence(number):
    path, = OPS.glob(f'PG{number}-*/manifest.json')
    document = read(path)
    assert document['actualExit'] == 0
    return (pin(path), document)


def main():
    start, = PMO.glob('601_*/1588_*.json')
    context = read(start)
    core = context['values']['productionCoreMain']
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip() == context['values']['source']
    review = read(REVIEW)
    prior_receipt, prior = evidence(40850)
    assert compat_review(review, prior)
    holdings = {row['id']: row for row in prior['rows']}
    numbers = (41074, 41148, 41102, 41144, 41146, 41154, 41078, 41158, 41160, 41162, 41128)
    proofs = {n: evidence(n) for n in numbers}
    data = {n: value for n, (_, value) in proofs.items()}
    current_core_fields = {
        41074: 'source', 41148: 'currentProductCore', 41102: 'productionCore', 41144: 'productionCore',
        41146: 'core', 41154: 'productionCore', 41078: 'productionCore', 41160: 'productionCore',
        41128: 'productionCore',
    }
    assert all(data[n][field] == core for n, field in current_core_fields.items())
    assert data[41158]['toolSource'] == data[41160]['toolSource'] == data[41162]['source']
    assert data[41148]['unknownInternalEdges'] == 0 and data[41148]['prohibitedProductEdges'] == []
    assert data[41154]['combinedTestCount'] is None and data[41078]['actualDBStarted'] == 0
    assert data[41158]['unexpected'] == 0 and data[41160]['actualNative'] == data[41128]['actualChr'] == 0
    proof_deltas = {
        'F02': ([41074, 41148], dict(packaged=1 + len(data[41074]['savedUnchangedLibraryReferences']),
              totalModules=6, checkedBatchPhysical=data[41148]['qualifiedBatchPhysical'],
              totalBatchPhysical=data[41074]['currentClassNames']),
             'QA-056適用範囲、正規API／Web JAR、Storage旧JDBC一辺とSSC461、同候補13要求の実runtime'),
        'F03': ([41102, 41144, 41146], dict(sourceStyle=data[41102]['sourceTotals'],
              typedBatchPhysical=data[41144]['verifiedPhysical'], typedBatchHeld=data[41144]['holdOrTransitive'],
              pmdAlreadyClassifiedSourceFiles=data[41146]['diffMainCount']),
             'Test保留32、QA-056四型と型付き静的の全六、Root11、PMDの未成立範囲と全451'),
        'P004-03': ([41154], dict(scopedOwners=data[41154]['threeScopedOwners'],
              heldOwners=data[41154]['otherOwnersHeld'], currentDaoTests=data[41154]['currentBorrowingAndValueTests']),
             'DurableRecordFiles／MaintenanceRunFilesの実原本と所有・退役、業務DB後条件'),
        'P004-05': ([41078], dict(localOwners=2, wholeOwners=4, currentBorrowedOutboxTests=data[41078]['tests']),
             'ApiJdbcPool／JdbcSyncRequestProcessor、実PostgreSQL role、UTC・取引境界・資源・監査後条件'),
        'P018-08': ([41158, 41160, 41162], dict(localToolCases=len(data[41158]['cases']),
              retainedStreams=len(data[41160]['results']), actualNative=data[41160]['actualNative']),
             '現候補の正規native capture、三子の正常・異常・停止、同sourceの真正owner・終端・CRC/session'),
        'P020-01': ([41128], dict(verifiedComparisonToolTests=data[41128]['completedTests'],
              verifiedExecutableCrcs=data[41128]['executableCrcsVerified'], actualChr=data[41128]['actualChr']),
             '現候補の真正Current/NKとBrowser、QA051 final、全三子とG01～G06'),
    }
    rows = []
    for key, original in holdings.items():
        item = dict(id=key, criteria=original['requiredCriteria'],
                    exitDecision=original['originalParent']['終了判断ID'], status='NOT_ACCEPTED',
                    countedAsNew=0, remainingFirstEvidence=original['remainingFirstEvidence'],
                    existingProofInheritedFrom=prior_receipt, commonReleaseAnd451Required=True)
        if key in proof_deltas:
            ns, evidence_counts, next_evidence = proof_deltas[key]
            item.update(localEvidence=[proofs[n][0] for n in ns], measured=evidence_counts,
                        remainingFirstEvidence=next_evidence)
        rows.append(item)
    output = OPS / RUN
    output.mkdir()
    record = dict(actualExit=0, terminalAtUTC=datetime.now(timezone.utc).isoformat(), core=core,
                  oldCore=prior['core'], initialPlan=pin(REVIEW), shortPlanPricePp=143.371,
                  oldCriteria=prior_receipt, rows=rows, priorUniqueCriteria=prior['uniqueCriteria'],
                  originalAccepted=17, newAccepted=0, coreAccepted=0, designatedAccepted=0, effortRate=None,
                  currentMinimumAllConditionsMet=False, recipientsAcknowledged=None,
                  estimatedAtGroupStart=context['values']['estimateAtGroupStartPp'],
                  replayedTests=0, runtimeOperations=0, acceptanceChange=0,
                  allocatedActualCostPp=None, remainingCostReestimatePp=None,
                  duplicateWorkIdCountedOnce='WBS-P018-10.03/1', duplicateWorkIdSinglePricePp=0.35)
    target = output / 'manifest.json'
    with target.open('x') as stream:
        json.dump(record, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(pin(target))


def compat_review(review, prior):
    assert review['baseline']['accepted'] == prior['originalAccepted'] == 17
    assert review['baseline']['originalItems'] == 190
    assert review['costBoundary']['cumulativeThroughAllTargetsPp'] == 143.371
    assert set(review['finalTarget']['ids']) == {row['id'] for row in prior['rows']}
    assert prior['uniqueCriteria'] == 59
    assert prior['coreAccepted'] == prior['shortAccepted'] == 0
    assert next(r for r in prior['rows'] if r['id'] == 'P019-02')['requiredCriteria'] == []
    return True


if __name__ == '__main__':
    main()
