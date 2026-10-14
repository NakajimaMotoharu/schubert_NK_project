"""Current latest-nine CRC/session evidence joined to fresh full3653; no VM replay."""
import inspect
import json
import subprocess
import pg2564_strict_current_native_qualification as previous
from pg2578_current_jdbc_group_full_six import SOURCE, validate
from pg1446_current_cold_stage import W


def qualify_snapshot():
    outer = json.loads((W / 'pg2579-current-jdbc-group-full-qualified-v1/manifest.safe.json').read_bytes())
    if type(outer.get('actualExit')) is not int or outer['actualExit'] != 0:
        raise ValueError('actual independently qualified grouped full required')
    full = outer['result']
    expected = {'productionSource': SOURCE, 'tests': 3653, 'suites': 540, 'mainClasses': 1643,
                'FESFlakyNotRun': 0, 'staticSixModules': 0}
    if any(type(full.get(k)) is not type(v) or full[k] != v for k, v in expected.items()):
        raise ValueError('exact fresh3653/540/1643/static6 required')
    validate(full['sourceSnapshot'])
    if subprocess.check_output(['git', 'status', '--porcelain']) or subprocess.check_output(
        ['git', 'diff', '--name-only', full['sourceSnapshot'], 'HEAD', '--',
         'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization']):
        raise ValueError('clean whole grouped snapshot inputs required')


def server():
    raw = previous.server().replace('PG2564', 'PG2582').replace('PG2510', 'PG2578').replace(
        'qualified2510Tests', 'qualified2578Tests').replace('3650', '3653')
    compile(raw, '<same current native full3653 CRC/session qualifier>', 'exec')
    return raw


def source():
    raw = previous.source().replace('pg2564-strict-current-native-qualified-v1',
        'pg2582-current-jdbc-group-native-qualified-v1').replace('PG2564', 'PG2582').replace(
        'pg2511-strict-reference-full-qualified-v1', 'pg2579-current-jdbc-group-full-qualified-v1')
    compile(raw, '<grouped full current native transport>', 'exec')
    return raw


def entry():
    ns = {**previous.entry().__globals__, 'CODE': server(), 'SOURCE': SOURCE,
          'qualify_snapshot': qualify_snapshot}
    exec(compile(source(), '<current native exact grouped snapshot>', 'exec'), ns)
    return ns['main']


if __name__ == '__main__':
    raise SystemExit(entry()())
