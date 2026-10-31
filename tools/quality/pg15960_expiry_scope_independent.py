"""Independent literal/TWR oracle and full two-Source counter/identity validation."""
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg15956_expiry_successful_scope_whole24_pt as original
import pg15958_expiry_successful_scope_whole24_post as post

PIN = '772283e4544eca7dca600fc21f2d2b58b471c543f226559b3dc48ccdb7d4af98'
OUT = data.BASE / 'PG15960-expiry-successful-scope-independent-v1'
TOTALS = {k: dict(covered=c, missed=m) for k, c, m in [('LINE', 27, 226), ('METHOD', 5, 21), ('CLASS', 3, 2), ('BRANCH', 12, 176)]}
TRUE = ['singleSession', 'officialGeneratedFiltersUnchanged', 'unexecutedCodeIncludedInAllDenominators', 'previousHelpersNotReaccepted', 'onlyInjectedJdkResourcePortsAndAuditValues', 'actualCompilerGeneratedTwrOracleInvoked', 'actualJdkThrowableSuppressionInvoked']
FALSE = ['targetUnitFour100', 'allMeasuredApplicableCountersCovered', 'cryptoOrKeyOperationsInvoked', 'testOwnNewSlotPublicEvidenceWrites', 'testOwnedTemporaryFileIo', 'actualFilesOpenedByProduct', 'actualPrivateFilesOpened', 'actualSecretKeysLoaded', 'actualCredentialValuesUsed', 'actualAuthenticationOrSessionIssued', 'formalUpdated', 'whole451Accepted', 'wholeF03Accepted', 'oldCoverageTransferred', 'priorProductResultsReused', 'rootMainInvoked', 'actualJdbcBackendConnected', 'actualRetainedAuditOrExpiryDeletionInvoked', 'outerBusinessCodeProbeAbsence']

def require(ok, message):
    if not ok:
        raise ValueError(message)

