"""Same-source66 limited completion, original plan/build failures preserved outside success binding."""
from pathlib import Path
import json
import platform
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind

SOURCE='f75d2fea05a98fe40d731d1a3046a64d20bbbb65'
OUT=data.BASE/'PG12760-metric-context-completion-v1'
PINS={
 'normal':('PG12745-metric-context-six-compile-v2','e4830adef59daf5496f23b5fe72f2288757ed3d6785b87077938d29e9626983f'),
 'host':('PG12744-metric-context-host-v1','c3c41d37e0ade8e22f6c50f2424fc1e6d6ecd67cc4f5c6e5346e94fa60d45381'),
 'post':('PG12748-metric-context-post-v1','01190b958bf4c5fa867e158b1a5642f014eb57aae4df5353a01d3109cfb14486'),
 'context':('PG12750-metric-context-context-v1','4424f49ea3ed72c64cd7d2249c3759ae5012c0a36e7eca1bff9a87ddbee71ea8'),
 'contextPost':('PG12752-metric-context-context-post-v1','edbecc33de2ad980274691ba638bf147cd882904c889fb7350e7610bddd5a524'),
 'trace':('PG12754-metric-context-trace-v1','40a26a0b8151850f78e6cc0025bd8709585bab998bcbac96a94750c75ecb4c7b'),
 'tracePost':('PG12755-metric-context-trace-post-v1','e92b7a7666112a2874139f4adfc496de8635748dfc4081534a2ea4556156e01c'),
 'delta':('PG12756-current-metric-context-delta-v1','956f0c52d9abb700497ba49a32838686b1aa87c14154fc3e201835b2fb6f4964'),
 'deltaPost':('PG12758-current-metric-context-delta-post-v1','fddbd60d5b0d8db34774a1c30ec60590ac81d4d68fd1d46d89972eff61517185')}


