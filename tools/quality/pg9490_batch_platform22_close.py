"""Close Batch platform22 metadata, separate all runtime PT/coverage and exclusive cost."""
from pathlib import Path
import trace_group_close as close

if __name__=='__main__':
    close.run(Path(__file__),'G13_BATCH_PLATFORM22_SOURCE_V1',close.BASE/'PG9490-batch-platform22-metrics-v1',
      close.BASE/'PG9492-batch-platform22-public-delta-v1','f63190509e4433d508656fb56e9bc53c7a91e88d',dict(
        groupStartEstimatePp=dict(low=.5,base=2,high=6),groupCapPp=10,
        quotaBefore=dict(usedPercent=1,remainingPercent=99,resetsAt=1793513544),quotaAfter=dict(usedPercent=1,remainingPercent=99,resetsAt=1793513544),
        quotaBeforeObservedAtUTC='2026-10-25T06:26:14Z',quotaAfterObservedAtUTC='2026-10-25T06:28:13Z',sameQuotaWindow=True,observedSharedPp=0,
        attemptResult='22_BATCH_PLATFORM_SOURCE_PRIMARY_RELATED_RESPONSIBILITIES_REGISTERED_REMAIN116',
        originalPlanEngineeringDelta=dict(item='EXACT_BATCH_PLATFORM22_SOURCE_PRIMARY_RESPONSIBILITIES',wholeG13Accepted=False),
        additionalDiscoveries=dict(bugs=[],ykt=[]),
        sourceReauthentication=dict(old826CanonicalRelatedRuntimeArtifactFieldsPreserved=True,oldSourceResultsTransferred=False,currentNormalSnapshotHashesExact=True),
        toolConstructionAndEnvironmentRework=dict(producerAttempts=1,producerRetries=0,primaryMembershipPreflight=22,targetCompile=0,targetRuntimeInvocation=0,exclusivePp=None),
        technicalMeasurementDelta=dict(newSourceOwnerCandidates=22,sourceRows=848,javaPaths=1789,registered=1673,registeredMain=965,totalMain=965,
          registeredTest=708,totalTest=824,unregisteredTest=116,remainingMultiOwner=98,remainingNoMainCp=18,
          verifiedSourceClosure=30,independentTestClassDeclarations=85,independentMainClassDeclarations=123,independentUniqueMainSourceFiles=39,
          catalogNegatives=9,mapperNegatives=8,neighbourInvariance=22,snapshotNegatives=6,
          productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,formalAccepted=0),
        sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1925_G13BatchPlatform22_主関連責任結果.md'],
        tokenMeasurementIds=['db8b60ae217c0cfef4fd2191eb31b66fc592e9602438be5cc8164c28d88e2661'],
        nextCommand='9492 publicdelta/save-push; fresh current-window remaining>10 then remaining116 source responsibilities or independent ordinary PGPT'),[
        ('PG9482-batch-platform22-source-metadata-v1/manifest.json','5b1ae75f2003e104021422da9c16ab93d944434b68cc600bf1a897f407787318'),
        ('PG9484-batch-platform22-source-post-v1/manifest.json','8d463a2ce2a9dd4a4e677604372d689b527641df5bd950fe07fd6b69050418be'),
        ('PG9486-batch-platform22-source-join-v1/manifest.json','960c0986edd66ef7626d8d752497bf3a49700ed3e68019db1d3ac31b708ff405'),
        ('PG9488-batch-platform22-snapshot-post-v1/manifest.json','66bf7c4d9b8a2de42478858f3cbeddf443f4d04259a164ba71044f8944b94aeb')])