def assess(p):
    require(p['actualExit'] == 0 and p['source'] == original.SOURCE and p['originalManifestSha256'] == post.RAW and type(p['tests']) is int and p['tests'] == 24 and p['suites'] == 1, 'genuine current original24')
    require(all(p[k] is True for k in TRUE) and all(p[k] is False for k in FALSE), 'actual fake-port/JDK effects, no real authority or full quality')
    require(all(type(p[k]) is int and p[k] == 0 for k in ['failures', 'errors', 'skipped', 'reruns', 'newAccepted', 'actualVmActions', 'actualDatabaseActions', 'actualServiceActions', 'actualNetworkActions', 'actualJdbcMethodsInvoked', 'actualSqlStatementsPreparedOrExecuted', 'actualBoundSockets']) and p['effortPercent'] is None, 'typed finite result, no external effects')
    require(p['strictFour100GateExit'] == 1 and p['crcMismatch'] == 0 and p['sessionIdentity'] == original.SESSION and p['totals'] == TOTALS, 'full partial denominator retained')
    closure = {name: sorted(group) for name, group in original.CLOSURES.items()}
    physical = {name for group in closure.values() for name in group}
    require(p['completeSourceUnitClosure'] == closure and set(p['fullSourceUnits']) == set(closure) and set(p['physicalClasses']) == set(p['sourcePhysicalInventory']) == physical and len(physical) == 8, 'both complete source closures')
    require(set(p['metadataClasses']) == original.METADATA and len(p['metadataClasses']) == 3 and set(p['executable']) == physical - original.METADATA and p['manualCounterExclusions'] == [], 'three actual NoCode interfaces, five Code families')
    for name, row in p['sourcePhysicalInventory'].items():
        if name in original.METADATA:
            require(row['flags'] == 1536 and row['methods'] and not any(m['hasCode'] for m in row['methods']), 'real NoCode')
        else:
            require(any(m['hasCode'] for m in row['methods']), 'Code not excluded')
    require(set(p['unexecutedCodeClasses']) == original.UNEXECUTED and len(p['unexecutedCodeClasses']) == 2, 'Stage/Prior unexecuted Code retained')
    require(all(c['covered'] == 0 for n in original.UNEXECUTED for c in p['executable'][n]['counters'].values()), 'unexecuted classes all missed')
    require({n for n, r in p['executable'].items() if r['counters']['CLASS']['covered'] == 1} == original.EXECUTED, 'only outer static/Snapshot/fixed exception Code')
    require({k: {role: sum(r['counters'][k][role] for r in p['executable'].values()) for role in ('covered', 'missed')} for k in TOTALS} == TOTALS, 'independent physical counter sums')
    repo = p['fullSourceUnits'][original.ROOT + 'ExpiryAuditRepository']
    exception = p['fullSourceUnits'][original.ROOT + 'BatchRepositoryException']
    require(repo['physical'] == closure[original.ROOT + 'ExpiryAuditRepository'] and all(repo[k] is False for k in ['four100', 'metadataOnly', 'branchNaturallyZero', 'threeCounter100']), 'repository not a whole successful program')
    require(exception['four100'] is exception['metadataOnly'] is False and exception['branchNaturallyZero'] is exception['threeCounter100'] is True, 'exception is natural B0, never strict four100')
    for name, unit in p['fullSourceUnits'].items():
        require(unit['totals'] == {k: {role: sum(p['executable'][n]['counters'][k][role] for n in unit['physical'] if n in p['executable']) for role in ('covered', 'missed')} for k in TOTALS}, 'per-Source sums')
    require(p['helperPreviousSourceProofs'] == {} and len(p['owners']) == 3 and sum(r['ownershipStatus'] == 'BASELINE_LOGICAL_REFERENCE' for r in p['owners'].values()) == 2 and sum(r['ownershipStatus'] == 'UNKNOWN' for r in p['owners'].values()) == 1, 'two exact baseline Main owners/one unresolved Test owner, no reassignment')
    require(p['forbiddenProductProbeHits'] == 0 and len(p['passiveNativeBoundaryAbsence']['rows']) == 6 and all(r[3] == '0' for r in p['passiveNativeBoundaryAbsence']['rows']) and all(s['actualExit'] == 0 and not s['timedOut'] for s in p['stages']), 'four-held/six-native data-only audits, actual own terminals')

