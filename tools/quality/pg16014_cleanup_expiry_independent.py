"""Literal wire oracle and exact normal TestID bindings, independent of production methods."""
import copy
import hashlib
import json
import re
import textwrap
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg16010_cleanup_expiry_whole16_pt as original

OUT = data.BASE / 'PG16014-cleanup-expiry-independent-v1'
POST = '431ee399b3846c5d2e920482dd9b00aec55346644764276bf83d8bfd33bf3112'
BASE = 'NKEXPIRY1\nrun=38100000-2222-4333-8444-555555555555\nactivation=38100000-6666-4777-8888-999999999999\ncutoff=2026-09-30T00:00:00Z\nboot=38100000-3333-4333-8444-555555555555\nepoch=38100000-4444-4333-8444-555555555555\nbroker=11111111111111111111111111111111\nstep_id=42\nattempt=1\nstarted=2026-09-30T00:00:01Z\nskipped=false\n'
SKIP = 'NKEXPIRYSKIP2\nrun=38100000-2222-4333-8444-555555555555\nactivation=38100000-6666-4777-8888-999999999999\ncutoff=2026-09-30T00:00:00Z\nboot=38100000-3333-4333-8444-555555555555\nepoch=38100000-4444-4333-8444-555555555555\nbroker=11111111111111111111111111111111\nstep_id=43\nattempt=2\nstarted=2026-09-30T00:00:03Z\nskipped=true\nprior_run_id=38100000-2222-4333-8444-555555555555\nprior_cutoff_utc=2026-09-30T00:00:00Z\nprior_step_id=42\nprior_attempt=1\nprior_started=2026-09-30T00:00:01Z\nprior_ended=2026-09-30T00:00:02Z\n'
CLEANUP = 'NKCLEAN1\nrun=31100027-2222-4333-8444-555555555555\nactivation=31100027-6666-4777-8888-999999999999\ncutoff=2026-09-27T15:00:00Z\nmanifest=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef\n'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def assess(p, expected_cases):
    require(p['source'] == original.SOURCE and p['actualExit'] == 0 and (p['tests'], p['suites']) == (16, 3), 'same source16/3 actual success')
    require(p['singleSession'] is True and p['sessionIdentity'] == original.SESSION and p['crcMismatch'] == p['forbiddenProductProbeHits'] == 0, 'one CRC/session and held absence')
    require(p['completeSourceUnitClosure'] == original.CLOSURES and p['metadataClasses'] == p['unexecutedCodeClasses'] == p['manualCounterExclusions'] == [], 'whole one Source allthree Code classes')
    require(p['totals'] == {name: dict(covered=count, missed=0) for name, count in [('LINE', 150), ('METHOD', 18), ('CLASS', 3), ('BRANCH', 108)]} and p['targetUnitFour100'] is True and p['strictFour100GateExit'] == 0, 'full measured four counters')
    require(len(p['cases']) == len({(r['classname'], r['name']) for r in p['cases']}) == 16 and {(r['classname'], r['name']) for r in p['cases']} == expected_cases and all(r['result'] == 'PASS' for r in p['cases']), 'exact original ordinary Test methods, not additions')
    for field in ('oldCoverageTransferred', 'priorProductResultsReused', 'sourceChanged', 'whole451Accepted', 'wholeF03Accepted', 'formalUpdated', 'actualSecretKeysLoaded', 'actualCredentialValuesUsed', 'actualAuthenticationOrSessionIssued', 'realRootObjectsOrFactoryCreated', 'actualRetainedAuditOrExpiryDeletionInvoked', 'actualFilesOpenedByProduct', 'actualPrivateFilesOpened', 'testOwnedTemporaryFileIo', 'rootMainInvoked', 'actualJdbcBackendConnected'):
        require(p[field] is False, 'no old authority/PASS/undeclared effect: ' + field)
    require(p['cryptoOrKeyOperationsInvoked'] is p['syntheticUuidEntropyUsed'] is p['onlyPublicDataCodecsAndIdentityValues'] is True and p['cryptoOperationKind'] == 'JDK_UUID_RANDOM_UUID_FOR_SYNTHETIC_TEST_FIXTURES_ONLY' and p['ownVirtualTaskCount'] == 2, 'original synthetic UUID entropy/two tasks disclosed')
    for field in ('failures', 'errors', 'skipped', 'reruns', 'newTestIds', 'newAccepted', 'productTestsReexecutedByPost', 'actualVmActions', 'actualDatabaseActions', 'actualServiceActions', 'actualNetworkActions', 'actualJdbcMethodsInvoked', 'actualSqlStatementsPreparedOrExecuted'):
        require(type(p[field]) is int and p[field] == 0, 'zero actual effect/counter, not bool: ' + field)
    require(p['effortPercent'] is None and all(row[-1] == '0' for row in p['passiveNativeBoundaryAbsence']['rows']), 'unknown effort and six native absences')


def check_oracles(values):
    require(values == dict(expiry=BASE, skipped=SKIP, cleanup=CLEANUP), 'exact three independently specified golden vectors')
    require(len(BASE.splitlines()) == 11 and len(SKIP.splitlines()) == 17 and len(CLEANUP.splitlines()) == 5, 'fixed field/header counts')
    for value in values.values():
        require(value.endswith('\n') and value.isascii() and '\r' not in value and '\0' not in value, 'ASCII/LF only')


