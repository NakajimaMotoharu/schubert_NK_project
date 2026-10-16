"""Exact before/after seven-case oracle and fresh Main-family counters, no native/global claim."""
import base64
import hashlib
import json
import shlex
import subprocess
import xml.etree.ElementTree as E
from lan_server import run
from pg3962_prior_invariant_selected import ROOT, W, MAIN, TEST, require
from pg3280_wbs_current_source import redact_report, report_counters


def main():
    results = []; files = {}; test_bytes = []
    for label, slot, missed in [('PG3962', 'pg3962-prior-invariant-before-v1', 5), ('PG3964', 'pg3964-prior-invariant-after-v1', 0)]:
        p = W / slot / 'manifest.safe.json'; local = json.loads(p.read_bytes()); v = local['result']
        require(local['actualExit'] == v['actualExit'] == v['FESAbortedNotRun'] == 0 and v['tests'] == 7 and v['targetCounters']['BRANCH']['missed'] == missed and local['wholeNewSourceQualification'] is False, 'genuine scoped before/after7 only')
        code = """import base64,hashlib,json
from pathlib import Path
p=Path('/home/mini/schubert-nk-pgpt/runs')/SLOT;raw=(p/'manifest.safe.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==EXPECTED;v=json.loads(raw)
assert v['mainRecompiled']is True and v['mainFilesRecompiled']==1 and v['wholeNewSourceQualification']is False
print(json.dumps({'metadata':{k:v[k]for k in ['startUTC','endUTC','commands','compiledMainHashes','mainRecompiled','mainFilesRecompiled','phase','wholeNewSourceQualification']},'inputs':v['input']['files'],'xml':base64.b64encode((p/'tests.xml').read_bytes()).decode(),'coverage':base64.b64encode((p/'target-coverage.xml').read_bytes()).decode()}))
"""
        status, output = run('python3 -c ' + shlex.quote('SLOT=' + repr(label + '-candidate-v1') + '\nEXPECTED=' + repr(v['manifestSha256']) + '\n' + code), timeout=30); require(status == 0, 'exact original scoped receipt')
        actual = json.loads(next(x for x in output.splitlines() if x.startswith('{')))
        xml = base64.b64decode(actual['xml'], validate=True); coverage = base64.b64decode(actual['coverage'], validate=True)
        require(hashlib.sha256(xml).hexdigest() == v['xmlSha256'] and hashlib.sha256(coverage).hexdigest() == v['coverageXmlSha256'], 'exact original XML/counter bytes')
        tree = E.fromstring(xml); require(len(tree.findall('testcase')) == 7 and all(tree.get(k) == '0' for k in ['failures', 'errors', 'skipped']) and not tree.findall('.//failure'), 'all7 actual clean cases')
        counters = report_counters(E.fromstring(coverage)); expected = {k: counters[k] for k in ['LINE', 'METHOD', 'CLASS', 'BRANCH']}
        redacted, projection = redact_report(coverage, {**expected, 'classByteMismatch': 0, 'formal': False})
        files[label + '/tests.xml'] = xml; files[label + '/scoped-main-coverage.xml'] = redacted
        source = subprocess.check_output(['git', 'show', local['testSource'] + ':' + TEST], cwd=ROOT); test_bytes.append(source)
        require(hashlib.sha256(source).hexdigest() == actual['inputs'][TEST], 'actual same independent oracle bytes')
        results.append({'run': label, 'phase': local['phase'], 'mainSource': local['mainSource'], 'testSource': local['testSource'], 'testSha256': hashlib.sha256(source).hexdigest(),
                        'mainInputSha256': actual['inputs'][MAIN], 'auxiliaryFullSource': local['auxiliaryFullSource'], 'actualExit': 0, 'tests': 7, 'FESAbortedNotRun': 0,
                        'metadata': actual['metadata'], 'targetCounters': v['targetCounters'], 'originalServerManifestSha256': v['manifestSha256'], 'coverageRedaction': projection})
    require(test_bytes[0] == test_bytes[1], 'no expected-value edits between before and after')
    out = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3965-prior-invariant-before-after-v1'; out.mkdir()
    for name, raw in files.items():
        p = out / name; p.parent.mkdir(exist_ok=True); p.write_bytes(raw)
    value = {'actualExit': 0, 'run': 'PG3965-prior-invariant-before-after-v1', 'newJUnitMethods': 1, 'sameIndependentOracleBeforeAfter': True,
             'results': results, 'globalQualification': False, 'nativeImported': False, 'vmActions': 0, 'formalAccepted': False, 'acceptedLeafDelta': 0,
             'branchMeaning': 'Five redundant predicates removed after exact immutable admission; not five new executed branch outcomes or an exclusion.',
             'files': {n: hashlib.sha256(raw).hexdigest() for n, raw in files.items()}, 'rawSessionPublished': False}
    raw = (json.dumps(value, sort_keys=True) + '\n').encode(); (out / 'manifest.json').write_bytes(raw)
    print(json.dumps({'actualExit': 0, 'beforeTests': 7, 'afterTests': 7, 'newJUnitMethods': 1, 'targetFourCounters100': True, 'manifestSha256': hashlib.sha256(raw).hexdigest()})); return 0


if __name__ == '__main__':
    raise SystemExit(main())
