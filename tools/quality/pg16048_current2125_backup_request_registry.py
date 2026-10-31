"""Add original public Backup codec9 and one complete Source, preserving every old proof/cost/history."""
from collections import Counter
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from trace_owner_join import canonical

SOURCE = '6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV = ('PG16032-current2116-failed-profile-registry-v1', 'a8a019d0f660dba06a1d5b137ae2d0af77b6b2a9e5d1cbf9501054b768ab372a')
PREV_POST = ('PG16034-current2116-failed-profile-registry-post-v1', 'c3118ee60747bab0a770902a3aa6c49a3fd44d2acbca9850feb6fcf72081d3ca')
POST = ('PG16044-backup-public-request-whole9-post-v1', 'b3445a0312322fbd7e5f81e10dd4dcd7492a052fa76bc78250612dbf34a23109')
INDEPENDENT = ('PG16046-backup-public-request-independent-v1', '68e21c5b9421aaff03fcc58650a71e6d8e96fc14d42f2954b7f39b093e916cc0')
NAME = 'dev/codex/schubert/nk/batch/platform/BackupWorkerRequest'
SCOPE = 'ORIGINAL_BACKUP_PUBLIC_REQUEST9_ONE_WHOLE_SOURCE_TWO_CODE_CLASSES_NO_AUTHORITY'
OUT = data.BASE / 'PG16048-current2125-backup-request-registry-v1'


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
    require(q['semanticNegativeVectors'] == 24 and q['independentOracleNegativeVectors'] == 5 and p['tests'] == q['tests'] == 9 and p['suites'] == 1, 'whole original9/1 and independent literal oracle')
    require(p['targetUnitFour100'] is p['singleSession'] is True and p['crcMismatch'] == p['forbiddenProductProbeHits'] == 0 and p['metadataClasses'] == [], 'whole source same exec/session/CRC')
    require(p['onlyPublicDataCodecsAndIdentityValues'] is p['onlyNonsecretBackupRequestByteContracts'] is q['helpersNotReaccepted'] is True and q['actualAuthorizationIssued'] is False, 'public request bytes/formatting, not authority')
    require(p['actualSecretKeysLoaded'] is p['actualCredentialValuesUsed'] is p['actualJdbcBackendConnected'] is p['rootMainInvoked'] is False, 'no private backend or Root action')
    require(set(p['fullSourceUnits']) == {NAME} and NAME not in old['fullSourceUnits'], 'new one entire Source only')
    result = copy.deepcopy(old)
    cases = {(r['classname'], r['name']) for r in old['cases']}
    added = {(r['classname'], r['name']) for r in p['cases']}
    require(len(added) == 9 and not added & cases and all(r['result'] == 'PASS' for r in p['cases']), 'no double counted methods')
    cases |= added
    unit = p['fullSourceUnits'][NAME]
    require(len(unit['physical']) == 2 and unit['physical'] == p['completeSourceUnitClosure'][NAME] and unit['four100'] is True and unit['totals'] == p['totals'], 'full two-physical denominator')
    result['fullSourceUnits'][NAME] = dict(post=POST[0], postSha256=POST[1], physical=copy.deepcopy(unit['physical']), counters=copy.deepcopy(unit['totals']), four100=True, execSha256=p['execSha256'], sessionIdentity=p['sessionIdentity'], metadataOnly=False, branchNaturallyZero=False)
    logical = {r['path']: r for r in json.loads((data.ROOT / 'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for path, row in p['owners'].items():
        require(data.sha((data.ROOT / path).read_bytes()) == row['sha256'] and all(row[k] == v for k, v in canonical(path, logical).items()), 'actual canonical logical ownership, not dynamic permission')
        require(path not in result['owners'] or result['owners'][path] == row, 'all old owner rows unchanged')
        result['owners'][path] = copy.deepcopy(row)
    result['originalPostReferences'].append(dict(name=POST[0], sha256=POST[1], tests=9, suites=1, execSha256=p['execSha256'], sessionIdentity=p['sessionIdentity'], scope=SCOPE))
    units = result['fullSourceUnits']
    physical = {n for u in units.values() for n in u['physical']}
    four = {n for u in units.values() if u['four100'] for n in u['physical']}
    require(len(physical) == sum(len(u['physical']) for u in units.values()), 'all Source closures disjoint')
    updates = dict(previousUniqueRegistryReference=list(PREV), previousRegistryPostReference=list(PREV_POST), cases=[dict(classname=c, name=n) for c, n in sorted(cases)], suiteNames=sorted({c for c, n in cases}), tests=len(cases), suites=len({c for c, n in cases}), originalExecs=old['originalExecs'] + 1, totalProductExecs=old['totalProductExecs'] + 1, totalMethodExecutions=old['totalMethodExecutions'] + 9, uniqueProductMethodDelta=9, newTestIds=9, sourceProgramDelta=1, measuredSourcePrograms=len(units), measuredPhysical=len(physical), executablePhysical=len(physical - result['metadataClasses'].keys()), four100SourcePrograms=sum(u['four100'] for u in units.values()), four100Physical=len(four), four100ExecutablePhysical=len(four - result['metadataClasses'].keys()), ownerStatusCounts=dict(Counter(r['ownershipStatus'] for r in result['owners'].values())), unknownOwnerPaths=sum(r['canonicalOwner'] is None for r in result['owners'].values()), lastUpdateKind='CURRENT_SOURCE_ORIGINAL_TEST_ADDITION_WITH_DISCLOSURE_HISTORY_RETAINED')
    result.update(updates, invocation=invocation)
    require((result['tests'], result['suites'], len(units), len(physical), result['executablePhysical'], result['four100SourcePrograms'], len(four), result['four100ExecutablePhysical'], result['incompleteSourcePrograms'], result['totalProductExecs'], result['totalMethodExecutions'], result['totalRepeatedOriginalMethods']) == (2125, 284, 477, 662, 623, 256, 374, 363, 39, 127, 2257, 132), 'derived complete addition, old incomplete domains unchanged')
    require(result['ownerStatusCounts'] == dict(BASELINE_LOGICAL_REFERENCE=392, NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED=229, UNKNOWN=167), 'one baseline Source and one explicit UNKNOWN Test owner')
    decl = copy.deepcopy(old['currentOrdinaryTestDeclarationReference'])
    inventory = read(('PG15950-g13-current-test-declaration-inventory-v1', decl['inventoryManifestSha256']))
    bindings = data.read_checked(data.BASE / 'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json', inventory['files']['exact-ordinary-bindings.json'])
    keys = {(r['className'], r['method']) for r in bindings}
    require(len(keys) == 5786 and added <= keys and len(cases & keys) == 2116 and len(cases - keys) == 9, 'normal ordinary versus separate quality fixtures')
    decl.update(ordinaryCaseReferences=2116, ordinaryWithoutCurrentCaseReference=3670)
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
