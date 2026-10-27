"""Bind actual8 checksum/health oracles, exact11 corrections and explicitly partial Web ready counters."""
from pathlib import Path
import datetime as dt
import platform
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
from pg9978_plain_core_quality_post import test_classes
from pg9906_user_query_oracle_source_post import jar_classes
from pg11929_storage_fixture_class_metadata import parts,selftest

SOURCE='7368ba9d4a38677f5eade903771832e612aa42b5'
OUT=data.BASE/'PG12298-api-value-completion-v1'
PINS={'normal':('PG12286-api-value-six-compile-v1','776c71c70a1953bcdbf96f0d3b220cdcb91f7523a2ae38fa6664bdb33494104b'),'host':('PG12288-api-value-host-v1','c0478ed0d574dce6353c8de4643f28c44f094f26d91b61f32db0d93eb69848b0'),'post':('PG12292-api-value-post-v1','443e7cf38169f2a1197358b23a62d870e37d39037a49ea53a277a064e4c0b894'),'context':('PG12293-api-value-context-v1','4d3f6cf82d1bb4d5a0a5a3a50afcfe3accea90fa446dd9fe634daf1e6f87abb1'),'contextPost':('PG12295-api-value-context-post-v1','94f068630be89a535e7666b02f140bd3692442a4a06f360bcb4367733fe88e38'),'trace':('PG12294-api-value-trace-v1','8eb0ba8d94e60eba9ad0e8bda763e6f2868be2cc5bc09b1061106e8273aea27a'),'tracePost':('PG12296-api-value-trace-post-v1','9b9e073e6c0f77e2e652dee6e4f3514d8cbe8cf9f5f4f0cad9dc1f4d6c3cddb5')}

def main():
    invocation=capture(__file__);assert not OUT.exists()
    bound=bind([(data.BASE/f/'manifest.json',h) for f,h in PINS.values()],SOURCE)
    v={k:data.read_checked(data.BASE/f/'manifest.json',h) for k,(f,h) in PINS.items()};normal,host,post=(v[k] for k in ('normal','host','post'))
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    assert host['observedTestExecutions']==18 and not host['oldExecUnion'] and all(s['actualExit']==0 and not s['timedOut'] for s in host['stages'])
    previous=data.read_checked(data.BASE/'PG12224-check-health-six-compile-v1/manifest.json','d65964a4fd58702926206ea8ae5c101ac445b66936e15bda5c9a29c355b129e2')
    assert jar_classes(previous)==jar_classes(normal) and len(jar_classes(normal))==1843
    old,new=test_classes(previous),test_classes(normal);assert set(old)==set(new) and len(new)==1962
    changed=[key for key in old if old[key]!=new[key]];assert len(changed)==5;details=[]
    for role,entry in changed:
        a=parts((Path(previous['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        b=parts((Path(normal['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        details.append(dict(module=role,entry=entry,sourceFile=b['model']['sourceFile'],beforePhysicalSha256=old[(role,entry)],physicalSha256=new[(role,entry)],beforeRawCodeRepresentationSha256=a['rawCodeRepresentationSha256'],rawCodeRepresentationSha256=b['rawCodeRepresentationSha256'],beforeDebugTablesSha256=a['debugTablesSha256'],debugTablesSha256=b['debugTablesSha256']))
    assert {r['sourceFile'] for r in details}=={'StubAnswerProviderTest.java','PasswordPolicyTest.java','OutboxDlqMetadataTest.java','GeneratedMetricValueContractTest.java'}
    vectors=selftest();measure=data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256'])
    counts={role:{kind:dict(missed=sum(u['counters'][kind]['missed'] for u in m['selectedValueMain'].values()),covered=sum(u['counters'][kind]['covered'] for u in m['selectedValueMain'].values())) for kind in ('LINE','METHOD','CLASS','BRANCH')} for role,m in measure.items()}
    assert set(measure)=={'api'} and len(measure['api']['selectedValueMain'])==13
    assert not measure['api']['wholeArtifactCoverage100'] and not measure['api']['selectedValueFourCounters100']
    static=data.read_checked(data.BASE/'PG12290-api-value-static-v1/manifest.json','3d593e24fabfd7a5ec0323f9b308c47c1b2106dfa66dc16210c6a5f80e89954c');assert static['actualExit']==1 and static['reports']['pmd']['findings']==2 and all(s['processingErrors']==0 for s in static['reports'].values())
    inverse=data.read_checked(data.BASE/'PG12284-api-value-source-post-v1/manifest.json','e99f268993a69db56a11e4c56f1292fc8051af028e263d9ddff879f1bacb8194');assert inverse['metadataNegativeVectors']==30
    assert v['contextPost']['metadataNegativeVectors']==12 and v['context']['sourceContexts']==2
    assert len(host['begin']['requiredClassDefinitions'])==12 and all(p==[host['begin']['moduleJars']['api']] for p in host['begin']['requiredClassDefinitions'].values())
    root=Path(host['begin']['testCwd']);expected_file='target/question-stub-traces/PT-ASY-STB005.txt'
    assert {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}=={expected_file}
    assert data.sha((root/expected_file).read_bytes())==host['publicFixtureFileHashes'][expected_file]
    closure=host['begin']['eligibilityClosureSourceHashes'];assert len(closure)==12 and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in closure.items())
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2317_API純値四fixture九件_単体テスト仕様.md';result=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2318_API純値四fixture九件_製造単体結果.md'
    verify(invocation);OUT.mkdir();data.write(OUT/'code-debug.json',dict(source=SOURCE,rows=details,structuralReaderVectors=vectors,meaningProof='strict original raw inverse30 vectors plus actual18; opaque CP index representation is not standalone semantic proof'))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,sourceChangeCommit=SOURCE,invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),boundOriginalRuns=bound,specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),relatedBugs=['BUG-1960','BUG-1961','BUG-1962'],relatedYkt=['YKT-1709','YKT-1710','YKT-1711'],implementationDecision='PG-D735',tests=host['begin']['cases'],actual=dict(tests=18,suites=4,newProductTestIds=0,failures=0,errors=0,skipped=0,aborted=0),selectedMainMeasuredCounters=counts,defaultJacocoFilters=True,zeroBranchCountersAreNA=True,noManualExclusions=True,eligibilityClosureSourceHashes=closure,codeDebugSha256=data.sha((OUT/'code-debug.json').read_bytes()),allMainClassesUnchanged=1843,otherTestClassesUnchanged=1957,testClassesChanged=5,stringConstants=9,referencesReplaced=50,rawDiagnosticsCorrected=9,rawStaticBefore=11,rawStatic=2,sourceLocalContexts=2,unclassifiedRaw=0,rawStaticGateExit=1,actualSecretCount=None,fullArtifactsCoverage100=False,wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByCompletion=0,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
