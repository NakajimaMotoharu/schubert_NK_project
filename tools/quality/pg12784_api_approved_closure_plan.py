"""Read-only same-source38 scope and unchanged normal-input binding; no product run."""
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from fixture_scope_advisory import audit
from host_tool_invocation import capture, verify

SOURCE='639bbc777593cd98d95db1b0316e8113b40b886b'
OUT=data.BASE/'PG12784-api-approved-closure-plan-v1'
PREFIX='src/schubert-nk-api/src/'
MAIN=PREFIX+'main/java/dev/codex/schubert/nk/api/monitoring/'
TEST=PREFIX+'test/java/dev/codex/schubert/nk/api/monitoring/'
COUNTS={'ApiDurationMetricExporterTest':24,'ApiMetricScrapeTest':14}
RECORDERS=['OutboxRowsMetricRecorder','OutboxAgeMetricRecorder','AsyncJobMetricRecorder','DbPoolMetricRecorder','MqPressureMetricRecorder','InboxReplayMetricRecorder','OperationMismatchMetricRecorder','MqRedeliveryMetricRecorder','MqMessageMetricRecorder','DbQueryDurationMetricRecorder','MqProcessingDurationMetricRecorder']


def main():
    invocation=capture(__file__);assert not OUT.exists()
    normal=data.read_checked(data.BASE/'PG12766-api-duration-six-compile-v1/manifest.json','39678a3c3b3ac634f9ee698f7acc900fa13248522829ce5338752b6bba920072')
    previous=data.read_checked(data.BASE/'PG12764-api-duration-plan-v1/manifest.json','a7410b3431bb0c3290a925dcbde0227ca2acb97311063cbe25a84c714e1853b3')
    registry=data.read_checked(data.BASE/'PG12774-api-duration-trace-v1/manifest.json','a6689186e503460076c061adb2f69a50bae57a1965740a8bd08b8729b311af8b')
    assert normal['source']==registry['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    hashes=normal['begin']['inputHashes'];snapshot=Path(normal['jars']['api']['path']).parent.parent.parent.parent
    assert all(data.sha((data.ROOT/path).read_bytes())==data.sha((snapshot/path).read_bytes())==digest for path,digest in hashes.items())
    reviewed={**previous['eligibilityClosureSourceHashes'],**{MAIN+name+'.java':hashes[MAIN+name+'.java'] for name in ['ApiMetricScrape','ApiScalarMetricExporter','ExactDurationMeterRegistry','ExactDurationSupport',*RECORDERS]}}
    assert len(reviewed)==26 and all(hashes[path]==digest for path,digest in reviewed.items())
    paths=[TEST+name+'.java' for name in COUNTS]
    texts={path:(data.ROOT/path).read_text() for path in [*reviewed,*paths]}
    advisory=audit(texts,list(reviewed),paths,hashes,registry['sourceRows'],{'WBS-P018-09'})
    assert advisory['metadataConsistent'] and not advisory['executionQualified'] and not advisory['holdReleased']
    assert all(row['canonicalOwner']==row['canonicalCostOwner']=='WBS-P018-09' for row in advisory['originalOwners'])
    cases=[]
    for name,count in COUNTS.items():
        path=TEST+name+'.java';text=texts[path]
        assert not any(word in text for word in ['@Before','@After','@ExtendWith','@Disabled','@TempDir','DriverManager','getConnection(','ProcessBuilder','Class.forName','System.getenv','java.net.','java.nio.file','WebStartupException','TemporaryInfrastructureException'])
        methods=re.findall(r'@Test\s+void\s+(\w+)\s*\(\s*\)',text)
        assert len(methods)==len(set(methods))==count
        cases.extend(dict(className='dev.codex.schubert.nk.api.monitoring.'+name,method=method,path=path,sourceSha256=hashes[path]) for method in methods)
    assert len(cases)==38
    # Independent SS351 domain arithmetic; not calculated through Product methods.
    assert 3+3+4+5+6*6==51 and 64*12+8+6*3+7==801 and 51+801+(2*2+1*2)*(6+2)==900
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2379_ApiDuration承認catalog同一exec閉鎖_単体テスト仕様書.md'
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,normalManifestSha256='39678a3c3b3ac634f9ee698f7acc900fa13248522829ce5338752b6bba920072',normalRecompiled=False,allInputsUnchanged=True,codeChanges=0,sourceChanges=[],eligibilityClosureSourceHashes=reviewed,wholeTestSourceHashes={path:hashes[path] for path in paths},cases=cases,originalTests=38,originalSuites=2,necessaryGenericRegression=24,necessaryApprovedCaller=14,newTestIds=0,metadataAdvisory=advisory,independentDomainArithmetic=dict(gauges=51,counters=801,histogramSeries=6,samples=900),judgement='PT_DEFAULT_WHOLE_GENERIC24_APPROVED_POLICY14_MEMORY_RECORDER_SDK_NO_EXTERNAL_IO',sameExecRequired=True,oldExecUnion=False,specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),productTestsExecuted=0,newAccepted=0,coverage=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
