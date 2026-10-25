"""Close API transaction/JMS20 source registration only; runtime PT/coverage remain unchanged."""
from pathlib import Path
import trace_group_close as close

if __name__=='__main__':
    close.run(Path(__file__),'G13_API_JMS20_SOURCE_V1',close.BASE/'PG9442-api-jms20-metrics-v1',
      close.BASE/'PG9444-api-jms20-public-delta-v1','73f4c5dc5a811c78a2183c7ff55daee7d5355ea2',dict(
        groupStartEstimatePp=dict(low=.5,base=2,high=6),groupCapPp=10,
        quotaBefore=dict(usedPercent=67,remainingPercent=33,resetsAt=1793382075),quotaAfter=dict(usedPercent=67,remainingPercent=33,resetsAt=1793382075),
        quotaBeforeObservedAtUTC='2026-10-25T05:36:16Z',quotaAfterObservedAtUTC='2026-10-25T05:43:10Z',sameQuotaWindow=True,observedSharedPp=0,
        attemptResult='API_TX3_JMS17_EXACT_SOURCE_PRIMARY_AND_RELATED_SCOPES_REGISTERED_NOT_RUNTIME_PT; REMAIN203',
        originalPlanEngineeringDelta=dict(item='EXACT_API_TRANSACTION_JMS20_PRIMARY_SOURCE_RESPONSIBILITIES',wholeG13Accepted=False),
        additionalDiscoveries=dict(bugs=[],ykt=[],namedFactoryNotAutomaticP00504=True),
        sourceReauthentication=dict(old741CanonicalRelatedRuntimeArtifactFieldsPreserved=True,oldSourceResultsTransferred=False,currentNormalSnapshotHashesExact=True),
        toolConstructionAndEnvironmentRework=dict(producerAttempts=1,producerRetries=0,targetCompile=0,targetRuntimeInvocation=0,sourceSelectionVectors=5,exclusivePp=None),
        technicalMeasurementDelta=dict(newSourceOwnerCandidates=20,sourceRows=761,javaPaths=1789,registered=1586,registeredMain=965,totalMain=965,
          registeredTest=621,totalTest=824,unregisteredTest=203,verifiedSourceClosure=25,independentTestClassDeclarations=52,
          independentMainClassDeclarations=43,independentUniqueMainSourceFiles=41,catalogNegatives=9,mapperNegatives=8,neighbourInvariance=20,snapshotNegatives=6,
          productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,formalAccepted=0),
        sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1917_G13ApiJms20_主関連責任結果.md'],
        tokenMeasurementIds=['9a23df3a19870f463712d2d6d5ea8ad204efefae55394bc2eb0c78a6a02c5898'],
        nextCommand='9444 public scan/save-push; remaining203 business composite/shared fixture source responsibilities then independent PG/PT'),[
        ('PG9434-api-jms20-source-metadata-v1/manifest.json','829cfcd34370eb408c3097295a410a528e5f390d6a052f8892ac1ba908831d61'),
        ('PG9436-api-jms20-source-post-v1/manifest.json','3ef738b8dbb2f759be25e2058257a7396a439e1274e90792094577eb97002614'),
        ('PG9438-api-jms20-source-join-v1/manifest.json','0eb6d96826969b6f605e4001e738c0f4ab802ce3f6cfbe734f2811ecdf41fd88'),
        ('PG9440-api-jms20-snapshot-post-v1/manifest.json','db06f67895f86862026ff4cc2c393f2cda047831fa048abd35bf7f5907638956')])