def main():
    invocation = capture(__file__)
    require(not OUT.exists(), 'new-only')
    p = data.read_checked(post.OUT / 'manifest.json', PIN)
    raw = data.read_checked(data.BASE / 'PG15956-expiry-successful-scope-whole24-pt-v1/manifest.json', post.RAW)
    post.assess(raw)
    assess(p)
    require(p['cases'] == raw['cases'] and len({(r['classname'], r['name']) for r in p['cases']}) == 24, 'original24 once, no borrowed success')
    text = original.TEST.read_text()
    require(data.sha(text.encode()) == original.TEST_SHA and text.count('@Test') == 24, 'fixed original test body')
    required = ['Instant.parse("2026-10-17T00:00:02Z")', 'OBSERVED.minusNanos(1)', 'OBSERVED.plusNanos(1)', '"WARNING", "FAILED", "RUNNING", "UNKNOWN", "", "success"', 'try (JdbcClose owned = release::close)', 'referencePrimary.getClass()', 'new Throwable[] {secondary, secondary}', 'new Throwable[] {rowClose, statementClose}', 'assertSame(referencePrimary, reference.getCause())', 'assertEquals(0, opens.get())', 'assertEquals(0, closes.get())']
    require(all(token in text for token in required), 'literal status/time/null/port/identity/TWR oracles')
    reference = text.split('private static Optional<ExpiryAuditRepository.Prior> javaTwr(', 1)[1].split('private interface JdbcClose', 1)[0]
    require('ExpiryAuditRepository.usingJdbc' not in reference and 'body.read()' in reference and 'release::close' in reference, 'reference TWR must not call target helper')
    design = 'documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md'
    design_raw = (data.ROOT / design).read_bytes()
    require(design_raw == subprocess.check_output(['git', 'show', 'origin/main:' + design], cwd=data.ROOT), 'approved design byte, no code-driven revision')
    require(all(token in design_raw.decode() for token in ['## SSC304', 'self-suppression', 'acquire/release/read', 'verifySuccessfulAudit']), 'approved exact TWR and successful audit contract')
    labels = []
    for key, value in [('source', 'OLD'), ('tests', True), ('totals', {}), ('completeSourceUnitClosure', {}), ('physicalClasses', {}), ('metadataClasses', []), ('unexecutedCodeClasses', []), ('manualCounterExclusions', ['Stage']), ('strictFour100GateExit', 0), ('crcMismatch', 1), ('cryptoOrKeyOperationsInvoked', True), ('actualDatabaseActions', 1), ('actualJdbcMethodsInvoked', 1), ('actualRetainedAuditOrExpiryDeletionInvoked', True), ('formalUpdated', True), ('oldCoverageTransferred', True), ('actualCompilerGeneratedTwrOracleInvoked', False), ('actualJdkThrowableSuppressionInvoked', False), ('outerBusinessCodeProbeAbsence', True)]:
        bad = copy.deepcopy(p)
        bad[key] = value
        try:
            assess(bad)
        except (ValueError, KeyError):
            labels.append(key)
        else:
            raise ValueError('false scope/quality accepted: ' + key)
    for label, mutate in [('natural-promoted', lambda v: v['fullSourceUnits'][original.ROOT + 'BatchRepositoryException'].update(four100=True)), ('natural-erased', lambda v: v['fullSourceUnits'][original.ROOT + 'BatchRepositoryException'].update(branchNaturallyZero=False)), ('repo-promoted', lambda v: v['fullSourceUnits'][original.ROOT + 'ExpiryAuditRepository'].update(four100=True)), ('stage-probe', lambda v: v['executable'][original.ROOT + 'ExpiryAuditRepository$Stage']['counters']['LINE'].update(covered=1)), ('NoCode-disguised', lambda v: v['sourcePhysicalInventory'][next(iter(original.METADATA))]['methods'][0].update(hasCode=True))]:
        bad = copy.deepcopy(p)
        mutate(bad)
        try:
            assess(bad)
        except ValueError:
            labels.append(label)
        else:
            raise ValueError('false Source/metadata classification accepted: ' + label)
    verify(p['invocation'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json', dict(actualExit=0, source=original.SOURCE, invocation=invocation, postSha256=PIN,
        tests=24, sourcePrograms=2, physicalClasses=8, executablePhysicalClasses=5, metadataPhysicalClasses=3,
        four100SourcePrograms=0, naturallyBranchZeroSourcePrograms=1, incompleteSourcePrograms=1,
        semanticNegativeVectors=len(labels), negativeLabels=labels, totals=TOTALS, strictFour100GateExit=1,
        approvedDesignSha256=data.sha(design_raw), independentOracle='FIXED_STATUS_TIME_NULL_PORT_EVENTS_AND_SEPARATE_COMPILER_TWR_NOT_TARGET_HELPER',
        onlyInjectedJdkResourcePortsAndAuditValues=True, actualCompilerGeneratedTwrOracleInvoked=True,
        actualJdkThrowableSuppressionInvoked=True, actualJdbcBackendConnected=False, actualRetainedAuditOrExpiryDeletionInvoked=False,
        cryptoOrKeyOperationsInvoked=False, actualSecretKeysLoaded=False, actualPrivateFilesOpened=False, actualFilesOpenedByProduct=False,
        oldHelperProofsPreserved=True, previousHelperProofs={}, forbiddenProductProbeHits=0,
        newProductExecutions=0, newAccepted=0, formalUpdated=False, effortPercent=None, wholeF03Accepted=False, whole451Accepted=False))
    print(data.sha((OUT / 'manifest.json').read_bytes()))
    print(json.dumps(dict(actualExit=0, semanticNegativeVectors=len(labels), tests=24, incompleteSources=1)))

if __name__ == '__main__':
    main()
