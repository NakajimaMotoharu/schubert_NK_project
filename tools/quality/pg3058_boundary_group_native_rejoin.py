"""Sealed same-a9 two-activation native against new3691; no guest read or replay."""
import inspect
import json
import subprocess
import pg3032_same_a9_two_activation_join as previous
from pg3054_boundary_group_full_six import SOURCE, validate
from pg1446_current_cold_stage import W

SLOT = 'pg3058-boundary-group-native-qualified-v1'


def build_payload(full):
    if any(full.get(k) != v for k, v in {'productionSource': SOURCE, 'tests': 3691, 'suites': 542, 'mainClasses': 1643, 'FESFlakyNotRun': 0, 'staticSixModules': 0}.items()):
        raise ValueError('exact actual3691 full input required')
    raw = previous.payload().replace('PG3032', 'PG3058').replace('PG3026', 'PG3054').replace('3685', '3691')
    marker = "old=inputs[0]['qualifiedFull'];full=inputs[1]['qualifiedFull'];"
    if raw.count(marker) != 1:
        raise ValueError('one explicit host input boundary required')
    raw = raw.replace(marker, "old=inputs[0]['qualifiedFull'];full=FULL;")
    # Immutable raw capsule and complete jar are checked again after the six analyses.
    marker = "result={'actualExit':0"
    if raw.count(marker) != 1:
        raise ValueError('one final result boundary required')
    guard = """for root,v,digest in zip(roots,inputs,MANIFESTS,strict=True):
 require(sha(root/'manifest.safe.json')==digest)
 for n,h in v['files'].items():require(sha(root/n)==h)
for m in modules:require(sha(jars[m])==full['jarHashes'][m])
"""
    raw = raw.replace(marker, guard + marker)
    raw = 'FULL=' + repr(full) + '\n' + raw
    compile(raw, '<sealed native18 new3691 exact input>', 'exec')
    return raw


def payload():
    receipt = json.loads((W / 'pg3056-boundary-group-full-qualified-v1/manifest.safe.json').read_bytes())
    if receipt['actualExit'] != 0:
        raise ValueError('new3691 independent full actual0 required')
    full = receipt['result']
    validate(full['sourceSnapshot'])
    if subprocess.check_output(['git', 'status', '--porcelain']) or subprocess.check_output(['git', 'diff', full['sourceSnapshot'], 'HEAD', '--', 'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization']):
        raise ValueError('fixed exact current full scope required')
    return build_payload(full)


def main():
    raw = inspect.getsource(previous.previous.main).replace('pg2284-current-signed-native-qualified-v1', 'pg2934-format-fixed-same-native-qualified-v1').replace('pg2384-current-resume-native-qualified-v1', 'pg3030-current-resume-native-qualified-v1').replace('PG2390', 'PG3058')
    ns = {**previous.previous.__dict__, 'SOURCE': SOURCE, 'SLOT': SLOT, 'payload': payload}
    exec(compile(raw, '<actual sealed native only rejoin>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
