"""Current original56 tests and exact source/byte/counter/context/trace bindings, not whole acceptance."""
import datetime as dt
import platform
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind

SOURCE='eee3d32be87396f61f94e6013f4864330ceee4f3'
OUT=data.BASE/'PG11716-jvm-system-literal-completion-v1'
PINS={
 'normal':('PG11704-jvm-system-literal-six-compile-v1','e4715f0201f26ed2372db61d1c97e23c0c2b80fb6d7ff309053a74fb93e36e83'),
 'host':('PG11706-jvm-system-literal-host-v1','4d0ea9f465242330d41e634af31aa1fc5222e2f6f6a22a16286cce49cafe1d57'),
 'post':('PG11710-jvm-system-literal-post-v1','f537d671e637a3d80d1ef1e437cad7cc41b6e2b8f972c6bc0cdfb0859b269bfc'),
 'context':('PG11711-jvm-system-owner-context-v1','87b6809f45d7227b9ed1bb8e8deb642a3885b88c57492b319d550c3d5f96efe9'),
 'contextPost':('PG11713-jvm-system-owner-context-post-v1','19506bb83ccf33ea04fa3c595dc2b8f5aeff4741c08984d09600233eef954eb4'),
 'trace':('PG11712-jvm-system-literal-trace-v1','6e0850491a9e078bb7e7f8db5509de1c74f12a324c2f671d8f612c70f658e449'),
 'tracePost':('PG11714-jvm-system-literal-trace-post-v1','c2431ee3b40c22c526a0766013b12b2df457d96c387e5afd976f18fec238f1b5')}

def main():
    invocation=capture(__file__);assert not OUT.exists();bound=bind([(data.BASE/f/'manifest.json',h) for f,h in PINS.values()],SOURCE)
    v={k:data.read_checked(data.BASE/f/'manifest.json',h) for k,(f,h) in PINS.items()};normal,host,post=(v[k] for k in ('normal','host','post'))
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    assert host['actualExit']==0 and host['observedTestExecutions']==56 and not host['oldExecUnion'] and all(s['actualExit']==0 and not s['timedOut'] for s in host['stages'])
    sp=data.BASE/'PG11708-jvm-system-literal-static-v1/manifest.json';static=data.read_checked(sp,'1c4dfa2d0c8d054f3588ab1c4391912ac6d339c00dc2337db64670b05e8155ae');assert static['actualExit']==1 and static['source']==SOURCE and static['reports']['pmd']['findings']==16
    measures=data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256']);totals={k:dict(missed=0,covered=0) for k in ('LINE','METHOD','CLASS','BRANCH')}
    for role,value in measures.items():
        assert role in ('api','web') and value['selectedValueFourCounters100'] and not value['wholeArtifactCoverage100']
        assert len(value['selectedValueMain'])==2
        for unit in value['selectedValueMain'].values():
            for k,c in unit['counters'].items():
                for status in totals[k]:totals[k][status]+=c[status]
    assert {k:(v['missed'],v['covered']) for k,v in totals.items()}=={'LINE':(0,66),'METHOD':(0,16),'CLASS':(0,4),'BRANCH':(0,38)}
    assert v['context']['sourceContexts']==16 and v['contextPost']['metadataNegativeVectors']==8
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2247_JvmSystem同値十八是正_製造単体仕様.md';result=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2248_JvmSystem同値十八是正_製造単体結果.md'
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,sourceChangeCommit=SOURCE,invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),boundOriginalRuns=bound,specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),relatedBugs=['BUG-1930'],relatedYkt=['YKT-1679'],tests=host['begin']['cases'],actual=dict(tests=56,suites=4,newProductTestIds=0,failures=0,errors=0,skipped=0,aborted=0),selectedMainFourCounters=totals,allMainClassesUnchanged=1843,otherTestClassesUnchanged=post['otherTestClassesUnchanged'],testClassesChanged=post['testClassesChanged'],stringConstants=14,referencesReplaced=100,orderConstants=4,comparisonReferences=4,rawStaticBefore=34,rawStatic=16,rawStaticGateExit=1,actualSecretCount=None,fullArtifactCoverage100=False,wholeF03Accepted=False,whole451Accepted=False,oldRuntimeReassigned=False,formalUpdated=False,newAccepted=0,effortPercent=None,productTestsExecutedByCompletion=0,externalActions=0));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
