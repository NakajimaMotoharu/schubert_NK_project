"""Verify the three canary outcomes using direct diagnostics and frozen hashes."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess


OPS = Path('evidence/01_PT/018_NK-OPS-001/evidence')


def pin(path):
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def verified(ref):
    path = Path(ref['path'])
    assert pin(path) == ref
    return path


def main():
    terminal = next(OPS.glob('PG40646-*')) / 'terminal.json'
    result = json.loads(terminal.read_bytes())
    begin = json.loads(verified(result['begin']).read_bytes())
    cases = result['observedOutcomes']
    assert set(cases) == {'valid', 'nullable', 'unchecked'}
    core = result['productionCore']
    assert core == begin['productionCore'] and result['source'] == begin['source']
    assert result['actualProductionFilesCompiled'] == result['productTests'] == 0
    assert begin['expectedCases'] == 3
    for ref in begin['pomInputs']:
        p = verified(ref)
        assert p.read_bytes() == subprocess.check_output(['git', 'show', f'{core}:{p}'])
    for ref in (begin['java'], begin['compiler'], begin['maven']):
        verified(ref)
    logs = {}
    common_command = cases['valid']['command']
    assert common_command[-1] == 'compile' and '-o' in common_command and '-N' in common_command
    for case in cases.values():
        assert case['command'] == common_command
        verified(case['source'])
        report = verified(case['log']).read_text()
        assert 'enforcer:3.6.3:enforce (toolchain-and-dependency-contract)' in report
        assert 'spotless:3.10.2:check (java-format-contract)' in report
        assert 'compiler:3.14.0:compile (default-compile)' in report
        assert 'Compiling 1 source file with javac [forked debug release 25]' in report
        logs[case['source']['path'].split('/')[-1].removesuffix('.java.txt')] = report

    guarded = verified(cases['valid']['source']).read_text()
    dereference = verified(cases['nullable']['source']).read_text()
    assert guarded.replace('value == null ? 0 : ', '', 1) == dereference
    assert '[INFO] BUILD SUCCESS' in logs['valid']
    assert all(prefix not in logs['valid'] for prefix in ('[ERROR]', '[WARNING]'))
    assert cases['valid']['actualExit'] == 0
    assert cases['valid']['resultingClassNames'] == ['CompilerContractCanary.class']

    assert "[NullAway] dereferenced expression 'value' is @Nullable" in logs['nullable']
    assert '[unchecked]' not in logs['nullable'] and '-Werror specified' not in logs['nullable']
    assert '[unchecked] unchecked cast' in logs['unchecked']
    assert 'warnings found and -Werror specified' in logs['unchecked']
    assert '[NullAway]' not in logs['unchecked']
    for name in ('nullable', 'unchecked'):
        assert cases[name]['actualExit'] == 1 and cases[name]['resultingClassNames'] == []
        assert '[INFO] BUILD FAILURE' in logs[name]

    out = OPS / 'PG40648-f03-real-compiler-controls-independent-v1'
    out.mkdir()
    manifest = out / 'manifest.json'
    with manifest.open('x') as stream:
        json.dump(dict(actualExit=0, terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                       source=result['source'], productionCore=core,
                       testIds=['PT-F03-COMPILER-001', 'PT-F03-COMPILER-002', 'PT-F03-COMPILER-003'],
                       actualToolTerminals=[0, 1, 1], positiveCompiles=1, intendedRejections=2,
                       testedCompilerPlugin='3.14.0', compiledProductInputs=0,
                       terminal=pin(terminal), productTestsExecuted=0, wholeF03=False,
                       whole451=False), stream, indent=2)
        stream.write('\n')
    print(pin(manifest))


if __name__ == '__main__':
    main()
