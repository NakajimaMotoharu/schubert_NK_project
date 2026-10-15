"""Prove one PMD label false-positive and retained unsafe-key sensitivity without suppression."""
import base64
import hashlib
import inspect
import json
import os
from pathlib import Path

from lan_server import run

ROOT = Path(__file__).resolve().parents[2]
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')


def server(data):
    import base64
    import hashlib
    import json
    import os
    from pathlib import Path
    import subprocess
    import xml.etree.ElementTree as E

    os.umask(0o077); b = Path('/home/mini/schubert-nk-pgpt'); out = b / 'runs/PG3424-crypto-rule-canary-v1'; out.mkdir()
    old = b / 'runs/PG3382-static-gate-v1/result'; fixed = json.loads((old / 'manifest.safe.json').read_bytes())
    files = []
    for name, material in data['sources'].items():
        path = out / name; path.write_bytes(base64.b64decode(material, validate=True)); files.append(path)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == data['sourceSha256'][name]
    java = b / 'tools/jdk-25.0.4/bin'; classes = out / 'classes'; classes.mkdir()
    with (out / 'compile.private.log').open('xb') as log:
        compiled = subprocess.run([str(java / 'javac'), '--release', '25', '-Xlint:all', '-Werror', '-d', str(classes), *map(str, files)], stdout=log, stderr=subprocess.STDOUT, timeout=60)
    assert compiled.returncode == 0
    actual = subprocess.run([str(java / 'java'), '-cp', str(classes), 'DynamicKeyRuleCanary'], capture_output=True, timeout=5)
    assert actual.returncode == 0 and actual.stderr == b''
    assert actual.stdout == b'PASS dynamic-two-independent-inputs; label-not-key; caller-mutation-isolated\n'
    listing = out / 'all-java.txt'; listing.write_text(''.join(str(p) + '\n' for p in files))
    argv = list(fixed['pmd']['argv']); overlay = b / 'runs/PG3386-pmd-record-after-v1/pmd-record-1298.jar'
    assert hashlib.sha256(overlay.read_bytes()).hexdigest() == '4859fb956de018a843abe55ddb92b0a98921878b80525aaa2a77c5b5d8c2820c'
    argv[2] = str(overlay) + ':' + argv[2]
    argv[argv.index('--file-list') + 1] = str(listing)
    argv[argv.index('--aux-classpath') + 1] = str(classes)
    argv[argv.index('--report-file') + 1] = str(out / 'pmd.xml')
    with (out / 'pmd.private.log').open('xb') as log:
        pmd = subprocess.run(argv, stdout=log, stderr=subprocess.STDOUT, timeout=120)
    report = E.parse(out / 'pmd.xml').getroot(); assert not report.findall('.//{*}error') and pmd.returncode == 4
    findings = []
    for node in report.findall('{*}file'):
        for violation in node.findall('{*}violation'):
            if violation.get('rule') == 'HardCodedCryptoKey':
                name = Path(node.get('name')).name; line = int(violation.get('beginline'))
                code = (out / name).read_text().splitlines()[line - 1]
                findings.append({'source': name, 'line': line, 'sourceLine': code.strip()})
    assert len(findings) == 2 and {f['source'] for f in findings} == set(data['sources'])
    assert all(('"currentKey"' in f['sourceLine'] if f['source'].startswith('Dynamic') else 'new byte[]' in f['sourceLine']) for f in findings)
    result = {'actualExit': 0, 'run': 'PG3424-crypto-rule-canary-v1', 'compileExit': 0, 'dynamicRuntimeExit': 0,
              'dynamicIndependentValues': 2, 'callerMutationIsolated': True, 'pmdExit': pmd.returncode,
              'sameFrozenRules': True, 'sourceSha256': data['sourceSha256'], 'findings': findings,
              'trueUnsafeCounterexampleStillDetected': True, 'dynamicValidationLabelFalsePositiveReproduced': True,
              'pmdReportSha256': hashlib.sha256((out / 'pmd.xml').read_bytes()).hexdigest(),
              'newProductionPtCredit': 0, 'productionChanged': False, 'suppressionAdded': False, 'F03Accepted': False}
    (out / 'manifest.safe.json').write_text(json.dumps(result, sort_keys=True)); print(json.dumps(result))


def main():
    names = ['DynamicKeyRuleCanary.java', 'UnsafeKeyRuleCanary.java']; inputs = {name: (ROOT / 'tools/quality/static/canaries' / name).read_bytes() for name in names}
    data = {'sources': {n: base64.b64encode(v).decode() for n, v in inputs.items()},
            'sourceSha256': {n: hashlib.sha256(v).hexdigest() for n, v in inputs.items()}}
    raw = inspect.getsource(server) + '\nserver(' + repr(data) + ')\n'
    os.umask(0o077); out = W / 'pg3424-crypto-rule-canary-v1'; out.mkdir()
    (out / 'canary.private.py').write_text(raw)
    rc, text = run("python3 - <<'CANARY'\n" + raw + '\nCANARY', timeout=200)
    (out / 'observer.private.log').write_text(text)
    assert rc == 0, 'canary not qualified; preserve new-only slot'
    result = json.loads(text.strip()); (out / 'manifest.safe.json').write_text(json.dumps(result, sort_keys=True))
    public = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3424-crypto-rule-canary'; public.mkdir()
    path = public / 'manifest.json'; path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'actualExit': 0, 'labelFalsePositive': 1, 'unsafeDetectionRetained': 1,
                      'manifestSha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'F03Accepted': False}))


if __name__ == '__main__':
    main()
