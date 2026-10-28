"""Same-source whole24, fixture2 and three Main four-counter100; not wholeF03/451."""
import platform
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind

SOURCE='f8ad1ae16aa52db0119fefbad9e2cea6d6affe55'
OUT=data.BASE/'PG12864-monitor-sequence-completion-v1'
PINS={
 'normal':('PG12846-monitor-sequence-six-compile-v1','48d6cc8b9d01d392bdcd94c070fb9357ae774e42119324c21c6096051f2ece17'),
 'host':('PG12848-monitor-sequence-host-v1','89f4bac39fcdfe6410e3f3badbe50d03c13899241317f516133592cc2138e733'),
 'post':('PG12852-monitor-sequence-post-v1','a3297ed8bbdb614f3ffb237edb34638a45d2375eb8dab20ed852244f4e271923'),
 'context':('PG12854-monitor-sequence-context-v1','3273a1622d8a8121316e31c28821651d27b5f81db7944f4e62998d7cba75403e'),
 'contextPost':('PG12856-monitor-sequence-context-post-v1','aa4e7a66e1b83f630c11c08c2db119f54ef84e3d27853b83ffcbedea8c3ba3e7'),
 'trace':('PG12858-monitor-sequence-trace-v1','05668fb67894a11ac8226baabd546fac403ee14525a393b04cb5b8011078e6cc'),
 'tracePost':('PG12859-monitor-sequence-trace-post-v1','c6956b07c21c40abd749909ce17b803fc3a61c1b54113614efbc21e6587b8d84'),
 'delta':('PG12860-current-monitor-sequence-delta-v1','3d0e54ec1bc26a9865b7ac38fc89f527565b2359cb9ad592a6e8f1f0c1464390'),
 'deltaPost':('PG12862-current-monitor-sequence-delta-post-v1','3163d97f2edbbebe7a13141151d6d041e26906f5c17c0f25aae397a9794a27d1')}


def main():
    invocation=capture(__file__);assert not OUT.exists();bound=bind([(data.BASE/name/'manifest.json',pin) for name,pin in PINS.values()],SOURCE)
    v={key:data.read_checked(data.BASE/name/'manifest.json',pin) for key,(name,pin) in PINS.items()};n,h,p=[v[k] for k in ['normal','host','post']]
    assert n['actualExit']==n['testsExecuted']==0 and len(n['jars'])==6 and h['observedTestExecutions']==p['observedTestExecutions']==24 and not h['oldExecUnion']
    assert all(data.sha((data.ROOT/path).read_bytes())==digest for path,digest in n['begin']['inputHashes'].items())
    assert p['allMainClassesUnchanged']==1843 and p['allTestPhysical']==1962 and p['changedTestPhysical']==2 and p['otherTestPhysicalUnchanged']==1960
    expected={'ContinuousConditionWindow':(13,2,1,14),'MonitoringObservationClock':(17,2,1,4),'MonitoringPoller':(28,4,1,8)}
    assert set(p['selectedThreeMain'])==set(expected) and p['selectedThreeMainCoverage100']
    for name,values in expected.items():
        assert p['selectedThreeMain'][name]['counters']=={kind:dict(missed=0,covered=count) for kind,count in zip(['LINE','METHOD','CLASS','BRANCH'],values)}
    assert len(p['selectedMethodDetails'])==8 and all(r['missed']==0 for row in p['selectedMethodDetails'].values() for r in row['counters'].values())
    assert p['rawStatic']==17 and p['spotbugsSixExit']==p['forbiddenProbeHits']==0 and not p['wholeArtifactCoverage100']
    static=data.read_checked(data.BASE/'PG12850-monitor-sequence-static-v1/manifest.json','77ddcdcd19da753042dca663d3940012a6ef1fdfae74bf463e546a122ff8c3e3')
    assert static['source']==SOURCE and static['actualExit']==1 and static['reports']['pmd']['findings']==17 and static['reports']['checkstyle']['findings']==0 and static['spotbugsSixExit']==0 and static['stages']['spotbugs-six']['actualExit']==0
    assert v['context']['sourceContexts']==17 and v['context']['newMainContexts']==8 and v['contextPost']['metadataNegativeVectors']==24
    assert v['tracePost']['oldRowsChangedShaOnly']==2 and v['tracePost']['allOtherPriorRowsUnchanged']==981 and v['tracePost']['wholeWbsAuditAfter']['actualExit']==1
    changes=v['trace']['currentMonitorSequenceFixtureBinding']['sourceChanges'];assert len(changes)==2 and all(row['canonicalOwner']==row['canonicalCostOwner']=='WBS-P018-09' for row in changes)
    assert v['delta']['sourceDerivedRaw']==8469 and v['deltaPost']['totalPriorCorrections']==948 and v['deltaPost']['joinedContextWarnings']==3188 and v['deltaPost']['sourceReboundCurrentWholePending']==846
    plan=data.read_checked(data.BASE/'PG12844-monitor-sequence-plan-v1/manifest.json','af75aa949766cfffb5342f11bcec67fd2e61c484d60dca63b83d2d7a48715568')
    assert plan['totalCorrections']==2 and plan['metadataNegativeVectors']==10 and plan['allMainAndOtherInputsUnchanged'] and plan['originalTests']==24 and len(plan['eligibilityClosureSourceHashes'])==10 and plan['supportTestSelectedMethods']==0
    assert h['begin']['supportTestSourceHashes']==plan['supportTestSourceHashes']
    docs={path:data.sha((data.ROOT/path).read_bytes()) for path in ['evidence/01_PT/018_NK-OPS-001/2386_MonitorWindowClockPoller原24_単体テスト仕様書.md','evidence/01_PT/018_NK-OPS-001/2387_MonitorWindowClockPoller原24_製造単体結果.md']}
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,hostOs=platform.platform(),boundOriginalRuns=bound,actual=dict(tests=24,suites=3,failures=0,errors=0,skipped=0,aborted=0,newTestIds=0),tests=h['begin']['cases'],documentHashes=docs,relatedBugs=['BUG2006'],relatedYkt=['YKT1754'],horizontalExpansionCompleteWithinThisScope=True,implementationDecision='PG-D761',canonicalOwner='WBS-P018-09',allMainClassesUnchanged=1843,changedTestPhysical=2,allOtherTestPhysicalUnchanged=1960,selectedThreeMain=p['selectedThreeMain'],selectedMethodDetails=p['selectedMethodDetails'],selectedMainCoverage100=True,completeArtifactCounters=p['completeArtifactCounters'],measurementSha256=p['measurementSha256'],physicalTestMetadataSha256=p['physicalTestMetadataSha256'],manualCoverageExclusionsAdded=False,wholeArtifactCoverage100=False,rawStatic=17,sourceRawCorrections=2,sourceDerivedRaw=8469,totalCorrections=948,newMainContexts=8,historicalNullableThreadRebindings=9,actualViolationCount=None,implementedToolDefects=0,buildFailures=0,productTestFailures=0,whole451Accepted=False,wholeF03Accepted=False,newAccepted=0,formalUpdated=False,formalTests=1964,formalScopes=53,acceptedItems=17,totalItems=190,effortPercent=None,actualAllocatedPp=None,tokenN=None,tokenT=None,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
