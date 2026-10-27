"""Bind actual8 checksum/health oracles, exact11 corrections and explicitly partial Web ready counters."""
from pathlib import Path
import datetime as dt
import platform
import ast
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
from pg9978_plain_core_quality_post import test_classes
from pg9906_user_query_oracle_source_post import jar_classes
from pg11929_storage_fixture_class_metadata import parts,selftest

SOURCE='14198cb1878ec73319511ba1067133992d335e63'
OUT=data.BASE/'PG12395-pool-batch-completion-v2'
PINS={'normal':('PG12378-pool-batch-six-compile-v1','27e5dafc18e19fb5e29edd96958a5ba2f05da01611aa12b1ca8208735eb52b75'),'host':('PG12380-pool-batch-host-v1','d12e56ad21684f4c31b690880763c69db7744be141228db54119ce0dcf71c12f'),'post':('PG12384-pool-batch-post-v1','c89e090a9e054d00206a094b29c0e41694cd87e3433f81211e1ae0048791724d'),'context':('PG12386-pool-batch-context-v1','f7c2f9ed8356a354b4c93755f783cff32d23c532a62129b7f1fcecf555e86a07'),'contextPost':('PG12388-pool-batch-context-post-v1','4add8469630e4c0325a7db3698013a3d0f1af78804526ae688e278d6185b8152'),'trace':('PG12390-pool-batch-trace-v1','b2481b73b8a2da895ef7e3eca042a82a8d0ca975bbab0eebd367da90770f63b8'),'tracePost':('PG12392-pool-batch-trace-post-v1','000041dc9a01c10f2b008f35d191ff2dbaa40513967d4e89358c93af7a7e2495')}

def explicit_reference_audit():
    names=['pg12374_pool_batch_plan.py','pg12376_pool_batch_source_post.py','pg12378_pool_batch_six_compile.py','pg12380_pool_batch_host.py','pg12382_pool_batch_static.py','pg12384_pool_batch_post.py','pg12386_pool_batch_context.py','pg12388_pool_batch_context_post.py','pg12390_pool_batch_trace.py','pg12392_pool_batch_trace_post.py','pg12394_pool_batch_completion.py','pg12396_current_pool_batch_delta.py','pg12398_current_pool_batch_delta_post.py','pg12395_pool_batch_completion_v2.py']
    rows=[];sources={}
    for name in names:
        p=data.ROOT/'tools/quality'/name;raw=p.read_bytes();sources[str(p.relative_to(data.ROOT))]=data.sha(raw)
        for node in ast.walk(ast.parse(raw)):
            if not isinstance(node,ast.Call) or not isinstance(node.func,ast.Attribute) or node.func.attr!='read_checked' or len(node.args)<2:continue
            path,pin=node.args[:2]
            if not isinstance(path,ast.BinOp) or not isinstance(path.op,ast.Div) or not isinstance(path.left,ast.Attribute) or not isinstance(path.left.value,ast.Name) or (path.left.value.id,path.left.attr)!=('data','BASE') or not isinstance(path.right,ast.Constant) or not isinstance(path.right.value,str) or not path.right.value.endswith('/manifest.json') or not isinstance(pin,ast.Constant) or not isinstance(pin.value,str):continue
            actual=data.sha((data.BASE/path.right.value).read_bytes())
            rows.append(dict(tool=name,line=node.lineno,path=path.right.value,pin=pin.value,actualSha256=actual,matches=pin.value==actual))
    bad=[r for r in rows if not r['matches']]
    assert len(bad)==1 and bad[0]['tool']=='pg12394_pool_batch_completion.py' and bad[0]['path']=='PG12352-pool-capacity-six-compile-v1/manifest.json'
    assert all(re.fullmatch('[0-9a-f]{64}',r['pin']) for r in rows)
    return dict(sources=sources,directLiteralPairs=rows,preservedKnownBadPairs=bad,dynamicOrVariableReferences='NOT_STATICALLY_RESOLVED; successful per-entry read_checked and source binding remain required',productTestsExecuted=0)

