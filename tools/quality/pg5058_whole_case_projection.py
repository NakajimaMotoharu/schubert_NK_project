"""Allowlisted projection of original3791 XML; never executes/requalifies the tests."""
import hashlib
import inspect
import json
import os
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
from lan_server import run
from pg4968_ssc304_full import SOURCE, ROOT, W

SLOT = 'PG4968-existing3791-cases'


def project_xml(module, name, blob, digest):
    if hashlib.sha256(blob).hexdigest() != digest:
        raise ValueError('original qualified XML changed')
    tree = ET.fromstring(blob)
    if tree.tag != 'testsuite' or any(int(tree.attrib.get(k, 0)) != 0 for k in ('failures', 'errors', 'skipped')):
        raise ValueError('zero-failure physical original suite required')
    forbidden = {'failure', 'error', 'skipped', 'flakyFailure', 'flakyError', 'rerunFailure', 'rerunError'}
    if any(n.tag in forbidden for n in tree.iter()):
        raise ValueError('failed/flaky/skipped/rerun cannot project as pass')
    cases = list(tree.iter('testcase'))
    if not cases or int(tree.attrib['tests']) != len(cases):
        raise ValueError('exact physical original case count')
    output = []
    for i, case in enumerate(cases, 1):
        clazz, label = case.attrib['classname'], case.attrib['name']
        if re.fullmatch(r'dev\.codex\.schubert\.[A-Za-z0-9_$.]+', clazz) is None or not label:
            raise ValueError('known project class and nonempty private case name required')
        identity = '\0'.join((module, name, str(i), clazz, label)).encode()
        output.append({'testId': 'PT-WHOLE-' + hashlib.sha256(identity).hexdigest(), 'module': module,
                       'class': clazz, 'caseOrdinalInXml': i, 'caseNameSha256': hashlib.sha256(label.encode()).hexdigest(),
                       'sourceXml': name, 'xmlSha256': digest, 'result': 'PASS_ORIGINAL_XML'})
    return output


def export(data):
    base = Path('/home/mini/schubert-nk-pgpt')
    source = base / 'source-full-PG4968'
    manifest = base / 'runs/PG4968-six-v1/manifest.safe.json'
    if hashlib.sha256(manifest.read_bytes()).hexdigest() != data['serverManifestSha256']:
        raise ValueError('same original terminal manifest')
    if subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip() != data['source']:
        raise ValueError('same original source snapshot')
    archive = base / 'transfer/PG4968-source.tar'
    digest = hashlib.sha256()
    with archive.open('rb') as f:
        while chunk := f.read(1048576):
            digest.update(chunk)
    if digest.hexdigest() != data['archiveSha256']:
        raise ValueError('same original source archive')
    all_cases = []
    for module, metadata in data['modules'].items():
        folder = source / ('src/schubert-nk-' + module + '/target/surefire-reports')
        actual = {p.name: p for p in folder.glob('TEST-*.xml')}
        if set(actual) != set(metadata['xmlHashes']) or len(actual) != metadata['suites']:
            raise ValueError('same original complete XML inventory')
        cases = []
        for name, sha in sorted(metadata['xmlHashes'].items()):
            path = actual[name]
            if path.is_symlink():
                raise ValueError('physical original XML only')
            blob = path.read_bytes()
            cases.extend(project_xml(module, name, blob, sha))
            if path.read_bytes() != blob:
                raise ValueError('original XML changed while reading')
        if len(cases) != metadata['tests']:
            raise ValueError('same original per-module test count')
        all_cases.extend(cases)
    if len(all_cases) != 3791 or len({x['testId'] for x in all_cases}) != 3791:
        raise ValueError('all3791 unique physical case references')
    return all_cases


def main():
    p = W / 'pg4970-ssc304-whole-qualified-v1/manifest.safe.json'
    raw = p.read_bytes()
    proof = json.loads(raw)
    r = proof['result']
    if not (type(proof['actualExit']) is int and proof['actualExit'] == 0 and proof['source'] == SOURCE
            and r['productionSource'] == SOURCE and r['sourceSnapshot'] == SOURCE and r['tests'] == 3791
            and r['suites'] == 553 and r['mainClasses'] == 1650 and r['FESFlakyNotRun'] == 0
            and r['oldNativeImported'] is False):
        raise ValueError('genuine original qualified3791/553/1650 required')
    data = {'source': SOURCE, 'serverManifestSha256': r['serverManifestSha256'],
            'archiveSha256': r['sourceArchiveSha256'], 'modules': r['modules']}
    payload = ('import hashlib,json,subprocess,re\nfrom pathlib import Path\nimport xml.etree.ElementTree as ET\n'
               + inspect.getsource(project_xml) + '\n' + inspect.getsource(export)
               + '\nprint(json.dumps(export(' + repr(data) + ')))\n')
    code, output = run("python3 -B - <<'PG5058_READ_ONLY'\n" + payload + '\nPG5058_READ_ONLY', timeout=120)
    if code:
        raise ValueError('original XML read-only projection failed; no rerun')
    cases = json.loads(output)
    if len(cases) != 3791:
        raise ValueError('all existing cases required before publication')
    os.umask(0o077)
    out = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional' / SLOT
    out.mkdir(mode=0o755)
    encoded = (json.dumps(cases, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode()
    with (out / 'cases.json').open('xb') as f:
        f.write(encoded)
    value = {'source': SOURCE, 'originalRun': 'PG4968', 'qualifiedBy': 'PG4970', 'tests': 3791, 'suites': 553,
             'mainClasses': 1650, 'projectionActualExit': 0, 'testExecutionsIssued': 0,
             'sourceArchiveSha256': r['sourceArchiveSha256'], 'serverManifestSha256': r['serverManifestSha256'],
             'qualificationManifestSha256': hashlib.sha256(raw).hexdigest(),
             'casesSha256': hashlib.sha256(encoded).hexdigest(), 'rawNamesOutputOrEnvironmentExported': False,
             'methodTrace': 'Original XML filename + ordinal + original XML SHA + case-name SHA; private name not published.',
             'global100': False, 'F03Accepted': False, 'formalAccepted': False, 'oldNativeImported': False}
    with (out / 'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(json.dumps(value))


if __name__ == '__main__':
    main()
