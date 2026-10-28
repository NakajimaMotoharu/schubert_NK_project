"""Same-source whole19 and registry outer/inner four-counter100, not whole451/F03."""
import platform
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind

SOURCE='0124b5938a50f4ceea542486c336ba12146cb1b4'
OUT=data.BASE/'PG12834-exact-registry-completion-v1'
PINS={
 'normal':('PG12819-exact-registry-six-compile-v2','8a5081b03b988d4370df0c3fa45c69eeeda6d5296543a38f1e2239b0ae088f89'),
 'host':('PG12839-exact-registry-caller-host-v2','70426a057be6c8f8b53e7b52ea98f2a3e2e9269039864c73da0d6a81ad562291'),
 'post':('PG12842-exact-registry-caller-post-v1','3ba0058d651605f37b1a03293001919b431ce83471ebc14464de1a14bbe00aa3'),
 'context':('PG12824-exact-registry-context-v1','c96c20868b97aaf236ac1209719c68d5bbfe88b8a12c8babb35204b7c5806774'),
 'contextPost':('PG12826-exact-registry-context-post-v1','1ef6be7fa63772894cc8f8a540922e5a4d68805825a57145e4074649fc426bbd'),
 'trace':('PG12828-exact-registry-trace-v1','14eac4d619670517db4a0c0c411845769a1e26049c3526cd38fe2310b84fcdbb'),
 'tracePost':('PG12829-exact-registry-trace-post-v1','ba63e24197492e5e0eb2f9052147182661a60d38acde72126b96d076d013d196'),
 'delta':('PG12831-current-exact-registry-delta-v2','9aad05bffcc0861002090a5f7d655d3c3cc63527a6d06edb8371ffac978b86fa'),
 'deltaPost':('PG12832-current-exact-registry-delta-post-v1','d982ff5f7ebd2647aa18c83f6d3ddfd3c05db0c81d7b3d71cf95848fa7bd829c')}


