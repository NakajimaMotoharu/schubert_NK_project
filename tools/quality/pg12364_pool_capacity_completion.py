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

SOURCE='e2a04c5d5775b8629ce3c4f17259d8378b2bb5f9'
OUT=data.BASE/'PG12364-pool-capacity-completion-v1'
PINS={'normal':('PG12352-pool-capacity-six-compile-v1','5b954538ef967b5ced149c9f0b4f3b11a15e88676e07c2ea56c22215e9a1e0b0'),'host':('PG12354-pool-capacity-host-v1','4ff7ea2da45aeae1e1e91d69c8f9b30cd5f943905b126231426908398ac706aa'),'post':('PG12358-pool-capacity-post-v1','ba2318f2be2028cc5b662d651f3f9f755802b51d6f08bf3232bfe760bed6383f'),'context':('PG12359-pool-capacity-context-v1','f12539d10a80416aaebafc9210b2c3587801da0e6a0f21855b032d4e85a0bfec'),'contextPost':('PG12361-pool-capacity-context-post-v1','6f530c411da67198fb192b7dd86e337491986f626d803280d6b53865473a5a4e'),'trace':('PG12360-pool-capacity-trace-v1','9a5e109ab907bb8a5019881127c7924dbc93246b9bcd0b959ef601fab95321f7'),'tracePost':('PG12362-pool-capacity-trace-post-v1','4d073194c4b5f6132f9a28a02202daf67ca39c2eaf303ee006b5e229339aa8ca')}

def main():
    invocation=capture(__file__);assert not OUT.exists()
    bound=bind([(data.BASE/f/'manifest.json',h) for f,h in PINS.values()],SOURCE)
    v={k:data.read_checked(data.BASE/f/'manifest.json',h) for k,(f,h) in PINS.items()};normal,host,post=(v[k] for k in ('normal','host','post'))
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    assert host['observedTestExecutions']==29 and not host['oldExecUnion'] and all(s['actualExit']==0 and not s['timedOut'] for s in host['stages'])
    previous=data.read_checked(data.BASE/'PG12312-readiness-dependency-six-compile-v1/manifest.json','96605de485f83a38656ca3d0f479f679f708193d263671784582acb088d4b88b')
    assert jar_classes(previous)==jar_classes(normal) and len(jar_classes(normal))==1843
    old,new=test_classes(previous),test_classes(normal);assert set(old)==set(new) and len(new)==1962
    changed=[key for key in old if old[key]!=new[key]];assert len(changed)==9;details=[]
    for role,entry in changed:
        a=parts((Path(previous['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        b=parts((Path(normal['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        details.append(dict(module=role,entry=entry,sourceFile=b['model']['sourceFile'],beforePhysicalSha256=old[(role,entry)],physicalSha256=new[(role,entry)],beforeRawCodeRepresentationSha256=a['rawCodeRepresentationSha256'],rawCodeRepresentationSha256=b['rawCodeRepresentationSha256'],beforeDebugTablesSha256=a['debugTablesSha256'],debugTablesSha256=b['debugTablesSha256']))
    assert {r['sourceFile'] for r in details}=={'DbPoolMetricObservationTest.java','WebDbPoolMetricObservationTest.java','OperationMismatchMetricRecorderTest.java','TransferCapacityTest.java'}
    vectors=selftest();measure=data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256'])
    counts={role:{kind:dict(missed=sum(u['counters'][kind]['missed'] for u in m['selectedValueMain'].values()),covered=sum(u['counters'][kind]['covered'] for u in m['selectedValueMain'].values())) for kind in ('LINE','METHOD','CLASS','BRANCH')} for role,m in measure.items()}
    assert set(measure)=={'api','web','protocol'} and sum(len(m['selectedValueMain']) for m in measure.values())==16
    assert all(not m['wholeArtifactCoverage100'] and not m['selectedValueFourCounters100'] for m in measure.values())
    core_stems={'DbPoolMetricObservation','WebDbPoolMetricObservation','OperationMismatchMetricRecorder','TransferCapacity','CapacityExceededException'}
    core={p:u for m in measure.values() for p,u in m['selectedValueMain'].items() if p.rpartition('/')[2][:-6].split('$',1)[0] in core_stems}
    assert len(core)==9 and all(c['missed']==0 for u in core.values() for c in u['counters'].values())
    core_counts={k:sum(u['counters'][k]['covered'] for u in core.values()) for k in ('LINE','METHOD','CLASS','BRANCH')}
    assert core_counts==dict(LINE=108,METHOD=19,CLASS=9,BRANCH=53)
    static=data.read_checked(data.BASE/'PG12356-pool-capacity-static-v1/manifest.json','fce42d8b4757ef8be42f5d7d8f9436f5f5cf52928e1c4b9535fca984e5387b16');assert static['actualExit']==1 and static['reports']['pmd']['findings']==24 and all(s['processingErrors']==0 for s in static['reports'].values())
    inverse=data.read_checked(data.BASE/'PG12350-pool-capacity-source-post-v1/manifest.json','b5297ac25b1c62894a2f22d950edc2983541174046702017501b39373993dbe0');assert inverse['metadataNegativeVectors']==60
    assert v['contextPost']['metadataNegativeVectors']==22 and v['context']['sourceContexts']==24
    assert len(host['begin']['requiredClassDefinitions'])==8
    for target,locations in host['begin']['requiredClassDefinitions'].items():
        role=target.split('/')[4];assert locations==[host['begin']['moduleJars'][role]]
    assert not list(Path(host['begin']['testCwd']).iterdir())
    closure=host['begin']['eligibilityClosureSourceHashes'];assert len(closure)==8 and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in closure.items())
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2325_供給Pool容量四fixture十六件_単体テスト仕様.md';result=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2326_供給Pool容量十六件_製造単体結果.md'
    verify(invocation);OUT.mkdir();data.write(OUT/'code-debug.json',dict(source=SOURCE,rows=details,structuralReaderVectors=vectors,meaningProof='strict original raw inverse60 typed vectors plus actual29; opaque CP index representation is not standalone semantic proof'))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,sourceChangeCommit=SOURCE,invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),boundOriginalRuns=bound,specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),relatedBugs=['BUG-1967'],relatedYkt=['YKT-1715'],implementationDecision='PG-D738',tests=host['begin']['cases'],actual=dict(tests=29,suites=4,newProductTestIds=0,failures=0,errors=0,skipped=0,aborted=0),selectedMainMeasuredCounters=counts,coreNineMainMeasuredCovered=core_counts,defaultJacocoFilters=True,zeroBranchCountersAreNA=True,noManualExclusions=True,eligibilityClosureSourceHashes=closure,codeDebugSha256=data.sha((OUT/'code-debug.json').read_bytes()),allMainClassesUnchanged=1843,otherTestClassesUnchanged=1953,testClassesChanged=9,stringConstants=5,referencesReplaced=24,numericConstants=11,numericReferences=11,rawDiagnosticsCorrected=16,rawStaticBefore=40,rawStatic=24,sourceLocalContexts=24,unclassifiedRaw=0,rawStaticGateExit=1,actualSecretCount=None,fullArtifactsCoverage100=False,wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByCompletion=0,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
