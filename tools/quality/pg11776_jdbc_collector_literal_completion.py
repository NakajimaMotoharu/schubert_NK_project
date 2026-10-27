"""Current original16 tests and exact source/byte/counter/context/trace bindings, not whole acceptance."""
import datetime as dt
import platform
import subprocess
import re
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind

SOURCE='21daf2722f9b280ec005b1b971300774a1d3716f'
OUT=data.BASE/'PG11776-jdbc-collector-literal-completion-v1'
PINS={
 'normal':('PG11764-jdbc-collector-literal-six-compile-v1','a47324817b02678e07f4b83fdd7450ac1f58bb3aef28c910bdd05cddc2df20f0'),
 'host':('PG11766-jdbc-collector-literal-host-v1','d5565981b616135c0d08d6cc686245143ad405c89c0cb020ba834101bba2ed0d'),
 'post':('PG11770-jdbc-collector-literal-post-v1','bc29e89b6700df09f1f7e76bc8939fd556dfe7187cddc8cedc4274ab15eb1411'),
 'context':('PG11771-jdbc-collector-owner-context-v1','64a2ab92fd7052a20b648757f326d1fdacc6d42bdc9c930d314b492a379abef1'),
 'contextPost':('PG11773-jdbc-collector-owner-context-post-v1','e2dba97dfdd1195e72f2abd48bacf56887e6820766711c9bdfa98159269f8cb1'),
 'trace':('PG11772-jdbc-collector-literal-trace-v1','3a81588ff2bc82ed6d67b49a97856a08de85c5d291aed089db4e5238f4d36514'),
 'tracePost':('PG11774-jdbc-collector-literal-trace-post-v1','7ea27bb743c7fd023838c6d1bb05da3060a1593b4a1bbd803805e60d2971e8f8')}

def main():
    invocation=capture(__file__);assert not OUT.exists();bound=bind([(data.BASE/f/'manifest.json',h) for f,h in PINS.values()],SOURCE)
    v={k:data.read_checked(data.BASE/f/'manifest.json',h) for k,(f,h) in PINS.items()};normal,host,post=(v[k] for k in ('normal','host','post'))
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    assert host['actualExit']==0 and host['observedTestExecutions']==16 and not host['oldExecUnion'] and all(s['actualExit']==0 and not s['timedOut'] for s in host['stages'])
    sp=data.BASE/'PG11768-jdbc-collector-literal-static-v1/manifest.json';static=data.read_checked(sp,'1fb16cae2dcaf613917f2a8bd4abce746130911ecf3525ab45b66c00748b3c68');assert static['actualExit']==1 and static['source']==SOURCE and static['reports']['pmd']['findings']==12
    measures=data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256']);totals={k:dict(missed=0,covered=0) for k in ('LINE','METHOD','CLASS','BRANCH')}
    for role,value in measures.items():
        assert role=='api' and value['selectedValueFourCounters100'] and not value['wholeArtifactCoverage100']
        assert len(value['selectedValueMain'])==2
        for unit in value['selectedValueMain'].values():
            for k,c in unit['counters'].items():
                for status in totals[k]:totals[k][status]+=c[status]
    assert {k:(v['missed'],v['covered']) for k,v in totals.items()}=={'LINE':(0,38),'METHOD':(0,6),'CLASS':(0,2),'BRANCH':(0,4)}
    assert v['context']['sourceContexts']==12 and v['contextPost']['metadataNegativeVectors']==8
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2255_JdbcCollector同値十四是正_製造単体仕様.md';result=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2256_JdbcCollector同値十四是正_製造単体結果.md'
    closure=host['begin']['eligibilityClosureSourceHashes'];assert len(closure)==9 and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in closure.items())
    run=Path(host['begin']['testCwd']).parent;raw=(run/'classload-metadata.log').read_bytes();assert data.sha(raw)==host['classloadSha256'];loaded=set(re.findall(r'\[class,load\]\s+(\S+)\s+source:',raw.decode()))
    fixtures={'dev.codex.schubert.nk.api.monitoring.AsyncJobCountRepositoryTest$Fixture','dev.codex.schubert.nk.api.monitoring.OutboxObservationRepositoryTest$Fixture'}
    assert fixtures<=loaded and not any(n.startswith(('dev.codex.schubert.nk.api.error.','dev.codex.schubert.nk.web.bootstrap.','org.postgresql.','org.apache.activemq.')) for n in loaded)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,sourceChangeCommit=SOURCE,invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),boundOriginalRuns=bound,specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),relatedBugs=['BUG-1932'],relatedYkt=['YKT-1681'],tests=host['begin']['cases'],actual=dict(tests=16,suites=2,newProductTestIds=0,failures=0,errors=0,skipped=0,aborted=0),selectedMainFourCounters=totals,eligibilityClosureSourceHashes=closure,strictMemoryFixtureClassesLoaded=sorted(fixtures),heldErrorBootstrapClassesLoaded=0,allMainClassesUnchanged=1843,otherTestClassesUnchanged=post['otherTestClassesUnchanged'],testClassesChanged=post['testClassesChanged'],stringConstants=13,referencesReplaced=98,extractedPrefixAssignments=1,rawStaticBefore=26,rawStatic=12,rawStaticGateExit=1,actualSecretCount=None,fullApiArtifactCoverage100=False,webArtifactMeasured=False,wholeF03Accepted=False,whole451Accepted=False,oldRuntimeReassigned=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByCompletion=0,externalActions=0));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
