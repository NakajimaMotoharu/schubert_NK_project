"""Current activation's latest nine against exact new3685 and all1643 Main/member bytes."""
import json
import subprocess
import pg2908_network_current_native_qualification as transport
import pg2934_format_fixed_same_native as member_qualified
from pg3026_extra_row_full_six import SOURCE, validate
from pg1446_current_cold_stage import W


def qualify_snapshot():
    outer = json.loads((W / 'pg3028-extra-row-full-qualified-v1/manifest.safe.json').read_bytes())
    full = outer['result']
    required = {'productionSource': SOURCE, 'tests': 3685, 'suites': 542, 'mainClasses': 1643, 'FESFlakyNotRun': 0, 'staticSixModules': 0}
    if outer.get('actualExit') != 0 or any(type(full.get(k)) is not type(v) or full[k] != v for k, v in required.items()):
        raise ValueError('actual exact3685 whole input required')
    validate(full['sourceSnapshot'])
    if subprocess.check_output(['git', 'status', '--porcelain']) or subprocess.check_output(['git', 'diff', full['sourceSnapshot'], 'HEAD', '--', 'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization']):
        raise ValueError('clean unchanged Main/Test/settings from qualified whole snapshot required')


def server():
    raw = member_qualified.server().replace('PG2930', 'PG3026').replace('qualified2930Tests', 'qualified3026Tests').replace('PG2934', 'PG3030').replace('3684', '3685')
    compile(raw, '<new3685/current native/all1643 byte comparison>', 'exec')
    return raw


def source():
    raw = transport.source()
    for a, b in [('pg2906-network-current-native-catalog-v1', 'pg3022-current-resume-native-catalog-v1'), ('pg2908-network-current-native-qualified-v2', 'pg3030-current-resume-native-qualified-v1'), ('pg2800-jdbc-null-fixed-full-qualified-v1', 'pg3028-extra-row-full-qualified-v1'), ('PG2908', 'PG3030')]:
        raw = raw.replace(a, b)
    raw = raw.replace('PG3030-native-v2', 'PG3030-native-v1').replace('PG3030-native-input-v2.tar', 'PG3030-native-input-v1.tar')
    marker = "data['libraries']=libs"
    if raw.count(marker) != 1:
        raise ValueError('one explicit whole-member baseline authority required')
    extra = """old_native=json.loads((W/'pg2908-network-current-native-qualified-v2/input.safe.json').read_bytes())
    if old_native['productionSource']!=SOURCE:raise ValueError('only same a9 original jar members allowed')
    data['nativeQualifiedFull']=old_native['qualifiedFull']
    """
    raw = raw.replace(marker, extra + marker)
    compile(raw, '<current native new-full exact transport>', 'exec')
    return raw


def entry():
    ns = {**transport.entry().__globals__, 'CODE': server(), 'SOURCE': SOURCE, 'qualify_snapshot': qualify_snapshot}
    exec(compile(source(), '<actual current native/whole3685 qualification>', 'exec'), ns)
    return ns['main']


if __name__ == '__main__':
    raise SystemExit(entry()())
