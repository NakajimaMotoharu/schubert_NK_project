"""Related Inspector four tests, exact3694 Main and finite UNKNOWN client oracle."""
import inspect
import pg3244_backup_cycle_selected as previous

ROOT = previous.ROOT
TEST = ROOT + 'platform/InspectorUnitCycleTest.java'
FILES = [TEST, *previous.FILES[1:]]
METHOD = 'iuc3246001UnknownStartAndStopMustReapBeforeParentReacquire'
CHOICES = {'cycle': ('PG3246', 'pg3246-inspector-cycle-selected-v1', 'InspectorUnitCycleTest', 'MorningBackupUnitCycle', [METHOD])}


def server(choice):
    raw = previous.server(choice).replace('PG3244', 'PG3246').replace('platform.MorningBackupUnitCycleTest', 'platform.InspectorUnitCycleTest')
    marker = '{' + ','.join(repr(name) for name in sorted(previous.METHODS)) + '}'
    if raw.count(marker) != 1: raise ValueError('one exact required-method set expected')
    raw = raw.replace(marker, '{' + repr(METHOD) + '}')
    from pyflakes.api import check
    if check('INPUT={}\n' + raw, '<whole Inspector four tests>'): raise ValueError('complete namespace required')
    compile(raw, '<whole Inspector/client UNKNOWN tests>', 'exec')
    return raw


def main():
    ns = {**previous.__dict__, 'FILES': FILES, 'TEST': TEST, 'CHOICES': CHOICES, 'server': server}
    exec(compile(inspect.getsource(previous.main), '<related Inspector transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
