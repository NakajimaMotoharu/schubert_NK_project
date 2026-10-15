"""Current3697 Main, whole62 Session tests and fixed27 RO statement fault oracle."""
import inspect
import pg3244_backup_cycle_selected as previous

ROOT = previous.ROOT
TEST = ROOT + 'repository/MorningDatabaseSessionTest.java'
FILES = [TEST, *previous.FILES[1:]]
METHOD = 'mdb3254001ReadOnlyStatementCompoundFailuresKeepRowsAndCloseEveryOwner'
CHOICES = {'statement': ('PG3254', 'pg3254-recheck-statement-selected-v1', 'MorningDatabaseSessionTest', 'MorningDatabaseSession$Session', [METHOD])}


def server(choice):
    if choice != 'statement': raise ValueError('one fixed RO statement contract suite required')
    raw = previous.server('cycle').replace('PG3244', 'PG3254').replace('source-full-PG3204', 'source-full-PG3248')
    raw = raw.replace('platform.MorningBackupUnitCycleTest', 'repository.MorningDatabaseSessionTest')
    raw = raw.replace('platform/MorningBackupUnitCycle', 'repository/MorningDatabaseSession$Session')
    raw = raw.replace("classes.rglob('MorningBackupUnitCycle*.class')", "classes.rglob('MorningDatabaseSession*.class')")
    marker = '{' + ','.join(repr(name) for name in sorted(previous.METHODS)) + '}'
    if raw.count(marker) != 1: raise ValueError('one fixed new-method contract required')
    raw = raw.replace(marker, '{' + repr(METHOD) + '}')
    from pyflakes.api import check
    if check('INPUT={}\n' + raw, '<whole62 real Session and fixed27 fault tuples>'): raise ValueError('complete namespace required')
    compile(raw, '<current3697 unchanged Main selected contract>', 'exec')
    return raw


def main():
    raw = inspect.getsource(previous.main).replace('pg3206-expiry-group-full-qualified-v1', 'pg3250-cycle-group-full-qualified-v1').replace('3694', '3697')
    raw = raw.replace("ROOT + 'platform/' + test", "ROOT + 'repository/' + test")
    ns = {**previous.__dict__, 'FILES': FILES, 'TEST': TEST, 'CHOICES': CHOICES, 'server': server}
    exec(compile(raw, '<RO statement current3697 selected transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
