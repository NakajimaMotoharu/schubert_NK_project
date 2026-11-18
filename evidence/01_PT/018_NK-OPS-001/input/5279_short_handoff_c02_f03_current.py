"""Build the current four-role handoff from independent immutable public receipts."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess

D = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))
E = Path('evidence/01_PT/018_NK-OPS-001/evidence')
TEST = ('src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/'
        'platform/BrokerJournalValueContractTest.java')


def load(path):
    return json.loads(Path(path).read_bytes())


def ref(path):
    return dict(path=str(path), sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest())


def git(*args):
    return subprocess.check_output(['git', *args], timeout=40)


def main():
    start = load(next(D.glob('600_四担当*.json')))
    v = start['values']
    core = v['productionCoreMain']
    assert git('rev-parse', 'HEAD').decode().strip() == v['source']
    refs = v['oracleReferences']
    assert all(ref(pin['path']) == pin for pin in refs)
    previous, arch, journal, monitors, unit, reader, scan = (load(pin['path']) for pin in refs)
    assert previous['sourceCore'] == core == arch['productionCoreMain'] == journal['sourceCore']
    assert monitors['sourceCore'] == unit['sourceCore'] == reader['productionCoreMain'] == core
    assert git('diff', '--name-status', previous['head'], v['source'], '--', 'src').decode().splitlines() == [
        'A\t' + TEST
    ]
    assert previous['primaryFive'] == 0 and previous['primaryFiveCriteria'] == 25
    assert previous['uniqueShortTerms'] == 11 and previous['allShortCriteria'] == 59
    assert previous['officialAcceptance'] == 17 and previous['officialDenominator'] == 190
    assert previous['ssc447']['rawMiss'] == dict(L=4, M=4, C=0, B=58, I=85)
    assert not previous['ssc447']['appliedToCurrentSource']
    assert arch['correctedCorrect'] == 12 and arch['initialIncorrect'] == 8
    assert unit['files'] == 14 and unit['edges'] == 28 and unit['tests'] == 9
    assert monitors['unclassifiedAfter'] == 34 and monitors['cumulativeApplicableInOriginal45'] == 11
    assert journal['tests'] == journal['firstDynamicSuccess'] == 2
    assert reader['namedCases'] == 8 and set(reader['results'].values()) == {'ok'}
    assert scan['confirmedSecrets'] == scan['unresolvedCandidates'] == 0
    assert not any((arch['wholeF02Accepted'], monitors['wholeF03Accepted'], unit['wholeC02Accepted']))
    f02 = previous['f02'] | dict(architectureToolCanaries=12, initialMissesCorrected=8, toolProof=refs[1])
    f03 = previous['f03'] | dict(nonHeldTest=1104, allTest=1136, addedTestFile=TEST, exactProductTests=2,
          additionalFixtureStatic=0, oldSubsetFindings=45, appliedOpenInSubset=11, unclassifiedInSubset=34,
          exactSourceProof=refs[3], testProof=refs[2])
    c02 = previous['c02'] | dict(localTextChecks=9, declaredOrderingVertices=12, declaredOrderingEdges=28,
          caddyEffectiveDependencyMissing=True, textProof=refs[4])
    result = dict(
        actualExit=0, sourceCore=core, head=v['source'], startEvent=start['eventId'],
        formalIntake=17, formalDenominator=190, officialPT=previous['formalPT'], officialScopes=previous['formalScopes'],
        netNew=0, effortRate=None, shortCoreAccepted=0, shortCoreCount=5, shortCoreCriteria=25,
        shortUniqueCriteria=59, shortUniqueCount=11, shortPlannedPrice=143.371,
        oldSsc447=previous['ssc447'], f02=f02, f03=f03, c02=c02, f04=previous['f04'],
        shortToolReader=dict(newVectors=8, coverageCounted=0, trueNativeAcquired=0, proof=refs[5]),
        latestIntervalScan=refs[6], rolesPublished=['F02', 'F03', 'C02', 'F04'],
        externalReceiverAcknowledgement=None, externalContacts=0, testsRerun=0,
        initialHandoffSetupExit=1, initialHandoffCause='Previous primaryFive stores the accepted count, not the target denominator',
        planPriceDiscountAsCompletion=False, formalUpdated=False, refs=refs,
        terminalAtUTC=datetime.now(timezone.utc).isoformat(), verifier=ref(__file__))
    output = E / v['run']
    output.mkdir()
    path = output / 'manifest.json'
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(ref(path))


if __name__ == '__main__':
    main()
