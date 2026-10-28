"""Two owned-pool wrappers only; exact original tokens and complete pure38 method closure."""
import difflib
import re
import sys
from pathlib import Path
import g07_host_class_provenance_inputs as data
from fixture_scope_advisory import audit
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX

BEFORE='f8ad1ae16aa52db0119fefbad9e2cea6d6affe55'
OUT=data.BASE/'PG12868-pure-health-lifecycle-plan-v1'
BASE='src/schubert-nk-batch/src/'
MAIN=BASE+'main/java/dev/codex/schubert/nk/batch/monitoring/'
TEST=BASE+'test/java/dev/codex/schubert/nk/batch/monitoring/'
COUNTS={'AlertLifecycleTest':12,'TimedFilesystemMonitorTest':6,'FilesystemHealthObservationTest':10,'MonitoringObservationClockTest':8,'AlertContinuityTest':2}
CHANGED=[TEST+'AlertLifecycleTest.java',TEST+'TimedFilesystemMonitorTest.java']
NAMES=['ContinuousConditionWindow','MonitoringObservationClock','MonitoringPoller','ObservationContext','AlertThresholds','AlertLifecycle','FilesystemHealthObservation','FilesystemHealthMonitor','TimedFilesystemMonitor','HealthUsageRatio','MonitoringStatusText','MonitoringModePolicy']


def tokens(text):
    return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]


def before():
    n=data.read_checked(data.BASE/'PG12846-monitor-sequence-six-compile-v1/manifest.json','48d6cc8b9d01d392bdcd94c070fb9357ae774e42119324c21c6096051f2ece17')
    assert n['source']==BEFORE and n['actualExit']==n['testsExecuted']==0
    root=Path(n['jars']['batch']['path']).parent.parent.parent.parent
    old={path:(root/path).read_text() for path in CHANGED}
    assert all(data.sha(text.encode())==n['begin']['inputHashes'][path] for path,text in old.items())
    return n,old


def intended(old):
    new={}
    for path,text in old.items():
        start='    var executor = Executors.newFixedThreadPool(4);\n    try {'
        end='      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));\n    }\n'
        assert text.count(start)==text.count(end)==1
        text=text.replace(start,'    try (var executor = Executors.newFixedThreadPool(4)) {\n    try {',1)
        new[path]=text.replace(end,end+'    }\n',1)
    return new


def require(old,new):
    opening=tokens('try (var executor = Executors.newFixedThreadPool(4)) {')
    for path,text in new.items():
        actual=tokens(text);matches=[i for i in range(len(actual)) if actual[i:i+len(opening)]==opening];assert len(matches)==1
        start=matches[0];depth=1;close=start+len(opening)
        while depth:
            depth+=(actual[close]=='{')-(actual[close]=='}');close+=1
        restored=actual[:start]+tokens('var executor = Executors.newFixedThreadPool(4);')+actual[start+len(opening):close-1]+actual[close:]
        assert restored==tokens(old[path])


def emit():
    _,old=before();new=intended(old);require(old,new);patch='*** Begin Patch\n'
    for path in old:
        assert (data.ROOT/path).read_text()==old[path]
        patch+='*** Update File: '+str(data.ROOT/path)+'\n'+'\n'.join('@@' if line.startswith('@@') else line for line in list(difflib.unified_diff(old[path].splitlines(),new[path].splitlines(),n=3))[2:])+'\n'
    return patch+'*** End Patch\n'


def main():
    invocation=capture(__file__);assert not OUT.exists();n,old=before();new={path:(data.ROOT/path).read_text() for path in old};require(old,new)
    hashes=n['begin']['inputHashes'];assert all(data.sha((data.ROOT/path).read_bytes())==digest for path,digest in hashes.items() if path not in old)
    labels=[]
    for path in CHANGED:
        for first,last in [('try (var executor = Executors.newFixedThreadPool(4))','try (var executor = Executors.newFixedThreadPool(5))'),('executor.shutdownNow();',''),('executor.awaitTermination(10, TimeUnit.SECONDS)','executor.awaitTermination(1, TimeUnit.SECONDS)'),('BigInteger.valueOf(65)','BigInteger.valueOf(64)'),('@Test','@Disabled')]:
            bad=dict(new);bad[path]=bad[path].replace(first,last,1);assert bad[path]!=new[path]
            try:require(old,bad)
            except (AssertionError,IndexError):labels.append(path+':'+first)
            else:raise AssertionError('changed original pool/control/oracle accepted')
    reviewed={MAIN+name+'.java':hashes[MAIN+name+'.java'] for name in NAMES}
    paths=[TEST+name+'.java' for name in COUNTS]
    registry=data.read_checked(data.BASE/'PG12858-monitor-sequence-trace-v1/manifest.json','05668fb67894a11ac8226baabd546fac403ee14525a393b04cb5b8011078e6cc')
    texts={path:(data.ROOT/path).read_text() for path in [*reviewed,*paths]};texts.update(old)
    advisory=audit(texts,list(reviewed),paths,hashes,registry['sourceRows'],{'WBS-P018-09'})
    assert advisory['metadataConsistent'] and not advisory['executionQualified'] and not advisory['holdReleased'] and len(advisory['originalOwners'])==5
    cases=[];whole={}
    for name,count in COUNTS.items():
        path=TEST+name+'.java';text=(data.ROOT/path).read_text();whole[path]=data.sha(text.encode());methods=re.findall(r'@Test\s+void\s+(\w+)\s*\(\s*\)',text);assert len(methods)==len(set(methods))==count
        assert not any(word in text for word in ['@Before','@After','@ExtendWith','@Disabled','@TempDir','DriverManager','getConnection(','ProcessBuilder','Class.forName','System.getenv','java.net.','TemporaryInfrastructureException','WebStartupException'])
        cases.extend(dict(className=path.split('/java/',1)[1][:-5].replace('/','.'),method=method,path=path,sourceSha256=whole[path]) for method in methods)
    assert len(cases)==38
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2388_PureFilesystemAlertLifecycle原38_単体テスト仕様書.md'
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=BEFORE,invocation=invocation,sourceChanges=[dict(path=path,beforeSha256=data.sha(old[path].encode()),sha256=data.sha(new[path].encode())) for path in old],totalCorrections=2,metadataNegativeVectors=len(labels),negativeVectorLabels=labels,eligibilityClosureSourceHashes=reviewed,wholeTestSourceHashes=whole,supportTestSourceHashes={},supportTestSelectedMethods=0,metadataAdvisory=advisory,cases=cases,originalTests=38,originalSuites=5,newTestIds=0,sameExecRequired=True,oldExecUnion=False,allMainAndOtherInputsUnchanged=True,judgement='PT_DEFAULT_WHOLE_PURE_ALERT_FILESYSTEM38_FIXED_CLOCK_VALUES_STUB_STORE_FINITE_WORKERS_NO_ACTUAL_IO',specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),productTestsExecuted=0,newAccepted=0,coverage=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:print(emit(),end='')
    else:assert not sys.argv[1:];main()
