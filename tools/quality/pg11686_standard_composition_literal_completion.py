"""Current original26 tests and exact source/byte/counter/context/trace bindings, not whole acceptance."""
import datetime as dt
import platform
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind

SOURCE='5a16139a752e2404cd6c26504760f4568ac413fd'
OUT=data.BASE/'PG11686-standard-composition-literal-completion-v1'
PINS={
 'normal':('PG11674-standard-composition-literal-six-compile-v1','15a6eeb057afdb021d0403af21625b84664c7df00c9da343954cfe02762a4ce1'),
 'host':('PG11676-standard-composition-literal-host-v1','0b1d596e787572a815067ee1abaf91b5ef18f7b0c89a26c0a6fd58dfa46b570b'),
 'post':('PG11680-standard-composition-literal-post-v1','d70ecaf62d1eea0b4f28d2a989819429032ccf30328687113d34cc0bb75457f6'),
 'context':('PG11681-standard-composition-owner-context-v1','f95d9c351fa88d09670621a26d29bd918851b1e05c733a30db40ffffbd38d225'),
 'contextPost':('PG11683-standard-composition-owner-context-post-v1','85d75233029ef6a6149dc2539dd90c73af5e4e40e1472f9cb0dddd420e69293c'),
 'trace':('PG11682-standard-composition-literal-trace-v1','13bf63d703563dadf0f6e53520e280439a73a286ff87e3a3ada300d82500b522'),
 'tracePost':('PG11684-standard-composition-literal-trace-post-v1','050a1eda3c2bce3ca67206f06ea7cfb3ccb2797a2738ba58a6041ff39e62bd15')}

def main():
    invocation=capture(__file__);assert not OUT.exists();bound=bind([(data.BASE/f/'manifest.json',h) for f,h in PINS.values()],SOURCE)
    v={k:data.read_checked(data.BASE/f/'manifest.json',h) for k,(f,h) in PINS.items()};normal,host,post=(v[k] for k in ('normal','host','post'))
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    assert host['actualExit']==0 and host['observedTestExecutions']==26 and not host['oldExecUnion'] and all(s['actualExit']==0 and not s['timedOut'] for s in host['stages'])
    sp=data.BASE/'PG11678-standard-composition-literal-static-v1/manifest.json';static=data.read_checked(sp,'d8819401772f3a93f4ed5eceb2b2a7ceb7373583b393b74690f2ca1b6f5ae73e');assert static['actualExit']==1 and static['source']==SOURCE and static['reports']['pmd']['findings']==8
    measures=data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256']);totals={k:dict(missed=0,covered=0) for k in ('LINE','METHOD','CLASS','BRANCH')}
    for role,value in measures.items():
        assert role in ('api','web') and value['selectedValueFourCounters100'] and not value['wholeArtifactCoverage100']
        assert len(value['selectedValueMain'])==1
        for unit in value['selectedValueMain'].values():
            for k,c in unit['counters'].items():
                for status in totals[k]:totals[k][status]+=c[status]
    assert {k:(v['missed'],v['covered']) for k,v in totals.items()}=={'LINE':(0,39),'METHOD':(0,12),'CLASS':(0,2),'BRANCH':(0,11)}
    assert v['context']['sourceContexts']==8 and v['contextPost']['metadataNegativeVectors']==8
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2243_ApiWeb標準組立十二命名_製造単体仕様.md';result=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2244_ApiWeb標準組立十二命名_製造単体結果.md'
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,sourceChangeCommit=SOURCE,invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),boundOriginalRuns=bound,specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),relatedBugs=['BUG-1929'],relatedYkt=['YKT-1678'],tests=host['begin']['cases'],actual=dict(tests=26,suites=2,newProductTestIds=0,failures=0,errors=0,skipped=0,aborted=0),selectedMainFourCounters=totals,allMainClassesUnchanged=1843,otherTestClassesUnchanged=post['otherTestClassesUnchanged'],testClassesChanged=post['testClassesChanged'],stringConstants=12,referencesReplaced=76,rawStaticBefore=20,rawStatic=8,rawStaticGateExit=1,actualSecretCount=None,fullArtifactCoverage100=False,wholeF03Accepted=False,whole451Accepted=False,oldRuntimeReassigned=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByCompletion=0,externalActions=0));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
