"""Join existing API/Web timeout test receipts and current signed source without running tests."""
import ast
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess

D = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))
E = Path('evidence/01_PT/018_NK-OPS-001/evidence')
DIRECTIVES = ('TimeoutStartSec', 'TimeoutStopSec')
EXPECTED = {'api': ('120s', '60s'), 'web': ('120s', '30s')}
EFFECTIVE = ('TimeoutStartUSec', 'TimeoutStopUSec')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], timeout=20)


def declarations(source):
    group = None
    found = {}
    for lineno, line in enumerate(source.decode().splitlines(), 1):
        if line.startswith('[') and line.endswith(']'):
            group = line[1:-1]
        if group == 'Service':
            key, assignment, value = line.partition('=')
            if assignment and key in DIRECTIVES:
                assert key not in found
                found[key] = (value, lineno)
    return found


def main():
    start = json.loads(next(D.glob('652_C02*')).read_bytes())['values']
    head = git('rev-parse', 'HEAD').decode().strip()
    assert head == start['source']
    pins = start['oracleReferences']
    data = [Path(p['path']).read_bytes() for p in pins]
    assert [sha(d) for d in data] == [p['sha256'] for p in pins]
    order, shutdown = map(json.loads, data[:2])
    core = start['productionCoreMain']
    assert order['sourceCore'] == shutdown['productionCore'] == core
    assert order['sourceOnly'] and not order['currentHostObservation'] and not order['returnedUnitEvidence']
    assert order['actualExit'] == shutdown['actualExit'] == 0 and shutdown['actualEffectiveUnits'] == 0
    assert not order['wholeC02Accepted'] and not shutdown['wholeC02Accepted']
    assert order['tests'][0]['testId'] == 'PT-C02-TEXT-001' and order['tests'][0]['passed']
    assert shutdown['afterMatched'] == 6
    assert order['verifier']['sha256'] == pins[2]['sha256']
    assert Path(order['verifier']['path']).resolve() == Path(pins[2]['path']).resolve()

    design = order['canonical']
    assert git('rev-parse', 'origin/main').decode().strip() == design['source']
    canonical = git('show', f"{design['source']}:{design['path']}")
    assert sha(canonical) == design['sha256']
    design_rows = []
    for key, text in zip(DIRECTIVES, ('120s', 'Web 30s/API 60s'), strict=True):
        line, = [n for n, s in enumerate(canonical.decode().splitlines(), 1)
                 if s.startswith(f'| `{key}` | {text} |')]
        design_rows.append(line)
    matrix = {}
    for line in data[3].decode().splitlines():
        cells = line.split('\t')
        if len(cells) >= 9 and cells[2] in ('WBS-C02-a', 'WBS-C02-b'):
            matrix[cells[2]] = dict(sequence=int(cells[0]), subject=cells[6], closure=cells[-1])
    assert matrix.keys() == {'WBS-C02-a', 'WBS-C02-b'}

    # Confirm the archived test included the timeout directives, using AST only.
    tree = ast.parse(data[2].decode())
    variables = {n.targets[0].id: n.value for n in tree.body
                 if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)}
    keys = ast.literal_eval(variables['KEYS'])
    cases = {k.id: ast.literal_eval(v) for k, v in zip(variables['DECLARED'].keys, variables['DECLARED'].values)
             if isinstance(k, ast.Name) and k.id.lower() in EXPECTED}
    assert set(cases) == {'API', 'WEB'}
    indexed = [keys.index(k) for k in DIRECTIVES]
    files = {row['path']: row for row in order['currentFiles']}
    green_ref = shutdown['candidates'][-1]
    green = json.loads(Path(green_ref['path']).read_bytes())
    assert sha(Path(green_ref['path']).read_bytes()) == green_ref['sha256']
    assert green['sourceDefinitions'] == order['currentFiles']
    assert not green['effectiveSystemdPolicyObserved'] and green['backendActions'] == 0
    results = []
    for name, expected in EXPECTED.items():
        path = Path(f'src/deployment/systemd/schubert-nk-{name}.service.template')
        raw = git('show', f'{head}:{path}')
        assert raw == git('show', f'{core}:{path}') == path.read_bytes()
        assert sha(raw) == files[str(path)]['sha256']
        values = declarations(raw)
        assert tuple(values[k][0] for k in DIRECTIVES) == expected
        assert tuple(cases[name.upper()][i] for i in indexed) == expected
        for key, effective, dline in zip(DIRECTIVES, EFFECTIVE, design_rows, strict=True):
            observed, line = values[key]
            results.append(dict(service=name, directive=key, literal=observed, file=str(path), line=line,
                                fileSha256=sha(raw), designLine=dline, existingTest='PT-C02-TEXT-001',
                                textStatus='QUALIFIED_REUSED', effectiveProperty=effective,
                                effectiveObserved=None, runtimeTerminalAccepted=False))
    manifest = dict(actualExit=0, source=head, productionCore=core, canonical=design,
                    acceptanceRows=matrix, timeoutRows=results, references=pins,
                    missingEvidence=[
                        'Same deployment source/boot and retained owner, with effective API/Web start and stop times.',
                        'Same invocation readiness and genuine start and stop terminal results, including owned resource postconditions.',
                        'Separate Web to Caddy readiness, TLS, Inspector terminal and native ownership, plus 451.'],
                    priorTestsReused=1, priorTestsReexecuted=0, newProductTests=0,
                    systemdInvocations=0, sshAttempts=0, wholeC02Accepted=False, newFormalAcceptance=0,
                    terminalAtUTC=datetime.now(timezone.utc).isoformat())
    out = E / start['run']
    out.mkdir()
    p = out / 'manifest.json'
    p.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(sha(p.read_bytes()))


if __name__ == '__main__':
    main()
