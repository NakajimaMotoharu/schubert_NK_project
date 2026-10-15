"""Freeze actual shared-browser ABI, independent oracle and retained credential RO proof."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg1446_current_cold_stage import W, P
from pg1674_critical_management_gate import management_gate

ROOT = Path(__file__).resolve().parents[2]
SLOT = 'pg3138-browser-cohort-ready-v4'
JAVA = Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')
SHARED = [
    'program/characterization/tests/java/dev/codex/schubert/characterization/CurrentCharacterizationTest.java',
    'program/characterization/tests/java/dev/codex/schubert/characterization/NativeNkBootstrapAuthentication.java',
]
SOURCES = SHARED + [
    'tools/quality/vm/050_s1/NativeNkBrowserBusinessCohort.java',
    'tools/quality/vm/050_s1/NativeNkBrowserBusinessOracleTest.java',
]
ORACLES = ['tools/quality/pg3122_prepared_browser_resume_contract_test.py', 'tools/quality/pg3134_browser_resume_contract_test.py', 'tools/quality/pg3136_browser_rows_oracle_test.py', 'tools/quality/pg3160_partial_login_rows_oracle_test.py', 'tools/quality/pg3166_browser_tls_witness_test.py']
PINNED = SOURCES + ORACLES + [
    'program/characterization/baseline/current/artifacts/CHR-U01.json',
    'tools/quality/pg3120_prepared_browser_observer.py', 'tools/quality/pg3122_prepared_browser_resume_once.py',
    'tools/quality/pg3124_browser_resume_live_binding.py', 'tools/quality/pg3130_browser_resume_terminal.py',
    'tools/quality/pg3126_browser_business_socks.py',
    'tools/quality/pg3132_browser_resume_rows.py', 'tools/quality/pg3134_browser_resume_full_seal.py',
    'tools/quality/pg3136_browser_rows_oracle.py', 'tools/quality/pg3140_browser_business_actual.py',
    'tools/quality/pg3138_browser_cohort_ready.py',
    'tools/quality/pg3160_partial_login_rows_oracle.py',
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def classpath(classes):
    return str(classes) + ':' + str(W / 'pg460-chr-host/test-classes') + ':' + str(W / 'pg460-chr-host/classes') + ':' + (W / 'pg459-chr-classpath.private').read_text().strip()


def require_ready():
    out = W / SLOT
    value = json.loads((out / 'manifest.safe.json').read_bytes())
    if value['actualExit'] != 0 or value['sourceQualified'] is not True or value['plannedCases'] != 12 or not value['credentialReadOnlyQualified']:
        raise ValueError('all planned Browser preconditions required')
    if value['inputs'] != {name: sha(ROOT / name) for name in PINNED}:
        raise ValueError('prepared Browser input bytes drifted')
    if value['classes'] != {str(path.relative_to(out / 'classes')): sha(path) for path in (out / 'classes').rglob('*.class')}:
        raise ValueError('sealed Browser ABI changed')
    return value


def main():
    os.umask(0o077)
    if subprocess.check_output(['git', 'status', '--porcelain']):
        raise ValueError('clean frozen Browser preparation required')
    out = W / SLOT
    out.mkdir(mode=0o700)
    classes = out / 'classes'; classes.mkdir(mode=0o700)
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    inputs = {name: sha(ROOT / name) for name in PINNED}
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    commands = [[str(JAVA / 'javac'), '-Xlint:all', '-Werror', '-cp', classpath(classes), '-d', str(classes), *SOURCES]]
    commands += [[str(JAVA / 'java'), '-cp', classpath(classes), 'dev.codex.schubert.characterization.NativeNkBrowserBusinessOracleTest']]
    commands += [['python3', '-B', name] for name in ORACLES]
    commands += [[str(JAVA / 'java'), '-cp', classpath(classes), 'dev.codex.schubert.characterization.NativeNkBrowserBusinessCohort', 'preflight', str(out / 'credential-ro')]]
    results = []
    for number, command in enumerate(commands, 1):
        with (out / ('phase-' + str(number) + '.private.log')).open('xb') as log:
            if number == len(commands):
                with management_gate(P / 'current-management-critical.lock'):
                    result = subprocess.run(command, stdout=log, stderr=log, timeout=90)
            else:
                result = subprocess.run(command, stdout=log, stderr=log, timeout=90)
        results.append(result.returncode)
        if result.returncode:
            break
    qualified = inputs == {name: sha(ROOT / name) for name in PINNED} and head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip() and not subprocess.check_output(['git', 'status', '--porcelain'])
    value = {'actualExit': next((code for code in results if code), 0), 'sourceQualified': qualified, 'operatorSource': head, 'productionSource': 'a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25', 'plannedCases': 12, 'phases': results, 'credentialReadOnlyQualified': len(results) == len(commands) and not any(results), 'inputs': inputs, 'classes': {str(path.relative_to(classes)): sha(path) for path in classes.rglob('*.class')}, 'startedUTC': start, 'completedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'rootBrowserStarts0': True, 'formalAccepted': False}
    with (out / 'manifest.safe.json').open('x') as file:
        json.dump(value, file, sort_keys=True); file.flush(); os.fsync(file.fileno())
    for path in classes.rglob('*.class'):
        path.chmod(0o400)
    print(json.dumps({key: value[key] for key in ['actualExit', 'sourceQualified', 'plannedCases', 'phases', 'credentialReadOnlyQualified', 'rootBrowserStarts0', 'formalAccepted']}))
    return value['actualExit'] or (0 if qualified else 1)


if __name__ == '__main__':
    raise SystemExit(main())
