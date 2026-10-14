"""Current a79 all1643 Main/resource bridge; retain current native, never old0fd."""
import inspect
import json
import subprocess
from pyflakes.api import check
import pg2622_permit_expiry_group_native_qualified as previous
from pg2640_wire_oracle_group_full_six import SOURCE, validate
from pg1446_current_cold_stage import W


def qualify_snapshot():
    outer = json.loads((W / 'pg2641-wire-oracle-full-qualified-v1/manifest.safe.json').read_bytes())
    if type(outer.get('actualExit')) is not int or outer['actualExit'] != 0:
        raise ValueError('actual independently qualified all3664 required')
    full = outer['result']
    expected = {'productionSource': SOURCE, 'tests': 3664, 'suites': 540,
                'mainClasses': 1643, 'FESFlakyNotRun': 0, 'staticSixModules': 0}
    if any(type(full.get(k)) is not type(v) or full[k] != v for k, v in expected.items()):
        raise ValueError('exact whole all3664 required')
    validate(full['sourceSnapshot'])
    if subprocess.check_output(['git', 'status', '--porcelain']) or subprocess.check_output(
        ['git', 'diff', '--name-only', full['sourceSnapshot'], 'HEAD', '--',
         'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization']):
        raise ValueError('clean whole source input equality required')


def server():
    raw = previous.server().replace('PG2622', 'PG2642').replace('PG2620', 'PG2640').replace('3663', '3664')
    raw = raw.replace('qualified2620Tests', 'qualified2640Tests')
    if check('ARCHIVE_SHA=""\ncoordinates=lambda a,b:{}\n' + raw, '<all3664 byte bridge>'):
        raise ValueError('whole native bridge namespace required')
    compile(raw, '<current retained native bridge all3664>', 'exec')
    return raw


def source():
    raw = previous.source().replace('pg2622-permit-expiry-group-native-qualified-v1', 'pg2642-wire-oracle-native-qualified-v1').replace(
        'PG2622', 'PG2642').replace('pg2621-permit-expiry-group-full-qualified-v1', 'pg2641-wire-oracle-full-qualified-v1')
    if 'SSH+' in raw:
        raise ValueError('VM recapture refused')
    compile(raw, '<current retained native transport all3664>', 'exec')
    return raw


def entry():
    ns = {**previous.entry().__globals__, 'CODE': server(), 'SOURCE': SOURCE,
          'qualify_snapshot': qualify_snapshot}
    exec(compile(source(), '<exact source retained native all3664>', 'exec'), ns)
    return ns['main']


if __name__ == '__main__':
    raise SystemExit(entry()())
