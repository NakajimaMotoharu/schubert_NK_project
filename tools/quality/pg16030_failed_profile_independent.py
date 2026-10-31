"""Independent literal eleven-field/two FAILED-row oracle and original six-method semantics."""
import copy
import datetime
import json
import re
import textwrap
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg16026_failed_profile_whole6_pt as original

POST = '244fabbaa33f6361fe7ac5d21b896b073f29adb0c012aaef1260592fb0807896'
OUT = data.BASE / 'PG16030-failed-profile-independent-v1'
GOLDEN = 'NKCLEANFAIL1\nrun=11111111-2222-4333-8444-555555555555\nactivation=21111111-2222-4333-8444-555555555555\ncutoff=2026-09-27T15:00:00Z\nboot=31111111-2222-4333-8444-555555555555\nepoch=41111111-2222-4333-8444-555555555555\nbackup_invocation=51111111-2222-4333-8444-555555555555\nbackup_started_monotonic=1000000000\nbackup_ended_monotonic=2000000000\nbackup_exit=30\ndatabase=7,4,2026-09-28,2026-09-30T01:02:03.123456Z,2026-09-30T01:02:05.654321Z,FAILED,1,0,1,0,COMMAND_FAILURE,batch command failed\nconfiguration=8,4,2026-09-28,2026-09-30T01:02:03.123456Z,2026-09-30T01:02:05.654321Z,FAILED,1,0,1,0,COMMAND_FAILURE,batch command failed\n'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def golden_contract(value):
    require(value == GOLDEN and value.isascii() and value.endswith('\n') and '\r' not in value, 'independent fixed ASCII/LF vector')
    lines = value.splitlines()
    fields = dict(line.split('=', 1) for line in lines[1:])
    require(len(lines) == 12 and len(fields) == 11 and lines[0] == 'NKCLEANFAIL1', 'fixed eleven data fields')
    db, config = fields['database'].split(','), fields['configuration'].split(',')
    require(len(db) == len(config) == 12 and db[0] == '7' and config[0] == '8' and db[1:] == config[1:], 'independent complete pair values')
    require(db[5:] == ['FAILED', '1', '0', '1', '0', 'COMMAND_FAILURE', 'batch command failed'], 'fixed failed SQL-shaped claims, not SQL execution')
    cutoff = datetime.datetime.fromisoformat(fields['cutoff'])
    require((cutoff + datetime.timedelta(hours=9)).date().isoformat() == db[2] == '2026-09-28', 'independent JST civil-date arithmetic')
    require(int(fields['backup_started_monotonic']) == 1000000000 and int(fields['backup_ended_monotonic']) == 2000000000 and 2**64 - 1 == 18446744073709551615 and int(fields['backup_exit']) == 30, 'literal unsigned bounds and times')


def assess(p, methods):
    require(p['source'] == original.SOURCE and p['actualExit'] == 0 and (p['tests'], p['suites']) == (6, 2), 'same-source whole original6')
    require(p['completeSourceUnitClosure'] == original.CLOSURES and p['metadataClasses'] == p['unexecutedCodeClasses'] == p['manualCounterExclusions'] == [], 'two whole Sources/three actual Code classes')
    require(p['totals'] == {kind: dict(covered=count, missed=0) for kind, count in [('LINE', 93), ('METHOD', 11), ('CLASS', 3), ('BRANCH', 84)]} and p['targetUnitFour100'] is True and p['strictFour100GateExit'] == 0, 'genuine four counters, no excluded Code')
    require(p['singleSession'] is True and p['sessionIdentity'] == original.SESSION and p['crcMismatch'] == p['forbiddenProductProbeHits'] == 0, 'exact own exec/session and held absence')
    require(len(p['cases']) == len({(r['classname'], r['name']) for r in p['cases']}) == 6 and {(r['classname'], r['name']) for r in p['cases']} == methods and all(r['result'] == 'PASS' for r in p['cases']), 'six exact ordinary cases')
    require(p['onlyPublicDataCodecsAndIdentityValues'] is p['onlyPublicLiteralManagerSnapshots'] is True and p['cryptoOperationKind'] == 'NONE_IN_REVIEWED_DOMAIN_BODY', 'only literal parser/immutable values')
    for field in ('cryptoOrKeyOperationsInvoked', 'syntheticUuidEntropyUsed', 'actualSecretKeysLoaded', 'actualCredentialValuesUsed', 'actualAuthenticationOrSessionIssued', 'actualManagerOrSystemctlObservationInvoked', 'actualBackupRecoveryOrRetirementInvoked', 'rootMainInvoked', 'realRootObjectsOrFactoryCreated', 'actualFilesOpenedByProduct', 'actualPrivateFilesOpened', 'actualJdbcBackendConnected', 'oldCoverageTransferred', 'priorProductResultsReused', 'sourceChanged', 'whole451Accepted', 'wholeF03Accepted', 'formalUpdated'):
        require(p[field] is False, 'no undeclared effect/promotion: ' + field)
    for field in ('failures', 'errors', 'skipped', 'reruns', 'newTestIds', 'newAccepted', 'productTestsReexecutedByPost', 'actualVmActions', 'actualDatabaseActions', 'actualServiceActions', 'actualNetworkActions', 'actualJdbcMethodsInvoked', 'actualSqlStatementsPreparedOrExecuted', 'ownVirtualTaskCount'):
        require(type(p[field]) is int and p[field] == 0, 'actual zero not bool: ' + field)
    require(p['effortPercent'] is None and all(row[-1] == '0' for row in p['passiveNativeBoundaryAbsence']['rows']), 'unmeasured effort/six native absences')


