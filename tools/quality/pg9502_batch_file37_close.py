"""Close Batch file37 metadata only, maintaining all runtime holds and frozen estimates."""
from pathlib import Path
import trace_group_close as close

if __name__=='__main__':
    close.run(Path(__file__),'G13_BATCH_FILE37_SOURCE_V1',close.BASE/'PG9502-batch-file37-metrics-v1',
      close.BASE/'PG9504-batch-file37-public-delta-v1','0e05ec12b50e8afa5a173f4562c1249b8f1e914b',dict(
        groupStartEstimatePp=dict(low=.5,base=3,high=7),groupCapPp=10,
        quotaBefore=dict(usedPercent=1,remainingPercent=99,resetsAt=1793513544),quotaAfter=dict(usedPercent=1,remainingPercent=99,resetsAt=1793513544),
        quotaBeforeObservedAtUTC='2026-10-25T06:29:26Z',quotaAfterObservedAtUTC='2026-10-25T06:31:53Z',sameQuotaWindow=True,observedSharedPp=0,
        attemptResult='37_BATCH_FILE_SOURCE_PRIMARY_RELATED_RESPONSIBILITIES_REGISTERED_REMAIN79',
        originalPlanEngineeringDelta=dict(item='EXACT_BATCH_FILE37_SOURCE_PRIMARY_RESPONSIBILITIES',wholeG13Accepted=False),
        additionalDiscoveries=dict(bugs=[],ykt=[]),
        sourceReauthentication=dict(old848CanonicalRelatedRuntimeArtifactFieldsPreserved=True,oldSourceResultsTransferred=False,currentNormalSnapshotHashesExact=True),
        toolConstructionAndEnvironmentRework=dict(producerAttempts=1,producerRetries=0,primaryMembershipPreflight=37,orchestrationJsSyntaxFailureBeforeAnyToolOperation=1,targetCompile=0,targetRuntimeInvocation=0,exclusivePp=None),
        technicalMeasurementDelta=dict(newSourceOwnerCandidates=37,sourceRows=885,javaPaths=1789,registered=1710,registeredMain=965,totalMain=965,
          registeredTest=745,totalTest=824,unregisteredTest=79,remainingMultiOwner=61,remainingNoMainCp=18,
          verifiedSourceClosure=53,independentTestClassDeclarations=113,independentMainClassDeclarations=227,independentUniqueMainSourceFiles=91,
          catalogNegatives=9,mapperNegatives=8,neighbourInvariance=37,snapshotNegatives=6,
          productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,formalAccepted=0),
        sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1927_G13BatchFile37_主関連責任結果.md'],
        tokenMeasurementIds=['93b1684670641024a8e31bffbe1b9f0e743dc8fa260cf961be4847c00b301af3'],
        nextCommand='9504 publicdelta/save-push; fresh current-window remaining>10 then remaining79 source responsibilities or independent ordinary PGPT'),[
        ('PG9494-batch-file37-source-metadata-v1/manifest.json','c106e5255ee73e9a8a4cebb9b1ea7426d7f7450f04ce51a767232840dbca939c'),
        ('PG9496-batch-file37-source-post-v1/manifest.json','a605e5d152e320db77396d02ee6044c0745786d57ad2928c0be2991be9253e70'),
        ('PG9498-batch-file37-source-join-v1/manifest.json','96770fbedea32222e1492af2b158cfa9055622a31d15486c4ac7b4033723a1a4'),
        ('PG9500-batch-file37-snapshot-post-v1/manifest.json','21584536e9199c9d4f2c17a07ddfa6c4e03bde5005a5419540d25be27f4d32ed')])
