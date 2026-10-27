"""Bind8 fatal comparisons and22 current source contexts to original30 tests, four Main counters and incomplete whole quality."""
import datetime as dt
import platform
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind

SOURCE='b4810698856cc2ae7edabb899a47aad34ef52cc2'
OUT=data.BASE/'PG11656-db-pool-binding-fatal-case-completion-v1'
PINS={
 'context':('PG11651-db-pool-binding-current-owner-context-v1','581e4415fdddde304b466767d4cebed8a249dd7c82f3a41158b804a5b1df316b'),
 'contextPost':('PG11653-db-pool-binding-current-owner-context-post-v1','a8db93c59a7d7afba60a8327589df2b9adbda7f406509b8d953967dd76299875'),
 'normal':('PG11644-db-pool-binding-fatal-case-six-compile-v1','b6ab06836da09a0be7d6337e3c3d269b030afc06efc18352b9eb1034886b77b6'),
 'host':('PG11646-db-pool-binding-fatal-case-host-v1','056a66e456e83ecdbcaffad464d50ce41d25955286457a364b188b92d43b687a'),
 'post':('PG11650-db-pool-binding-fatal-case-post-v1','824e6ae171170484a2358a9a47f1203ea3335abdd583cba4aa74d5e201baa038'),
 'trace':('PG11652-db-pool-binding-fatal-case-trace-v1','4655c47b3d9e011a9532cb2b1516c2ac3707597bd7a90b14b77fba2b81266f09'),
 'tracePost':('PG11654-db-pool-binding-fatal-case-trace-post-v1','7a9c65dd0fa791718202313e9e70a7dd1b1fb761806af66093ba3a5732dc9550')}

def main():
    invocation=capture(__file__);assert not OUT.exists()
    bound=bind([(data.BASE/n/'manifest.json',h) for n,h in PINS.values()],SOURCE)
    values={k:data.read_checked(data.BASE/n/'manifest.json',h) for k,(n,h) in PINS.items()}
    normal,host,post=(values[k] for k in ('normal','host','post'))
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    assert host['actualExit']==0 and host['observedTestExecutions']==30 and not host['oldExecUnion']
    assert all(s['actualExit']==0 and not s['timedOut'] for s in host['stages'])
    static_path=data.BASE/'PG11648-db-pool-binding-fatal-case-static-v1/manifest.json';static_sha='acead561d795d044cc51826684268d6b2729f529fd86bd2bfa21688e887869c2'
    static=data.read_checked(static_path,static_sha);assert static['actualExit']==1 and static['source']==SOURCE and static['reports']['pmd']['findings']==22
    measurement=data.read_checked(data.BASE/PINS['post'][0]/'measurement.json',post['measurementSha256'])
    totals={kind:dict(missed=0,covered=0) for kind in ('LINE','METHOD','CLASS','BRANCH')}
    for value in measurement.values():
        assert value['selectedValueFourCounters100'] and not value['wholeArtifactCoverage100'] and value['zeroDenominatorCountersAreNA']
        for unit in value['selectedValueMain'].values():
            for kind,counter in unit['counters'].items():
                for status in ('missed','covered'):totals[kind][status]+=counter[status]
    assert {k:(v['missed'],v['covered']) for k,v in totals.items()}=={'LINE':(0,66),'METHOD':(0,16),'CLASS':(0,4),'BRANCH':(0,8)}
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2239_DBPoolBinding異常case八比較_製造単体仕様.md'
    result=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2240_DBPoolBinding異常case八比較_製造単体結果.md'
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,recordedUTC=dt.datetime.now(dt.timezone.utc).isoformat(),hostOs=platform.platform(),
        branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),sourceChangeCommit=SOURCE,boundOriginalRuns=bound,
        specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),resultPath=str(result.relative_to(data.ROOT)),resultSha256=data.sha(result.read_bytes()),
        relatedBugs=['BUG-1928'],relatedYkt=['YKT-1677'],tests=host['begin']['cases'],actual=dict(tests=30,suites=2,newProductTestIds=0,failures=0,errors=0,skipped=0,aborted=0),
        originalProducerExit=0,originalTargetJvmExit=0,expected='Unchanged manual four-getter values/order/missing vs zero/max integer/exception identity/one-attempt supplier/partial owner and bounded worker vectors',
        aggregateFourMainCounters=totals,artifactMeasurements=measurement,completeArtifactsFourCounters100=False,bindingZeroBranches='NA_NOT_100',
        rawStaticManifest=str(static_path.relative_to(data.ROOT)),rawStaticManifestSha256=static_sha,rawStaticExit=1,rawPmd=22,sourceLocalContextsReviewed=22,currentWholePendingRaw=22,unclassifiedRaw=0,checkstyle=0,processingErrors=0,
        productTestsExecutedByCompletion=0,newAccepted=0,formal1964Scope53Unchanged=True,individualAccepted=17,individualTotal=190,effortPercent=None,qa051Final='HOLD',whole451Accepted=False,externalActions=0,oldRuntimeReassigned=False,
        secretScanScope='Separate explicit public delta, not wholeG07'))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
