"""Same sealed native27 against new3694, all1643 Main/resource bytes; no guest op."""
import inspect
import json
import subprocess
import pg3058_boundary_group_native_rejoin as builder
import pg3190_browser_three_activation_join as three
import pg2390_same_source_native_join as transport
from pg1446_current_cold_stage import W
from pg3204_expiry_group_full_six import SOURCE, validate

SLOT = 'pg3208-expiry-group-native-qualified-v1'


def build_payload(full, capsule_full, digest):
    raw = inspect.getsource(builder.build_payload).replace('3691', '3694').replace('PG3054', 'PG3204')
    ns = dict(builder.__dict__)
    exec(compile(raw, '<exact new3694 native27 builder>', 'exec'), ns)
    raw = three.expand(ns['build_payload'](full), digest).replace('PG3190', 'PG3208')
    marker = "inputs[2]['qualifiedFull']==FULL"
    if raw.count(marker) != 1 or capsule_full['tests'] != 3691 or capsule_full['productionSource'] != SOURCE:
        raise ValueError('exact native27 capsule host provenance required')
    raw = 'CAPSULE_FULL=' + repr(capsule_full) + '\n' + raw.replace(marker, "inputs[2]['qualifiedFull']==CAPSULE_FULL")
    compile(raw, '<all sealed native27 and new whole3694>', 'exec')
    return raw


def payload():
    receipt = json.loads((W / 'pg3206-expiry-group-full-qualified-v1/manifest.safe.json').read_bytes())
    if receipt['actualExit'] != 0:
        raise ValueError('actual3694 independent full required')
    full = receipt['result']
    validate(full['sourceSnapshot'])
    if subprocess.check_output(['git', 'status', '--porcelain']) or subprocess.check_output(['git', 'diff', full['sourceSnapshot'], 'HEAD', '--', 'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization']):
        raise ValueError('clean exact current Test/Main byte scope required')
    capsule = json.loads((W / 'pg3188-browser-native-qualified-v1/manifest.safe.json').read_bytes())
    old = json.loads((W / 'pg3056-boundary-group-full-qualified-v1/manifest.safe.json').read_bytes())
    if capsule['actualExit'] != 0 or old['actualExit'] != 0:
        raise ValueError('actual sealed same-a9 provenance required')
    return build_payload(full, old['result'], capsule['manifestSha256'])


def main():
    raw = inspect.getsource(transport.main).replace('pg2284-current-signed-native-qualified-v1', 'pg2934-format-fixed-same-native-qualified-v1').replace('pg2384-current-resume-native-qualified-v1', 'pg3030-current-resume-native-qualified-v1').replace("'pg3030-current-resume-native-qualified-v1']", "'pg3030-current-resume-native-qualified-v1','pg3188-browser-native-qualified-v1']").replace('PG2390', 'PG3208')
    ns = {**transport.__dict__, 'SOURCE': SOURCE, 'SLOT': SLOT, 'payload': payload}
    exec(compile(raw, '<sealed native only new3694 rejoin transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
