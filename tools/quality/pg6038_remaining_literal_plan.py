"""Plan all remaining33 constant conditions/22Main; no Production edits or dynamic PT."""
import hashlib
import json
import os
from collections import defaultdict
from pg6004_api_bounds_plan import private_source, formatted
from pg5940_private_lock_compile import ROOT, BASE, W, sha
from pg6034_corrected_boundary_static import SOURCE

# Entire exact if-condition before/after plus independently declared same-value constants.
RULES = {
 'ApiProcessMain': [('if (failureCode.length != 1)', 'if (failureCode.length != EXPECTED_FAILURE_STATUS_COUNT)', ['int EXPECTED_FAILURE_STATUS_COUNT = 1'])],
 'BackupManifest': [('if (startedAt.atZone(JST).getYear() > 9999)', 'if (startedAt.atZone(JST).getYear() > MAXIMUM_DIRECTORY_YEAR)', ['int MAXIMUM_DIRECTORY_YEAR = 9999'])],
 'BackupArtifactVerifier': [('if ((raw.mode() & 0xf000) != 0x8000)', 'if ((raw.mode() & FILE_TYPE_MASK) != REGULAR_FILE_TYPE)', ['int FILE_TYPE_MASK = 0xf000', 'int REGULAR_FILE_TYPE = 0x8000'])],
 'MaintenanceRunFiles': [('if (index < 5)', 'if (index < FIXED_ROOT_FILE_COUNT)', ['int FIXED_ROOT_FILE_COUNT = 5'])],
 'MorningCleanupExecution': [('if (receipt.exitCode() == 30)', 'if (receipt.exitCode() == REJECTED_EXIT_STATUS)', ['int REJECTED_EXIT_STATUS = 30']), ('if (terminal.exitCode() == 30)', 'if (terminal.exitCode() == REJECTED_EXIT_STATUS)', ['int REJECTED_EXIT_STATUS = 30'])],
 'MorningExpiryExecution': [('if (actual.exitCode() == 30)', 'if (actual.exitCode() == REJECTED_EXIT_STATUS)', ['int REJECTED_EXIT_STATUS = 30'])],
 'RootServiceExecutableAdmission': [('if (mode != 0xa1ff)', 'if (mode != RETAINED_SYMBOLIC_LINK_MODE)', ['int RETAINED_SYMBOLIC_LINK_MODE = 0xa1ff'])],
 'RootServiceLauncher': [('if (args.length != 1)', 'if (args.length != EXPECTED_SERVICE_ARGUMENTS)', ['int EXPECTED_SERVICE_ARGUMENTS = 1'])],
 'StartupAdmissionFile': [('if (capacity < 1)', 'if (capacity < MINIMUM_PRIVATE_VIEW_CAPACITY)', ['int MINIMUM_PRIVATE_VIEW_CAPACITY = 1'])],
 'ArtemisAcceptorReadinessClient': [('if (values.size() != 1)', 'if (values.size() != EXPECTED_ACCEPTOR_COUNT)', ['int EXPECTED_ACCEPTOR_COUNT = 1'])],
 'ArtemisManagementReadinessClient': [('if (remaining < 1_000_000L)', 'if (remaining < MINIMUM_REQUEST_TIMEOUT_NANOS)', ['long MINIMUM_REQUEST_TIMEOUT_NANOS = 1_000_000L'])],
 'ConfigurationGroupResolver': [("if (value == ':')", 'if (value == GROUP_FIELD_SEPARATOR)', ["char GROUP_FIELD_SEPARATOR = ':'"])],
 'InspectorStaticEnvironment': [('if (Integer.parseInt(Objects.requireNonNull(match.group(1))) > 65535)', 'if (Integer.parseInt(Objects.requireNonNull(match.group(1))) > MAXIMUM_TCP_PORT)', ['int MAXIMUM_TCP_PORT = 65535']), ('if (names.length() > 65536)', 'if (names.length() > MAXIMUM_INTERFACE_NAMES_CHARACTERS)', ['int MAXIMUM_INTERFACE_NAMES_CHARACTERS = 65536'])],
 'MorningCaddyReadiness': [('if (io.login() != 200)', 'if (io.login() != SUCCESS_HTTP_STATUS)', ['int SUCCESS_HTTP_STATUS = 200']), ('if (++count > 65536)', 'if (++count > MAXIMUM_SOCKET_DIRECTORY_ENTRIES)', ['int MAXIMUM_SOCKET_DIRECTORY_ENTRIES = 65536']), ('if (literal.length == 4)', 'if (literal.length == IPV4_ADDRESS_BYTES)', ['int IPV4_ADDRESS_BYTES = 4'])],
 'MorningServiceReadiness': [('if (json.length() > 1)', 'if (json.length() > JSON_OPENING_DELIMITER_LENGTH)', ['int JSON_OPENING_DELIMITER_LENGTH = 1']), ('if (++count > 65536)', 'if (++count > MAXIMUM_SOCKET_DIRECTORY_ENTRIES)', ['int MAXIMUM_SOCKET_DIRECTORY_ENTRIES = 65536']), ('if (status != 200)', 'if (status != SUCCESS_HTTP_STATUS)', ['int SUCCESS_HTTP_STATUS = 200'])],
 'SystemctlStateSource': [('if (bytes[0].length > 1024)', 'if (bytes[0].length > MAXIMUM_STATE_OUTPUT_BYTES)', ['int MAXIMUM_STATE_OUTPUT_BYTES = 1024'])],
 'ServiceDatabaseSource': [('if (seconds != 3)', 'if (seconds != FIXED_LOGIN_TIMEOUT_SECONDS)', ['int FIXED_LOGIN_TIMEOUT_SECONDS = 3'])],
 'InspectorAesCredential': [('if (decoded.length != 32)', 'if (decoded.length != AES_KEY_BYTES)', ['int AES_KEY_BYTES = 32'])],
 'InspectorDbCredential': [("if (input[length - 1] == '\\n')", 'if (input[length - 1] == OPTIONAL_LINE_TERMINATOR)', ["char OPTIONAL_LINE_TERMINATOR = '\\n'"]), ("if (decoded[0] == '\\ufeff')", 'if (decoded[0] == BYTE_ORDER_MARK)', ["char BYTE_ORDER_MARK = '\\ufeff'"])],
 'LinuxSystemdSession': [('if (outputState[slot] != 2)', 'if (outputState[slot] != COMPLETE_OUTPUT_STATE)', ['int COMPLETE_OUTPUT_STATE = 2']), ('if (integer("sd_bus_is_ready", bus) != 1)', 'if (integer("sd_bus_is_ready", bus) != READY_STATUS)', ['int READY_STATUS = 1']), ('if (integer("sd_bus_message_read_basic", reply, (byte) kind, value) != 1)', 'if (integer("sd_bus_message_read_basic", reply, (byte) kind, value) != EXPECTED_BASIC_READ_VALUES)', ['int EXPECTED_BASIC_READ_VALUES = 1']), ("if (property.type == 's')", 'if (property.type == STRING_PROPERTY_TYPE)', ["char STRING_PROPERTY_TYPE = 's'"]), ('if (end > 4096)', 'if (end > MAXIMUM_PROPERTY_UTF8_BYTES)', ['int MAXIMUM_PROPERTY_UTF8_BYTES = 4096'])],
 'MaintenanceOwnerFrame': [('if (remaining < 1_000_000_000L)', 'if (remaining < MINIMUM_QUERY_TIMEOUT_NANOS)', ['long MINIMUM_QUERY_TIMEOUT_NANOS = 1_000_000_000L'])],
 'SystemManagerObservation': [('if (result.length() > 4096)', 'if (result.length() > MAXIMUM_PUBLIC_OBSERVATION_CHARACTERS)', ['int MAXIMUM_PUBLIC_OBSERVATION_CHARACTERS = 4096'])],
}


