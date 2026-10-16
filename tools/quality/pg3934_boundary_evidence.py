"""Publish exact selected XML/counter metadata, never raw native/session/private DB."""
import base64
import hashlib
import json
import shlex
import subprocess
import xml.etree.ElementTree as E
from pathlib import Path
from lan_server import run
from pg3920_current_abandoned_boundary import ROOT, W, SOURCE, FILES, require
from pg3280_wbs_current_source import redact_report, report_counters


def main():
    out = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3934-current-session-boundaries-v1'
    require(not out.exists(), 'new-only publication')
    proofs = []; artifacts = {}
    for label, slot, count in [('PG3922', 'pg3922-current-abandoned-boundary-v1', 64), ('PG3926', 'pg3926-current-failed-pair-boundary-v1', 65)]:
        original = json.loads((W / slot / 'manifest.safe.json').read_bytes()); v = original['result']
        require(original['actualExit'] == v['actualExit'] == v['FESAbortedNotRun'] == 0 and original['productionSource'] == SOURCE and v['tests'] == count, 'genuine exact selected success')
        expected = v['manifestSha256']
        code = """import base64,hashlib,json
from pathlib import Path
p=Path('/home/mini/schubert-nk-pgpt/runs')/SLOT
m=p/'manifest.safe.json';assert hashlib.sha256(m.read_bytes()).hexdigest()==EXPECTED
v=json.loads(m.read_bytes());print(json.dumps({'metadata':{k:v[k]for k in ['startUTC','endUTC','commands','extraLibraries','baseFixturesUnchanged','mainRecompiled','nativeImported','vmActions']},'xml':base64.b64encode((p/'tests.xml').read_bytes()).decode(),'coverage':base64.b64encode((p/'target-coverage.xml').read_bytes()).decode()}))
"""
        status, output = run('python3 -c ' + shlex.quote('SLOT=' + repr(label + '-candidate-v1') + '\nEXPECTED=' + repr(expected) + '\n' + code), timeout=40)
        require(status == 0, 'exact original receipt read')
        fetched = json.loads(next(x for x in output.splitlines() if x.startswith('{')))
        xml = base64.b64decode(fetched['xml'], validate=True); cov = base64.b64decode(fetched['coverage'], validate=True)
        require(hashlib.sha256(xml).hexdigest() == v['xmlSha256'] and hashlib.sha256(cov).hexdigest() == v['coverageXmlSha256'], 'original saved byte hashes')
        tree = E.fromstring(xml)
        require(len(tree.findall('testcase')) == count and all(tree.get(k) == '0' for k in ['failures', 'errors', 'skipped']) and not tree.findall('.//failure'), 'exact XML no missing/failed case')
        values = report_counters(E.fromstring(cov))
        expected_counters = {k: values[k] for k in ['LINE', 'METHOD', 'CLASS', 'BRANCH']}
        public_cov, redaction = redact_report(cov, {**expected_counters, 'classByteMismatch': 0, 'formal': False})
        artifacts[label + '/tests.xml'] = xml
        artifacts[label + '/selected-only-coverage.xml'] = public_cov
        source = subprocess.check_output(['git', 'show', original['testSource'] + ':' + FILES[0]], cwd=ROOT)
        proofs.append({'run': label, 'productionSource': SOURCE, 'testSource': original['testSource'], 'testSha256': hashlib.sha256(source).hexdigest(),
                       'actualExit': 0, 'tests': count, 'FESAbortedNotRun': 0, 'originalServerManifestSha256': expected,
                       'originalLocalReceiptSha256': hashlib.sha256((W / slot / 'manifest.safe.json').read_bytes()).hexdigest(),
                       'metadata': fetched['metadata'], 'targetCounters': v['targetCounters'], 'coverageRedaction': redaction,
                       'coverageMeaning': 'Selected suite only, not global/native union or formal qualification'})
    out.mkdir()
    for name, raw in artifacts.items():
        target = out / name; target.parent.mkdir(exist_ok=True); target.write_bytes(raw)
    manifest = {'actualExit': 0, 'productionSource': SOURCE, 'run': 'PG3934-current-session-boundaries-v1', 'proofs': proofs,
                'newJUnitMethods': 2, 'acceptedLeafDelta': 0, 'formalAccepted': False, 'global100': False,
                'failedRunsPreserved': ['PG3920 compile failure/BUG1328', 'PG3924 new test oracle failure/SS343 SSC124'],
                'files': {n: hashlib.sha256(raw).hexdigest() for n, raw in artifacts.items()}, 'rawSessionPublished': False}
    raw = (json.dumps(manifest, sort_keys=True) + '\n').encode(); (out / 'manifest.json').write_bytes(raw)
    print(json.dumps({'actualExit': 0, 'runs': 2, 'newJUnitMethods': 2, 'manifestSha256': hashlib.sha256(raw).hexdigest()}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
