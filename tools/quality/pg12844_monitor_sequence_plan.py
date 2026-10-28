"""Two fixture-only changes, whole24 source inverse, explicit pure port closure and original owners."""
import difflib
import re
import sys
from pathlib import Path
import g07_host_class_provenance_inputs as data
from fixture_scope_advisory import audit
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX

BEFORE='0124b5938a50f4ceea542486c336ba12146cb1b4'
OUT=data.BASE/'PG12844-monitor-sequence-plan-v1'
BASE='src/schubert-nk-batch/src/'
MAIN=BASE+'main/java/dev/codex/schubert/nk/batch/monitoring/'
TEST=BASE+'test/java/dev/codex/schubert/nk/batch/monitoring/'
WINDOW=TEST+'ContinuousConditionWindowTest.java'
POLLER=TEST+'MonitoringPollerTest.java'
SELECTED=[WINDOW,TEST+'MonitoringObservationClockTest.java',POLLER]
NAMES=['ContinuousConditionWindow','MonitoringObservationClock','MonitoringPoller','ObservationContext','AlertThresholds','AlertLifecycle','FilesystemHealthObservation','FilesystemHealthMonitor','TimedFilesystemMonitor','HealthUsageRatio']
SUPPORT=TEST+'FilesystemHealthObservationTest.java'


def tokens(text):
    return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]


def before():
    n=data.read_checked(data.BASE/'PG12819-exact-registry-six-compile-v2/manifest.json','8a5081b03b988d4370df0c3fa45c69eeeda6d5296543a38f1e2239b0ae088f89')
    assert n['source']==BEFORE and n['actualExit']==n['testsExecuted']==0
    root=Path(n['jars']['batch']['path']).parent.parent.parent.parent
    old={path:(root/path).read_text() for path in [WINDOW,POLLER]}
    assert all(data.sha(text.encode())==n['begin']['inputHashes'][path] for path,text in old.items())
    return n,old


def intended(old):
    text=old[WINDOW];start=text.index('  void monWindow007');end=text.index('  @Test\n  void monWindow008',start);block=text[start:end]
    anchor='    var executor = Executors.newFixedThreadPool(4);\n    try {'
    assert block.count(anchor)==1 and block.endswith('  }\n\n')
    block=block.replace(anchor,'    try (var executor = Executors.newFixedThreadPool(4)) {\n    try {',1)
    block=block[:-len('  }\n\n')]+'    }\n  }\n\n'
    text=text[:start]+block+text[end:]
    renamed=old[POLLER];positions=[m for m in LEX.finditer(renamed) if m.group()=='AT'];assert len(positions)==2
    for m in reversed(positions):renamed=renamed[:m.start()]+'BASE_INSTANT'+renamed[m.end():]
    return {WINDOW:text,POLLER:renamed}


def require(old,new):
    original=tokens(old[WINDOW]);actual=tokens(new[WINDOW]);opening=tokens('try (var executor = Executors.newFixedThreadPool(4)) {')
    matches=[i for i in range(len(actual)) if actual[i:i+len(opening)]==opening];assert len(matches)==1
    start=matches[0];depth=1;close=start+len(opening)
    while depth:
        depth+=(actual[close]=='{')-(actual[close]=='}');close+=1
    restored=actual[:start]+tokens('var executor = Executors.newFixedThreadPool(4);')+actual[start+len(opening):close-1]+actual[close:]
    assert restored==original
    renamed=tokens(new[POLLER]);assert renamed.count('BASE_INSTANT')==2 and not renamed.count('AT')
    assert ['AT' if value=='BASE_INSTANT' else value for value in renamed]==tokens(old[POLLER])


def emit():
    _,old=before();new=intended(old);require(old,new);patch='*** Begin Patch\n'
    for path in old:
        assert (data.ROOT/path).read_text()==old[path]
        patch+='*** Update File: '+str(data.ROOT/path)+'\n'+'\n'.join('@@' if line.startswith('@@') else line for line in list(difflib.unified_diff(old[path].splitlines(),new[path].splitlines(),n=3))[2:])+'\n'
    return patch+'*** End Patch\n'