def main():
    invocation = capture(__file__)
    require(not OUT.exists(), 'new-only')
    p = data.read_checked(data.BASE / 'PG16028-failed-profile-whole6-post-v1/manifest.json', POST)
    d = data.read_checked(data.BASE / 'PG15950-g13-current-test-declaration-inventory-v1/manifest.json', '0173083ac6c1ed92d23a3fad673afc7d545186d718353366398c1ecd28c6c139')
    bindings = data.read_checked(data.BASE / 'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json', d['files']['exact-ordinary-bindings.json'])
    classes = {'dev.codex.schubert.nk.batch.platform.' + name for name in original.TESTS}
    methods = {(r['className'], r['method']) for r in bindings if r['className'] in classes}
    require(len(methods) == 6 and all(data.sha(file.read_bytes()) == original.TEST_HASHES[name] for name, file in original.TESTS.items()), 'fixed exact normal Test domain')
    for file in original.TESTS.values():
        match = re.search(r'private static final String GOLDEN =\s*"""\n(.*?)      """;', file.read_text(), re.S)
        require(match is not None, 'explicit original Test golden')
        golden_contract(textwrap.dedent(match.group(1)))
    assess(p, methods)
    negatives = []
    for field, value in [('source', '0' * 40), ('tests', 5), ('totals', {}), ('singleSession', False), ('targetUnitFour100', False), ('crcMismatch', 1), ('metadataClasses', [original.PROFILE]), ('manualCounterExclusions', [original.PROFILE]), ('oldCoverageTransferred', True), ('priorProductResultsReused', True), ('whole451Accepted', True), ('newAccepted', True), ('newTestIds', 6), ('effortPercent', 100), ('cryptoOrKeyOperationsInvoked', True), ('actualManagerOrSystemctlObservationInvoked', True), ('actualBackupRecoveryOrRetirementInvoked', True), ('actualJdbcBackendConnected', True), ('rootMainInvoked', True), ('forbiddenProductProbeHits', 1)]:
        bad = copy.deepcopy(p)
        bad[field] = value
        try:
            assess(bad, methods)
        except ValueError:
            negatives.append(field)
        else:
            raise ValueError('unrejected semantic mutation: ' + field)
    for label, mutate in [('missing-case', lambda v: v['cases'].pop()), ('failed-case', lambda v: v['cases'][0].update(result='FAIL')), ('duplicate-case', lambda v: v['cases'].append(copy.deepcopy(v['cases'][0]))), ('missing-Row', lambda v: v['completeSourceUnitClosure'][original.NAME].remove(original.NAME + '$Row'))]:
        bad = copy.deepcopy(p)
        mutate(bad)
        try:
            assess(bad, methods)
        except ValueError:
            negatives.append(label)
        else:
            raise ValueError('unrejected semantic structure: ' + label)
    oracle_negatives = []
    for label, value in [('LF', GOLDEN[:-1]), ('row-status', GOLDEN.replace('FAILED,1', 'SUCCESS,1')), ('same-id', GOLDEN.replace('configuration=8,4', 'configuration=7,4')), ('JST-date', GOLDEN.replace('2026-09-28,', '2026-09-27,')), ('canonical-exit', GOLDEN.replace('backup_exit=30', 'backup_exit=030'))]:
        try:
            golden_contract(value)
        except ValueError:
            oracle_negatives.append(label)
        else:
            raise ValueError('unrejected golden mutation: ' + label)
    verify(p['invocation'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json', dict(actualExit=0, invocation=invocation, source=original.SOURCE,
        postSha256=POST, tests=6, newUniqueMethods=6, normalOrdinaryTestSourceDomain=True,
        semanticNegativeVectors=len(negatives), independentOracleNegativeVectors=len(oracle_negatives),
        literalGolden=dict(bytes=len(GOLDEN.encode('ascii')), sha256=data.sha(GOLDEN.encode('ascii'))),
        targetUnitFour100=True, fullSourcePrograms=2, allPhysicalClasses=3, helpersNotReaccepted=True,
        onlyPublicLiteralManagerSnapshots=True, actualAuthorizationIssued=False,
        productTestsExecutedByIndependent=0, oldRuntimeTransferred=False, whole451Accepted=False,
        wholeF03Accepted=False, newAccepted=0, formalUpdated=False, effortPercent=None, externalActions=0))
    print(data.sha((OUT / 'manifest.json').read_bytes()))
    print(json.dumps(dict(actualExit=0, semanticNegativeVectors=len(negatives), independentOracleNegativeVectors=len(oracle_negatives))))


if __name__ == '__main__':
    main()
