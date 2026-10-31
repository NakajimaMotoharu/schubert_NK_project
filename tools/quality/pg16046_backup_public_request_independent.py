"""Literal wire oracle and exact normal TestID bindings, independent of production methods."""
import copy
import hashlib
import datetime
import json
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg16042_backup_public_request_whole9_pt as original

OUT = data.BASE / 'PG16046-backup-public-request-independent-v1'
POST = 'b3445a0312322fbd7e5f81e10dd4dcd7492a052fa76bc78250612dbf34a23109'
BASE = 'NKBACKUP1\nrun=11111111-2222-4333-8444-555555555555\nstarted=2026-09-27T14:59:59.123456Z\n'
VERIFY = 'NKBACKUPVERIFY1\nrun=11111111-2222-4333-8444-555555555555\nstarted=2026-09-27T14:59:59.123456Z\nmanifest_sha256=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\ndump_size=3\ndump_sha256=ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad\n'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def assess(p, expected_cases):
    require(p['source'] == original.SOURCE and p['actualExit'] == 0 and (p['tests'], p['suites']) == (9, 1), 'same source16/3 actual success')
    require(p['singleSession'] is True and p['sessionIdentity'] == original.SESSION and p['crcMismatch'] == p['forbiddenProductProbeHits'] == 0, 'one CRC/session and held absence')
    require(p['completeSourceUnitClosure'] == original.CLOSURES and p['metadataClasses'] == p['unexecutedCodeClasses'] == p['manualCounterExclusions'] == [], 'whole one Source allthree Code classes')
    require(p['totals'] == {name: dict(covered=count, missed=0) for name, count in [('LINE', 61), ('METHOD', 8), ('CLASS', 2), ('BRANCH', 52)]} and p['targetUnitFour100'] is True and p['strictFour100GateExit'] == 0, 'full measured four counters')
    require(len(p['cases']) == len({(r['classname'], r['name']) for r in p['cases']}) == 9 and {(r['classname'], r['name']) for r in p['cases']} == expected_cases and all(r['result'] == 'PASS' for r in p['cases']), 'exact original ordinary Test methods, not additions')
    for field in ('oldCoverageTransferred', 'priorProductResultsReused', 'sourceChanged', 'whole451Accepted', 'wholeF03Accepted', 'formalUpdated', 'actualSecretKeysLoaded', 'actualCredentialValuesUsed', 'actualAuthenticationOrSessionIssued', 'realRootObjectsOrFactoryCreated', 'actualRetainedAuditOrExpiryDeletionInvoked', 'actualFilesOpenedByProduct', 'actualPrivateFilesOpened', 'testOwnedTemporaryFileIo', 'rootMainInvoked', 'actualJdbcBackendConnected'):
        require(p[field] is False, 'no old authority/PASS/undeclared effect: ' + field)
    require(p['cryptoOrKeyOperationsInvoked'] is p['syntheticUuidEntropyUsed'] is p['actualBackupArchivesReadOrWritten'] is False and p['onlyNonsecretBackupRequestByteContracts'] is p['jdkTimezoneRulesFormattingUsed'] is p['ownFourThreadExecutorUsed'] is True and p['cryptoOperationKind'] == 'NONE_IN_REVIEWED_DOMAIN_BODY' and p['ownVirtualTaskCount'] == 0 and p['ownExecutorTaskCount'] == 32, 'only public bytes, JDK formatting and own4thread32tasks')
    for field in ('failures', 'errors', 'skipped', 'reruns', 'newTestIds', 'newAccepted', 'productTestsReexecutedByPost', 'actualVmActions', 'actualDatabaseActions', 'actualServiceActions', 'actualNetworkActions', 'actualJdbcMethodsInvoked', 'actualSqlStatementsPreparedOrExecuted'):
        require(type(p[field]) is int and p[field] == 0, 'zero actual effect/counter, not bool: ' + field)
    require(p['effortPercent'] is None and all(row[-1] == '0' for row in p['passiveNativeBoundaryAbsence']['rows']), 'unknown effort and six native absences')


