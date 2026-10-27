"""Bind original audit6, strict raw inverse29, actual counters, static raw5 and canonical trace."""
from pathlib import Path
import datetime as dt
import platform
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
from pg9978_plain_core_quality_post import test_classes
from pg9906_user_query_oracle_source_post import jar_classes
from pg11929_storage_fixture_class_metadata import parts,selftest

SOURCE='4b5f6faa078be348132a6ece9140b0c1a31d7907'
OUT=data.BASE/'PG12206-audit-metric-completion-v1'
PINS={'normal':('PG12194-audit-metric-six-compile-v1','971ee001e169f9fa05df627e0cd0789704518d952105c27328eabf86ebd4adff'),'host':('PG12196-audit-metric-host-v1','5611da6fac4d7f4959d97882e2a0c297d5d9681fa7b29e3a8721f15373d75fc8'),'post':('PG12200-audit-metric-post-v1','554698fe99408bc21057694826c982c3ab4d6eafe44629ae4cf9cdaf1c9e20fb'),'context':('PG12201-audit-metric-context-v1','12c21f28214a9869f24549a69d8fdf577b12316a0c31b6bc822cd6bcf94a2ee2'),'contextPost':('PG12203-audit-metric-context-post-v1','f7b5d181661634f8cfff2aade0bbf30eefc7d22ae0942cfac58d529b64ca9e07'),'trace':('PG12202-audit-metric-trace-v1','b0a68a0a64aaf11d2b0abdd94814207edd67e9391e36f49354e254979e2d55be'),'tracePost':('PG12204-audit-metric-trace-post-v1','c0d5c5cfb9413d1b9f3fe5483fc9b7ca322a920803a2816cda01ee684762b74a')}

def main():
    invocation=capture(__file__);assert not OUT.exists()
    bound=bind([(data.BASE/f/'manifest.json',h) for f,h in PINS.values()],SOURCE)
    v={k:data.read_checked(data.BASE/f/'manifest.json',h) for k,(f,h) in PINS.items()};normal,host,post=(v[k] for k in ('normal','host','post'))
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    assert host['observedTestExecutions']==19 and not host['oldExecUnion'] and all(s['actualExit']==0 and not s['timedOut'] for s in host['stages'])
    previous=data.read_checked(data.BASE/'PG12164-audit-fixture-six-compile-v1/manifest.json','462a900efa1799ab71b9f192cb22f88c80aafcc8afd1453bffb2c577b0499048')
    assert jar_classes(previous)==jar_classes(normal) and len(jar_classes(normal))==1843
    old,new=test_classes(previous),test_classes(normal);assert set(old)==set(new) and len(new)==1962
    changed=[key for key in old if old[key]!=new[key]];assert len(changed)==10;details=[]
    for role,entry in changed:
        a=parts((Path(previous['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        b=parts((Path(normal['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        details.append(dict(module=role,entry=entry,sourceFile=b['model']['sourceFile'],beforePhysicalSha256=old[(role,entry)],physicalSha256=new[(role,entry)],beforeRawCodeRepresentationSha256=a['rawCodeRepresentationSha256'],rawCodeRepresentationSha256=b['rawCodeRepresentationSha256'],beforeDebugTablesSha256=a['debugTablesSha256'],debugTablesSha256=b['debugTablesSha256']))
    assert {r['sourceFile'] for r in details}=={'WebSecurityAuditTest.java','BatchMetricRecorderTest.java','BatchMetricContractTest.java'}
    vectors=selftest();measure=data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256'])
    counts={role:{kind:dict(missed=sum(u['counters'][kind]['missed'] for u in m['selectedValueMain'].values()),covered=sum(u['counters'][kind]['covered'] for u in m['selectedValueMain'].values())) for kind in ('LINE','METHOD','CLASS','BRANCH')} for role,m in measure.items()}
    expected={'web':dict(LINE=89,METHOD=11,CLASS=3,BRANCH=52),'batch':dict(LINE=83,METHOD=17,CLASS=4,BRANCH=32)}
    assert set(measure)==set(expected) and all(m['selectedValueFourCounters100'] and not m['wholeArtifactCoverage100'] for m in measure.values())
    assert all({k:c['covered'] for k,c in counts[role].items()}==expected[role] and all(c['missed']==0 for c in counts[role].values()) for role in counts)
    static=data.read_checked(data.BASE/'PG12198-audit-metric-static-v1/manifest.json','a10133ca7dedd88083f8f39c8b96b0af1cde5ffc161655dc8feb3591b10d8255');assert static['actualExit']==1 and static['reports']['pmd']['findings']==5 and all(s['processingErrors']==0 for s in static['reports'].values())
    inverse=data.read_checked(data.BASE/'PG12192-audit-metric-source-post-v1/manifest.json','f61343ad316c1f233619fb776fc19f3007353700111d55c2942c539f6f5e1d0c');assert inverse['metadataNegativeVectors']==24
    assert v['contextPost']['metadataNegativeVectors']==8 and v['context']['sourceContexts']==5
    assert len(host['begin']['requiredClassDefinitions'])==4 and all(p==[host['begin']['moduleJars']['batch' if '/batch/' in target else 'web']] for target,p in host['begin']['requiredClassDefinitions'].items())
    assert not list(Path(host['begin']['testCwd']).iterdir());closure=host['begin']['eligibilityClosureSourceHashes'];assert len(closure)==9 and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in closure.items())
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2306_監査Metric九是正_単体テスト仕様書.md';result=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2307_監査Metric九是正_製造単体結果.md'
    verify(invocation);OUT.mkdir();data.write(OUT/'code-debug.json',dict(source=SOURCE,rows=details,structuralReaderVectors=vectors,meaningProof='strict original raw inverse29 vectors plus actual6; opaque CP index representation is not standalone semantic proof'))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,sourceChangeCommit=SOURCE,invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),boundOriginalRuns=bound,specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),relatedBugs=['BUG-1956'],relatedYkt=['YKT-1705'],implementationDecision='PG-D730',tests=host['begin']['cases'],actual=dict(tests=19,suites=3,newProductTestIds=0,failures=0,errors=0,skipped=0,aborted=0),selectedMainMeasuredCounters=counts,defaultJacocoFilters=True,zeroBranchCountersAreNA=True,noManualExclusions=True,eligibilityClosureSourceHashes=closure,codeDebugSha256=data.sha((OUT/'code-debug.json').read_bytes()),allMainClassesUnchanged=1843,otherTestClassesUnchanged=1952,testClassesChanged=10,stringConstants=5,referencesReplaced=40,fieldRenames=3,ifIndexConstants=1,rawDiagnosticsCorrected=9,rawStaticBefore=14,rawStatic=5,sourceLocalContexts=5,unclassifiedRaw=0,rawStaticGateExit=1,actualSecretCount=None,fullArtifactsCoverage100=False,wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByCompletion=0,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
