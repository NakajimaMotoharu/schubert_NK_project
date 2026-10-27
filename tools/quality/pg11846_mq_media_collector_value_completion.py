"""Current original16 tests and exact source/byte/counter/context/trace bindings, not whole acceptance."""
import datetime as dt
import platform
import subprocess
import re
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind

SOURCE='69d50093df9e655a39eadcd7a392646ff65bfbb0'
OUT=data.BASE/'PG11846-mq-media-collector-value-completion-v1'
PINS={
 'normal':('PG11834-mq-media-collector-value-six-compile-v1','878f67c2cd766901460e5a35ae4d2be7769778b3f8b775cc7fd6e03514aa561b'),
 'host':('PG11836-mq-media-collector-value-host-v1','e2911e57d15ba6dc00b7e68ffe075b4f2edb2e05e9ffadf3e2d4e72cd281016d'),
 'post':('PG11840-mq-media-collector-value-post-v1','a7e0e82cb52c1a3c4d40d0aaf9a071d6c539455b869f2fe0aebfa8df66f5de7c'),
 'context':('PG11841-mq-media-collector-owner-context-v1','a86573a6cd91408d192bf148f327295e306f5a07821518ac2b2fcccb759fa54e'),
 'contextPost':('PG11843-mq-media-collector-owner-context-post-v1','0179fd915f8964f4b36fcdb5d91db9423be8a51f6d9af2cd3502aa775ba05e44'),
 'trace':('PG11842-mq-media-collector-value-trace-v1','6375311efc5a86b41dccc4a6cfec38cdc9cd3bc4e9d4bf852e04a639d2b5c35e'),
 'tracePost':('PG11844-mq-media-collector-value-trace-post-v1','fa2537891b286f218cdc2c7a64d1b066dd23948282a12c32b1642dfc11fef2a9')}

def main():
    invocation=capture(__file__);assert not OUT.exists();bound=bind([(data.BASE/f/'manifest.json',h) for f,h in PINS.values()],SOURCE)
    v={k:data.read_checked(data.BASE/f/'manifest.json',h) for k,(f,h) in PINS.items()};normal,host,post=(v[k] for k in ('normal','host','post'))
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    assert host['actualExit']==0 and host['observedTestExecutions']==16 and not host['oldExecUnion'] and all(s['actualExit']==0 and not s['timedOut'] for s in host['stages'])
    sp=data.BASE/'PG11838-mq-media-collector-value-static-v1/manifest.json';static=data.read_checked(sp,'1c5b7a45fd5c3a1b3b3d4ab49355213784cdd36d4cb5068da46eaaeeb67d45ab');assert static['actualExit']==1 and static['source']==SOURCE and static['reports']['pmd']['findings']==20
    measures=data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256']);totals={k:dict(missed=0,covered=0) for k in ('LINE','METHOD','CLASS','BRANCH')}
    for role,value in measures.items():
        assert role in ('api','web') and value['selectedValueFourCounters100'] and not value['wholeArtifactCoverage100']
        assert len(value['selectedValueMain'])==1
        for unit in value['selectedValueMain'].values():
            for k,c in unit['counters'].items():
                for status in totals[k]:totals[k][status]+=c[status]
    assert {k:(v['missed'],v['covered']) for k,v in totals.items()}=={'LINE':(0,33),'METHOD':(0,6),'CLASS':(0,2),'BRANCH':(0,8)}
    assert v['context']['sourceContexts']==20 and v['contextPost']['metadataNegativeVectors']==9
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2263_MqMedia供給collector十一命名_製造単体仕様.md';result=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2264_MqMedia供給collector十一命名_製造単体結果.md'
    closure=host['begin']['eligibilityClosureSourceHashes'];assert len(closure)==7 and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in closure.items())
    run=Path(host['begin']['testCwd']).parent;raw=(run/'classload-metadata.log').read_bytes();assert data.sha(raw)==host['classloadSha256'];loaded=set(re.findall(r'\[class,load\]\s+(\S+)\s+source:',raw.decode()))
    assert not any(n.startswith(('dev.codex.schubert.nk.api.error.','dev.codex.schubert.nk.web.bootstrap.','org.postgresql.','org.apache.activemq.')) for n in loaded)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,sourceChangeCommit=SOURCE,invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),boundOriginalRuns=bound,specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),relatedBugs=['BUG-1934'],relatedYkt=['YKT-1683'],tests=host['begin']['cases'],actual=dict(tests=16,suites=2,newProductTestIds=0,failures=0,errors=0,skipped=0,aborted=0),selectedMainFourCounters=totals,eligibilityClosureSourceHashes=closure,memorySuppliedFunctionOnly=True,heldErrorBootstrapClassesLoaded=0,allMainClassesUnchanged=1843,otherTestClassesUnchanged=post['otherTestClassesUnchanged'],testClassesChanged=post['testClassesChanged'],stringConstants=9,referencesReplaced=67,readOrdinalConstants=2,rawStaticBefore=31,rawStatic=20,rawStaticGateExit=1,actualSecretCount=None,fullApiArtifactCoverage100=False,webArtifactMeasured=True,wholeF03Accepted=False,whole451Accepted=False,oldRuntimeReassigned=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByCompletion=0,externalActions=0));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