def check_oracles(values):
    require(values == dict(ordinary=BASE, verification=VERIFY), 'two independent complete ASCII vectors')
    require(len(BASE.splitlines()) == 3 and len(VERIFY.splitlines()) == 6, 'fixed original field counts')
    require(hashlib.sha256(b'abc').hexdigest() == VERIFY.split('dump_sha256=')[1].strip(), 'independent standard hash vector')
    for value in values.values():
        require(value.endswith('\n') and value.isascii() and '\r' not in value and '\0' not in value, 'ASCII LF only')
    t = datetime.datetime.fromisoformat('2026-09-27T14:59:59.123456Z') + datetime.timedelta(hours=9)
    require(t.strftime('%Y%m%d-%H%M%S') == '20260927-235959', 'modern explicit plus9hours directory literal')
    # Arithmetic of the approved fixed boundary vector, not a claim to qualify all JDK tzdb.
    require(14 * 3600 + 41 * 60 + 1 + 33539 == 86400 and (15 * 3600 + 33539) % 86400 == 18 * 60 + 59, 'fixed year0 boundary-vector arithmetic')


def main():
    invocation = capture(__file__)
    require(not OUT.exists(), 'new-only')
    p = data.read_checked(data.BASE / 'PG16044-backup-public-request-whole9-post-v1/manifest.json', POST)
    decl = data.read_checked(data.BASE / 'PG15950-g13-current-test-declaration-inventory-v1/manifest.json', '0173083ac6c1ed92d23a3fad673afc7d545186d718353366398c1ecd28c6c139')
    bindings = data.read_checked(data.BASE / 'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json', decl['files']['exact-ordinary-bindings.json'])
    classes = {'dev.codex.schubert.nk.batch.platform.' + name for name in original.TESTS}
    expected = {(r['className'], r['method']) for r in bindings if r['className'] in classes}
    require(len(expected) == 9 and all(data.sha(file.read_bytes()) == original.TEST_HASHES[name] for name, file in original.TESTS.items()), 'same whole original normal declarations/bytes')
    text = original.TESTS['BackupWorkerRequestTest'].read_text()
    values = {}
    for marker, target in [('private static final String GOLDEN =', 'ordinary'), ('String golden =', 'verification')]:
        body = text.split(marker, 1)[1].split(';', 1)[0]
        values[target] = ''.join(json.loads(literal) for literal in re.findall(r'"(?:[^"\\]|\\.)*"', body))
    check_oracles(values)
    assess(p, expected)
    negatives = []
    for field, value in [('source', '0' * 40), ('tests', 15), ('totals', {}), ('singleSession', False), ('targetUnitFour100', False), ('crcMismatch', 1), ('manualCounterExclusions', ['outer']), ('oldCoverageTransferred', True), ('priorProductResultsReused', True), ('whole451Accepted', True), ('newAccepted', True), ('newTestIds', 16), ('effortPercent', 100), ('cryptoOrKeyOperationsInvoked', True), ('syntheticUuidEntropyUsed', True), ('actualSecretKeysLoaded', True), ('ownExecutorTaskCount', 0), ('actualJdbcBackendConnected', True), ('rootMainInvoked', True), ('forbiddenProductProbeHits', 1)]:
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
    for name, wrong in [('ordinary', BASE[:-1]), ('verification', VERIFY.replace('VERIFY1', 'VERIFY2')), ('verification', VERIFY.replace('dump_size=3', 'dump_size=03')), ('ordinary', BASE.replace('run=', 'path=')), ('verification', VERIFY.replace('ba7816bf', 'zz7816bf'))]:
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
        postSha256=POST, tests=9, newUniqueMethods=9, normalOrdinaryTestSourceDomain=True,
        semanticNegativeVectors=len(negatives), independentOracleNegativeVectors=len(oracle_negatives),
        literalVectors={name: dict(bytes=len(value.encode('ascii')), sha256=hashlib.sha256(value.encode('ascii')).hexdigest()) for name, value in values.items()},
        targetUnitFour100=True, fullSourcePrograms=1, allPhysicalClasses=2,
        helpersNotReaccepted=True, syntheticUuidEntropyUsed=False, actualAuthorizationIssued=False,
        productTestsExecutedByIndependent=0, oldRuntimeTransferred=False, whole451Accepted=False,
        wholeF03Accepted=False, newAccepted=0, formalUpdated=False, effortPercent=None, externalActions=0))
    print(data.sha((OUT / 'manifest.json').read_bytes()))
    print(json.dumps(dict(actualExit=0, semanticNegativeVectors=len(negatives), independentOracleNegativeVectors=len(oracle_negatives))))


if __name__ == '__main__':
    main()
