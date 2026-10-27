"""Bind same-source successful original proofs, keep static raw1 and incomplete parent criteria."""
from pathlib import Path
import platform
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from source_evidence_binding import bind

SOURCE='af3f0f86d295ed721f5c1b41670ef224eb1d49e3'
OUT=data.BASE/'PG12736-alert-threshold-completion-v1'
PINS={
 'normal':('PG12718-alert-threshold-six-compile-v1','5433fb79732be52686b99e8ec665a0ebb02752a90004cc777eedb3b4d31ba1c7'),
 'host':('PG12720-alert-threshold-host-v1','ccb4a097f17f8e40779ca3f01f3ab79a876f0c33eccb94d27c31f54661562513'),
 'post':('PG12724-alert-threshold-post-v1','29794dc297f068c62bdc0444c535810c238adb66a17c12aa701b0e677250bf4c'),
 'context':('PG12726-alert-threshold-context-v1','f6359bf01da291c5f348e690f1f0ebe2ba99e7fbfa1d0ed89fa6836396e33b47'),
 'contextPost':('PG12728-alert-threshold-context-post-v1','9b270b68bf8b92247e7e41dabed06f24b4d5bca4d15795b652674a5f3e13ca36'),
 'trace':('PG12730-alert-threshold-trace-v1','96a9450934b0b40186c01eae11e90119b1419943b8826e74aa77136da887d270'),
 'tracePost':('PG12731-alert-threshold-trace-post-v1','79200e4b015545385168f036e5a565990ae8775693434353f1de56bf7e0faf87'),
 'delta':('PG12732-current-alert-threshold-delta-v1','b7507bc466f309f45a650f75cfa5ccf39299d9ceea55b881bbb1b936acdfc80c'),
 'deltaPost':('PG12734-current-alert-threshold-delta-post-v1','bfbb8d38a58c3cc752c6ee5e470b989fe4cd9b3082c7cf85c578f82f7b4e1cdf')}


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    bound=bind([(data.BASE/name/'manifest.json',digest) for name,digest in PINS.values()],SOURCE)
    values={key:data.read_checked(data.BASE/name/'manifest.json',digest) for key,(name,digest) in PINS.items()}
    n,h,p=[values[key] for key in ['normal','host','post']]
    assert n['actualExit']==n['testsExecuted']==0 and len(n['jars'])==6 and h['observedTestExecutions']==p['observedTestExecutions']==14 and not h['oldExecUnion']
    assert all(data.sha((data.ROOT/path).read_bytes())==digest for path,digest in n['begin']['inputHashes'].items())
    assert p['allMainPhysical']==1843 and len(p['changedMainPhysical'])==1 and p['otherMainUnchanged']==1842
    assert p['allTestPhysical']==1962 and len(p['changedTestPhysical'])==1 and p['otherTestsUnchanged']==1961
    assert p['thresholdMainCounters']==dict(LINE=dict(missed=0,covered=66),METHOD=dict(missed=0,covered=21),CLASS=dict(missed=0,covered=1),BRANCH=dict(missed=0,covered=102))
    assert not p['completeBatchCoverage100'] and p['spotbugsSixExit']==0 and not list(Path(h['begin']['testCwd']).iterdir())
    static=data.read_checked(data.BASE/'PG12722-alert-threshold-static-v1/manifest.json','2cd61dcada2767e9c62b6e580d0e5e2215758471408d6e69833e9d6452996707')
    assert static['source']==SOURCE and static['actualExit']==1 and static['reports']['pmd']['findings']==4 and static['reports']['checkstyle']['findings']==0
    assert values['context']['sourceContexts']==4 and values['contextPost']['metadataNegativeVectors']==22
    assert values['tracePost']['oldRowsChangedShaOnly']==2 and values['tracePost']['allOtherPriorRowsUnchanged']==981 and values['tracePost']['wholeWbsAuditAfter']['actualExit']==1
    changes=values['trace']['currentAlertThresholdBinding']['sourceChanges']
    assert len(changes)==2 and all(row['canonicalOwner']==row['canonicalCostOwner']=='WBS-P018-09' for row in changes)
    assert values['delta']['sourceDerivedRaw']==8491 and values['deltaPost']['totalPriorCorrections']==926
    plan=data.read_checked(data.BASE/'PG12716-alert-threshold-plan-v1/manifest.json','9f59c8646f08f5df99f88b599219640d5b4aa531b3e4c8dabeb733f5ae414500')
    assert plan['metadataNegativeVectors']==9 and plan['totalCorrections']==2 and plan['allOtherInputsUnchanged']
    docs={path:data.sha((data.ROOT/path).read_bytes()) for path in ['evidence/01_PT/018_NK-OPS-001/2373_AlertThreshold上限命名・所有pool是正_単体テスト仕様書.md','evidence/01_PT/018_NK-OPS-001/2374_AlertThreshold上限命名・所有pool是正_製造単体結果.md']}
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,hostOs=platform.platform(),boundOriginalRuns=bound,actual=dict(tests=14,suites=1,failures=0,errors=0,skipped=0,aborted=0,newTestIds=0),tests=h['begin']['cases'],documentHashes=docs,relatedBugs=['BUG1996'],relatedYkt=['YKT1744'],horizontalExpansionComplete=False,pendingExpansion=['TransferCleanup real retained-root/FFM whole fixture unqualified HOLD'],implementationDecision='PG-D755',canonicalOwner='WBS-P018-09',mainPhysicalChanged=1,testPhysicalChanged=1,thresholdMainCounters=p['thresholdMainCounters'],completeBatchCounters=p['completeBatchCounters'],measurementSha256=p['measurementSha256'],manualCoverageExclusionsAdded=False,wholeArtifactCoverage100=False,rawStatic=4,staticActualExit=1,sourceRawCorrections=2,sourceDerivedRaw=8491,totalCorrections=926,oldContextRebindings=4,newContextClassifications=0,actualViolationCount=None,implementedToolDefects=0,productTestFailures=0,whole451Accepted=False,wholeF03Accepted=False,newAccepted=0,formalUpdated=False,formalTests=1964,formalScopes=53,acceptedItems=17,totalItems=190,effortPercent=None,actualAllocatedPp=None,tokenN=None,tokenT=None,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