def main():
    invocation=capture(__file__);assert not OUT.exists()
    bound=bind([(data.BASE/name/'manifest.json',digest) for name,digest in PINS.values()],SOURCE)
    v={key:data.read_checked(data.BASE/name/'manifest.json',digest) for key,(name,digest) in PINS.items()}
    n,h,p=[v[key] for key in ['normal','host','post']]
    assert n['actualExit']==n['testsExecuted']==0 and len(n['jars'])==6 and h['observedTestExecutions']==p['observedTestExecutions']==66 and not h['oldExecUnion']
    assert all(data.sha((data.ROOT/path).read_bytes())==digest for path,digest in n['begin']['inputHashes'].items())
    assert p['allMainClassesUnchanged']==1843 and p['allTestPhysical']==1962 and p['changedTestPhysical']==8 and p['otherTestPhysicalUnchanged']==1954
    expected={'api':dict(LINE=dict(missed=0,covered=76),METHOD=dict(missed=0,covered=13),CLASS=dict(missed=0,covered=1),BRANCH=dict(missed=0,covered=27)),'web':dict(LINE=dict(missed=0,covered=72),METHOD=dict(missed=0,covered=13),CLASS=dict(missed=0,covered=1),BRANCH=dict(missed=0,covered=24))}
    assert {role:row['counters'] for role,row in p['selectedContextMain'].items()}==expected
    assert set(p['completeArtifactCounters'])=={'api','web','batch','protocol','storage','bootstrap'} and not p['wholeArtifactCoverage100'] and p['forbiddenProbeHits']==0
    static=data.read_checked(data.BASE/'PG12746-metric-context-static-v1/manifest.json','6ea3560962d32afd4d0921d7c81f2ef47f101c3c7aca7bca3f0c0ab38f6b9e75')
    assert static['source']==SOURCE and static['actualExit']==1 and static['reports']['pmd']['findings']==38 and static['reports']['checkstyle']['findings']==0 and static['spotbugsSixExit']==0
    assert v['context']['sourceContexts']==38 and v['contextPost']['metadataNegativeVectors']==24 and v['contextPost']['newOwnershipContexts']==4
    assert v['tracePost']['oldRowsChangedShaOnly']==2 and v['tracePost']['allOtherPriorRowsUnchanged']==981 and v['tracePost']['wholeWbsAuditAfter']['actualExit']==1
    changes=v['trace']['currentMetricContextFixtureBinding']['sourceChanges'];assert len(changes)==2 and all(row['canonicalOwner']==row['canonicalCostOwner']=='WBS-P018-09' for row in changes)
    assert v['delta']['sourceDerivedRaw']==8475 and v['delta']['newContextClassifications']==4 and v['deltaPost']['totalPriorCorrections']==942
    plan=data.read_checked(data.BASE/'PG12743-metric-context-plan-v3/manifest.json','8f93b0e7cfe3fdcd9e6dacbd13d936cafcb335645a571815097540574c6b7dd4')
    assert plan['totalCorrections']==16 and plan['metadataNegativeVectors']==34 and plan['allMainAndOtherInputsUnchanged'] and len(plan['eligibilityClosureSourceHashes'])==38
    assert not list(Path(h['begin']['testCwd']).iterdir())
    failed_plan=data.BASE/'PG12740-metric-context-plan-failure-v1/manifest.json'
    failure=json.loads(failed_plan.read_bytes())
    assert failure['actualExit']==1 and failure['source']=='af3f0f86d295ed721f5c1b41670ef224eb1d49e3' and failure['productTestsExecuted']==0
    assert data.sha((data.ROOT/failure['entryPath']).read_bytes())==failure['entrySha256']=='95f5e768d006b081c0802a2ed52c6911d5f8d06e0aa2ab9f69e74aa781195ab4'
    failed_normal=data.read_checked(data.BASE/'PG12742-metric-context-six-compile-v1/manifest.json','e0568bf3bf71b4c3f170e2b4a7f7e6e5ac038756731074a04acb08088bf53d2d')
    assert failed_normal['actualExit']==1 and failed_normal['testsExecuted']==0 and failed_normal['source']=='f29aec6e2624e7663128c93cfd74c3e8a0798ee6' and len(failed_normal['jars'])==3
    docs={path:data.sha((data.ROOT/path).read_bytes()) for path in ['evidence/01_PT/018_NK-OPS-001/2375_MetricContext二role所有fixture是正_単体テスト仕様書.md','evidence/01_PT/018_NK-OPS-001/2376_MetricContext二role所有fixture是正_製造単体結果.md']}
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,hostOs=platform.platform(),boundOriginalRuns=bound,actual=dict(tests=66,suites=2,failures=0,errors=0,skipped=0,aborted=0,newTestIds=0),tests=h['begin']['cases'],documentHashes=docs,relatedBugs=['BUG1997','BUG1998'],relatedYkt=['YKT1745','YKT1746'],horizontalExpansionComplete=True,implementationDecision='PG-D756',canonicalOwner='WBS-P018-09',allMainClassesUnchanged=1843,changedTestPhysical=8,allOtherTestPhysicalUnchanged=1954,selectedContextMain=p['selectedContextMain'],completeArtifactCounters=p['completeArtifactCounters'],measurementSha256=p['measurementSha256'],physicalTestMetadataSha256=p['physicalTestMetadataSha256'],manualCoverageExclusionsAdded=False,wholeArtifactCoverage100=False,rawStatic=38,staticActualExit=1,sourceRawCorrections=16,sourceDerivedRaw=8475,totalCorrections=942,oldContextRebindings=34,newContextClassifications=4,actualViolationCount=None,implementedToolDefects=1,originalBuildFailures=1,productTestFailures=0,failedPlanManifestSha256=data.sha(failed_plan.read_bytes()),failedNormalManifestSha256='e0568bf3bf71b4c3f170e2b4a7f7e6e5ac038756731074a04acb08088bf53d2d',oldFailuresPromoted=False,whole451Accepted=False,wholeF03Accepted=False,newAccepted=0,formalUpdated=False,formalTests=1964,formalScopes=53,acceptedItems=17,totalItems=190,effortPercent=None,actualAllocatedPp=None,tokenN=None,tokenT=None,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
