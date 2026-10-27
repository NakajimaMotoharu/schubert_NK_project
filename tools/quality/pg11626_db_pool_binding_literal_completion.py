"""Bind21 fixture corrections to original30 current-source tests, four Main counters and incomplete whole quality."""
import datetime as dt
import platform
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind

SOURCE='b2790ba78d8876c058dfcebf46e25805ac0bf56e'
OUT=data.BASE/'PG11626-db-pool-binding-literal-completion-v1'
PINS={
 'normal':('PG11614-db-pool-binding-literal-six-compile-v1','da1fa15da3656d99970d1bd3afe64efee9a7fe5e153d2144af2f79c69662f16f'),
 'host':('PG11616-db-pool-binding-literal-host-v1','99a7d4eff8df99df5fa0f9b697ebf87c4b6ed662aa6499bd779900c5b8f9de67'),
 'post':('PG11620-db-pool-binding-literal-post-v1','4752359ce64abacc7e6fe314c6cbb62fd20a18ef52395e65849899bc30f366f3'),
 'trace':('PG11622-db-pool-binding-literal-trace-v1','0e8c747d86054be0e261d200ca4da88de4ccb341d4a1fe9ee1d08985cdfcead6'),
 'tracePost':('PG11624-db-pool-binding-literal-trace-post-v1','6503948a97983126e3a08a0b8796f8f359c25d292b1cab3a3f68828e8de09399')}

def main():
    invocation=capture(__file__);assert not OUT.exists()
    bound=bind([(data.BASE/n/'manifest.json',h) for n,h in PINS.values()],SOURCE)
    values={k:data.read_checked(data.BASE/n/'manifest.json',h) for k,(n,h) in PINS.items()}
    normal,host,post=(values[k] for k in ('normal','host','post'))
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    assert host['actualExit']==0 and host['observedTestExecutions']==30 and not host['oldExecUnion']
    assert all(s['actualExit']==0 and not s['timedOut'] for s in host['stages'])
    static_path=data.BASE/'PG11618-db-pool-binding-literal-static-v1/manifest.json';static_sha='5a3585696589d6307496597bc5672bde35d35d71dddc2db09962b48c353bc334'
    static=data.read_checked(static_path,static_sha);assert static['actualExit']==1 and static['source']==SOURCE and static['reports']['pmd']['findings']==30
    measurement=data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256'])
    totals={kind:dict(missed=0,covered=0) for kind in ('LINE','METHOD','CLASS','BRANCH')}
    for value in measurement.values():
        assert value['selectedValueFourCounters100'] and not value['wholeArtifactCoverage100'] and value['zeroDenominatorCountersAreNA']
        for unit in value['selectedValueMain'].values():
            for kind,counter in unit['counters'].items():
                for status in ('missed','covered'):totals[kind][status]+=counter[status]
    assert {k:(v['missed'],v['covered']) for k,v in totals.items()}=={'LINE':(0,66),'METHOD':(0,16),'CLASS':(0,4),'BRANCH':(0,8)}
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2235_DBPoolBinding二十一同値命名_製造単体仕様.md'
    result=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2236_DBPoolBinding二十一同値命名_製造単体結果.md'
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),
        branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),sourceChangeCommit=SOURCE,boundOriginalRuns=bound,
        specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),
        relatedBugs=['BUG-1927'],relatedYkt=['YKT-1676'],tests=host['begin']['cases'],actual=dict(tests=30,suites=2,newProductTestIds=0,failures=0,errors=0,skipped=0,aborted=0),
        originalProducerExit=0,originalTargetJvmExit=0,expected='Unchanged manual four-getter values/order/missing vs zero/max integer/exception identity/one-attempt supplier/partial owner and bounded worker vectors',
        aggregateFourMainCounters=totals,artifactMeasurements=measurement,completeArtifactsFourCounters100=False,bindingZeroBranches='NA_NOT_100',
        rawStaticManifest=str(static_path.relative_to(data.ROOT)),rawStaticManifestSha256=static_sha,rawStaticExit=1,rawPmd=30,sourceLocalContextsReviewed=0,unclassifiedRaw=30,checkstyle=0,processingErrors=0,
        productTestsExecutedByCompletion=0,newAccepted=0,formal1964Scope53Unchanged=True,individualAccepted=17,individualTotal=190,effortPercent=None,qa051Final='HOLD',whole451Accepted=False,externalActions=0,oldRuntimeReassigned=False,
        secretScanScope='Separate explicit public delta, not wholeG07'))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
