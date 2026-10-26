"""Recover original 11042 actual terminal/XML only; never compile or execute target tests."""
from collections import Counter
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

RUN = data.ROOT.parent/'pgpt-runs/PG379/pg11042-api-request-host-v1'
OUT = data.BASE/'PG11043-api-request-original-recovery-v1'


def require_trace(actual,expected):
    if actual != expected:
        raise ValueError('literal independent public trace required')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    begin_path = RUN/'begin.safe.json'
    begin = json.loads(begin_path.read_bytes())
    assert begin['source'] == '9b255cbe300d1feffeeee076cfa5af318c9b1bb1'
    verify(begin['invocation'])
    stages = [json.loads((RUN/(name+'-exit.safe.json')).read_bytes()) for name in ('compile-launcher','api-request-jp')]
    assert all(s['actualExit'] == 0 and not s['timedOut'] for s in stages)
    assert Path(stages[1]['cwd']) == Path(begin['testCwd']) == RUN/'test-cwd'
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**begin['dependencyHashes'],**begin['physicalTestFiles']}.items())
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in begin['sourceInputHashes'].items())
    assert data.sha(Path(begin['helperPath']).read_bytes()) == begin['helperSha256']
    expected = Counter((r['className'],r['method']) for r in begin['cases'])
    actual,xmls = [],{}
    for file in sorted((RUN/'xml').glob('TEST-*.xml')):
        root = ET.parse(file).getroot()
        assert all(root.get(k) == '0' for k in ('failures','errors','skipped'))
        actual += [dict(classname=r.get('classname'),name=r.get('name'),nonPass=[n.tag for n in r]) for r in root.findall('testcase')]
        xmls[file.name] = data.sha(file.read_bytes())
    assert len(xmls) == 4 and len(actual) == 16 and not any(r['nonPass'] for r in actual)
    assert Counter((r['classname'],r['name']) for r in actual) == expected
    assert (RUN/'xml/summary.safe.txt').read_text() == 'found=16;started=16;succeeded=16;failed=0;skipped=0;aborted=0;containerFailed=0;containerAborted=0;passed=true'
    cwd = Path(begin['testCwd'])
    trace_name = 'target/question-submit-traces/PT-QST-SUB008.txt'
    assert sorted(str(p.relative_to(cwd)) for p in cwd.rglob('*') if p.is_file()) == [trace_name]
    assert not cwd.is_symlink() and all(not p.is_symlink() for p in cwd.rglob('*'))
    expected_trace = chr(10).join(('layout=QSBREQ01','interaction=A','dataLength=4144','canonicalFieldCount=1','canonicalField=question/X1','target=QUESTION:NEW','metadataExcluded=true','rawBodySaved=false',''))
    trace = (cwd/trace_name).read_text()
    require_trace(trace,expected_trace)
    negatives = 0
    for bad in (trace.replace(chr(10),r'\n'),trace[:-1],trace.replace('false','true')):
        try:
            require_trace(bad,expected_trace)
        except ValueError:
            negatives += 1
        else:
            raise AssertionError('changed trace accepted')
    verify(invocation)
    value = dict(actualExit=0,source=begin['source'],begin=begin,stages=stages,cases=actual,xmlHashes=xmls,
        invocation=invocation,originalBeginSha256=data.sha(begin_path.read_bytes()),originalRun=str(RUN),
        originalProducerExit=1,originalProducerManifestMissing=not (RUN/'manifest.safe.json').exists(),
        recoveryOnly=True,targetTestsExecutedByRecovery=0,metadataNegativeVectors=negatives,
        observedTestExecutions=16,sessionId='PG11042-APIREQ-JP',execSha256=data.sha((RUN/'jacoco.exec').read_bytes()),
        classloadSha256=data.sha((RUN/'classload-metadata.log').read_bytes()),
        publicTrace=dict(path=trace_name,sha256=data.sha((cwd/trace_name).read_bytes()),expected=expected_trace,actual=trace),
        oldExecUnion=False,coveragePendingIndependentPost=True,whole451Accepted=False,newAccepted=0,effortPercent=None)
    OUT.mkdir()
    data.write(OUT/'manifest.json',value)
    for file in (RUN/'xml').glob('*'):
        with (OUT/file.name).open('xb') as stream:
            stream.write(file.read_bytes())
    print(json.dumps(dict(actualExit=0,original16Passed=True,targetTestsExecuted=0,manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
