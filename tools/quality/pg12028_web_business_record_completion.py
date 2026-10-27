"""Bind original8 plus4 actual contracts, independent vectors and directly measured nine Main counters."""
import datetime as dt
from pathlib import Path
import platform
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
from pg9978_plain_core_quality_post import test_classes
from pg11929_storage_fixture_class_metadata import parts,selftest
SOURCE='54e84fe04836dd88c3adfda5ac3f010eb591a7ee'
OUT=data.BASE/'PG12028-web-business-record-completion-v1'
PINS={
 'normal':('PG12016-web-business-record-six-compile-v1','214dca80b3e55dcddd14932b1d2e77a4f5ba48bc9e2a0521890890081292b94a'),
 'host':('PG12018-web-business-record-host-v1','83e830344ae46b8097d1ca8027c34e7d2dc7fb3596206e9da2ffe3c0308a4048'),
 'post':('PG12022-web-business-record-post-v1','c5d6237eca375bc4735b29fab91cc52ca8e57b3667d36836b0591eb73e709e17'),
 'context':('PG12023-web-business-record-owner-context-v1','4f6727e8ba7420a072ea01a4e7dd3a30b0782ac9b690810a2c3c2c87babcca13'),
 'contextPost':('PG12025-web-business-record-owner-context-post-v1','226c47f3145461e122cf49fc96a8295e9119212d56fd20719af9007f652f8d4c'),
 'trace':('PG12024-web-business-record-trace-v1','b20e91c8e05ae52ab6df7f34ed93053b7d05f324659e75e6987d7fc3c7fbc167'),
 'tracePost':('PG12026-web-business-record-trace-post-v1','11c8375862bf5b37eb85e325f6d3b4612e7be40ee408da897eede282ade73c8e')}

def main():
    invocation=capture(__file__);assert not OUT.exists();bound=bind([(data.BASE/f/'manifest.json',h) for f,h in PINS.values()],SOURCE);v={k:data.read_checked(data.BASE/f/'manifest.json',h) for k,(f,h) in PINS.items()};normal,host,post=(v[k] for k in ('normal','host','post'));assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items()) and host['observedTestExecutions']==12 and not host['oldExecUnion'];assert all(s['actualExit']==0 and not s['timedOut'] for s in host['stages'])
    plan=data.read_checked(data.BASE/'PG12012-web-business-record-oracle-plan-v1/manifest.json','c550a50234d1798bc97b34a3cee5e3cc5f57b73eead048943d87985170181aba');inverse=data.read_checked(data.BASE/'PG12014-web-business-record-source-post-v1/manifest.json','d08647673459a18664b757eab45a393a3588bb225d3d7935589aa9173f9a8a17');assert plan['actualExit']==inverse['actualExit']==0 and inverse['newMethods']==4 and inverse['metadataNegativeVectors']==12 and all(normal['begin']['inputHashes'][r['path']]==r['sha256'] for r in plan['sourceChanges']);newcases=[c for c in host['begin']['cases'] if c['method'].startswith(('wire009','wire010','wire011','wire012'))];assert len(newcases)==4 and len({c['method'] for c in newcases})==4
    previous=data.read_checked(data.BASE/'PG11984-web-business-wire-fixture-six-compile-v1/manifest.json','ba7eb4d008ea6968016bcc4767cdc552d294def6e13f9ac3c0e232bbe34c17f8');old,new=test_classes(previous),test_classes(normal);assert set(old)==set(new) and len(new)==1962;changed=[key for key in old if old[key]!=new[key]];assert len(changed)==2;detail=[]
    for role,entry in changed:
        a=parts((Path(previous['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry);b=parts((Path(normal['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry);detail.append(dict(module=role,entry=entry,sourceFile=b['model']['sourceFile'],beforePhysicalSha256=old[(role,entry)],physicalSha256=new[(role,entry)],rawCodeRepresentationChanged=a['rawCodeRepresentationSha256']!=b['rawCodeRepresentationSha256'],debugTablesChanged=a['debugTablesSha256']!=b['debugTablesSha256'],beforeRawCodeRepresentationSha256=a['rawCodeRepresentationSha256'],rawCodeRepresentationSha256=b['rawCodeRepresentationSha256'],beforeDebugTablesSha256=a['debugTablesSha256'],debugTablesSha256=b['debugTablesSha256']))
    assert {r['sourceFile'] for r in detail}=={'WebBusinessWireClientsTest.java'};vectors=selftest();measure=data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256']);counts={}
    for role in ('web',):
        m=measure[role];assert m['selectedValueFourCounters100'] and not m['wholeArtifactCoverage100'];counts[role]={kind:dict(missed=sum(u['counters'][kind]['missed'] for u in m['selectedValueMain'].values()),covered=sum(u['counters'][kind]['covered'] for u in m['selectedValueMain'].values())) for kind in ('LINE','METHOD','CLASS','BRANCH')}
    assert {k:(c['missed'],c['covered']) for k,c in counts['web'].items()}==dict(LINE=(0,113),METHOD=(0,24),CLASS=(0,9),BRANCH=(0,26));static=data.read_checked(data.BASE/'PG12020-web-business-record-static-v1/manifest.json','3bfc240dc4772cdaec9c574f9e0527fdab3d6ba89d28872161c2de5aaaf3ae3b');assert static['actualExit']==1 and static['reports']['pmd']['findings']==2
    run=Path(host['begin']['testCwd']).parent;loadedraw=(run/'classload-metadata.log').read_bytes();assert data.sha(loadedraw)==host['classloadSha256'];loaded=set(re.findall(r'\[class,load\]\s+(\S+)\s+source:',loadedraw.decode()));assert not any(n.startswith(('org.postgresql.','dev.codex.schubert.nk.api.error.','dev.codex.schubert.nk.web.bootstrap.')) or 'ConnectionFactory' in n for n in loaded);closure=host['begin']['eligibilityClosureSourceHashes'];assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in closure.items());assert not list(Path(host['begin']['testCwd']).iterdir())
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2287_Web共通wire_record境界追加PT仕様.md';result=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2288_Web共通wire_record境界追加PT結果.md';verify(invocation);OUT.mkdir();data.write(OUT/'code-debug.json',dict(source=SOURCE,rows=detail,structuralReaderVectors=vectors,meaningProof='strict raw inverse40 negatives plus original12 actual PT, raw constant pool indices not semantic proof'))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,sourceChangeCommit=SOURCE,invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),boundOriginalRuns=bound,specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),relatedBugs=[],relatedYkt=[],implementationDecision='PG-D723',tests=host['begin']['cases'],actual=dict(tests=12,suites=1,newProductTestIds=4,failures=0,errors=0,skipped=0,aborted=0),selectedMainMeasuredCounters=counts,enumDefaultFilters=True,zeroBranchCountersAreNA=True,noManualExclusions=True,eligibilityClosureSourceHashes=closure,codeDebugSha256=data.sha((OUT/'code-debug.json').read_bytes()),allMainClassesUnchanged=1843,otherTestClassesUnchanged=1960,testClassesChanged=2,originalMethodsPreserved=8,additionalMethods=4,independentGoldenVectors=3,rawStaticBefore=2,rawStatic=2,rawStaticGateExit=1,actualSecretCount=None,fullArtifactsCoverage100=False,wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByCompletion=0,externalActions=0));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