def main():
    invocation=capture(__file__);assert not OUT.exists();pin_audit=explicit_reference_audit()
    bound=bind([(data.BASE/f/'manifest.json',h) for f,h in PINS.values()],SOURCE)
    v={k:data.read_checked(data.BASE/f/'manifest.json',h) for k,(f,h) in PINS.items()};normal,host,post=(v[k] for k in ('normal','host','post'))
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    assert host['observedTestExecutions']==38 and not host['oldExecUnion'] and all(s['actualExit']==0 and not s['timedOut'] for s in host['stages'])
    previous=data.read_checked(data.BASE/'PG12352-pool-capacity-six-compile-v1/manifest.json','5b954538ef967b5ced149c9f0b4f3b11a15e88676e07c2ea56c22215e9a1e0b0')
    assert jar_classes(previous)==jar_classes(normal) and len(jar_classes(normal))==1843
    old,new=test_classes(previous),test_classes(normal);assert set(old)==set(new) and len(new)==1962
    changed=[key for key in old if old[key]!=new[key]];assert len(changed)==10;details=[]
    for role,entry in changed:
        a=parts((Path(previous['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        b=parts((Path(normal['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        details.append(dict(module=role,entry=entry,sourceFile=b['model']['sourceFile'],beforePhysicalSha256=old[(role,entry)],physicalSha256=new[(role,entry)],beforeRawCodeRepresentationSha256=a['rawCodeRepresentationSha256'],rawCodeRepresentationSha256=b['rawCodeRepresentationSha256'],beforeDebugTablesSha256=a['debugTablesSha256'],debugTablesSha256=b['debugTablesSha256']))
    assert {r['sourceFile'] for r in details}=={'DbPoolMetricCollectorTest.java','WebDbPoolMetricCollectorTest.java','TransferMetricRecorderTest.java','MonitoringRetentionConfigurationTest.java','MetricContractTest.java'}
    vectors=selftest();measure=data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256'])
    counts={role:{kind:dict(missed=sum(u['counters'][kind]['missed'] for u in m['selectedValueMain'].values()),covered=sum(u['counters'][kind]['covered'] for u in m['selectedValueMain'].values())) for kind in ('LINE','METHOD','CLASS','BRANCH')} for role,m in measure.items()}
    assert set(measure)=={'api','web','batch'} and sum(len(m['selectedValueMain']) for m in measure.values())==19
    assert all(not m['wholeArtifactCoverage100'] and not m['selectedValueFourCounters100'] for m in measure.values())
    core_stems={'DbPoolMetricCollector','WebDbPoolMetricCollector','MetricContract','TransferMetricRecorder'}
    core={p:u for m in measure.values() for p,u in m['selectedValueMain'].items() if p.rpartition('/')[2][:-6].split('$',1)[0] in core_stems}
    assert len(core)==8 and all(c['missed']==0 for u in core.values() for c in u['counters'].values())
    core_counts={k:sum(u['counters'][k]['covered'] for u in core.values()) for k in ('LINE','METHOD','CLASS','BRANCH')}
    assert core_counts==dict(LINE=132,METHOD=33,CLASS=8,BRANCH=30)
    static=data.read_checked(data.BASE/'PG12382-pool-batch-static-v1/manifest.json','ef847e28425796fadd1e804a7367c5f4fca93da901c84a8ea544838b0e277d5e');assert static['actualExit']==1 and static['reports']['pmd']['findings']==26 and all(s['processingErrors']==0 for s in static['reports'].values())
    inverse=data.read_checked(data.BASE/'PG12376-pool-batch-source-post-v1/manifest.json','adb98e35478e485d103b28109954ef8ae52fe13aacdfd9444b65feba77709739');assert inverse['metadataNegativeVectors']==42
    assert v['contextPost']['metadataNegativeVectors']==22 and v['context']['sourceContexts']==26
    assert len(host['begin']['requiredClassDefinitions'])==9
    for target,locations in host['begin']['requiredClassDefinitions'].items():
        role=target.split('/')[4];assert locations==[host['begin']['moduleJars'][role]]
    assert not list(Path(host['begin']['testCwd']).iterdir())
    closure=host['begin']['eligibilityClosureSourceHashes'];assert len(closure)==9 and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in closure.items())
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2328_供給PoolCollector・Batch監視九件_単体テスト仕様書.md';result=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2329_供給PoolCollector・Batch監視九件_製造単体結果.md'
    verify(invocation);OUT.mkdir();data.write(OUT/'code-debug.json',dict(source=SOURCE,rows=details,structuralReaderVectors=vectors,meaningProof='strict original raw inverse42 exact String vectors plus actual38; opaque CP index representation is not standalone semantic proof'))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,sourceChangeCommit=SOURCE,invocation=invocation,explicitReferenceAudit=pin_audit,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),boundOriginalRuns=bound,specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),relatedBugs=['BUG-1968'],relatedYkt=['YKT-1716'],implementationDecision='PG-D739',tests=host['begin']['cases'],actual=dict(tests=38,suites=5,newProductTestIds=0,failures=0,errors=0,skipped=0,aborted=0),selectedMainMeasuredCounters=counts,coreEightMainMeasuredCovered=core_counts,defaultJacocoFilters=True,zeroBranchCountersAreNA=True,noManualExclusions=True,eligibilityClosureSourceHashes=closure,codeDebugSha256=data.sha((OUT/'code-debug.json').read_bytes()),allMainClassesUnchanged=1843,otherTestClassesUnchanged=1952,testClassesChanged=10,stringConstants=9,referencesReplaced=73,numericConstants=0,numericReferences=0,rawDiagnosticsCorrected=9,rawStaticBefore=35,rawStatic=26,sourceLocalContexts=26,unclassifiedRaw=0,rawStaticGateExit=1,actualSecretCount=None,fullArtifactsCoverage100=False,wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByCompletion=0,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
