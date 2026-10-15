"""Current Browser activation CRC/session/member proof against qualified3691.

SS355/451; PT-OPS-3188-001. Existing jar bytes only, no build/deploy/Root replay.
"""
import json
import subprocess
import pg3030_current_resume_native_qualified as previous
from pg3054_boundary_group_full_six import SOURCE, validate
from pg1446_current_cold_stage import W


def qualify_snapshot():
    receipt = json.loads((W / 'pg3056-boundary-group-full-qualified-v1/manifest.safe.json').read_bytes())
    full = receipt['result']
    required = {'productionSource': SOURCE, 'tests': 3691, 'suites': 542, 'mainClasses': 1643, 'FESFlakyNotRun': 0, 'staticSixModules': 0}
    if receipt['actualExit'] != 0 or any(type(full.get(k)) is not type(v) or full[k] != v for k, v in required.items()):
        raise ValueError('actual exact3691 whole input required')
    validate(full['sourceSnapshot'])
    if subprocess.check_output(['git', 'status', '--porcelain']) or subprocess.check_output(['git', 'diff', full['sourceSnapshot'], 'HEAD', '--', 'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization']):
        raise ValueError('clean unchanged Main/Test/settings required')


def server():
    raw = previous.server().replace('PG3030', 'PG3188').replace('PG3026', 'PG3054').replace('qualified3026Tests', 'qualified3054Tests').replace('3685', '3691')
    compile(raw, '<current Browser CRC/session/all Main-resource bytes>', 'exec')
    return raw


def source():
    raw = previous.source().replace('pg3022-current-resume-native-catalog-v1', 'pg3186-browser-native-catalog-v1').replace('pg3030-current-resume-native-qualified-v1', 'pg3188-browser-native-qualified-v1').replace('pg3028-extra-row-full-qualified-v1', 'pg3056-boundary-group-full-qualified-v1').replace('PG3030', 'PG3188')
    compile(raw, '<current Browser qualified3691 transport>', 'exec')
    return raw


def entry():
    ns = {**previous.entry().__globals__, 'CODE': server(), 'SOURCE': SOURCE, 'qualify_snapshot': qualify_snapshot}
    exec(compile(source(), '<actual current Browser native qualification>', 'exec'), ns)
    return ns['main']


if __name__ == '__main__':
    raise SystemExit(entry()())
