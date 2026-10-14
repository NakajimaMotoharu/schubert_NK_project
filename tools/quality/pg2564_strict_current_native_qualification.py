"""Fresh latest-nine sessions/all1643 CRC against full3650; only explicit A01 result may differ."""
import inspect
import json
import subprocess
from pathlib import Path
import pg2474_question_native_qualified_results as previous
from pg2510_strict_reference_full_six import validate, SOURCE
from pg1446_current_cold_stage import W

ARTIFACT = 'program/characterization/reports/nk/PG2550-native-a01-v1/artifacts/CHR-A01.json'


def result_changes(changes, artifact, baseline, receipt):
    raw = inspect.getsource(previous.result_changes)
    ns = {**previous.__dict__, 'ARTIFACT':ARTIFACT, 'SOURCE':SOURCE}
    exec(compile(raw, '<explicit independent new A01 result classification>', 'exec'), ns)
    return ns['result_changes'](changes, artifact, baseline, receipt)


def qualify_snapshot():
    outer = json.loads((W / 'pg2511-strict-reference-full-qualified-v1/manifest.safe.json').read_bytes())
    if type(outer.get('actualExit')) is not int or outer['actualExit'] != 0:
        raise ValueError('actual fresh full3650 qualification required')
    full = outer['result']
    expected = {'productionSource':SOURCE, 'tests':3650, 'suites':540, 'mainClasses':1643, 'FESFlakyNotRun':0, 'staticSixModules':0}
    if any(type(full.get(k)) is not type(v) or full[k] != v for k,v in expected.items()):
        raise ValueError('fresh exact full3650/540/1643/static6 required')
    validate(full['sourceSnapshot'])
    if subprocess.check_output(['git', 'status', '--porcelain']):
        raise ValueError('fixed clean new input/result operator required')
    changes = subprocess.check_output(['git', 'diff', '--name-only', full['sourceSnapshot'], 'HEAD', '--',
        'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization'], text=True).splitlines()
    if changes:
        result_changes(changes, Path(ARTIFACT).read_bytes(), Path(previous.BASELINE).read_bytes(),
                       json.loads((W / 'pg2550-chr-a01-native-v1.safe.json').read_bytes()))


def server():
    raw = previous.server().replace('PG2474', 'PG2564').replace('PG2404', 'PG2510').replace(
        'qualified2404Tests', 'qualified2510Tests').replace('3637', '3650').replace(previous.SOURCE, SOURCE)
    compile(raw, '<fresh latest-nine exact full3650 CRC/session server>', 'exec')
    return raw


def source():
    raw = previous.source()
    for before, after in [('pg2466-question-current-native-catalog-v1', 'pg2562-strict-current-native-catalog-v1'),
        ('pg2474-question-current-native-qualified-v1', 'pg2564-strict-current-native-qualified-v1'),
        ('PG2474', 'PG2564'), ('pg2405-question-jdbc-full-qualified-v1', 'pg2511-strict-reference-full-qualified-v1')]:
        raw = raw.replace(before, after)
    compile(raw, '<fresh actual native transport>', 'exec')
    return raw


def entry():
    ns = {**previous.entry().__globals__, 'CODE':server(), 'SOURCE':SOURCE, 'qualify_snapshot':qualify_snapshot}
    exec(compile(source(), '<fresh Source all1643 current sessions qualification>', 'exec'), ns)
    return ns['main']


if __name__ == '__main__':
    raise SystemExit(entry()())
