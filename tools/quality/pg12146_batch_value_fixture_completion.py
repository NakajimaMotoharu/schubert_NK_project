"""Bind actual4 Batch pure values, enum5 measured miss0, inverse30, raw1, host-only operation isolation and canonical trace."""
from pathlib import Path
import datetime as dt
import platform
import re
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
from pg9978_plain_core_quality_post import test_classes
from pg9906_user_query_oracle_source_post import jar_classes
from pg11929_storage_fixture_class_metadata import parts,selftest
SOURCE='8a229695c0ea503ebac8761993665242eeba0107'
OUT=data.BASE/'PG12146-batch-value-fixture-completion-v1'
PINS={'normal': ('PG12134-batch-value-fixture-six-compile-v1', '6894ef3e885fbe1d4995e5809fd82dc16fa88b0a3ccb02613c120370fdf56bb9'), 'host': ('PG12137-batch-value-fixture-host-v2', '6d36cec96c35f98711f9f6e4ac9debe5e6f67160bb9a640e41c1a9209cb0ae67'), 'post': ('PG12145-batch-value-fixture-post-v2', '3ce8bd128c33539f9ef8eb6b953d37e550e54c64be6a7b98d914e460d6633de2'), 'context': ('PG12141-batch-value-fixture-context-v1', 'f7de8c789c6e84d9663b892c5646561e981b3cdda626321565f45b994f684da6'), 'contextPost': ('PG12143-batch-value-fixture-context-post-v1', 'b1ba08a8aff7c90d790484d1331ab06dccabbf9ab75828e953825b51d5c701e5'), 'trace': ('PG12142-batch-value-fixture-trace-v1', '95182aa0540dc507d795ad23a7ac7ade2226a1d8fc1cb7c43fc79c895db08abc'), 'tracePost': ('PG12144-batch-value-fixture-trace-post-v1', '90cc05579fbd5133a5946296983e4033c60eb550147fadd9387bbc63992ee9a1')}
def main():
    invocation=capture(__file__);assert not OUT.exists();bound=bind([(data.BASE/f/'manifest.json',h) for f,h in PINS.values()],SOURCE)
    v={k:data.read_checked(data.BASE/f/'manifest.json',h) for k,(f,h) in PINS.items()};normal,host,post=(v[k] for k in ('normal','host','post'))
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    assert host['observedTestExecutions']==4 and not host['oldExecUnion'] and all(s['actualExit']==0 and not s['timedOut'] for s in host['stages'])
    previous=data.read_checked(data.BASE/'PG12104-authz-fixture-six-compile-v1/manifest.json','1cffddad23dd78451013a1bb325a7e84682d733fb80d57f3205279d12d9774f9')
    assert jar_classes(previous)==jar_classes(normal) and len(jar_classes(normal))==1843
    old,new=test_classes(previous),test_classes(normal);assert set(old)==set(new) and len(new)==1962
    changed=[key for key in old if old[key]!=new[key]];assert len(changed)==3;details=[]
    for role,entry in changed:
        a=parts((Path(previous['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        b=parts((Path(normal['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry)
        details.append(dict(module=role,entry=entry,sourceFile=b['model']['sourceFile'],beforePhysicalSha256=old[(role,entry)],physicalSha256=new[(role,entry)],beforeRawCodeRepresentationSha256=a['rawCodeRepresentationSha256'],rawCodeRepresentationSha256=b['rawCodeRepresentationSha256'],beforeDebugTablesSha256=a['debugTablesSha256'],debugTablesSha256=b['debugTablesSha256']))
    assert {r['sourceFile'] for r in details}=={'EnumValueCatalogCompatibilityTest.java','ArtemisDetailedValuesTest.java'}
    vectors=selftest();measure=data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256'])['batch']
    counts={kind:dict(missed=sum(u['counters'][kind]['missed'] for u in measure['selectedValueMain'].values()),covered=sum(u['counters'][kind]['covered'] for u in measure['selectedValueMain'].values())) for kind in ('LINE','METHOD','CLASS','BRANCH')}
    assert measure['selectedValueFourCounters100'] and not measure['wholeArtifactCoverage100'] and {k:v['covered'] for k,v in counts.items()}==dict(LINE=64,METHOD=20,CLASS=5,BRANCH=4) and all(c['missed']==0 for c in counts.values())
    static=data.read_checked(data.BASE/'PG12139-batch-value-fixture-static-v2/manifest.json','5511be09a7cb8e0f986d5a510a428a93d0b66d8bad813bb75d5b7193513a6a18');assert static['actualExit']==1 and static['reports']['pmd']['findings']==1
    failure=data.BASE/PINS['host'][0]/'prior-failures.safe.json';f=json.loads(failure.read_bytes());entries=[r for r in f['failures'] if r.get('entry')]
    assert len(f['failures'])==4 and len(entries)==3 and all(t['bodyExit']==1 and data.sha((data.ROOT/t['entry']).read_bytes())==t['entrySha256'] for t in entries) and not f['platformRefusal'] and f['successfulProductTestsReexecuted']==f['normalBuildsReexecuted']==f['successfulStaticRunsReexecuted']==0
    assert {t['entrySha256'] for t in entries}=={'a7320b616f608667e1e3554df314cae5b6fae1604c2d3fc855b3c048a9b90547','9dbb7430301101a370b5bd57fb278d06a5bcf533c7ddff622126eca3c903cefb','9bdf111667c7acebec0951f0066c9ee69e6ed0dde813a6c929e7649d521ee5ad'}
    old=data.read_checked(data.BASE/'PG12136-batch-value-fixture-host-v1/manifest.json','9606a0db949ba9902cd3595b58fbaac985917208c32eb6f72c4af0e20d7fcf8a');assert old['actualExit']==1 and old['observedTestExecutions']==0
    assert len(host['begin']['requiredClassDefinitions'])==2 and all(p==[host['begin']['moduleJars']['batch']] for p in host['begin']['requiredClassDefinitions'].values()) and post['metadataNegativeVectors']==6 and static['exactSourcePathSelectionVectors']==4
    assert measure['operationIsolationInstructionsCovered']==0 and len(measure['operationIsolationMethods'])==178 and measure['completeClasses']==645 and measure['analyzedClasses']==644 and measure['nonExecutablePackageMetadata']==1
    assert v['contextPost']['metadataNegativeVectors']==10 and v['context']['sourceContexts']==1
    inverse=data.read_checked(data.BASE/'PG12132-batch-value-fixture-source-post-v1/manifest.json','8518f2bfae999441da38c66745979eba016b54906220cbbcffbdfeecec5407bf');assert inverse['metadataNegativeVectors']==30
    run=Path(host['begin']['testCwd']).parent;loadedraw=(run/'classload-metadata.log').read_bytes();assert data.sha(loadedraw)==host['classloadSha256']
    loaded=set(re.findall(r'\[class,load\]\s+(\S+)\s+source:',loadedraw.decode()));assert not any((n.startswith('dev.codex.schubert.nk.') and not n.startswith('dev.codex.schubert.nk.batch.')) or n.startswith('org.postgresql.') for n in loaded)
    assert not list(Path(host['begin']['testCwd']).iterdir());closure=host['begin']['eligibilityClosureSourceHashes'];assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in closure.items())
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2299_Batch純値十二是正_製造単体仕様.md';result=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2300_Batch純値十二是正_製造単体結果.md'
    verify(invocation);OUT.mkdir();data.write(OUT/'code-debug.json',dict(source=SOURCE,rows=details,structuralReaderVectors=vectors,meaningProof='strict original raw inverse30 vectors plus actual4; opaque CP index representation is not standalone semantic proof'))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,sourceChangeCommit=SOURCE,invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),boundOriginalRuns=bound,specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),relatedBugs=['BUG-1948','BUG-1949','BUG-1950','BUG-1951','BUG-1952'],relatedYkt=['YKT-1697','YKT-1698','YKT-1699','YKT-1700','YKT-1701'],implementationDecision='PG-D727',tests=host['begin']['cases'],actual=dict(tests=4,suites=2,newProductTestIds=0,failures=0,errors=0,skipped=0,aborted=0),selectedMainMeasuredCounters=counts,defaultJacocoFilters=True,zeroBranchCountersAreNA=True,noManualExclusions=True,eligibilityClosureSourceHashes=closure,codeDebugSha256=data.sha((OUT/'code-debug.json').read_bytes()),priorToolFailureRecordSha256=data.sha(failure.read_bytes()),failedToolEntryUnchanged=True,allMainClassesUnchanged=1843,otherTestClassesUnchanged=1959,testClassesChanged=3,stringConstants=12,referencesReplaced=59,rawStaticBefore=13,rawStatic=1,rawStaticGateExit=1,actualSecretCount=None,fullArtifactsCoverage100=False,wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByCompletion=0,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