def main():
    invocation=capture(__file__);assert not OUT.exists();n,old=before();new={path:(data.ROOT/path).read_text() for path in old};require(old,new)
    hashes=n['begin']['inputHashes'];assert all(data.sha((data.ROOT/path).read_bytes())==digest for path,digest in hashes.items() if path not in old)
    negatives=[]
    for path,first,last in [(WINDOW,'try (var executor = Executors.newFixedThreadPool(4))','try (var executor = Executors.newFixedThreadPool(5))'),(WINDOW,'executor.shutdownNow();',''),(WINDOW,'executor.awaitTermination(10, TimeUnit.SECONDS)','executor.awaitTermination(1, TimeUnit.SECONDS)'),(WINDOW,'assertEquals(Duration.ZERO, future.get())','assertEquals(Duration.ofSeconds(1), future.get())'),(WINDOW,'@Test','@Disabled'),(POLLER,'BASE_INSTANT','UNKNOWN_INSTANT'),(POLLER,'2026-10-23T00:00:00Z','2026-10-24T00:00:00Z'),(POLLER,'assertEquals(64, count[0])','assertEquals(63, count[0])'),(POLLER,'return 17;','return 18;'),(POLLER,'@Test','@Disabled')]:
        bad=dict(new);bad[path]=bad[path].replace(first,last,1);assert bad[path]!=new[path]
        try:require(old,bad)
        except (AssertionError,IndexError):negatives.append(path+':'+first)
        else:raise AssertionError('non-equivalent original control/oracle accepted')
    reviewed={MAIN+name+'.java':hashes[MAIN+name+'.java'] for name in NAMES};assert len(reviewed)==10
    registry=data.read_checked(data.BASE/'PG12828-exact-registry-trace-v1/manifest.json','14eac4d619670517db4a0c0c411845769a1e26049c3526cd38fe2310b84fcdbb')
    texts={path:(data.ROOT/path).read_text() for path in [*reviewed,*SELECTED,SUPPORT]};texts.update(old)
    advisory=audit(texts,list(reviewed),SELECTED,hashes,registry['sourceRows'],{'WBS-P018-09'})
    assert advisory['metadataConsistent'] and not advisory['executionQualified'] and not advisory['holdReleased'] and len(advisory['originalOwners'])==3
    cases=[];whole={}
    for path in SELECTED:
        text=(data.ROOT/path).read_text();whole[path]=data.sha(text.encode());methods=re.findall(r'@Test\s+void\s+(\w+)\s*\(\s*\)',text);assert len(methods)==len(set(methods))==8
        assert not any(word in text for word in ['@Before','@After','@ExtendWith','@Disabled','@TempDir','DriverManager','getConnection(','ProcessBuilder','Class.forName','System.getenv','java.net.','TemporaryInfrastructureException','WebStartupException'])
        cases.extend(dict(className=path.split('/java/',1)[1][:-5].replace('/','.'),method=method,path=path,sourceSha256=whole[path]) for method in methods)
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2386_MonitorWindowClockPoller原24_単体テスト仕様書.md'
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=BEFORE,invocation=invocation,sourceChanges=[dict(path=path,beforeSha256=data.sha(old[path].encode()),sha256=data.sha(new[path].encode())) for path in old],totalCorrections=2,metadataNegativeVectors=len(negatives),negativeVectorLabels=negatives,eligibilityClosureSourceHashes=reviewed,wholeTestSourceHashes=whole,supportTestSourceHashes={SUPPORT:hashes[SUPPORT]},supportTestSelectedMethods=0,metadataAdvisory=advisory,cases=cases,originalTests=24,originalSuites=3,newTestIds=0,sameExecRequired=True,oldExecUnion=False,allMainAndOtherInputsUnchanged=True,judgement='PT_DEFAULT_WHOLE_MONITOR_SEQUENCE24_FAKE_CLOCK_FILESTORE_SDK_FREE_FINITE_WORKERS_NO_ACTUAL_IO',specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),productTestsExecuted=0,newAccepted=0,coverage=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:print(emit(),end='')
    else:assert not sys.argv[1:];main()
