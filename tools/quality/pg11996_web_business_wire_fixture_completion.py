"""Bind current8, actual24 corrections, code-debug and measured coverage gaps retained."""
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
SOURCE='a2a44baa24d05392e4e483b051eb6b3fb070af60'
OUT=data.BASE/'PG11996-web-business-wire-fixture-completion-v1'
PINS={
 'normal':('PG11984-web-business-wire-fixture-six-compile-v1','ba7eb4d008ea6968016bcc4767cdc552d294def6e13f9ac3c0e232bbe34c17f8'),
 'host':('PG11986-web-business-wire-fixture-host-v1','f254717924ae1da7300c23582b5ba45fb3165607218667ed78df3837ff3bde40'),
 'post':('PG11990-web-business-wire-fixture-post-v1','b47e5e0e6c8b4c81ca403223fe849a53d05da71cdf6e9e571d4f65b1ca677a1f'),
 'context':('PG11991-web-business-wire-owner-context-v1','d1484d9a9eea1be89de7f8635a95d7b9ca5dbdd0f72f0004492679bf728694f5'),
 'contextPost':('PG11993-web-business-wire-owner-context-post-v1','f315e72960238b60f7c6397da556bffbff796010b012c3efe887efd42bad14a6'),
 'trace':('PG11992-web-business-wire-fixture-trace-v1','66488e1c299fc1d6150a246d8f1fc0ead09c08d945f8d93c8833c060aeb8c370'),
 'tracePost':('PG11994-web-business-wire-fixture-trace-post-v1','d4a7453b5cbb0b7eeb9c2bff59954a78ad109c3a35b4bd051418f088edeb4755')}

def main():
    invocation=capture(__file__);assert not OUT.exists();bound=bind([(data.BASE/f/'manifest.json',h) for f,h in PINS.values()],SOURCE);v={k:data.read_checked(data.BASE/f/'manifest.json',h) for k,(f,h) in PINS.items()};normal,host,post=(v[k] for k in ('normal','host','post'));assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items()) and host['observedTestExecutions']==8 and not host['oldExecUnion'];assert all(s['actualExit']==0 and not s['timedOut'] for s in host['stages'])
    previous=data.read_checked(data.BASE/'PG11954-jms-proxy-fixture-six-compile-v1/manifest.json','9914ca39739520420fbad05428dbf20ef4c776998175713a838b4ca0ab1b6824');old,new=test_classes(previous),test_classes(normal);assert set(old)==set(new) and len(new)==1962;changed=[key for key in old if old[key]!=new[key]];assert len(changed)==2;detail=[]
    for role,entry in changed:
        a=parts((Path(previous['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry);b=parts((Path(normal['jars'][role]['path']).parent/'test-classes'/entry).read_bytes(),entry);detail.append(dict(module=role,entry=entry,sourceFile=b['model']['sourceFile'],beforePhysicalSha256=old[(role,entry)],physicalSha256=new[(role,entry)],rawCodeRepresentationChanged=a['rawCodeRepresentationSha256']!=b['rawCodeRepresentationSha256'],debugTablesChanged=a['debugTablesSha256']!=b['debugTablesSha256'],beforeRawCodeRepresentationSha256=a['rawCodeRepresentationSha256'],rawCodeRepresentationSha256=b['rawCodeRepresentationSha256'],beforeDebugTablesSha256=a['debugTablesSha256'],debugTablesSha256=b['debugTablesSha256']))
    assert {r['sourceFile'] for r in detail}=={'WebBusinessWireClientsTest.java'};vectors=selftest();measure=data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256']);counts={}
    for role in ('web',):
        m=measure[role];assert not m['selectedValueFourCounters100'] and not m['wholeArtifactCoverage100'];counts[role]={kind:dict(missed=sum(u['counters'][kind]['missed'] for u in m['selectedValueMain'].values()),covered=sum(u['counters'][kind]['covered'] for u in m['selectedValueMain'].values())) for kind in ('LINE','METHOD','CLASS','BRANCH')}
    assert {k:(c['missed'],c['covered']) for k,c in counts['web'].items()}==dict(LINE=(2,111),METHOD=(1,23),CLASS=(0,9),BRANCH=(5,21));static=data.read_checked(data.BASE/'PG11988-web-business-wire-fixture-static-v1/manifest.json','7b9ba51d7145d037c91de548a8ef93ef35195f381bd626cdfd91cc282b15c10e');assert static['actualExit']==1 and static['reports']['pmd']['findings']==2
    run=Path(host['begin']['testCwd']).parent;loadedraw=(run/'classload-metadata.log').read_bytes();assert data.sha(loadedraw)==host['classloadSha256'];loaded=set(re.findall(r'\[class,load\]\s+(\S+)\s+source:',loadedraw.decode()));assert not any(n.startswith(('org.postgresql.','dev.codex.schubert.nk.api.error.','dev.codex.schubert.nk.web.bootstrap.')) or 'ConnectionFactory' in n for n in loaded);closure=host['begin']['eligibilityClosureSourceHashes'];assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in closure.items());assert not list(Path(host['begin']['testCwd']).iterdir())
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2283_Web業務wire二十四是正_製造単体仕様.md';result=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2284_Web業務wire二十四是正_製造単体結果.md';verify(invocation);OUT.mkdir();data.write(OUT/'code-debug.json',dict(source=SOURCE,rows=detail,structuralReaderVectors=vectors,meaningProof='strict raw inverse40 negatives plus original12 actual PT, raw constant pool indices not semantic proof'))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,sourceChangeCommit=SOURCE,invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),boundOriginalRuns=bound,specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),relatedBugs=['BUG-1940'],relatedYkt=['YKT-1689'],tests=host['begin']['cases'],actual=dict(tests=8,suites=1,newProductTestIds=0,failures=0,errors=0,skipped=0,aborted=0),selectedMainMeasuredCounters=counts,enumDefaultFilters=True,zeroBranchCountersAreNA=True,noManualExclusions=True,eligibilityClosureSourceHashes=closure,codeDebugSha256=data.sha((OUT/'code-debug.json').read_bytes()),allMainClassesUnchanged=1843,otherTestClassesUnchanged=1960,testClassesChanged=2,stringConstants=22,referencesReplaced=119,renamedFields=2,renamedBindings=4,rawStaticBefore=26,rawStatic=2,rawStaticGateExit=1,actualSecretCount=None,fullArtifactsCoverage100=False,wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByCompletion=0,externalActions=0));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
