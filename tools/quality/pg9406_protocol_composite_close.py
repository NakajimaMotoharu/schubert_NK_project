"""Explicit protocol10 primary/related source trace group, not functional PT."""
from pathlib import Path
import trace_group_close as close

if __name__=='__main__':
    close.run(Path(__file__),'G13_PROTOCOL_COMPOSITE10_EXPLICIT_V1',close.BASE/'PG9406-protocol-composite-metrics-v1',
      close.BASE/'PG9408-protocol-composite-public-delta-v1','5d9df30ac0805475e42bab45c27eace41d57c2a2',dict(
        groupStartEstimatePp=dict(low=.5,base=2,high=4),groupCapPp=10,
        quotaBefore=dict(usedPercent=65,remainingPercent=35,resetsAt=1793382075),quotaAfter=dict(usedPercent=65,remainingPercent=35,resetsAt=1793382075),
        quotaBeforeObservedAtUTC='2026-10-25T04:56:45Z',quotaAfterObservedAtUTC='2026-10-25T05:01:03Z',sameQuotaWindow=True,observedSharedPp=0,
        attemptResult='TEN_LITERAL_PROTOCOL_PRIMARY_AND_RELATED_SCOPES_REGISTERED; RUNTIME_REFLECTION_HOLD_RETAINED; REMAIN281',
        originalPlanEngineeringDelta=dict(item='EXACT_PROTOCOL10_SOURCE_PRIMARY_RELATED_RESPONSIBILITIES',wholeG13Accepted=False),
        additionalDiscoveries=dict(bugs=[],ykt=[],runtimeReasonsPreserved=True),
        sourceReauthentication=dict(old673CanonicalPreserved=True,oldSourceResultsTransferred=False,normalInputHashesExact=True),
        toolConstructionAndEnvironmentRework=dict(independentJavapTestClasses=15,subjectMainSourceFiles=8,namedDtoFixtureTypes=69,
          targetCompile=0,targetRuntimeInvocation=0,diagnosticPathFailure=1,producerRetries=0,exclusivePp=None),
        technicalMeasurementDelta=dict(newSourceOwnerCandidates=10,sourceRows=683,javaPaths=1789,registered=1508,registeredMain=965,totalMain=965,
          registeredTest=543,totalTest=824,unregisteredTest=281,catalogNegatives=7,mapperNegatives=8,neighbourInvariance=10,
          productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,formalAccepted=0),
        sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1911_G13ProtocolComposite_主関連責任十件結果.md'],
        tokenMeasurementIds=['f3e7f7312ab0cf84285949757b55d21c89f3b2066e74a924422d847c7b34d5b8'],
        nextCommand='9408 public delta/save-push; remaining281 API/Web/batch/bootstrap explicit primary-related responsibilities and independent PG/PT'),[
        ('PG9398-protocol-composite-metadata-v1/manifest.json','1f0068d0aaadee207c706383f05daf975c969386598a2a5940d30965545994d0'),
        ('PG9400-protocol-composite-post-v1/manifest.json','e4597b904e78d01633f2c0d5e8a6408b17554a32b792e9bc38e19039c9210061'),
        ('PG9402-protocol-composite-join-v1/manifest.json','6bc494ba796f9752639739ea1d6cdb811f160637dd82cd1fc0866b2943e9e985'),
        ('PG9404-protocol-composite-snapshot-post-v1/manifest.json','2fa5b29b5f1a014df9b2f456c2bd558778a095252ffa87f9840d853624ba8feb')])