def declarations(before, rules):
    changes, constants = [], set()
    for old, new, fields in rules:
        if before.count(old) != 1:
            raise ValueError('one exact current condition: '+old)
        changes.append((old, new, 1))
        constants.update('private static final '+f+';' for f in fields)
    return changes, sorted(constants)


def main():
    sp = BASE/'PG6034-corrected-boundary-static-v1/manifest.json'
    public = json.loads(sp.read_bytes()); pp = W/'pg6034-corrected-boundary-static-v1/manifest.safe.json'
    if sha(pp) != public['privateManifestSha256'] or public['source'] != SOURCE or public['actualExit'] != 0 or not public['originalSelectedOverallAccepted']:
        raise ValueError('current genuine965/zeroSpotBugs/all8511667 actual static first')
    proof = json.loads(pp.read_bytes()); raw = json.loads(sp.with_name('findings.json').read_bytes())
    if {p.relative_to(ROOT).as_posix(): sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')} != proof['allSourceHashes']:
        raise ValueError('all current851 source frozen to actual proof')
    groups = defaultdict(list)
    for row in raw:
        if row['rule'] == 'AvoidLiteralsInIfCondition':
            if row['status'] != 'NOT_REVIEWED_CURRENT_SOURCE':
                raise ValueError('only actual current unreviewed literal conditions')
            groups[row['sourcePath']].append(row)
    if len(groups) != 22 or sum(map(len, groups.values())) != 33 or {p.rsplit('/', 1)[1][:-5] for p in groups} != set(RULES):
        raise ValueError('complete all22/33 declared literal remainder,none hidden')
    plans = []
    for path, rows in sorted(groups.items()):
        before = (ROOT/path).read_text(); changes, constants = declarations(before, RULES[path.rsplit('/', 1)[1][:-5]])
        if len(changes) != len(rows) or any(r['sourceSha256'] != sha(ROOT/path) for r in rows):
            raise ValueError('exact current source and one diagnostic per declared if')
        after = formatted(private_source(before, changes, constants))
        plans.append(dict(path=path, beforeSha256=sha(ROOT/path), predictedAfterSha256=hashlib.sha256(after.encode()).hexdigest(),
                          changes=changes, constants=constants, findingIds=[r['findingId'] for r in rows], productionApplied=False))
    value = dict(actualExit=0, source=SOURCE, baseStaticManifestSha256=sha(sp), selectedSourceFiles=22,
                 selectedDiagnosticConditions=33, sourcePlans=plans, testsExecuted=0, productionApplied=False,
                 plannedWholeTests=3976, plannedWholeSuites=593, plannedPhysicalMain=1667,
                 allChangedMethodInstructionsMustRemainEquivalent=True, nativeCountersRemainPending=True,
                 noCoverageOrPtSuccessImported=True, formalAccepted=False, F03Accepted=False, ptAlternativeCompleted=0, vmActions=0)
    out = BASE/'PG6038-remaining33-plan-v1'; os.umask(0o077); out.mkdir()
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, sourceFiles=22, conditions=33, productionApplied=False, manifestSha256=sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
