"""Same-source whole38, fixture2 and four Main four-counter100; not wholeF03/451."""
import platform
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind

SOURCE='105fd644e90918945607b3ac3e4962843c7762bf'
OUT=data.BASE/'PG12888-pure-health-lifecycle-completion-v1'
PINS={
 'normal':('PG12870-pure-health-lifecycle-six-compile-v1','bc906632f1a362e7d688ac472784c1e4438008421799f7fec927dad8c818b52a'),
 'host':('PG12873-pure-health-lifecycle-host-v2','629cb07806640f9e8a2ec1c35306ca1fccf1b0471e0e16bf6aab5eaadf471330'),
 'post':('PG12876-pure-health-lifecycle-post-v1','927664b9e53c777f78d399ca5448afce4e4b15c39870934a25a6529f809249d4'),
 'context':('PG12878-pure-health-lifecycle-context-v1','75365584df3268405f71f92cfd55ef22bb9c03352699882ddbe542286fe7eb69'),
 'contextPost':('PG12880-pure-health-lifecycle-context-post-v1','bafd82a00b8366ece46209969ea91baa01f9b443f0b77e70cd61db85e888b251'),
 'trace':('PG12882-pure-health-lifecycle-trace-v1','fd37cf51c79ac0962e758ed695ae583e8554052861547e430ed04383ebab8f2a'),
 'tracePost':('PG12883-pure-health-lifecycle-trace-post-v1','dd339c6e3887a18c4c1d802f03a50e524c76d0d91bbf028135208359cd6ea46c'),
 'delta':('PG12884-current-pure-health-lifecycle-delta-v1','de897d470265e666cab9be3cb22fa5e8c49e0b943b7bd573a2d07a6344fe18c2'),
 'deltaPost':('PG12886-current-pure-health-lifecycle-delta-post-v1','70dc5e987edcc4b1fb5e64fb3637468198e23415af63b0045d81ef400acfffbd')}


