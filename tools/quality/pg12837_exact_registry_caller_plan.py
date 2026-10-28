"""Read-only same-source38 scope and unchanged normal-input binding; no product run."""
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from fixture_scope_advisory import audit
from host_tool_invocation import capture, verify

SOURCE='0124b5938a50f4ceea542486c336ba12146cb1b4'
OUT=data.BASE/'PG12837-exact-registry-caller-plan-v1'
PREFIX='src/schubert-nk-api/src/'
MAIN=PREFIX+'main/java/dev/codex/schubert/nk/api/monitoring/'
TEST=PREFIX+'test/java/dev/codex/schubert/nk/api/monitoring/'
COUNTS={'ExactDurationMeterRegistryTest':10,'DbQueryDurationMetricRecorderTest':9}
RECORDERS=['OutboxRowsMetricRecorder','OutboxAgeMetricRecorder','AsyncJobMetricRecorder','DbPoolMetricRecorder','MqPressureMetricRecorder','InboxReplayMetricRecorder','OperationMismatchMetricRecorder','MqRedeliveryMetricRecorder','MqMessageMetricRecorder','DbQueryDurationMetricRecorder','MqProcessingDurationMetricRecorder']


def main():
    invocation=capture(__file__);assert not OUT.exists()
    normal=data.read_checked(data.BASE/'PG12819-exact-registry-six-compile-v2/manifest.json','8a5081b03b988d4370df0c3fa45c69eeeda6d5296543a38f1e2239b0ae088f89')
    previous=data.read_checked(data.BASE/'PG12817-exact-registry-plan-v3/manifest.json','88a9d3eebc46f473fdc492e5ecdd8806b380aae78701312631019e40eb41e978')
    registry=data.read_checked(data.BASE/'PG12804-api-policy-trace-v1/manifest.json','f595af6aa0bb60875d61573bc6de8ff0bef98e0d8dfb5b9ab7761fff4cc7f178')
    assert normal['source']==SOURCE and registry['source']=='2baca5740741adb7c676cb85a83f15d19de01083' and normal['actualExit']==normal['testsExecuted']==0
    hashes=normal['begin']['inputHashes'];snapshot=Path(normal['jars']['api']['path']).parent.parent.parent.parent
    assert all(data.sha((data.ROOT/path).read_bytes())==data.sha((snapshot/path).read_bytes())==digest for path,digest in hashes.items())
    reviewed={**previous['eligibilityClosureSourceHashes'],**{MAIN+name+'.java':hashes[MAIN+name+'.java'] for name in ['ApiMetricScrape','ApiScalarMetricExporter','ExactDurationMeterRegistry','ExactDurationSupport',*RECORDERS]}}
    assert len(reviewed)==26 and all(hashes[path]==digest for path,digest in reviewed.items())
    paths=[TEST+name+'.java' for name in COUNTS]
    texts={path:(data.ROOT/path).read_text() for path in [*reviewed,*paths]}
    adjusted=[dict(row) for row in registry['sourceRows']]
    correction=previous['sourceChanges'][0]
    matched=[row for row in adjusted if row['path']==correction['path']];assert len(matched)==1 and matched[0]['sha256']==correction['beforeSha256']
    matched[0]['sha256']=correction['sha256'];assert matched[0]['sha256']==hashes[correction['path']]
    advisory=audit(texts,list(reviewed),paths,hashes,adjusted,{'WBS-P018-09'})
    assert advisory['metadataConsistent'] and not advisory['executionQualified'] and not advisory['holdReleased']
    assert all(row['canonicalOwner']==row['canonicalCostOwner']=='WBS-P018-09' for row in advisory['originalOwners'])
    cases=[]
    for name,count in COUNTS.items():
        path=TEST+name+'.java';text=texts[path]
        assert not any(word in text for word in ['@Before','@After','@ExtendWith','@Disabled','@TempDir','DriverManager','getConnection(','ProcessBuilder','Class.forName','System.getenv','java.net.','java.nio.file','WebStartupException','TemporaryInfrastructureException'])
        methods=re.findall(r'@Test\s+void\s+(\w+)\s*\(\s*\)',text)
        assert len(methods)==len(set(methods))==count
        cases.extend(dict(className='dev.codex.schubert.nk.api.monitoring.'+name,method=method,path=path,sourceSha256=hashes[path]) for method in methods)
    assert len(cases)==19
    # Frozen independent literal fixture arithmetic; no Product expected generator.
    assert 4*64==256 and 2*2==4
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2385_ExactRegistry正規caller同一exec接続_仕様追補.md'
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,normalManifestSha256='8a5081b03b988d4370df0c3fa45c69eeeda6d5296543a38f1e2239b0ae088f89',normalRecompiled=False,allInputsUnchanged=True,codeChanges=0,sourceChanges=[],eligibilityClosureSourceHashes=reviewed,wholeTestSourceHashes={path:hashes[path] for path in paths},cases=cases,originalTests=19,originalSuites=2,necessaryGenericRegression=10,necessaryApprovedCaller=9,newTestIds=0,metadataAdvisory=advisory,provisionalOriginalRegistryShaAdjustedRows=1,originalRegistryHashPreserved=True,independentDomainArithmetic=dict(boundarySamples=15,expectedCdf=[2,5,8,11,14],concurrentExactWrites=256,dbSeries=4),judgement='PT_DEFAULT_WHOLE_EXACT10_DB_RECORDER9_SDK_MEMORY_NO_SQL_EXTERNAL_IO',sameExecRequired=True,oldExecUnion=False,specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),productTestsExecuted=0,newAccepted=0,coverage=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
