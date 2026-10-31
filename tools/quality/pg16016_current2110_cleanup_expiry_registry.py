"""Add original codec16 and one complete Source, preserving every old proof/cost/history."""
from collections import Counter
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from trace_owner_join import canonical

SOURCE = '6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV = ('PG15994-current2094-reference-value-registry-v1', '7eaf3d75b2eadf3ab0d38f642333aefff3bb56fd81acd5b31d16d55d02d58a17')
PREV_POST = ('PG15996-current2094-reference-value-registry-post-v1', 'c165c4b430a9d9166cd624d9e15b079624d3bc45b0e040b73da0e231b089a303')
POST = ('PG16012-cleanup-expiry-whole16-post-v1', '431ee399b3846c5d2e920482dd9b00aec55346644764276bf83d8bfd33bf3112')
INDEPENDENT = ('PG16014-cleanup-expiry-independent-v1', 'b52fc6846fb64234481f9ff86f608cfe979aa3c7f791ea56569efd5fcb19156a')
NAME = 'dev/codex/schubert/nk/batch/platform/CleanupWorkerRequest'
SCOPE = 'ORIGINAL_CLEANUP7_EXPIRY7_BOUNDARY2_ONE_WHOLE_SOURCE_THREE_CODE_CLASSES_NO_AUTHORITY'
OUT = data.BASE / 'PG16016-current2110-cleanup-expiry-registry-v1'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(pair):
    return data.read_checked(data.BASE / pair[0] / 'manifest.json', pair[1])


def wire(value):
    return json.dumps(value, sort_keys=True)


