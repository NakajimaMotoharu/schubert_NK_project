"""Close five fixture support responsibilities, separating graph/byte checks from product PT."""
from pathlib import Path
import trace_group_close as close

if __name__=='__main__':
    close.run(Path(__file__),'G13_FIXTURE_CONSUMER5_SOURCE_V1',close.BASE/'PG9538-fixture-consumer5-metrics-v1',
      close.BASE/'PG9540-fixture-consumer5-public-delta-v1','07045e0ba619b876f08d8d73202b60978c86dcf9',dict(
        groupStartEstimatePp=dict(low=.5,base=2,high=5),groupCapPp=10,
        quotaBefore=dict(usedPercent=2,remainingPercent=98,resetsAt=1793513544),quotaAfter=dict(usedPercent=2,remainingPercent=98,resetsAt=1793513544),
        quotaBeforeObservedAtUTC='2026-10-25T06:43:30Z',quotaAfterObservedAtUTC='2026-10-25T06:46:16Z',sameQuotaWindow=True,observedSharedPp=0,
        attemptResult='5_ZERO_MAIN_FIXTURES_WITH_ALL_DIRECT_CONSUMERS_SAME_KNOWN_OWNER_REGISTERED_REMAIN15',
        originalPlanEngineeringDelta=dict(item='EXACT_SINGLE_CONSUMER_OWNER_FIXTURE5_RESPONSIBILITIES_NOT_MAIN_CP',wholeG13Accepted=False),
        additionalDiscoveries=dict(bugs=[],ykt=[]),
        sourceReauthentication=dict(old944CanonicalRelatedRuntimeArtifactFieldsPreserved=True,oldSourceResultsTransferred=False,currentNormalSnapshotHashesExact=True),
        toolConstructionAndEnvironmentRework=dict(producerAttempts=1,producerRetries=0,targetCompile=0,targetRuntimeInvocation=0,exclusivePp=None),
        technicalMeasurementDelta=dict(newSourceOwnerCandidates=5,sourceRows=949,javaPaths=1789,registered=1774,registeredMain=965,totalMain=965,
          registeredTest=809,totalTest=824,unregisteredTest=15,remainingMultiOwner=2,remainingNoMainCpUnregistered=13,
          verifiedFixtureSources=5,verifiedConsumerSources=7,independentlyParsedTestClassFiles=1910,consumerOwnerVectors=5,
          catalogNegatives=11,mapperNegatives=8,neighbourInvariance=5,snapshotNegatives=6,
          productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,formalAccepted=0),
        sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1933_G13FixtureConsumer5_単一担当根拠結果.md'],
        tokenMeasurementIds=['e1db0df391b6dfaa77f0d0e94e4e76989c1435b72634a10f4ba7619b27726b8c'],
        nextCommand='9540 publicdelta/save-push; fresh current-window remaining>10 then remaining15 responsibility roots or independent ordinary PGPT'),[
        ('PG9530-fixture-consumer5-source-metadata-v1/manifest.json','8442076f79987ef37da29f49b1c46c496e41141aa3f84042c28266dd323aae4a'),
        ('PG9532-fixture-consumer5-source-post-v1/manifest.json','47eec05441e10730714bc835502afe653dce15881b71557a717050bffab2cd2b'),
        ('PG9534-fixture-consumer5-source-join-v1/manifest.json','69d5360bb5d7fb9f8e9eef09ca7427ecb24f01acfa3c682a5eb9bc41033a62e8'),
        ('PG9536-fixture-consumer5-snapshot-post-v1/manifest.json','6921dc3796ff6abd91a5cfd7da616470d3127003148ca1306b02320fd18c4c1e')])
