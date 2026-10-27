"""Current original16 tests and exact source/byte/counter/context/trace bindings, not whole acceptance."""
import datetime as dt
import platform
import subprocess
import re
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind

SOURCE='264dc69591876147d76c19082cb69658cfe03dd8'
OUT=data.BASE/'PG11906-session-json-fixture-completion-v1'
PINS={
 'normal':('PG11894-session-json-fixture-six-compile-v1','3cc0fa3b71e348b8d5821b1269e616a69999c0c5467d6f7bb38c9b3cf69830e0'),
 'host':('PG11896-session-json-fixture-host-v1','16c268b9a665056032da2b0a69fb3001692e88812022ef13c24f30fdce057e39'),
 'post':('PG11900-session-json-fixture-post-v1','66153a5517f24a764afb9405ea3ad93b31cc1e8f99bd0f276535d723c40ff9d0'),
 'context':('PG11901-session-json-owner-context-v1','bed3fc58d5eb27a5c30ca955caa7617f50bf36d3710b5fad401f76f7c92140da'),
 'contextPost':('PG11903-session-json-owner-context-post-v1','4073735d7018916a738d9bae1b7409f011c27ba9f2e551c21638978dad5d3999'),
 'trace':('PG11902-session-json-fixture-trace-v1','00e6893f9199cadc22404ad98cffcc76a339230838318ed86140a66deaa4505a'),
 'tracePost':('PG11904-session-json-fixture-trace-post-v1','afee2cfd44d82ae3a56d6347d919a447d6c3cff1c30053373482532243cfa84c')}

def main():
    invocation=capture(__file__);assert not OUT.exists();bound=bind([(data.BASE/f/'manifest.json',h) for f,h in PINS.values()],SOURCE)
    v={k:data.read_checked(data.BASE/f/'manifest.json',h) for k,(f,h) in PINS.items()};normal,host,post=(v[k] for k in ('normal','host','post'))
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    assert host['actualExit']==0 and host['observedTestExecutions']==12 and not host['oldExecUnion'] and all(s['actualExit']==0 and not s['timedOut'] for s in host['stages'])
    sp=data.BASE/'PG11898-session-json-fixture-static-v1/manifest.json';static=data.read_checked(sp,'edf4a68b01e404ff0b728a50b8520e1d0fdbdf40417333f61519e241ecfec488');assert static['actualExit']==1 and static['source']==SOURCE and static['reports']['pmd']['findings']==2
    measures=data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256']);totals={k:dict(missed=0,covered=0) for k in ('LINE','METHOD','CLASS','BRANCH')}
    for role,value in measures.items():
        assert role=='web' and value['selectedValueFourCounters100'] and not value['wholeArtifactCoverage100']
        assert len(value['selectedValueMain'])==1
        for unit in value['selectedValueMain'].values():
            for k,c in unit['counters'].items():
                for status in totals[k]:totals[k][status]+=c[status]
    assert {k:(v['missed'],v['covered']) for k,v in totals.items()}=={'LINE':(0,113),'METHOD':(0,15),'CLASS':(0,1),'BRANCH':(0,42)}
    assert v['context']['sourceContexts']==2 and v['contextPost']['metadataNegativeVectors']==8
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2271_SessionJSON七命名_製造単体仕様.md';result=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2272_SessionJSON七命名_製造単体結果.md'
    closure=host['begin']['eligibilityClosureSourceHashes'];assert len(closure)==10 and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in closure.items())
    run=Path(host['begin']['testCwd']).parent;raw=(run/'classload-metadata.log').read_bytes();assert data.sha(raw)==host['classloadSha256'];loaded=set(re.findall(r'\[class,load\]\s+(\S+)\s+source:',raw.decode()))
    assert not any(n.startswith(('dev.codex.schubert.nk.api.error.','dev.codex.schubert.nk.web.bootstrap.','org.postgresql.','org.apache.activemq.')) for n in loaded)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,sourceChangeCommit=SOURCE,invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),boundOriginalRuns=bound,specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),relatedBugs=['BUG-1936','BUG-1937'],relatedYkt=['YKT-1685','YKT-1686'],tests=host['begin']['cases'],actual=dict(tests=12,suites=2,changedMethods=7,relatedUnchangedV2Methods=5,newProductTestIds=0,failures=0,errors=0,skipped=0,aborted=0),selectedMainFourCounters=totals,eligibilityClosureSourceHashes=closure,memorySuppliedFunctionOnly=True,heldErrorBootstrapClassesLoaded=0,allMainClassesUnchanged=1843,otherTestClassesUnchanged=post['otherTestClassesUnchanged'],testClassesChanged=post['testClassesChanged'],stringConstants=6,referencesReplaced=33,readOrdinalConstants=1,rawJavaTokensRestored=3666,rawStaticBefore=9,rawStatic=2,rawStaticGateExit=1,actualSecretCount=None,apiArtifactMeasured=False,webArtifactMeasured=True,fullWebArtifactCoverage100=False,wholeF03Accepted=False,whole451Accepted=False,oldRuntimeReassigned=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByCompletion=0,externalActions=0));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
