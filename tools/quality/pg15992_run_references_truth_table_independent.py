"""Independently enumerate all four-bit vectors; never call Main to generate expectations."""
import copy
import itertools
import json
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg15988_run_references_truth_table_pt as original
import pg15990_run_references_truth_table_post as post

PIN = 'adef4b2453d8dcd84972f559419f5fb7538c9fd3ba8751d491c493b7d7a78a17'
OUT = data.BASE / 'PG15992-run-references-truth-table-independent-v1'
TOTALS = {kind: dict(missed=0, covered=n) for kind, n in [('LINE', 6), ('METHOD', 3), ('CLASS', 1), ('BRANCH', 14)]}

def require(ok, message):
    if not ok:
        raise ValueError(message)

def table(text):
    rows = re.findall(r'new Vector\(\s*(true|false)\s*,\s*(true|false)\s*,\s*(true|false)\s*,\s*(true|false)\s*,\s*(true|false)\s*,\s*(true|false)\s*\)', text)
    return [tuple(v == 'true' for v in row) for row in rows]

def assess(p):
    require(p['actualExit'] == 0 and p['source'] == original.SOURCE and p['originalManifestSha256'] == post.RAW and type(p['tests']) is int and p['tests'] == 3 and p['suites'] == 1, 'current new fixture three')
    for field in ('singleSession', 'officialGeneratedFiltersUnchanged', 'targetUnitFour100', 'allMeasuredApplicableCountersCovered', 'onlyReviewedPureValueSuites', 'onlyPublicBooleanTruthTableFixture'):
        require(p[field] is True, 'actual primitive value scope: ' + field)
    for field in ('formalUpdated', 'whole451Accepted', 'wholeF03Accepted', 'oldCoverageTransferred', 'priorProductResultsReused', 'rootMainInvoked', 'actualJdbcBackendConnected', 'actualJdbcProxyObjectsConstructed', 'actualFilesOpenedByProduct', 'cryptoOrKeyOperationsInvoked', 'actualSecretKeysLoaded', 'actualPrivateFilesOpened', 'actualRetainedAuditOrExpiryDeletionInvoked', 'actualCompilerGeneratedTwrOracleInvoked', 'actualJdkThrowableSuppressionInvoked'):
        require(p[field] is False, 'no backend/authority/foreign scope: ' + field)
    require(all(type(p[k]) is int and p[k] == 0 for k in ('failures', 'errors', 'skipped', 'reruns', 'newAccepted', 'actualVmActions', 'actualDatabaseActions', 'actualServiceActions', 'actualNetworkActions', 'actualJdbcMethodsInvoked', 'actualSqlStatementsPreparedOrExecuted')), 'no failed/unrun/external operations')
    require(p['totals'] == TOTALS and p['strictFour100GateExit'] == 0 and p['crcMismatch'] == 0 and p['sessionIdentity'] == original.SESSION and p['effortPercent'] is None and p['literalTruthRows'] == 16, 'all four counters in one exact exec')
    require(p['completeSourceUnitClosure'] == {original.NAME: [original.NAME]} and set(p['fullSourceUnits']) == {original.NAME} and set(p['physicalClasses']) == set(p['sourcePhysicalInventory']) == set(p['executable']) == {original.NAME}, 'one whole Source/class, no nested omission')
    unit = p['fullSourceUnits'][original.NAME]
    require(p['executable'][original.NAME]['counters'] == TOTALS and all(type(v) is int for c in p['executable'][original.NAME]['counters'].values() for v in c.values()), 'all actual typed executable counters equal Source totals')
    require(unit['totals'] == TOTALS and unit['four100'] is unit['threeCounter100'] is True and unit['metadataOnly'] is unit['branchNaturallyZero'] is False and p['metadataClasses'] == p['unexecutedCodeClasses'] == p['manualCounterExclusions'] == [], 'measured branch14, no fake NoCode/B0 or exclusions')
    require(len(p['owners']) == 1 and next(iter(p['owners'].values()))['canonicalOwner'] == 'WBS-P017-12' and p['helperPreviousSourceProofs'] == {}, 'only actual baseline value source responsibility, fixture not in normal Test scope')
    require(p['forbiddenProductProbeHits'] == 0 and len(p['passiveNativeBoundaryAbsence']['rows']) == 6 and all(row[3] == '0' for row in p['passiveNativeBoundaryAbsence']['rows']) and all(s['actualExit'] == 0 and not s['timedOut'] for s in p['stages']), 'actual held/native/session/CRC reader terminals')

