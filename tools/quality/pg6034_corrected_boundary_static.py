"""All851/1667 proof after necessary corrected965; original failed6026 remains immutable."""
import inspect
from collections import Counter
import pg6028_error_boundary_static as previous

SOURCE = '32f5537ea83d158716e687eea88df51a14d14daf'


def validate_source(source, root):
    scope = {**vars(previous), 'SOURCE': SOURCE}
    exec(compile(inspect.getsource(previous.validate_source), '<current corrected source maps>', 'exec'), scope)
    return scope['validate_source'](source, root)


def expected_rules(before, actual):
    expected = Counter(before)
    expected['AvoidCatchingGenericException'] -= 10
    expected['AvoidInstanceofChecksInCatchClause'] -= 5
    expected['DoNotUseThreads'] -= 4
    if expected != Counter(actual):
        raise ValueError('only four Error removals,duplicate catches/interrupt/checked discrimination;two Error warnings retained')


def runner_source():
    raw = previous.runner_source()
    begin = raw.index("    if current['actualExit'] != 1")
    end = raw.index('\n        raise ValueError(', begin)
    raw = raw[:begin]+"    if current['actualExit'] != 0 or current['mavenActualExit'] != 0 or not current['selectedQualified'] or current['phaseExits'] != [0,0] or (current['tests'],current['suites']) != (965,162) or not current['exactInventory'] or current['failedOrSkipped'] or not current['targetFour100'] or set(current['staticIssues']) != set(MODULES) or any(current['staticIssues'].values()):"+raw[end:]
    changes = {
        "originalSelectedOverallExit=1, originalSelectedOverallAccepted=False": "originalSelectedOverallExit=0, originalSelectedOverallAccepted=True",
        "unresolvedBug='BUG1526'": "resolvedGateBug='BUG1526'",
        'rawDiagnosticsRemovedByPg=21': 'rawDiagnosticsRemovedByPg=19',
        "target = BASE/'PG6028-error-boundary-static-v2'": "target = BASE/'PG6034-corrected-boundary-static-v1'"}
    for old, new in changes.items():
        if raw.count(old) != 1:
            raise ValueError('one genuine corrected static binding: '+old)
        raw = raw.replace(old, new, 1)
    compile(raw, '<corrected two-boundary static>', 'exec')
    return raw


def main():
    scope = {**vars(previous.engine), 'OLD': previous.OLD, 'COMPILE': 'pg6032-error-boundary-selected965-v1',
             'SLOT': 'pg6034-corrected-boundary-static-v1', 'NEW_INTERFACE': previous.NEW_INTERFACE,
             'validate_source': validate_source, 'physical_changes': previous.physical_changes,
             'validate_diagnostics': previous.validate_diagnostics, 'expected_rules': expected_rules,
             'plan': lambda: {'sourcePlans': [{'path': p} for p in previous.MAIN]}}
    exec(compile(runner_source(), '<actual corrected static,not PT replay>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    main()