def main():
    invocation = capture(__file__)
    require(not OUT.exists(), 'new-only')
    old, prior, p, q = [read(pair) for pair in (PREV, PREV_POST, POST, INDEPENDENT)]
    require(all(v['source'] == SOURCE and v['actualExit'] == 0 for v in (old, prior, p, q)) and prior['registryManifestSha256'] == PREV[1] and prior['metadataNegativeVectors'] == 34 and q['postSha256'] == POST[1], 'all fixed current independent witnesses')
    require(q['semanticNegativeVectors'] == 24 and q['independentOracleNegativeVectors'] == 5 and p['tests'] == q['tests'] == 16 and p['suites'] == 3, 'whole original16/3 and independent literal oracle')
    require(p['targetUnitFour100'] is p['singleSession'] is True and p['crcMismatch'] == p['forbiddenProductProbeHits'] == 0 and p['metadataClasses'] == [], 'whole source same exec/session/CRC')
    require(p['onlyPublicDataCodecsAndIdentityValues'] is p['syntheticUuidEntropyUsed'] is q['syntheticUuidEntropyUsed'] is q['helpersNotReaccepted'] is True and q['actualAuthorizationIssued'] is False, 'disclosed synthetic random values, not authority')
    require(p['actualSecretKeysLoaded'] is p['actualCredentialValuesUsed'] is p['actualJdbcBackendConnected'] is p['rootMainInvoked'] is False, 'no private backend or Root action')
    require(set(p['fullSourceUnits']) == {NAME} and NAME not in old['fullSourceUnits'], 'new one entire Source only')
    result = copy.deepcopy(old)
    cases = {(r['classname'], r['name']) for r in old['cases']}
    added = {(r['classname'], r['name']) for r in p['cases']}
    require(len(added) == 16 and not added & cases and all(r['result'] == 'PASS' for r in p['cases']), 'no double counted methods')
    cases |= added
    unit = p['fullSourceUnits'][NAME]
    require(len(unit['physical']) == 3 and unit['physical'] == p['completeSourceUnitClosure'][NAME] and unit['four100'] is True and unit['totals'] == p['totals'], 'full three-physical denominator')
    result['fullSourceUnits'][NAME] = dict(post=POST[0], postSha256=POST[1], physical=copy.deepcopy(unit['physical']), counters=copy.deepcopy(unit['totals']), four100=True, execSha256=p['execSha256'], sessionIdentity=p['sessionIdentity'], metadataOnly=False, branchNaturallyZero=False)
    logical = {r['path']: r for r in json.loads((data.ROOT / 'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for path, row in p['owners'].items():
        require(data.sha((data.ROOT / path).read_bytes()) == row['sha256'] and all(row[k] == v for k, v in canonical(path, logical).items()), 'actual canonical logical ownership, not dynamic permission')
        require(path not in result['owners'] or result['owners'][path] == row, 'all old owner rows unchanged')
        result['owners'][path] = copy.deepcopy(row)
    result['originalPostReferences'].append(dict(name=POST[0], sha256=POST[1], tests=16, suites=3, execSha256=p['execSha256'], sessionIdentity=p['sessionIdentity'], scope=SCOPE))
    units = result['fullSourceUnits']
    physical = {n for u in units.values() for n in u['physical']}
    four = {n for u in units.values() if u['four100'] for n in u['physical']}
    require(len(physical) == sum(len(u['physical']) for u in units.values()), 'all Source closures disjoint')
    updates = dict(previousUniqueRegistryReference=list(PREV), previousRegistryPostReference=list(PREV_POST), cases=[dict(classname=c, name=n) for c, n in sorted(cases)], suiteNames=sorted({c for c, n in cases}), tests=len(cases), suites=len({c for c, n in cases}), originalExecs=old['originalExecs'] + 1, totalProductExecs=old['totalProductExecs'] + 1, totalMethodExecutions=old['totalMethodExecutions'] + 16, uniqueProductMethodDelta=16, newTestIds=16, sourceProgramDelta=1, measuredSourcePrograms=len(units), measuredPhysical=len(physical), executablePhysical=len(physical - result['metadataClasses'].keys()), four100SourcePrograms=sum(u['four100'] for u in units.values()), four100Physical=len(four), four100ExecutablePhysical=len(four - result['metadataClasses'].keys()), ownerStatusCounts=dict(Counter(r['ownershipStatus'] for r in result['owners'].values())), unknownOwnerPaths=sum(r['canonicalOwner'] is None for r in result['owners'].values()), lastUpdateKind='CURRENT_SOURCE_ORIGINAL_TEST_ADDITION_WITH_DISCLOSURE_HISTORY_RETAINED')
    result.update(updates, invocation=invocation)
    require((result['tests'], result['suites'], len(units), len(physical), result['executablePhysical'], result['four100SourcePrograms'], len(four), result['four100ExecutablePhysical'], result['incompleteSourcePrograms'], result['totalProductExecs'], result['totalMethodExecutions'], result['totalRepeatedOriginalMethods']) == (2110, 281, 474, 657, 618, 253, 369, 358, 39, 125, 2242, 132), 'derived complete addition, old incomplete domains unchanged')
    require(result['ownerStatusCounts'] == dict(BASELINE_LOGICAL_REFERENCE=389, NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED=229, UNKNOWN=164), 'one baseline Source and three explicit UNKNOWN Test owners')
    decl = copy.deepcopy(old['currentOrdinaryTestDeclarationReference'])
    inventory = read(('PG15950-g13-current-test-declaration-inventory-v1', decl['inventoryManifestSha256']))
    bindings = data.read_checked(data.BASE / 'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json', inventory['files']['exact-ordinary-bindings.json'])
    keys = {(r['className'], r['method']) for r in bindings}
    require(len(keys) == 5786 and added <= keys and len(cases & keys) == 2101 and len(cases - keys) == 9, 'normal ordinary versus separate quality fixtures')
    decl.update(ordinaryCaseReferences=2101, ordinaryWithoutCurrentCaseReference=3685)
    result['currentOrdinaryTestDeclarationReference'] = decl
    changed = set(updates) | {'invocation', 'fullSourceUnits', 'owners', 'originalPostReferences', 'currentOrdinaryTestDeclarationReference'}
    require(all(wire(result[k]) == wire(v) for k, v in old.items() if k not in changed) and all(result['fullSourceUnits'][n] == v for n, v in old['fullSourceUnits'].items()) and all(result['owners'][n] == v for n, v in old['owners'].items()), 'all old helpers/histories/corrections/cost/fixtures/formal untouched')
    for value in (old, prior, p, q):
        verify(value['invocation'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json', result)
    print(data.sha((OUT / 'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
