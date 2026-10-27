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

SOURCE='d8a2b7952b321b75fe7fcc1c8d3acb287faca6ec'
OUT=data.BASE/'PG12236-check-health-completion-v1'
PINS={'normal':('PG12224-check-health-six-compile-v1','d65964a4fd58702926206ea8ae5c101ac445b66936e15bda5c9a29c355b129e2'),'host':('PG12226-check-health-host-v1','6e409c526939f7e256aa8c6d17831b9d599e679d44c54744a7f878fb614a9ec4'),'post':('PG12230-check-health-post-v1','318de790d7d7f2ddae2f9b9fc9091086967d37b8e68d1771d3b03f578769dffa'),'context':('PG12231-check-health-context-v1','2de10000666b0402a551ee2efb032761c6f3ff654f51aeffccb3222699ea3c86'),'contextPost':('PG12233-check-health-context-post-v1','bd3fe22d3fb448259d10d4b7afad63b976c1692816258e93e5131b49c60e7cdf'),'trace':('PG12232-check-health-trace-v1','090aeb1ffbd30cc6ff65a03d9b437580cd30ece93292cde31e765471e863221b'),'tracePost':('PG12234-check-health-trace-post-v1','d0e523f13955ea512ad61c55004ee4f88f03c9b7c61cfdf18dafb3cff275c634')}

def main():
    invocation=capture(__file__);assert not OUT.exists()
    bound=bind([(data.BASE/f/'manifest.json',h) for f,h in PINS.values()],SOURCE)
    v={k:data.read_checked(data.BASE/f/'manifest.json',h) for k,(f,h) in PINS.items()};normal,host,post=(v[k] for k in ('normal','host','post'))
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    assert host['observedTestExecutions']==8 and not host['oldExecUnion'] and all(s['actualExit']==0 and not s['timedOut'] for s in host['stages'])
    previous=data.read_checked(data.BASE/'PG12194-audit-metric-six-compile-v1/manifest.json','971ee001e169f9fa05df627e0cd0789704518d952105c27328eabf86ebd4adff')
    assert jar_classes(previous)==jar_classes(normal) and len(jar_classes(normal))==1843
    old,new=test_classes(previous),test_classes(normal);assert set(old)==set(new) and len(new)==1962
    changed=[key for key in old if old[key]!=new[key]];assert len(changed)==3;details=[]
    for role,entry in changed:
        a=parts((Path(previous['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        b=parts((Path(normal['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        details.append(dict(module=role,entry=entry,sourceFile=b['model']['sourceFile'],beforePhysicalSha256=old[(role,entry)],physicalSha256=new[(role,entry)],beforeRawCodeRepresentationSha256=a['rawCodeRepresentationSha256'],rawCodeRepresentationSha256=b['rawCodeRepresentationSha256'],beforeDebugTablesSha256=a['debugTablesSha256'],debugTablesSha256=b['debugTablesSha256']))
    assert {r['sourceFile'] for r in details}=={'AssetChecksumManifestTest.java','WebRuntimeHealthTest.java'}
    vectors=selftest();measure=data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256'])
    counts={role:{kind:dict(missed=sum(u['counters'][kind]['missed'] for u in m['selectedValueMain'].values()),covered=sum(u['counters'][kind]['covered'] for u in m['selectedValueMain'].values())) for kind in ('LINE','METHOD','CLASS','BRANCH')} for role,m in measure.items()}
    expected={'api':dict(LINE=(0,66),METHOD=(0,9),CLASS=(0,2),BRANCH=(0,36)),'web':dict(LINE=(1,6),METHOD=(1,1),CLASS=(0,1),BRANCH=(4,20))}
    assert set(measure)==set(expected) and all(not m['wholeArtifactCoverage100'] for m in measure.values())
    assert measure['api']['selectedValueFourCounters100'] and not measure['web']['selectedValueFourCounters100']
    assert all({k:(c['missed'],c['covered']) for k,c in counts[role].items()}==expected[role] for role in counts)
    static=data.read_checked(data.BASE/'PG12228-check-health-static-v1/manifest.json','3f9d9526d41956dae9ea25f17d123f3e1b948768fa06efb3fa65ce07fde40428');assert static['actualExit']==1 and static['reports']['pmd']['findings']==2 and all(s['processingErrors']==0 for s in static['reports'].values())
    inverse=data.read_checked(data.BASE/'PG12222-check-health-source-post-v1/manifest.json','08c473f6b4d69da5d575dc861adb92963d1f5640f3323cb54b92a9d0946d06e3');assert inverse['metadataNegativeVectors']==31
    assert v['contextPost']['metadataNegativeVectors']==8 and v['context']['sourceContexts']==2
    assert len(host['begin']['requiredClassDefinitions'])==3 and all(p==[host['begin']['moduleJars']['api' if '/api/' in target else 'web']] for target,p in host['begin']['requiredClassDefinitions'].items())
    assert not list(Path(host['begin']['testCwd']).iterdir());closure=host['begin']['eligibilityClosureSourceHashes'];assert len(closure)==9 and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in closure.items())
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2309_Checksum純Health十一是正_単体テスト仕様書.md';result=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2310_Checksum純Health十一是正_製造単体結果.md'
    verify(invocation);OUT.mkdir();data.write(OUT/'code-debug.json',dict(source=SOURCE,rows=details,structuralReaderVectors=vectors,meaningProof='strict original raw inverse29 vectors plus actual6; opaque CP index representation is not standalone semantic proof'))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,sourceChangeCommit=SOURCE,invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),boundOriginalRuns=bound,specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),relatedBugs=['BUG-1957'],relatedYkt=['YKT-1706'],implementationDecision='PG-D731',tests=host['begin']['cases'],actual=dict(tests=8,suites=2,newProductTestIds=0,failures=0,errors=0,skipped=0,aborted=0),selectedMainMeasuredCounters=counts,defaultJacocoFilters=True,zeroBranchCountersAreNA=True,noManualExclusions=True,eligibilityClosureSourceHashes=closure,codeDebugSha256=data.sha((OUT/'code-debug.json').read_bytes()),allMainClassesUnchanged=1843,otherTestClassesUnchanged=1959,testClassesChanged=3,stringConstants=10,referencesReplaced=76,readIncrementDecomposed=True,rawDiagnosticsCorrected=11,rawStaticBefore=13,rawStatic=2,sourceLocalContexts=2,unclassifiedRaw=0,rawStaticGateExit=1,actualSecretCount=None,fullArtifactsCoverage100=False,wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByCompletion=0,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