def main():
    invocation=capture(__file__);assert not OUT.exists();bound=bind([(data.BASE/name/'manifest.json',pin) for name,pin in PINS.values()],SOURCE)
    v={key:data.read_checked(data.BASE/name/'manifest.json',pin) for key,(name,pin) in PINS.items()};n,h,p=[v[k] for k in ['normal','host','post']]
    assert n['actualExit']==n['testsExecuted']==0 and len(n['jars'])==6 and h['observedTestExecutions']==p['observedTestExecutions']==38 and not h['oldExecUnion']
    assert all(data.sha((data.ROOT/path).read_bytes())==digest for path,digest in n['begin']['inputHashes'].items())
    assert p['allMainClassesUnchanged']==1843 and p['allTestPhysical']==1962 and p['changedTestPhysical']==2 and p['otherTestPhysicalUnchanged']==1960
    expected={'AlertLifecycle':(57,6,1,34),'TimedFilesystemMonitor':(37,3,1,14),'FilesystemHealthObservation':(11,2,1,6),'FilesystemHealthMonitor':(10,6,1,0)}
    assert set(p['selectedFourMain'])==set(expected) and p['selectedFourMainCoverage100']
    for name,values in expected.items():
        assert p['selectedFourMain'][name]['counters']=={kind:dict(missed=0,covered=count) for kind,count in zip(['LINE','METHOD','CLASS','BRANCH'],values)}
    assert len(p['selectedMethodDetails'])==17 and all(r['missed']==0 for row in p['selectedMethodDetails'].values() for r in row['counters'].values())
    assert p['rawStatic']==22 and p['spotbugsSixExit']==p['forbiddenProbeHits']==0 and not p['wholeArtifactCoverage100']
    static=data.read_checked(data.BASE/'PG12874-pure-health-lifecycle-static-v1/manifest.json','2369a8378b3be015e6ab03f034cbe38d4d4feb9d31797aa2119d13551fa2e90e')
    assert static['source']==SOURCE and static['actualExit']==1 and static['reports']['pmd']['findings']==22 and static['reports']['checkstyle']['findings']==0 and static['spotbugsSixExit']==0 and static['stages']['spotbugs-six']['actualExit']==0
    assert v['context']['sourceContexts']==22 and v['context']['newMainContexts']==5 and v['context']['newTestPrivateMonitorOracleContext']==1 and v['contextPost']['metadataNegativeVectors']==25
    assert v['tracePost']['oldRowsChangedShaOnly']==2 and v['tracePost']['allOtherPriorRowsUnchanged']==981 and v['tracePost']['wholeWbsAuditAfter']['actualExit']==1
    changes=v['trace']['currentPureHealthLifecycleFixtureBinding']['sourceChanges'];assert len(changes)==2 and all(row['canonicalOwner']==row['canonicalCostOwner']=='WBS-P018-09' for row in changes)
    assert v['delta']['sourceDerivedRaw']==8467 and v['deltaPost']['totalPriorCorrections']==950 and v['deltaPost']['joinedContextWarnings']==3194 and v['deltaPost']['sourceReboundCurrentWholePending']==866
    plan=data.read_checked(data.BASE/'PG12868-pure-health-lifecycle-plan-v1/manifest.json','e3b10e5565ac1d369b3693a5dc3c5b5c80f8022f8d29226d23c578721b64715b')
    assert plan['totalCorrections']==2 and plan['metadataNegativeVectors']==10 and plan['allMainAndOtherInputsUnchanged'] and plan['originalTests']==38 and len(plan['eligibilityClosureSourceHashes'])==12 and plan['supportTestSelectedMethods']==0
    assert h['begin']['supportTestSourceHashes']==plan['supportTestSourceHashes']
    docs={path:data.sha((data.ROOT/path).read_bytes()) for path in ['evidence/01_PT/018_NK-OPS-001/2388_PureFilesystemAlertLifecycle原38_単体テスト仕様書.md','evidence/01_PT/018_NK-OPS-001/2389_PureFilesystemAlertLifecycle原38_製造単体結果.md']}
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,hostOs=platform.platform(),boundOriginalRuns=bound,actual=dict(tests=38,suites=5,failures=0,errors=0,skipped=0,aborted=0,newTestIds=0),tests=h['begin']['cases'],documentHashes=docs,relatedBugs=['BUG2007','BUG2008'],relatedYkt=['YKT1755','YKT1756'],horizontalExpansionCompleteWithinThisScope=True,implementationDecision='PG-D762',canonicalOwner='WBS-P018-09',allMainClassesUnchanged=1843,changedTestPhysical=2,allOtherTestPhysicalUnchanged=1960,selectedFourMain=p['selectedFourMain'],selectedMethodDetails=p['selectedMethodDetails'],selectedMainCoverage100=True,completeArtifactCounters=p['completeArtifactCounters'],measurementSha256=p['measurementSha256'],physicalTestMetadataSha256=p['physicalTestMetadataSha256'],toolProvenanceLimitations=["HOST_LOADED_SOURCE_LIST_IS_CAPTURE_TIME_ONLY_LATE_LEX_NOT_ATTESTED_AT_IMPORT"],guardLexPlanCurrentCommittedSha256="dd47f8735a61ce849995633c3290a6ad047842ef3263829ce359db413778f7a0",fullToolchainQualification=False,manualCoverageExclusionsAdded=False,wholeArtifactCoverage100=False,rawStatic=22,sourceRawCorrections=2,sourceDerivedRaw=8467,totalCorrections=950,newMainContexts=5,newTestPrivateMonitorOracleContext=1,historicalThreadRebindings=16,actualViolationCount=None,implementedToolDefects=1,buildFailures=0,productTestFailures=0,whole451Accepted=False,wholeF03Accepted=False,newAccepted=0,formalUpdated=False,formalTests=1964,formalScopes=53,acceptedItems=17,totalItems=190,effortPercent=None,actualAllocatedPp=None,tokenN=None,tokenT=None,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
