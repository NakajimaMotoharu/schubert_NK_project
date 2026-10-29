"""Bounded periodic original evidence references only; no Product/coverage/VM reexecution."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import f03_main_monitor_eighty_one_trace_v2 as trace

OUT=data.BASE/'PG14106-used41-periodic-evidence-audit-v1'
BASE=('PG13956-used35-periodic-original-manifest-audit-v1','86593de60fa46eb34b7d2f85f587c3baa04d20aed1d84c3f88d5cdddb087761e')
DELTA=[
 ('PG14014-maintenance-parent-guard-whole-six-post-v1','ec2910e33c11f274908de9b2c47dde6e2e55d7df0925d6ea6d3fb25b4cb840f9',6,1),
 ('PG14094-context-hash-whole-three-post-v1','fce0833bbe6aa9026995f27d2ac264bdc70fd28099cc30e380a42cbce4f0b28e',3,1),
 ('PG14101-api-stop-budget-whole-eighteen-post-v2','3fc4a6469d7ff348981bfed1a53f42be7e102064f953d403bf00a69a9da3946c',18,1)]

def main():
    invocation=capture(__file__);assert not OUT.exists()
    base=data.read_checked(data.BASE/BASE[0]/'manifest.json',BASE[1])
    assert base['actualExit']==0 and base['source']==trace.SOURCE
    cases=[];posts=[]
    for ref in base['postReferences']:
        p=data.read_checked(data.ROOT/ref['path'],ref['sha256'])
        assert p['actualExit']==0 and p['source']==trace.SOURCE and len(p['cases'])==ref['methods']
        cases.extend((r['classname'],r['name']) for r in p['cases'])
        posts.append(dict(path=ref['path'],sha256=ref['sha256'],tests=ref['methods'],suites=ref['suites']))
    assert len(cases)==len(set(cases))==119 and len(posts)==11
    before_cases=set(cases);added=[]
    for name,pin,tests,suites in DELTA:
        p=data.read_checked(data.BASE/name/'manifest.json',pin)
        assert p['actualExit']==0 and p['source']==trace.SOURCE and p['tests']==tests and p['suites']==suites
        assert p['failures']==p['errors']==p['skipped']==p['reruns']==0
        keys={(r['classname'],r['name']) for r in p['cases']}
        assert len(keys)==tests and keys.isdisjoint(cases)
        cases.extend(sorted(keys));added.append(dict(path=str((data.BASE/name/'manifest.json').relative_to(data.ROOT)),sha256=pin,tests=tests,suites=suites))
    assert len(cases)==len(set(cases))==146 and len(set(cases)-before_cases)==27
    ids,refs,pending=trace.state_after()
    assert (len(ids),len(refs),len(pending),len(ids-refs))==(6247,3574,2713,2673)
    assert base['currentReferenceAfter']==3401 and base['unreferencedAfter']==2846
    budget=data.read_checked(data.BASE/DELTA[2][0]/'manifest.json',DELTA[2][1])
    assert budget['targetUnitFour100'] is True and budget['totals']==dict(LINE=dict(missed=0,covered=24),METHOD=dict(missed=0,covered=5),CLASS=dict(missed=0,covered=1),BRANCH=dict(missed=0,covered=12))
    hash_post=data.read_checked(data.BASE/DELTA[1][0]/'manifest.json',DELTA[1][1])
    assert hash_post['naturalZeroBranch'] is True and hash_post['targetUnitFour100'] is False
    guard=data.read_checked(data.BASE/DELTA[0][0]/'manifest.json',DELTA[0][1])
    assert guard['targetUnitFour100'] is False and guard['completeSourceCoverageMeasured'] is False and guard['unmeasuredExecutable']
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=trace.SOURCE,invocation=invocation,baselineManifestSha256=BASE[1],baselineEvent='PGPT-20261008-2931',baselineUsed=36,triggerUsed=41,currentObservedUsed=41,sharedDeltaPp=5,resetAt=1793774153,allocatedPgptPp=None,allocatedPmoPp=None,N=None,T=None,baselinePosts=posts,newPostReferences=added,originalExecCountBefore=11,originalExecCountAfter=14,uniqueMethodsBefore=119,uniqueMethodsAfter=146,newCurrentSourceMethodQualifications=27,newFunctionalTestIds=0,suiteReferencesBefore=23,suiteReferencesAfter=26,fullSourceProgramsFour100Before=9,fullSourceProgramsFour100After=10,naturalZeroBranchExtraSourcesBefore=1,naturalZeroBranchExtraSourcesAfter=2,parentGuardSourceStillPartial=True,sourceReferencesBefore=3401,sourceReferencesAfter=3574,newCurrentSourceReasonRows=173,retainedRaw=6247,priorCorrections=3194,unreferencedBefore=2846,unreferencedAfter=2673,currentWholePending=2713,productTestsExecutedByAudit=0,coverageExecReanalyzed=False,globalExecUnion=False,oldCoverageTransferred=False,newAccepted=0,acceptedCriteria=17,totalCriteria=190,formalTests=1964,formalScopes=53,formalUpdated=False,actualExternalPathDelta=0,actualExternalActions=0,mainSourceChanged=False,testSourceChanged=False,effortPercent=None,estimateRewritten=False,assessment='TECHNICAL_GAINS_BUT_NO_WHOLE_CLOSURE_COST_REMAINS_UNCALIBRATED',wholeF03Accepted=False,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
