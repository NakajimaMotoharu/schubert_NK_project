"""Full3663 current-native byte bridge using retained authenticated current streams only."""
import inspect
from pyflakes.api import check
import pg2602_retention_group_native_qualified as previous
from pg2620_permit_expiry_group_full_six import SOURCE, validate


def qualify_snapshot():
    raw = inspect.getsource(previous.qualify_snapshot).replace(
        'pg2601-retention-group-full-qualified-v1', 'pg2621-permit-expiry-group-full-qualified-v1').replace('3657', '3663')
    ns = {**previous.__dict__, 'SOURCE': SOURCE, 'validate': validate}
    exec(compile(raw, '<whole full3663 clean input guard>', 'exec'), ns)
    return ns['qualify_snapshot']()


def server():
    raw = previous.server().replace('PG2602', 'PG2622').replace('PG2600', 'PG2620').replace('3657', '3663')
    raw = raw.replace('qualified2578Tests', 'qualified2620Tests')
    if check('ARCHIVE_SHA=""\ncoordinates=lambda a,b:{}\n' + raw, '<full3663 Main byte bridge>'):
        raise ValueError('whole bridge namespace required')
    compile(raw, '<current full3663 retained native>', 'exec')
    return raw


def source():
    raw = previous.source().replace('pg2602-retention-group-native-qualified-v1',
        'pg2622-permit-expiry-group-native-qualified-v1').replace('PG2602', 'PG2622').replace(
        'pg2601-retention-group-full-qualified-v1', 'pg2621-permit-expiry-group-full-qualified-v1')
    if 'SSH+' in raw:
        raise ValueError('VM recapture refused')
    compile(raw, '<current retained full3663 transport>', 'exec')
    return raw


def entry():
    ns = {**previous.entry().__globals__, 'CODE': server(), 'SOURCE': SOURCE,
          'qualify_snapshot': qualify_snapshot}
    exec(compile(source(), '<exact full3663 retained current native>', 'exec'), ns)
    return ns['main']


if __name__ == '__main__':
    raise SystemExit(entry()())
