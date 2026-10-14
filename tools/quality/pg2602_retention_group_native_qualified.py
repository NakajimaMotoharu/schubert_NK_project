"""Fresh full3657/current retained native bridge, no VM recapture or lifecycle replay."""
import json
import subprocess
from pyflakes.api import check
import pg2582_current_jdbc_group_native_qualified as previous
from pg2600_retention_group_full_six import SOURCE, validate
from pg1446_current_cold_stage import W


def qualify_snapshot():
    outer = json.loads((W / 'pg2601-retention-group-full-qualified-v1/manifest.safe.json').read_bytes())
    if type(outer.get('actualExit')) is not int or outer['actualExit'] != 0:
        raise ValueError('actual independently qualified full3657 required')
    full = outer['result']
    expected = {'productionSource': SOURCE, 'tests': 3657, 'suites': 540,
                'mainClasses': 1643, 'FESFlakyNotRun': 0, 'staticSixModules': 0}
    if any(type(full.get(k)) is not type(v) or full[k] != v for k, v in expected.items()):
        raise ValueError('exact whole full3657 required')
    validate(full['sourceSnapshot'])
    if subprocess.check_output(['git', 'status', '--porcelain']) or subprocess.check_output(
        ['git', 'diff', '--name-only', full['sourceSnapshot'], 'HEAD', '--',
         'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization']):
        raise ValueError('clean whole source input equality required')


def server():
    raw = previous.server().replace('PG2582', 'PG2602').replace('PG2578', 'PG2600').replace('3653', '3657')
    if check('ARCHIVE_SHA=""\ncoordinates=lambda a,b:{}\n' + raw, '<retention Main byte bridge>'):
        raise ValueError('whole bridge namespace required')
    compile(raw, '<full3657 current retained native>', 'exec')
    return raw


def source():
    raw = previous.source().replace('pg2582-current-jdbc-group-native-qualified-v1',
        'pg2602-retention-group-native-qualified-v1').replace('PG2582', 'PG2602').replace(
        'pg2579-current-jdbc-group-full-qualified-v1', 'pg2601-retention-group-full-qualified-v1')
    if 'SSH+' in raw:
        raise ValueError('VM recapture refused')
    compile(raw, '<retained native transport>', 'exec')
    return raw


def entry():
    ns = {**previous.previous.entry().__globals__, 'CODE': server(), 'SOURCE': SOURCE,
          'qualify_snapshot': qualify_snapshot}
    exec(compile(source(), '<exact snapshot retained native>', 'exec'), ns)
    return ns['main']


if __name__ == '__main__':
    raise SystemExit(entry()())
