"""Same-source38/style1 limited completion; selected Duration Main four counters100 only."""
import platform
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind

SOURCE='2baca5740741adb7c676cb85a83f15d19de01083'
OUT=data.BASE/'PG12810-api-policy-completion-v1'
PINS={
 'normal':('PG12792-api-policy-six-compile-v1','c1b8967f460264fae3194e799ed8f486711472c36b142ad28f0ae05dfd978d85'),
 'host':('PG12794-api-policy-host-v1','87b3bb03310bcfa1b7b1b4d37912308c82553bf39e7df636e3ded69c10030d51'),
 'context':('PG12800-api-policy-context-v1','d434f64a0a860a9c5fc2ab11bcbbeb2dfc91783f468585d7a515776b1904c87f'),
 'contextPost':('PG12802-api-policy-context-post-v1','668d70434fc0b258dcbc13d9237d9e761943404acfdfa7e3c14a110519954153'),
 'post':('PG12798-api-policy-post-v1','b20fd41e7bbd0ca35b2bf110b65fb6a4918da18566d3d71a6e041a45c1ba7240'),
 'trace':('PG12804-api-policy-trace-v1','f595af6aa0bb60875d61573bc6de8ff0bef98e0d8dfb5b9ab7761fff4cc7f178'),
 'tracePost':('PG12805-api-policy-trace-post-v1','15dbc1310f348747cdfe604858b1b01f63feacadf66781d17d818b3138950278'),
 'delta':('PG12806-current-api-policy-delta-v1','4dea940beb157c9538740ad41ee73ce66488ef0cab9e9d9c9a8ad8f270cf8aee'),
 'deltaPost':('PG12808-current-api-policy-delta-post-v1','603fac98230b398b7fecb2484ca70ebd974ee6bf57422f00d3d746d924621292')}


def main():
    invocation=capture(__file__);assert not OUT.exists()
    bound=bind([(data.BASE/name/'manifest.json',digest) for name,digest in PINS.values()],SOURCE)
    v={key:data.read_checked(data.BASE/name/'manifest.json',digest) for key,(name,digest) in PINS.items()}
    n,h,p=[v[key] for key in ['normal','host','post']]
    assert n['actualExit']==n['testsExecuted']==0 and len(n['jars'])==6 and h['observedTestExecutions']==p['observedTestExecutions']==38 and not h['oldExecUnion']
    assert all(data.sha((data.ROOT/path).read_bytes())==digest for path,digest in n['begin']['inputHashes'].items())
    assert p['allMainClassesUnchanged']==1843 and p['allTestPhysical']==1962 and p['changedTestPhysical']==9 and p['otherTestPhysicalUnchanged']==1953
    assert p['selectedDurationMain']['counters']==dict(LINE=dict(missed=0,covered=87),METHOD=dict(missed=0,covered=10),CLASS=dict(missed=0,covered=1),BRANCH=dict(missed=0,covered=48))
    assert p['selectedMethodDetails'] and all(row['missed']==0 for value in p['selectedMethodDetails'].values() for row in value['counters'].values())
    assert not p['wholeArtifactCoverage100'] and p['rawStatic']==2 and p['spotbugsSixExit']==0 and p['forbiddenProbeHits']==0
    assert v['tracePost']['oldRowsChangedShaOnly']==1 and v['tracePost']['allOtherPriorRowsUnchanged']==982 and v['tracePost']['wholeWbsAuditAfter']['actualExit']==1
    changes=v['trace']['currentApiPolicyFixtureBinding']['sourceChanges'];assert len(changes)==1 and changes[0]['canonicalOwner']==changes[0]['canonicalCostOwner']=='WBS-P018-09'
    assert v['delta']['sourceDerivedRaw']==8472 and v['deltaPost']['totalPriorCorrections']==945
    plan=data.read_checked(data.BASE/'PG12790-api-policy-ownership-plan-v1/manifest.json','0678f561228d431c3af13dc3a91939c13424969827d0ce0e98fe36045b3c7f56')
    assert plan['totalCorrections']==1 and plan['metadataNegativeVectors']==8 and plan['allMainAndOtherInputsUnchanged']
    docs={path:data.sha((data.ROOT/path).read_bytes()) for path in ['evidence/01_PT/018_NK-OPS-001/2381_ApiPolicy閉鎖fixture所有是正_単体テスト仕様書.md','evidence/01_PT/018_NK-OPS-001/2382_ApiPolicy閉鎖fixture所有・承認catalog接続_製造単体結果.md']}
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,hostOs=platform.platform(),boundOriginalRuns=bound,actual=dict(tests=38,suites=2,failures=0,errors=0,skipped=0,aborted=0,newTestIds=0),tests=h['begin']['cases'],documentHashes=docs,relatedBugs=['BUG2000'],relatedYkt=['YKT1748'],horizontalExpansionComplete=True,implementationDecision='PG-D759',canonicalOwner='WBS-P018-09',allMainClassesUnchanged=1843,changedTestPhysical=9,allOtherTestPhysicalUnchanged=1953,selectedDurationMain=p['selectedDurationMain'],selectedMethodDetails=p['selectedMethodDetails'],selectedMainCoverage100=True,completeArtifactCounters=p['completeArtifactCounters'],measurementSha256=p['measurementSha256'],physicalTestMetadataSha256=p['physicalTestMetadataSha256'],manualCoverageExclusionsAdded=False,wholeArtifactCoverage100=False,rawStatic=2,sourceRawCorrections=1,sourceDerivedRaw=8472,totalCorrections=945,actualViolationCount=None,implementedToolDefects=0,productTestFailures=0,pendingCoverage=[],whole451Accepted=False,wholeF03Accepted=False,newAccepted=0,formalUpdated=False,formalTests=1964,formalScopes=53,acceptedItems=17,totalItems=190,effortPercent=None,actualAllocatedPp=None,tokenN=None,tokenT=None,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
