"""Both new Session methods, whole63 tests, no old62 substitution for new bytes."""
import inspect
import pg3254_recheck_statement_selected as previous

TEST = previous.TEST
FILES = previous.FILES
METHOD = 'mdb3256001CompletionGuardSqlFailurePreservesCommittedBeginsAndEmptyBackupRoot'
METHODS = [previous.METHOD, METHOD]
CHOICES = {'statement': ('PG3256', 'pg3256-completion-guard-selected-v1', 'MorningDatabaseSessionTest', 'MorningDatabaseSession$Session', METHODS)}


def server(choice):
    raw = previous.server(choice).replace('PG3254', 'PG3256')
    marker = '{' + repr(previous.METHOD) + '}'
    if raw.count(marker) != 1: raise ValueError('one earlier required-case set expected')
    raw = raw.replace(marker, '{' + ','.join(repr(name) for name in sorted(METHODS)) + '}')
    from pyflakes.api import check
    if check('INPUT={}\n' + raw, '<all63 Session both new contract methods>'): raise ValueError('complete namespace required')
    compile(raw, '<actual SQL guard plus27 compound faults>', 'exec')
    return raw


def main():
    ns = {**previous.__dict__, 'FILES': FILES, 'TEST': TEST, 'CHOICES': CHOICES, 'server': server}
    exec(compile(inspect.getsource(previous.main), '<new63 Session transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