def main():
    invocation = capture(__file__)
    require(not OUT.exists(), 'new-only')
    p = data.read_checked(data.BASE / 'PG16012-cleanup-expiry-whole16-post-v1/manifest.json', POST)
    decl = data.read_checked(data.BASE / 'PG15950-g13-current-test-declaration-inventory-v1/manifest.json', '0173083ac6c1ed92d23a3fad673afc7d545186d718353366398c1ecd28c6c139')
    bindings = data.read_checked(data.BASE / 'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json', decl['files']['exact-ordinary-bindings.json'])
    classes = {'dev.codex.schubert.nk.batch.platform.' + name for name in original.TESTS}
    expected = {(r['className'], r['method']) for r in bindings if r['className'] in classes}
    require(len(expected) == 16 and all(data.sha(file.read_bytes()) == original.TEST_HASHES[name] for name, file in original.TESTS.items()), 'same whole original normal declarations/bytes')
    expiry = original.TESTS['ExpiryWorkerRequestTest'].read_text()
    values = {}
    for field, target in [('GOLDEN', 'expiry'), ('SKIP_GOLDEN', 'skipped')]:
        match = re.search(r'static final String ' + field + r' =\s*"""\n(.*?)      """;', expiry, re.S)
        require(match is not None, 'fixed reviewed Test textblock')
        values[target] = textwrap.dedent(match.group(1))
    cleanup = original.TESTS['CleanupWorkerRequestTest'].read_text()
    declaration = cleanup.split('private static final String GOLDEN =', 1)[1].split(';', 1)[0]
    values['cleanup'] = ''.join(json.loads(literal) for literal in re.findall(r'"(?:[^"\\]|\\.)*"', declaration))
    check_oracles(values)
    assess(p, expected)
    negatives = []
    for field, value in [('source', '0' * 40), ('tests', 15), ('totals', {}), ('singleSession', False), ('targetUnitFour100', False), ('crcMismatch', 1), ('manualCounterExclusions', ['outer']), ('oldCoverageTransferred', True), ('priorProductResultsReused', True), ('whole451Accepted', True), ('newAccepted', True), ('newTestIds', 16), ('effortPercent', 100), ('cryptoOrKeyOperationsInvoked', False), ('syntheticUuidEntropyUsed', False), ('actualSecretKeysLoaded', True), ('ownVirtualTaskCount', 0), ('actualJdbcBackendConnected', True), ('rootMainInvoked', True), ('forbiddenProductProbeHits', 1)]:
        bad = copy.deepcopy(p)
        bad[field] = value
        try:
            assess(bad, expected)
        except ValueError:
            negatives.append(field)
        else:
            raise ValueError('unrejected field: ' + field)
    for label, change in [('missing-case', lambda v: v['cases'].pop()), ('failed-case', lambda v: v['cases'][0].update(result='FAIL')), ('duplicate-case', lambda v: v['cases'].append(copy.deepcopy(v['cases'][0]))), ('missing-outer', lambda v: v['completeSourceUnitClosure'][original.NAME].remove(original.NAME))]:
        bad = copy.deepcopy(p)
        change(bad)
        try:
            assess(bad, expected)
        except ValueError:
            negatives.append(label)
        else:
            raise ValueError('unrejected structure: ' + label)
    oracle_negatives = []
    for name, wrong in [('expiry', BASE[:-1]), ('skipped', SKIP.replace('SKIP2', 'SKIP1')), ('cleanup', CLEANUP.replace('manifest=', 'digest=')), ('expiry', BASE.replace('step_id=42', 'step_id=042')), ('skipped', SKIP.replace('prior_attempt=1', 'prior_attempt=2'))]:
        bad = dict(values)
        bad[name] = wrong
        try:
            check_oracles(bad)
        except ValueError:
            oracle_negatives.append(name)
        else:
            raise ValueError('unrejected independent golden mutation')
    verify(p['invocation'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json', dict(actualExit=0, invocation=invocation, source=original.SOURCE,
        postSha256=POST, tests=16, newUniqueMethods=16, normalOrdinaryTestSourceDomain=True,
        semanticNegativeVectors=len(negatives), independentOracleNegativeVectors=len(oracle_negatives),
        literalVectors={name: dict(bytes=len(value.encode('ascii')), sha256=hashlib.sha256(value.encode('ascii')).hexdigest()) for name, value in values.items()},
        targetUnitFour100=True, fullSourcePrograms=1, allPhysicalClasses=3,
        helpersNotReaccepted=True, syntheticUuidEntropyUsed=True, actualAuthorizationIssued=False,
        productTestsExecutedByIndependent=0, oldRuntimeTransferred=False, whole451Accepted=False,
        wholeF03Accepted=False, newAccepted=0, formalUpdated=False, effortPercent=None, externalActions=0))
    print(data.sha((OUT / 'manifest.json').read_bytes()))
    print(json.dumps(dict(actualExit=0, semanticNegativeVectors=len(negatives), independentOracleNegativeVectors=len(oracle_negatives))))


if __name__ == '__main__':
    main()
