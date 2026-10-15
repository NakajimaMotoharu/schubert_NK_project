"""Retest identical849 input/aux bytes with the one-class PMD record overlay only."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter

BASE = Path('/home/mini/schubert-nk-pgpt/runs')
OLD = BASE / 'PG3382-static-gate-v1/result'
OUT = BASE / 'PG3386-pmd-record-after-v1'
OVERLAY = OUT / 'pmd-record-1298.jar'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_inputs(before):
    assert all(digest(OLD / 'source' / p) == h for p, h in before['sourceSha256'].items())
    assert all(digest(Path(p)) == h for p, h in before['auxJarSha256'].items())
    assert digest(OLD / 'source/tools/quality/static/pmd.xml') == before['ruleSha256']['pmd.xml']
    assert before['sourceFiles'] == 849 and before['auxMainClasses'] == 1643


def main():
    os.umask(0o077)
    assert OUT.is_dir() and OVERLAY.is_file()
    result_dir = OUT / 'result'; result_dir.mkdir(mode=0o700)
    before = json.loads((OLD / 'manifest.safe.json').read_bytes())
    check_inputs(before)
    import zipfile
    with zipfile.ZipFile(OVERLAY) as z:
        names = [n for n in z.namelist() if n.endswith('.class')]
        assert names == ['net/sourceforge/pmd/lang/java/rule/multithreading/NonThreadSafeSingletonRule.class']
        assert hashlib.sha256(z.read(names[0])).hexdigest() == '91c6fb28937e0877e754e503cfe49e927470ffc130dbfc8b823bbcc5c96e0f15'
    argv = list(before['pmd']['argv']); assert argv[1] == '-cp'
    argv[2] = str(OVERLAY) + ':' + argv[2]
    argv[argv.index('--report-file') + 1] = str(result_dir / 'pmd.xml')
    with (result_dir / 'pmd.private.log').open('xb') as f:
        run = subprocess.run(argv, stdout=f, stderr=subprocess.STDOUT, cwd=OLD, timeout=180)
    root = ET.parse(result_dir / 'pmd.xml').getroot()
    violations = root.findall('.//{*}violation'); errors = root.findall('.//{*}error')
    rules = dict(Counter(x.get('rule') for x in violations)); check_inputs(before)
    # Require the exact same original findings, not merely a lower total.
    def rows(report):
        r = ET.parse(report).getroot()
        return sorted((f.get('name'), v.get('rule'), v.get('beginline'), v.get('endline'), (v.text or '').strip())
                      for f in r.findall('{*}file') for v in f.findall('{*}violation'))
    exact = rows(OLD / 'pmd.xml') == rows(result_dir / 'pmd.xml')
    value = {'run': 'PG3386-pmd-record-after-v1', 'productionSource': before['productionSource'],
             'pmdExit': run.returncode, 'violations': len(violations), 'processingErrors': len(errors),
             'exactOriginalFindingsRetained': exact, 'ruleCounts': rules, 'sourceFiles': 849, 'auxMainClasses': 1643,
             'sourceRuleAuxAllUnchangedBeforeAfter': True, 'overlayJarSha256': digest(OVERLAY),
             'beforeManifestSha256': digest(OLD / 'manifest.safe.json'),
             'reportSha256': digest(result_dir / 'pmd.xml'), 'logSha256': digest(result_dir / 'pmd.private.log'),
             'F03Accepted': False, 'staticGatePass': False, 'newProductionPtCredit': 0, 'formalUpdated': False}
    with (result_dir / 'manifest.safe.json').open('x') as f:
        json.dump(value, f, indent=2)
    assert run.returncode == 4 and len(errors) == 0 and len(violations) == 2220 and exact
    print(json.dumps(value))


if __name__ == '__main__':
    main()
