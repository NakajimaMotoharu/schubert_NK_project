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

SOURCE='92c80a593717465426a33bdf581bc7e94b1235f1'
OUT=data.BASE/'PG12176-audit-fixture-completion-v1'
PINS={'normal':('PG12164-audit-fixture-six-compile-v1','462a900efa1799ab71b9f192cb22f88c80aafcc8afd1453bffb2c577b0499048'),'host':('PG12166-audit-fixture-host-v1','bdbd9713e98261dc6928af9962c3e9743d91be68683cb6e015e8eb509ce236c1'),'post':('PG12170-audit-fixture-post-v1','6c89ad1065f665b2feb5cc056e5354be4bad0c3a7e0f3358e4869a0e116d42c7'),'context':('PG12175-audit-fixture-context-v2','6c4c5b7032d4c2bd6e103900648521ee961a816a184d89215ed46d50d5ab036e'),'contextPost':('PG12173-audit-fixture-context-post-v1','c099169331bb672f774c0833491c98dcb808eba0f8028ec68dd67970c70cefb6'),'trace':('PG12172-audit-fixture-trace-v1','9f8f91ef46a6aec9729c6915aa4ac3ef1339ffbf81789ec5c911638e03c846c4'),'tracePost':('PG12174-audit-fixture-trace-post-v1','6385ee863425c5f9a50319e622b529c57a12c2410c92e11c30cb19fdd81a365b')}

def main():
    invocation=capture(__file__);assert not OUT.exists()
    bound=bind([(data.BASE/f/'manifest.json',h) for f,h in PINS.values()],SOURCE)
    v={k:data.read_checked(data.BASE/f/'manifest.json',h) for k,(f,h) in PINS.items()};normal,host,post=(v[k] for k in ('normal','host','post'))
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    assert host['observedTestExecutions']==6 and not host['oldExecUnion'] and all(s['actualExit']==0 and not s['timedOut'] for s in host['stages'])
    previous=data.read_checked(data.BASE/'PG12134-batch-value-fixture-six-compile-v1/manifest.json','6894ef3e885fbe1d4995e5809fd82dc16fa88b0a3ccb02613c120370fdf56bb9')
    assert jar_classes(previous)==jar_classes(normal) and len(jar_classes(normal))==1843
    old,new=test_classes(previous),test_classes(normal);assert set(old)==set(new) and len(new)==1962
    changed=[key for key in old if old[key]!=new[key]];assert len(changed)==5;details=[]
    for role,entry in changed:
        a=parts((Path(previous['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        b=parts((Path(normal['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        details.append(dict(module=role,entry=entry,sourceFile=b['model']['sourceFile'],beforePhysicalSha256=old[(role,entry)],physicalSha256=new[(role,entry)],beforeRawCodeRepresentationSha256=a['rawCodeRepresentationSha256'],rawCodeRepresentationSha256=b['rawCodeRepresentationSha256'],beforeDebugTablesSha256=a['debugTablesSha256'],debugTablesSha256=b['debugTablesSha256']))
    assert {r['sourceFile'] for r in details}=={'WebSecurityAuditTest.java'}
    vectors=selftest();measure=data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256'])['web']
    counts={kind:dict(missed=sum(u['counters'][kind]['missed'] for u in measure['selectedValueMain'].values()),covered=sum(u['counters'][kind]['covered'] for u in measure['selectedValueMain'].values())) for kind in ('LINE','METHOD','CLASS','BRANCH')}
    assert measure['selectedValueFourCounters100'] and not measure['wholeArtifactCoverage100'] and {k:c['covered'] for k,c in counts.items()}==dict(LINE=89,METHOD=11,CLASS=3,BRANCH=52) and all(c['missed']==0 for c in counts.values())
    static=data.read_checked(data.BASE/'PG12168-audit-fixture-static-v1/manifest.json','7782fd394e8f7972e0dfc878264791ce2f6540da31574f8a0eb7dfbdc0840845');assert static['actualExit']==1 and static['reports']['pmd']['findings']==5 and all(s['processingErrors']==0 for s in static['reports'].values())
    inverse=data.read_checked(data.BASE/'PG12162-audit-fixture-source-post-v1/manifest.json','21ae5e6309518d1cdcfce8ffb65edede743b2f15d7865362727829831604a590');assert inverse['metadataNegativeVectors']==29
    assert v['contextPost']['metadataNegativeVectors']==8 and v['context']['sourceContexts']==3
    assert len(host['begin']['requiredClassDefinitions'])==2 and all(p==[host['begin']['moduleJars']['web']] for p in host['begin']['requiredClassDefinitions'].values())
    assert not list(Path(host['begin']['testCwd']).iterdir());closure=host['begin']['eligibilityClosureSourceHashes'];assert len(closure)==5 and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in closure.items())
    old_tool=data.ROOT/'tools/quality/pg12171_audit_fixture_context.py';assert data.sha(old_tool.read_bytes())=='506ed8ebdf6ef2ea03e75e521c6f0476599e2e0a726a444dd5af3b1b2e25f5c3'
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2303_Web局所監査十三定数_単体テスト仕様書.md';result=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2304_Web局所監査十三定数_製造単体結果.md'
    verify(invocation);OUT.mkdir();data.write(OUT/'code-debug.json',dict(source=SOURCE,rows=details,structuralReaderVectors=vectors,meaningProof='strict original raw inverse29 vectors plus actual6; opaque CP index representation is not standalone semantic proof'))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,sourceChangeCommit=SOURCE,invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),boundOriginalRuns=bound,specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),relatedBugs=['BUG-1954','BUG-1955'],relatedYkt=['YKT-1703','YKT-1704'],implementationDecision='PG-D729',tests=host['begin']['cases'],actual=dict(tests=6,suites=1,newProductTestIds=0,failures=0,errors=0,skipped=0,aborted=0),selectedMainMeasuredCounters=counts,defaultJacocoFilters=True,zeroBranchCountersAreNA=True,noManualExclusions=True,eligibilityClosureSourceHashes=closure,codeDebugSha256=data.sha((OUT/'code-debug.json').read_bytes()),oldFailedToolEntryUnchanged=True,allMainClassesUnchanged=1843,otherTestClassesUnchanged=1957,testClassesChanged=5,stringConstants=13,referencesReplaced=66,rawStaticBefore=18,rawStatic=5,sourceLocalContexts=3,unclassifiedRaw=2,rawStaticGateExit=1,actualSecretCount=None,fullArtifactsCoverage100=False,wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByCompletion=0,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
