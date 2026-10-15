"""Resume immutable PG3266 after first keyscan failure, only if remote never issued.

No alternate source, namespace overwrite, VM or existing whole-job restart.
"""
import ast
import hashlib
import json
import os
import subprocess
from lan_server import copy, run
from pg1446_current_cold_stage import W
from pg3258_statement_group_full_six import ROOT, SOURCE
import pg3266_header_protocol_regression as target


def main():
    os.umask(0o077)
    out = W / 'pg3266-header-protocol-regression-v1'
    script = out / 'regression.private.py'; archive = out / 'source.tar'
    if (out / 'manifest.safe.json').exists() or (out / 'resume-transport.private.log').exists():
        raise ValueError('single unissued transport recovery only')
    raw = script.read_text(); data = ast.literal_eval(raw.splitlines()[0].removeprefix('INPUT='))
    if raw != 'INPUT=' + repr(data) + '\n' + target.server() or data['source'] != SOURCE:
        raise ValueError('exact original sealed stage/server required')
    if hashlib.sha256(archive.read_bytes()).hexdigest() != data['archiveSha256']:
        raise ValueError('original fixed source archive required')
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT) or subprocess.check_output(
            ['git', 'diff', data['head'], 'HEAD', '--', 'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization'], cwd=ROOT):
        raise ValueError('same committed Main/Test/config scope as staged source required')
    base = '/home/mini/schubert-nk-pgpt'
    guard = "python3 -B - <<'ONCE'\nfrom pathlib import Path\nb=Path('" + base + "')\npaths=[b/'runs/PG3266-v1',b/'source-protocol-PG3266-v1',b/'transfer/PG3266-v1']\nassert all(not p.exists()and not p.is_symlink()for p in paths)\npaths[2].mkdir(mode=0o700)\nprint('EXACT_ALL_THREE_ABSENT_THEN_NEW_TRANSFER')\nONCE"
    code, observation = run(guard, timeout=40)
    if code or 'EXACT_ALL_THREE_ABSENT_THEN_NEW_TRANSFER' not in observation:
        raise ValueError('remote unissued proof and exclusive namespace reservation required')
    receipt = {'initialFailure': 'SSH_KEYSCAN_NONZERO_BEFORE_FIRST_REMOTE_COMMAND',
               'sameSourceArchive': data['archiveSha256'], 'fixedSourceSnapshot': data['head'],
               'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(),
               'freshRemoteAllThreeAbsent': True, 'wholePG3258Reissued': False, 'vmActions': 0}
    with (out / 'resume-reservation.safe.json').open('x') as stream:
        json.dump(receipt, stream, sort_keys=True)
    for p in [archive, script]:
        code, _ = copy(p, base + '/transfer/PG3266-v1/', 60)
        if code:
            raise ValueError('immutable existing Header archive/script transfer required')
    code, output = run('python3 -B ' + base + '/transfer/PG3266-v1/regression.private.py', 300)
    with (out / 'resume-transport.private.log').open('x') as stream:
        stream.write(output)
    value = {'actualExit': code, 'source': SOURCE, 'testSource': data['head'],
             'payloadSha256': receipt['payloadSha256'], 'formalAccepted': False,
             'transportRecovery': receipt}
    if code == 0:
        value['result'] = json.loads(next(line for line in output.splitlines() if line.startswith('{')))
    with (out / 'manifest.safe.json').open('x') as stream:
        json.dump(value, stream, sort_keys=True)
    print(json.dumps({k: v for k, v in value.items() if k != 'result'}))
    if code == 0:
        print(json.dumps({k: value['result'][k] for k in ['tests', 'suites', 'mainClasses', 'coverage', 'staticIssues', 'FESFlakyNotRun', 'startUTC', 'endUTC', 'allProtocolMainAndResourcesSameBytes']}))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
