"""Two new real contract tests, whole cycle class, fixed exact3694 Main only."""
import inspect
import pg3200_expiry_boundary_selected as previous

ROOT = previous.ROOT
TEST = ROOT + 'platform/MorningBackupUnitCycleTest.java'
FILES = [TEST, 'tools/quality/vm/050_s1/SelectedClassContractLauncher.java', 'tools/quality/vm/050_s1/NativeCoverageXml471.java']
METHODS = ['bucycle3244001CompletedBackupRequiresSameBaselineReceiptAndQuiescentTerminal', 'bucycle3244002ClosedPhaseAndTypedFailedHandoffKeepCompletionAfterReacquire']
CHOICES = {'cycle': ('PG3244', 'pg3244-backup-cycle-selected-v1', 'MorningBackupUnitCycleTest', 'MorningBackupUnitCycle', METHODS)}


def server(choice):
    if choice != 'cycle': raise ValueError('one fixed cycle suite required')
    raw = previous.server('cleanup').replace('PG3200', 'PG3244').replace('source-full-PG3054', 'source-full-PG3204')
    raw = raw.replace('repository.CleanupDatabaseSessionTest', 'platform.MorningBackupUnitCycleTest').replace('repository/CleanupDatabaseSession', 'platform/MorningBackupUnitCycle')
    raw = raw.replace("{'cdb3200001ExpiryFactoryRetainsRoleFreshSchemaAndClosesEveryOwner'}", '{' + ','.join(repr(name) for name in sorted(METHODS)) + '}')
    raw = raw.replace("classes.rglob('MorningDatabaseSession*.class')", "classes.rglob('MorningBackupUnitCycle*.class')")
    # Old installed internal jars are not allowed to supply duplicate Main; only
    # the six exact3694 jars precede immutable same-source Test fixtures.
    raw = raw.replace("p.suffix=='.jar'and p.is_relative_to(repo):", "p.suffix=='.jar'and p.is_relative_to(repo)and not str(p.relative_to(repo)).startswith('dev/codex/schubert/'):")
    from pyflakes.api import check
    if check('INPUT={}\n' + raw, '<complete twelve cycle tests>'): raise ValueError('complete isolated cycle namespace required')
    compile(raw, '<independent cycle contract tests>', 'exec')
    return raw


def main():
    raw = inspect.getsource(previous.main).replace('pg3056-boundary-group-full-qualified-v1', 'pg3206-expiry-group-full-qualified-v1').replace('3691', '3694')
    raw = raw.replace("ROOT + 'repository/' + test", "ROOT + 'platform/' + test")
    ns = {**previous.__dict__, 'ROOT': ROOT, 'FILES': FILES, 'CHOICES': CHOICES, 'server': server}
    exec(compile(raw, '<fixed cycle selected transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
