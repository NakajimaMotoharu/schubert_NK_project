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

SOURCE='442441c83f73935eb2bd33cd40a7b9884eb7dfe3'
OUT=data.BASE/'PG12324-readiness-dependency-completion-v1'
PINS={'normal': ('PG12312-readiness-dependency-six-compile-v1', '96605de485f83a38656ca3d0f479f679f708193d263671784582acb088d4b88b'), 'host': ('PG12314-readiness-dependency-host-v1', '2d3753991a8793fd02b77741a79f2a7d30edc4b6ff5d6db50328066761d6774c'), 'post': ('PG12319-readiness-dependency-post-v2', '4637b7fae4f42b67a7db0a04dd67c82513fd499b0f9287b67a43dde169604783'), 'boundary': ('PG12323-readiness-boundary-contract-v2', '6102554e6bdb9c73e3a55ea300eed11fa9dcad8b8b18d34fb0905d0bf1ea8ef3'), 'trace': ('PG12320-readiness-dependency-trace-v1', '206feacbec61213920ecf10430c8810644e76253619cd5f2a164ce9b43b76140'), 'tracePost': ('PG12322-readiness-dependency-trace-post-v1', 'fba547421c161c3839f1dda767b560c22fbe4976accf6fe97a3598fdf26c1c8a')}

def main():
    invocation=capture(__file__);assert not OUT.exists()
    bound=bind([(data.BASE/f/'manifest.json',h) for f,h in PINS.values()],SOURCE)
    v={k:data.read_checked(data.BASE/f/'manifest.json',h) for k,(f,h) in PINS.items()};normal,host,post=(v[k] for k in ('normal','host','post'))
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    assert host['observedTestExecutions']==4 and not host['oldExecUnion'] and all(s['actualExit']==0 and not s['timedOut'] for s in host['stages'])
    previous=data.read_checked(data.BASE/'PG12286-api-value-six-compile-v1/manifest.json','776c71c70a1953bcdbf96f0d3b220cdcb91f7523a2ae38fa6664bdb33494104b')
    assert jar_classes(previous)==jar_classes(normal) and len(jar_classes(normal))==1843
    old,new=test_classes(previous),test_classes(normal);assert set(old)==set(new) and len(new)==1962
    changed=[key for key in old if old[key]!=new[key]];assert len(changed)==2;details=[]
    for role,entry in changed:
        a=parts((Path(previous['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        b=parts((Path(normal['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        details.append(dict(module=role,entry=entry,sourceFile=b['model']['sourceFile'],beforePhysicalSha256=old[(role,entry)],physicalSha256=new[(role,entry)],beforeRawCodeRepresentationSha256=a['rawCodeRepresentationSha256'],rawCodeRepresentationSha256=b['rawCodeRepresentationSha256'],beforeDebugTablesSha256=a['debugTablesSha256'],debugTablesSha256=b['debugTablesSha256']))
    assert {r['sourceFile'] for r in details}=={'ApiReadinessPredicateTest.java','WebRuntimeDependencyTest.java'}
    vectors=selftest();measure=data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256'])
    counts={role:{kind:dict(missed=sum(u['counters'][kind]['missed'] for u in m['selectedValueMain'].values()),covered=sum(u['counters'][kind]['covered'] for u in m['selectedValueMain'].values())) for kind in ('LINE','METHOD','CLASS','BRANCH')} for role,m in measure.items()}
    assert set(measure)=={'api','web'} and len(measure['api']['selectedValueMain'])==3 and not measure['web']['selectedValueMain']
    assert not measure['api']['wholeArtifactCoverage100'] and not measure['api']['selectedValueFourCounters100']
    static=data.read_checked(data.BASE/'PG12316-readiness-dependency-static-v1/manifest.json','656d8b13e599bc581fd7410b9b13e7becc1903e2e5aa6a201621cb1874d82395');assert static['actualExit']==0 and static['reports']['pmd']['findings']==0 and all(s['processingErrors']==0 for s in static['reports'].values())
    inverse=data.read_checked(data.BASE/'PG12310-readiness-dependency-source-post-v1/manifest.json','241867d84ce82893944f6dd7ee760b38f66be2fa7b4b4a54d712100f7d9288cb');assert inverse['metadataNegativeVectors']==16
    assert v['boundary']['metadataNegativeVectors']==5 and post['typeResolutionNegativeVectors']==3
    assert len(host['begin']['requiredClassDefinitions'])==1 and all(p==[host['begin']['moduleJars']['api']] for p in host['begin']['requiredClassDefinitions'].values())
    assert not list(Path(host['begin']['testCwd']).iterdir())
    assert data.sha(Path(host['begin']['pomReadOnlyPath']).read_bytes())==host['begin']['pomSha256']
    closure=host['begin']['eligibilityClosureSourceHashes'];assert len(closure)==1 and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in closure.items())
    assert len(post['resolvedInterfaceMetadata'])==4 and all(not r['executionPermission'] and not r['staticInitializer'] for r in post['resolvedInterfaceMetadata'].values())
    assert all(not m['wholeArtifactCoverage100'] and m['nonPredicateApiMainInstructionHits']==0 for m in measure.values())
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2320_Readiness依存五件_単体テスト仕様.md';result=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2321_Readiness依存五件_製造単体結果.md'
    verify(invocation);OUT.mkdir();data.write(OUT/'code-debug.json',dict(source=SOURCE,rows=details,structuralReaderVectors=vectors,meaningProof='strict original raw inverse16 vectors plus actual4; opaque CP index representation is not standalone semantic proof'))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,sourceChangeCommit=SOURCE,invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),boundOriginalRuns=bound,specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),relatedBugs=['BUG-1963','BUG-1964','BUG-1965'],relatedYkt=['YKT-1712','YKT-1713','YKT-1714'],implementationDecision='PG-D736',tests=host['begin']['cases'],actual=dict(tests=4,suites=2,newProductTestIds=0,failures=0,errors=0,skipped=0,aborted=0),selectedMainMeasuredCounters=counts,defaultJacocoFilters=True,zeroBranchCountersAreNA=True,noManualExclusions=True,eligibilityClosureSourceHashes=closure,codeDebugSha256=data.sha((OUT/'code-debug.json').read_bytes()),allMainClassesUnchanged=1843,otherTestClassesUnchanged=1960,testClassesChanged=2,stringConstants=5,referencesReplaced=29,rawDiagnosticsCorrected=5,rawStaticBefore=5,rawStatic=0,sourceLocalContexts=0,unclassifiedRaw=0,rawStaticGateExit=0,actualSecretCount=None,fullArtifactsCoverage100=False,wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByCompletion=0,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
