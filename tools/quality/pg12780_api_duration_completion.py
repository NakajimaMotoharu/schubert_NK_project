"""Same-source24/style2 limited completion; keep six lines/one method/one branch unexecuted."""
import platform
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind

SOURCE='639bbc777593cd98d95db1b0316e8113b40b886b'
OUT=data.BASE/'PG12780-api-duration-completion-v1'
PINS={
 'normal':('PG12766-api-duration-six-compile-v1','39678a3c3b3ac634f9ee698f7acc900fa13248522829ce5338752b6bba920072'),
 'host':('PG12768-api-duration-host-v1','0eb7249eb52dd91ce58e71a06ee7b092537bc121bc4e2e014a4a003361e711ad'),
 'post':('PG12772-api-duration-post-v1','e82331f2ed803cff702ec1ae5b429b07c19d11aa5210b953a98f9de3e46e544a'),
 'trace':('PG12774-api-duration-trace-v1','a6689186e503460076c061adb2f69a50bae57a1965740a8bd08b8729b311af8b'),
 'tracePost':('PG12775-api-duration-trace-post-v1','94d8dabbbf348ae9c5e4bbf9375e4b4c85957a1365052aca153367df0bdc3357'),
 'delta':('PG12776-current-api-duration-delta-v1','77b45d8fb9676910e82774226bce893f2320e2e321012955913337bbf8242b59'),
 'deltaPost':('PG12778-current-api-duration-delta-post-v1','da710020152f1b5585d98aec3a88154088a9d582de3f1f974e2f6666283176fc')}


def main():
    invocation=capture(__file__);assert not OUT.exists()
    bound=bind([(data.BASE/name/'manifest.json',digest) for name,digest in PINS.values()],SOURCE)
    v={key:data.read_checked(data.BASE/name/'manifest.json',digest) for key,(name,digest) in PINS.items()}
    n,h,p=[v[key] for key in ['normal','host','post']]
    assert n['actualExit']==n['testsExecuted']==0 and len(n['jars'])==6 and h['observedTestExecutions']==p['observedTestExecutions']==24 and not h['oldExecUnion']
    assert all(data.sha((data.ROOT/path).read_bytes())==digest for path,digest in n['begin']['inputHashes'].items())
    assert p['allMainClassesUnchanged']==1843 and p['allTestPhysical']==1962 and p['changedTestPhysical']==9 and p['otherTestPhysicalUnchanged']==1953
    assert p['selectedDurationMain']['counters']==dict(LINE=dict(missed=6,covered=81),METHOD=dict(missed=1,covered=9),CLASS=dict(missed=0,covered=1),BRANCH=dict(missed=1,covered=47))
    assert any(name.startswith('scrapeApproved(') and value['counters']['METHOD']['missed']==1 for name,value in p['selectedMethodDetails'].items())
    assert not p['wholeArtifactCoverage100'] and p['rawStatic']==0 and p['spotbugsSixExit']==0 and p['forbiddenProbeHits']==0
    assert v['tracePost']['oldRowsChangedShaOnly']==1 and v['tracePost']['allOtherPriorRowsUnchanged']==982 and v['tracePost']['wholeWbsAuditAfter']['actualExit']==1
    changes=v['trace']['currentApiDurationFixtureBinding']['sourceChanges'];assert len(changes)==1 and changes[0]['canonicalOwner']==changes[0]['canonicalCostOwner']=='WBS-P018-09'
    assert v['delta']['sourceDerivedRaw']==8473 and v['deltaPost']['totalPriorCorrections']==944
    plan=data.read_checked(data.BASE/'PG12764-api-duration-plan-v1/manifest.json','a7410b3431bb0c3290a925dcbde0227ca2acb97311063cbe25a84c714e1853b3')
    assert plan['totalCorrections']==2 and plan['metadataNegativeVectors']==10 and plan['completeStringReferences']==19 and plan['allMainAndOtherInputsUnchanged']
    docs={path:data.sha((data.ROOT/path).read_bytes()) for path in ['evidence/01_PT/018_NK-OPS-001/2377_ApiDurationExporter全24fixture二定数是正_単体テスト仕様書.md','evidence/01_PT/018_NK-OPS-001/2378_ApiDurationExporter全24fixture二定数是正_製造単体結果.md']}
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,hostOs=platform.platform(),boundOriginalRuns=bound,actual=dict(tests=24,suites=1,failures=0,errors=0,skipped=0,aborted=0,newTestIds=0),tests=h['begin']['cases'],documentHashes=docs,relatedBugs=['BUG1999'],relatedYkt=['YKT1747'],horizontalExpansionComplete=True,implementationDecision='PG-D757',canonicalOwner='WBS-P018-09',allMainClassesUnchanged=1843,changedTestPhysical=9,allOtherTestPhysicalUnchanged=1953,selectedDurationMain=p['selectedDurationMain'],selectedMethodDetails=p['selectedMethodDetails'],selectedMainCoverage100=False,completeArtifactCounters=p['completeArtifactCounters'],measurementSha256=p['measurementSha256'],physicalTestMetadataSha256=p['physicalTestMetadataSha256'],manualCoverageExclusionsAdded=False,wholeArtifactCoverage100=False,rawStatic=0,sourceRawCorrections=2,sourceDerivedRaw=8473,totalCorrections=944,actualViolationCount=None,implementedToolDefects=0,productTestFailures=0,pendingCoverage=['scrapeApproved5L1M','encode catalog-present1L1B'],whole451Accepted=False,wholeF03Accepted=False,newAccepted=0,formalUpdated=False,formalTests=1964,formalScopes=53,acceptedItems=17,totalItems=190,effortPercent=None,actualAllocatedPp=None,tokenN=None,tokenT=None,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
