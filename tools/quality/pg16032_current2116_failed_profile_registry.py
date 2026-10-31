"""Add original failed-profile6 and two complete Sources, preserving every old proof/cost/history."""
from collections import Counter
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from trace_owner_join import canonical

SOURCE = '6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV = ('PG16016-current2110-cleanup-expiry-registry-v1', '08f7203d2b16473ec80ff3e17cd80d371890bfdbb14b0e4f8ff7fcce52a4ff25')
PREV_POST = ('PG16018-current2110-cleanup-expiry-registry-post-v1', 'e3d5d125c10ed503e85f44102d37e5d9ab8534041572b6cd29837b8134062864')
POST = ('PG16028-failed-profile-whole6-post-v1', '244fabbaa33f6361fe7ac5d21b896b073f29adb0c012aaef1260592fb0807896')
INDEPENDENT = ('PG16030-failed-profile-independent-v1', '161e7268afa298db85cdd2fb457535ae42b685990e13783fe9455a79f0eb4ca8')
NAME = 'dev/codex/schubert/nk/batch/platform/CleanupFailedBackupRequest'
PROFILE = 'dev/codex/schubert/nk/batch/platform/CleanupProfile'
NAMES = {NAME, PROFILE}
SCOPE = 'ORIGINAL_FAILED_PROFILE4_BOUNDARY2_TWO_WHOLE_SOURCES_THREE_CODE_CLASSES_NO_AUTHORITY'
OUT = data.BASE / 'PG16032-current2116-failed-profile-registry-v1'


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
    require(q['semanticNegativeVectors'] == 24 and q['independentOracleNegativeVectors'] == 5 and p['tests'] == q['tests'] == 6 and p['suites'] == 2, 'whole original6/2 and independent literal oracle')
    require(p['targetUnitFour100'] is p['singleSession'] is True and p['crcMismatch'] == p['forbiddenProductProbeHits'] == 0 and p['metadataClasses'] == [], 'whole source same exec/session/CRC')
    require(p['onlyPublicDataCodecsAndIdentityValues'] is p['onlyPublicLiteralManagerSnapshots'] is q['onlyPublicLiteralManagerSnapshots'] is q['helpersNotReaccepted'] is True and q['actualAuthorizationIssued'] is False, 'literal manager data, not actual observation/authority')
    require(p['actualSecretKeysLoaded'] is p['actualCredentialValuesUsed'] is p['actualJdbcBackendConnected'] is p['rootMainInvoked'] is False, 'no private backend or Root action')
    require(set(p['fullSourceUnits']) == NAMES and not NAMES & old['fullSourceUnits'].keys(), 'new two entire Sources only')
    result = copy.deepcopy(old)
    cases = {(r['classname'], r['name']) for r in old['cases']}
    added = {(r['classname'], r['name']) for r in p['cases']}
    require(len(added) == 6 and not added & cases and all(r['result'] == 'PASS' for r in p['cases']), 'no double counted methods')
    cases |= added
    for name, unit in p['fullSourceUnits'].items():
        require(unit['physical'] == p['completeSourceUnitClosure'][name] and unit['four100'] is True, 'whole Source closure including static interface Code')
        result['fullSourceUnits'][name] = dict(post=POST[0], postSha256=POST[1], physical=copy.deepcopy(unit['physical']), counters=copy.deepcopy(unit['totals']), four100=True, execSha256=p['execSha256'], sessionIdentity=p['sessionIdentity'], metadataOnly=False, branchNaturallyZero=False)
    require(sum(len(u['physical']) for u in p['fullSourceUnits'].values()) == 3, 'all three target physical classes')
    logical = {r['path']: r for r in json.loads((data.ROOT / 'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for path, row in p['owners'].items():
        require(data.sha((data.ROOT / path).read_bytes()) == row['sha256'] and all(row[k] == v for k, v in canonical(path, logical).items()), 'actual canonical logical ownership, not dynamic permission')
        require(path not in result['owners'] or result['owners'][path] == row, 'all old owner rows unchanged')
        result['owners'][path] = copy.deepcopy(row)
    result['originalPostReferences'].append(dict(name=POST[0], sha256=POST[1], tests=6, suites=2, execSha256=p['execSha256'], sessionIdentity=p['sessionIdentity'], scope=SCOPE))
    units = result['fullSourceUnits']
    physical = {n for u in units.values() for n in u['physical']}
    four = {n for u in units.values() if u['four100'] for n in u['physical']}
    require(len(physical) == sum(len(u['physical']) for u in units.values()), 'all Source closures disjoint')
    updates = dict(previousUniqueRegistryReference=list(PREV), previousRegistryPostReference=list(PREV_POST), cases=[dict(classname=c, name=n) for c, n in sorted(cases)], suiteNames=sorted({c for c, n in cases}), tests=len(cases), suites=len({c for c, n in cases}), originalExecs=old['originalExecs'] + 1, totalProductExecs=old['totalProductExecs'] + 1, totalMethodExecutions=old['totalMethodExecutions'] + 6, uniqueProductMethodDelta=6, newTestIds=6, sourceProgramDelta=2, measuredSourcePrograms=len(units), measuredPhysical=len(physical), executablePhysical=len(physical - result['metadataClasses'].keys()), four100SourcePrograms=sum(u['four100'] for u in units.values()), four100Physical=len(four), four100ExecutablePhysical=len(four - result['metadataClasses'].keys()), ownerStatusCounts=dict(Counter(r['ownershipStatus'] for r in result['owners'].values())), unknownOwnerPaths=sum(r['canonicalOwner'] is None for r in result['owners'].values()), lastUpdateKind='CURRENT_SOURCE_ORIGINAL_TEST_ADDITION_WITH_DISCLOSURE_HISTORY_RETAINED')
    result.update(updates, invocation=invocation)
    require((result['tests'], result['suites'], len(units), len(physical), result['executablePhysical'], result['four100SourcePrograms'], len(four), result['four100ExecutablePhysical'], result['incompleteSourcePrograms'], result['totalProductExecs'], result['totalMethodExecutions'], result['totalRepeatedOriginalMethods']) == (2116, 283, 476, 660, 621, 255, 372, 361, 39, 126, 2248, 132), 'derived complete addition, old incomplete domains unchanged')
    require(result['ownerStatusCounts'] == dict(BASELINE_LOGICAL_REFERENCE=391, NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED=229, UNKNOWN=166), 'two baseline Sources and two explicit UNKNOWN Test owners')
    decl = copy.deepcopy(old['currentOrdinaryTestDeclarationReference'])
    inventory = read(('PG15950-g13-current-test-declaration-inventory-v1', decl['inventoryManifestSha256']))
    bindings = data.read_checked(data.BASE / 'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json', inventory['files']['exact-ordinary-bindings.json'])
    keys = {(r['className'], r['method']) for r in bindings}
    require(len(keys) == 5786 and added <= keys and len(cases & keys) == 2107 and len(cases - keys) == 9, 'normal ordinary versus separate quality fixtures')
    decl.update(ordinaryCaseReferences=2107, ordinaryWithoutCurrentCaseReference=3679)
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
