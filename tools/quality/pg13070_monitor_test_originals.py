"""Preserve explicit ten original Test sources/31 diagnostics before lexical-only PG changes."""
import json
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = '7ced2d7078bf508afcb22dbc8e1d82cc15d56573'
NAMES = ['AsyncQueueMonitor','BackupHealthMonitor','DlqHealthMonitor','ExpiryBacklogMonitor','IntegrityHealthMonitor','RestartHealthMonitor','TimedDbPoolMonitor','TimedSyncLatencyMonitor','TransferHealthMonitor','WebLogBacklogMonitor']
MAIN_NAMES = NAMES+['AlertLifecycle','ObservationContext','TransferMetricRecorder','MonitoringPoller','AlertThresholds','ContinuousConditionWindow','MonitoringModePolicy','MetricContract','MonitoringObservationClock']
ROOT = 'src/schubert-nk-batch/src/'
PACKAGE = '/java/dev/codex/schubert/nk/batch/monitoring/'
OUT = data.BASE/'PG13070-monitor-test-originals-v1'

def main():
    invocation = capture(__file__); assert not OUT.exists()
    normal = data.read_checked(data.BASE/'PG13056-time-header-six-compile-v1/manifest.json','fa52be739663760cd603ff1e00bdf963499c75038c6fac9504ab6caa92a007f6')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in normal['begin']['inputHashes'].items())
    paths = [ROOT+'test'+PACKAGE+name+'Test.java' for name in NAMES]
    findings_path = data.BASE/'PG10690-current-global-static-post-v1/findings.json'
    all_rows = json.loads(findings_path.read_bytes()); rows = [r for r in all_rows if r['path'] in paths]
    assert len(rows) == 31
    fields = {r['id'] for r in rows if r['rule'] == 'AvoidFieldNameMatchingMethodName'}
    assert fields == set('PMD-04704 PMD-04707 PMD-04812 PMD-04815 PMD-04834 PMD-04890 PMD-04893 PMD-04903 PMD-04906 PMD-04917'.split())
    assert {r['id'] for r in rows if r['rule'] == 'AvoidDuplicateLiterals'} == {'PMD-04907'}
    assert sum(r['rule'] == 'DoNotUseThreads' for r in rows) == 20
    originals = {}; catalog = []; mains = {}
    for path in paths:
        raw = (data.ROOT/path).read_bytes(); sha = data.sha(raw); text = raw.decode()
        assert all(r['inputSha256'] == sha for r in rows if r['path'] == path)
        assert normal['begin']['inputHashes'][path] == sha
        assert 'private static final Instant AT =' in text and 'ObservationContext at(' in text
        assert not any(s in text for s in ['@Before','@After','@ExtendWith','@Disabled','@TempDir','java.nio.file','java.sql.','java.net.','ProcessBuilder','System.getenv','setAccessible','TemporaryInfrastructureException','WebStartupException'])
        methods = re.findall(r'@Test\s+void\s+(\w+)\s*\(\s*\)',text)
        count = 9 if path.endswith('/AsyncQueueMonitorTest.java') else 8
        assert len(methods) == len(set(methods)) == text.count('@Test') == count
        originals[path] = dict(sourceSha256=sha,text=text)
        catalog.extend(dict(className=path.split('/java/',1)[1][:-5].replace('/','.'),method=name,path=path,sourceSha256=sha) for name in methods)
    for name in MAIN_NAMES:
        path = ROOT+'main'+PACKAGE+name+'.java'; sha = data.sha((data.ROOT/path).read_bytes())
        assert normal['begin']['inputHashes'][path] == sha; mains[path] = sha
    assert len(catalog) == 81 and len(originals) == 10 and len(mains) == 19
    verify(invocation); OUT.mkdir();data.write(OUT/'originals.json',dict(source=SOURCE,tests=originals,mainSourceHashes=mains,cases=catalog,originalFindings=rows))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        originalsSha256=data.sha((OUT/'originals.json').read_bytes()),originalFindingsSha256=data.sha(findings_path.read_bytes()),
        tests=10,cases=81,mainClosure=19,originalRaw=31,namingTargets=sorted(fields),duplicateTargets=['PMD-04907'],retainedWorkerRaw=20,
        productTestsExecuted=0,sourceCodeChanged=False,newAccepted=0,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__': main()