def main():
    invocation=capture(__file__);assert not OUT.exists()
    bound=bind([(data.BASE/name/'manifest.json',pin) for name,pin in PINS.values()],SOURCE)
    v={key:data.read_checked(data.BASE/name/'manifest.json',pin) for key,(name,pin) in PINS.items()};n,h,p=[v[k] for k in ['normal','host','post']]
    assert n['actualExit']==n['testsExecuted']==0 and len(n['jars'])==6 and h['observedTestExecutions']==p['observedTestExecutions']==19 and not h['oldExecUnion']
    assert all(data.sha((data.ROOT/path).read_bytes())==digest for path,digest in n['begin']['inputHashes'].items())
    assert p['allMainClassesUnchanged']==1843 and p['allTestPhysical']==1962 and p['changedTestPhysical']==6 and p['otherTestPhysicalUnchanged']==1956
    assert p['selectedRegistryMain']['counters']==dict(LINE=dict(missed=0,covered=23),METHOD=dict(missed=0,covered=6),CLASS=dict(missed=0,covered=1),BRANCH=dict(missed=0,covered=14))
    assert p['selectedRegistryInner']['counters']==dict(LINE=dict(missed=0,covered=23),METHOD=dict(missed=0,covered=7),CLASS=dict(missed=0,covered=1),BRANCH=dict(missed=0,covered=10))
    assert len(p['selectedMethodDetails'])==13 and all(r['missed']==0 for row in p['selectedMethodDetails'].values() for r in row['counters'].values())
    assert p['rawStatic']==9 and p['spotbugsSixExit']==p['forbiddenProbeHits']==0 and not p['wholeArtifactCoverage100']
    static=data.read_checked(data.BASE/'PG12840-exact-registry-caller-static-v1/manifest.json','bc41a92bde38e75c3589339c5c4ba3540c6199061767c48aeb8bd64199b07bd5')
    assert static['source']==SOURCE and static['actualExit']==1 and static['reports']['pmd']['findings']==9 and static['reports']['checkstyle']['findings']==0 and static['spotbugsSixExit']==0
    assert not static['spotbugsSixExecutedByThisStage'] and static['reusedSameSourceSpotbugsManifestSha256']=='90c12edb90d3380de96ab28d71ac28d3445500890a49627be852eee106dd136b'
    assert v['context']['sourceContexts']==9 and v['context']['newPrivateMonitorContexts']==2 and v['contextPost']['metadataNegativeVectors']==22
    assert v['tracePost']['oldRowsChangedShaOnly']==1 and v['tracePost']['allOtherPriorRowsUnchanged']==982 and v['tracePost']['wholeWbsAuditAfter']['actualExit']==1
    changes=v['trace']['currentExactRegistryFixtureBinding']['sourceChanges'];assert len(changes)==1 and changes[0]['canonicalOwner']==changes[0]['canonicalCostOwner']=='WBS-P018-09'
    assert v['delta']['sourceDerivedRaw']==8471 and v['deltaPost']['totalPriorCorrections']==946 and v['deltaPost']['joinedContextWarnings']==3180 and v['deltaPost']['sourceReboundCurrentWholePending']==830
    plan=data.read_checked(data.BASE/'PG12817-exact-registry-plan-v3/manifest.json','88a9d3eebc46f473fdc492e5ecdd8806b380aae78701312631019e40eb41e978')
    assert plan['totalCorrections']==1 and plan['metadataNegativeVectors']==7 and plan['completeStringReferences']==6 and plan['allMainAndOtherInputsUnchanged']
    caller=data.read_checked(data.BASE/'PG12837-exact-registry-caller-plan-v1/manifest.json','b7dddb9dfdce042bc9076a45d0983f29f22a00777e8d3882c915034458bb3a01')
    assert caller['source']==SOURCE and caller['actualExit']==caller['codeChanges']==0 and caller['originalTests']==19 and not caller['normalRecompiled']
    documents={path:data.sha((data.ROOT/path).read_bytes()) for path in ['evidence/01_PT/018_NK-OPS-001/2383_ExactDurationRegistry全10・同期契約_単体テスト仕様書.md','evidence/01_PT/018_NK-OPS-001/2384_ExactDurationRegistry全10・同期契約_製造単体結果.md','evidence/01_PT/018_NK-OPS-001/2385_ExactRegistry正規caller同一exec接続_仕様追補.md']}
    failures=['PG12814-exact-registry-plan-lint-failure-v1','PG12816-exact-registry-six-compile-v1','PG12822-exact-registry-post-coverage-gap-v1','PG12838-exact-registry-caller-order-failure-v1','PG12830-exact-registry-delta-history-failure-v1']
    failure_refs={name:data.sha((data.BASE/name/'manifest.json').read_bytes()) for name in failures}
    assert all(data.read_checked(data.BASE/name/'manifest.json',pin)['actualExit']==1 for name,pin in failure_refs.items())
    partial=data.read_checked(data.BASE/'PG12823-exact-registry-partial-post-v1/manifest.json','94fd4fe7779ff5c177d996134baea03e989216f761685c56aa1f343450275319')
    assert partial['source']==SOURCE and partial['actualExit']==0 and partial['observedTestExecutions']==10 and partial['selectedRegistryMain']['counters']['BRANCH']['missed']==1
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,hostOs=platform.platform(),boundOriginalRuns=bound,actual=dict(tests=19,suites=2,failures=0,errors=0,skipped=0,aborted=0,newTestIds=0),tests=h['begin']['cases'],documentHashes=documents,historicalFailureManifestHashes=failure_refs,original10PartialPostManifestSha256='94fd4fe7779ff5c177d996134baea03e989216f761685c56aa1f343450275319',relatedBugs=['BUG2001','BUG2002','BUG2003','BUG2004','BUG2005'],relatedYkt=['YKT1749','YKT1750','YKT1751','YKT1752','YKT1753'],horizontalExpansionCompleteWithinThisScope=True,implementationDecision='PG-D760',canonicalOwner='WBS-P018-09',allMainClassesUnchanged=1843,changedTestPhysical=6,allOtherTestPhysicalUnchanged=1956,selectedRegistryMain=p['selectedRegistryMain'],selectedRegistryInner=p['selectedRegistryInner'],selectedMethodDetails=p['selectedMethodDetails'],selectedMainCoverage100=True,completeArtifactCounters=p['completeArtifactCounters'],measurementSha256=p['measurementSha256'],physicalTestMetadataSha256=p['physicalTestMetadataSha256'],manualCoverageExclusionsAdded=False,wholeArtifactCoverage100=False,rawStatic=9,sourceRawCorrections=1,sourceDerivedRaw=8471,totalCorrections=946,newPrivateMonitorContexts=2,historicalThreadMapRebindings=7,actualViolationCount=None,implementedToolDefects=3,formatBuildFailures=1,original10CoverageQualificationFailures=1,productTestFailures=0,whole451Accepted=False,wholeF03Accepted=False,newAccepted=0,formalUpdated=False,formalTests=1964,formalScopes=53,acceptedItems=17,totalItems=190,effortPercent=None,actualAllocatedPp=None,tokenN=None,tokenT=None,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
