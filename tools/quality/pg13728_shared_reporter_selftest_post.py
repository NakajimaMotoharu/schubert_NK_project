"""Independent tool receipt/XML/hash validation, without any reporter or Product rerun."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg13726_shared_reporter_selftest as original

PIN = '0a43e2c2ffa463f9475ca6b0158189a030eb2f3ca4fac80812da3bcf4d869f1c'
OUT = data.BASE/'PG13728-shared-reporter-selftest-post-v1'

def main():
    invocation = capture(__file__);assert not OUT.exists()
    raw = data.read_checked(original.OUT/'manifest.json',PIN);verify(raw['invocation'])
    assert raw['actualExit'] == raw['productTestsExecuted'] == 0 and raw['productClasspathsUsed'] is raw['oldProductResultsTransferred'] is False
    assert raw['toolChecks'] == 12 and raw['positiveToolRuns'] == 2 and raw['intendedNegativeToolRuns'] == 10
    assert raw['compileStage']['actualExit'] == 0 and raw['compileStage']['timedOut'] is False
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in raw['toolSourceHashes'].items())
    assert len(raw['dependencyHashes']) == 7 and all(data.sha(Path(p).read_bytes()) == h for p,h in raw['dependencyHashes'].items())
    assert {Path(p).name for p in raw['dependencyHashes']} == original.LIBRARIES
    rows = {r['profile']:r for r in raw['cases']};assert len(rows) == len(raw['cases']) == 12
    assert set(rows) == {r[0] for r in original.CASES}
    for profile,exitcode,counts,suites,failed,skipped in original.CASES:
        row = rows[profile];receipt = json.loads((original.SLOT/profile/'exit.safe.json').read_bytes())
        assert receipt == row['stage'] and receipt['actualExit'] == row['actualExit'] == row['expectedExit'] == exitcode and receipt['timedOut'] is row['timedOut'] is False
        assert row['productTestsExecuted'] == 0 and row['expectedOutcomeObserved'] is True
        assert receipt['command'][-2:] == [profile,str(original.SLOT/profile/'xml')]
        if counts is None:
            assert row['summary'] is None and row['xmlHashes'] == {} and not (original.SLOT/profile/'xml').exists()
            continue
        private = original.SLOT/profile/'xml/summary.safe.txt';public = original.OUT/profile/'summary.safe.txt'
        assert public.read_bytes() == private.read_bytes()
        fields = dict(v.split('=',1) for v in public.read_text().split(';'));assert set(fields) == original.KEYS
        expected = {k:0 for k in original.KEYS-{'passed'}};expected.update(counts)
        assert all(int(fields[k]) == v for k,v in expected.items()) and fields['passed'] == ('true' if profile in ['passing','two-passing'] else 'false')
        roots = {};seen = [];actual_failed = actual_skipped = 0
        assert {p.name for p in (original.OUT/profile).glob('TEST-*.xml')} == set(row['xmlHashes'])
        for filename,pin in row['xmlHashes'].items():
            a = original.SLOT/profile/'xml'/filename;b = original.OUT/profile/filename
            assert data.sha(a.read_bytes()) == data.sha(b.read_bytes()) == pin
            root = ET.fromstring(b.read_bytes());name = root.get('name');assert name.startswith(original.PREFIX)
            cases = root.findall('testcase');assert root.get('tests') == str(len(cases)) and root.get('errors') == '0'
            roots[name.removeprefix(original.PREFIX)] = sorted(c.get('name') for c in cases)
            seen.extend((c.get('classname'),c.get('name')) for c in cases)
            actual_failed += int(root.get('failures'));actual_skipped += int(root.get('skipped'))
            assert b'reporter-tool-only-failure' not in b.read_bytes() and b'reporter-tool-only-container-failure' not in b.read_bytes()
        assert len(seen) == len(set(seen)) and roots == {k:sorted(v) for k,v in suites.items()} and actual_failed == failed and actual_skipped == skipped
    compiled = {str(p.relative_to(original.SLOT/'classes')):data.sha(p.read_bytes()) for p in (original.SLOT/'classes').rglob('*.class')}
    assert len(compiled) == 12 and all(name.startswith(('SharedSelectedJunitReporterV1','ReporterToolDriverV1','dev/codex/schubert/nk/tooling/ReporterToolFixturesV1')) for name in compiled)
    runtime = {}
    for line in (original.SLOT/'passing.stdout').read_text().splitlines():
        if line.startswith(('runtime.version=','os.name=','os.arch=','os.version=')):
            key,value = line.split('=',1);runtime[key] = value
    assert set(runtime) == {'runtime.version','os.name','os.arch','os.version'} and runtime['runtime.version'].startswith('25.0.4')
    verify(raw['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,selftestManifestSha256=PIN,toolSourceHashes=raw['toolSourceHashes'],dependencyHashes=raw['dependencyHashes'],compiledClassInventoryRecordedAtPost=compiled,compiledClassHashesWereNotCapturedInOriginalManifest=True,runtime=runtime,toolChecksIndependentlyConfirmed=12,positiveToolRuns=2,intendedNegativeToolRuns=10,productTestsExecuted=0,productClasspathsUsed=False,reporterReexecuted=False,coverage=None,newAccepted=0,formalUpdated=False,effortPercent=None,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