def main():
    invocation = capture(__file__)
    require(not OUT.exists(), 'new-only')
    p = data.read_checked(post.OUT / 'manifest.json', PIN)
    raw = data.read_checked(data.BASE / 'PG15988-run-references-truth-table-three-pt-v1/manifest.json', post.RAW)
    post.assess(raw)
    assess(p)
    require(p['cases'] == raw['cases'] and len({(r['classname'], r['name']) for r in p['cases']}) == 3, 'new fixture once, no old case inference')
    text = original.TEST.read_text()
    require(data.sha(text.encode()) == original.TEST_SHA, 'fixed literal fixture')
    expected = [tuple(bits) + (any(bits), any(bits[:3])) for bits in itertools.product((False, True), repeat=4)]
    require(table(text) == expected and len({v[:4] for v in expected}) == 16 and sum(v[4] for v in expected) == 15 and sum(v[5] for v in expected) == 14, 'Python independent truth table, no Main expected calls')
    fixture_labels = []
    actual = table(text)
    for label, mutate in [('missing', lambda v: v.pop()), ('duplicate', lambda v: v.__setitem__(0, v[1])), ('allfalse-admitted', lambda v: v.__setitem__(0, (False, False, False, False, True, False))), ('consistent-is-presence', lambda v: v.__setitem__(1, (False, False, False, True, True, True))), ('flag-order', lambda v: v.__setitem__(2, v[4]))]:
        bad = copy.deepcopy(actual)
        mutate(bad)
        try:
            require(bad == expected, 'exact sixteen independent rows')
        except ValueError:
            fixture_labels.append(label)
        else:
            raise ValueError('bad oracle accepted: ' + label)
    design = 'documents/300_SS/330_データ・ファイル/331_DB物理・DDL・index・権限設計.md'
    design_raw = (data.ROOT / design).read_bytes()
    require(design_raw == subprocess.check_output(['git', 'show', 'origin/main:' + design], cwd=data.ROOT) and all(t in design_raw.decode() for t in ['has_batch_history', 'has_inbox_progress', 'has_log_progress', 'identity_consistent', '不存在はconsistent=true']), 'approved flag projection contract, no source-driven change')
    labels = []
    for field, value in [('source', 'OLD'), ('tests', True), ('totals', {}), ('strictFour100GateExit', 1), ('completeSourceUnitClosure', {}), ('metadataClasses', [original.NAME]), ('unexecutedCodeClasses', [original.NAME]), ('manualCounterExclusions', [original.NAME]), ('literalTruthRows', 15), ('formalUpdated', True), ('oldCoverageTransferred', True), ('actualJdbcBackendConnected', True), ('actualJdbcProxyObjectsConstructed', True), ('actualCompilerGeneratedTwrOracleInvoked', True), ('actualJdkThrowableSuppressionInvoked', True), ('cryptoOrKeyOperationsInvoked', True), ('actualFilesOpenedByProduct', True), ('actualRetainedAuditOrExpiryDeletionInvoked', True), ('forbiddenProductProbeHits', 1), ('effortPercent', 100)]:
        bad = copy.deepcopy(p)
        bad[field] = value
        try:
            assess(bad)
        except (ValueError, KeyError):
            labels.append(field)
        else:
            raise ValueError('false primitive qualification accepted: ' + field)
    for label, mutate in [('false-B0', lambda v: v['fullSourceUnits'][original.NAME].update(branchNaturallyZero=True)), ('four-erased', lambda v: v['fullSourceUnits'][original.NAME].update(four100=False)), ('counter-erased', lambda v: v['executable'][original.NAME]['counters']['BRANCH'].update(covered=0))]:
        bad = copy.deepcopy(p)
        mutate(bad)
        try:
            assess(bad)
        except ValueError:
            labels.append(label)
        else:
            raise ValueError('unrejected category or executable counter mutation')
    require(p['executable'][original.NAME]['counters'] == TOTALS, 'actual executable counters equal all Source totals')
    verify(p['invocation'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'independent-truth-table.json', expected)
    data.write(OUT / 'manifest.json', dict(actualExit=0, source=original.SOURCE, invocation=invocation, postSha256=PIN,
        tests=3, newUniqueMethods=3, sourcePrograms=1, physicalClasses=1, four100SourcePrograms=1,
        semanticNegativeVectors=len(labels), negativeLabels=labels, independentOracleNegativeVectors=len(fixture_labels), independentOracleNegativeLabels=fixture_labels,
        independentTruthRows=16, acceptedTupleRows=15, rejectedTupleRows=1, presenceTrueRows=14,
        independentTruthTableSha256=data.sha((OUT / 'independent-truth-table.json').read_bytes()), approvedDesignSha256=data.sha(design_raw),
        totals=TOTALS, strictFour100GateExit=0, onlyPublicBooleanTruthTableFixture=True, normalOrdinaryTestSourceDomain=False,
        productTestsReexecutedByIndependent=0, oldCoverageTransferred=False, wholeF03Accepted=False, whole451Accepted=False,
        newAccepted=0, formalUpdated=False, effortPercent=None, externalActions=0))
    print(data.sha((OUT / 'manifest.json').read_bytes()))
    print(json.dumps(dict(actualExit=0, semanticNegativeVectors=len(labels), independentOracleNegativeVectors=len(fixture_labels), four100Sources=1)))

if __name__ == '__main__':
    main()
