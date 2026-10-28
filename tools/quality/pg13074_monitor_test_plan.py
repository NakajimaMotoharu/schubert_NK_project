"""Freeze all original81 methods after token-preserving Test-only PG corrections."""
import copy
import re
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg13071_monitor_test_inverse import inverse, negative

SOURCE = '42ae92a74d57a9e1d031613d5b558af3ebe2925c'
OUT = data.BASE/'PG13074-monitor-test-plan-v1'

def main():
    invocation = capture(__file__); assert not OUT.exists()
    old_manifest = data.read_checked(data.BASE/'PG13070-monitor-test-originals-v1/manifest.json','faa795bf1bc06a56b4a926f48fdda20b60e7b8da7d0672439e0ab479628c598f')
    original = data.read_checked(data.BASE/'PG13070-monitor-test-originals-v1/originals.json',old_manifest['originalsSha256'])
    p = data.read_checked(data.BASE/'PG13072-monitor-test-preflight-v1/manifest.json','5d2af644b9565963525135f234de8f2f53de92f9bf991cfde721d9905931763e')
    n = data.read_checked(data.BASE/'PG13056-time-header-six-compile-v1/manifest.json','fa52be739663760cd603ff1e00bdf963499c75038c6fac9504ab6caa92a007f6')
    assert p['baseSource'] == n['source'] == original['source'] == '7ced2d7078bf508afcb22dbc8e1d82cc15d56573'
    assert p['actualExit'] == 1 and p['reports']['pmd']['findings'] == 20 and p['reports']['checkstyle']['findings'] == 0
    assert all(v['processingErrors'] == 0 for v in p['reports'].values())
    raw = data.BASE/'PG13072-monitor-test-preflight-v1/pmd.xml'
    assert data.sha(raw.read_bytes()) == p['reports']['pmd']['sha256']
    assert {x.get('rule') for x in ET.parse(raw).getroot().iter() if x.tag.rpartition('}')[2] == 'violation'} == {'DoNotUseThreads'}
    tests = p['candidateSourceHashes']; assert len(tests) == 10
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in n['begin']['inputHashes'].items() if path not in tests)
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in tests.items())
    counts = {}; negatives = {}; whole = {}
    for path,record in original['tests'].items():
        text = (data.ROOT/path).read_text(); transfer = path.endswith('/TransferHealthMonitorTest.java')
        counts[path] = inverse(record['text'],text,transfer); negatives[path] = negative(record['text'],text,transfer)
        assert negatives[path] == p['negativeVectors'][path] and counts[path] == p['tokenInverses'][path]
        methods = re.findall(r'@Test\s+void\s+(\w+)\s*\(\s*\)',text)
        assert methods == [r['method'] for r in original['cases'] if r['path'] == path] and len(methods) == text.count('@Test')
        whole[path] = tests[path]
    cases = copy.deepcopy(original['cases'])
    for row in cases: row['sourceSha256'] = tests[row['path']]
    mains = original['mainSourceHashes']; assert len(mains) == 19
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in mains.items())
    allowed = {path.split('/java/',1)[1][:-5].replace('/','.') for path in mains}
    for path in [*whole,*mains]:
        imports = re.findall(r'^import (dev\.codex\.schubert\.nk\.[\w.]+);',(data.ROOT/path).read_text(),re.M)
        assert all(any(value == item or value.startswith(item+'.') for item in allowed) for value in imports)
    changed = subprocess.check_output(['git','diff','--name-only',n['source'],SOURCE,'--','src'],cwd=data.ROOT,text=True).splitlines()
    assert set(changed) == set(tests) and len(cases) == len({(r['className'],r['method']) for r in cases}) == 81
    verify(invocation); OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,before=n['source'],invocation=invocation,cases=cases,
        wholeTestSourceHashes=whole,eligibilityClosureSourceHashes=mains,supportTestSourceHashes={},originalTests=81,newTests=0,totalTests=81,
        sameExecRequired=True,oldExecUnion=False,totalCorrections=11,scopeStaticFindings=20,tokenInverses=counts,negativeVectors=negatives,
        retainedWorkerOriginalIds=[r['id'] for r in original['originalFindings'] if r['rule'] == 'DoNotUseThreads'],
        unexecutedPorts=['MonitoringObservationClock','MonitoringPoller.observeNow'],
        judgement='All81 original methods after private AT rename and one DEBUG fixture extraction; no new assertion or Product Main change',
        newAccepted=0,whole451Accepted=False,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__': main()
