"""Catalog local criteria evidence, with unresolved same-source dependencies explicitly held."""
import hashlib
import json
import os
from pg5940_private_lock_compile import ROOT, BASE, sha
from pg6818_current_counter_delta import explicit_four100
from pg6092_current3985_static_join import source_case_candidates
from pg6892_original4213_artifacts import read_whole

MAIN = 'src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/transport/BrokerTopology.java'
TEST = 'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/transport/BrokerTopologyTest.java'
METHODS = ('sixDestinationsMatchTheIndependentPhysicalAndLimitOracle', 'nullUnknownAndNearMatchAddressesAreDenied')
CLASS = 'dev.codex.schubert.nk.protocol.transport.BrokerTopologyTest'


def check_scope(task):
    if task['ownedArtifacts'] != [MAIN] or task['sharedClassReferences'] or task['dependencies'] != ['WBS-P002-03', 'WBS-C04']:
        raise ValueError('one actual catalog scope and unchanged exit dependencies')


def join_cases(text, cases):
    rows = []
    for method in METHODS:
        digest = hashlib.sha256(source_case_candidates(text, method)[0].encode()).hexdigest()
        found = [c for c in cases if c['class'] == CLASS and c['caseNameSha256'] == digest]
        if len(found) != 1:
            raise ValueError('one actual original full case per catalog method')
        rows.append(dict(testId='PT-JMS-002/005', method=method, bodySha256=digest, originalCase=found[0]))
    return rows


def main():
    qp, q, cases = read_whole()
    master = json.loads((ROOT / 'documents/400_PGPT/470_PMO/481_PGPT詳細WBS.json').read_bytes())
    tasks = {r['id']: r for r in master['tasks']}
    task = tasks['WBS-P005-01']
    check_scope(task)
    counter = q['allActualClassCounters']['protocol:dev/codex/schubert/nk/protocol/transport/BrokerTopology.class']
    if not explicit_four100(counter) or sha(ROOT / MAIN) != q['allSourceHashes'][MAIN]:
        raise ValueError('current qualified Main and real positive four100')
    text = (ROOT / TEST).read_text()
    rows = join_cases(text, cases)
    dependencies = [dict(id=d, requiredSource=q['productionSource'], recordedSource=tasks[d]['acceptance']['source'],
      recordedStatus=tasks[d]['acceptance']['status'], result='HOLD_CURRENT_CRITERIA_REVALIDATION') for d in task['dependencies']]
    if any(r['recordedSource'] == q['productionSource'] for r in dependencies):
        raise ValueError('dependency changed: inspect actual criteria instead of stale HOLD label')
    value = dict(actualExit=0, source=q['productionSource'], wbs='WBS-P005-01', currentQualificationSha256=sha(qp),
      mainPath=MAIN, mainSha256=sha(ROOT / MAIN), testPath=TEST, testSha256=sha(ROOT / TEST), actualCounters=counter,
      independentOracle='SS321 section4 hand six-vector in BrokerTopologyTest; full explicit table in1509, not production expected',
      independentOriginalCaseJoins=rows, localScopeChecked=True, requirementsProjectionOnly=['MQ-001', 'MQ-002', 'MQ-003', 'MQ-004', 'MQ-005'],
      wholeRequirementBehaviorNotProvedByCatalog=True, exitDependencies=dependencies,
      acceptance='NOT_ACCEPTED', acceptedLeafDelta=0, formalAccepted=False, effortPercent=None,
      canonicalAcceptanceSource=tasks['WBS-C04']['acceptance']['source'], canonicalChanged=False,
      vmActions=0, testsExecuted=0, ptAlternativeCompleted=0, actualBrokerOperations=0,
      toolSha256=sha(ROOT / 'tools/quality/pg6906_broker_catalog_audit.py'))
    out = BASE / 'PG6906-broker-catalog-audit-v1'
    os.umask(0o077)
    out.mkdir()
    p = out / 'manifest.json'
    with p.open('x') as f:
        json.dump(value, f, sort_keys=True, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, manifestSha256=sha(p), originalCases=2, localFour100=True, exitDependenciesHeld=2, acceptedLeafDelta=0)))


if __name__ == '__main__':
    main()
