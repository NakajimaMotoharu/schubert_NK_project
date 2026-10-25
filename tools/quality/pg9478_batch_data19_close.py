"""Close Batch19 metadata group, separating tool correction and unknown exclusive cost."""
from pathlib import Path
import trace_group_close as close

if __name__=='__main__':
    close.run(Path(__file__),'G13_BATCH_DATA19_SOURCE_V1',close.BASE/'PG9478-batch-data19-metrics-v1',
      close.BASE/'PG9480-batch-data19-public-delta-v1','91d1ab3f4d4e664a274d92020cfa51c869631bc3',dict(
        groupStartEstimatePp=dict(low=.5,base=2,high=6),groupCapPp=10,
        quotaBefore=dict(usedPercent=0,remainingPercent=100,resetsAt=1793513544),quotaAfter=dict(usedPercent=1,remainingPercent=99,resetsAt=1793513544),
        quotaBeforeObservedAtUTC=None,quotaAfterObservedAtUTC='2026-10-25T06:24:06Z',sameQuotaWindow=True,observedSharedPp=1,
        quotaBeforeTimeCorrection='1922_PARENTHETICAL_TIME_NOT_MEASURED_DO_NOT_USE_START_EXACT_TIME_NULL',
        attemptResult='19_BATCH_DATA_PRIMARY_RELATED_SOURCE_RESPONSIBILITIES_REGISTERED_REMAIN138; BUG1751_TOOL_SCOPE_VERIFIED',
        originalPlanEngineeringDelta=dict(item='EXACT_BATCH_DATA19_SOURCE_PRIMARY_RESPONSIBILITIES',wholeG13Accepted=False),
        additionalDiscoveries=dict(bugs=['BUG-1751'],ykt=['YKT-1502'],productDefectDiscovered=False),
        sourceReauthentication=dict(old807CanonicalRelatedRuntimeArtifactFieldsPreserved=True,oldSourceResultsTransferred=False,currentNormalSnapshotHashesExact=True),
        toolConstructionAndEnvironmentRework=dict(producerAttempts=2,producerRetries=1,originalFailureCommit='5af3ead97',closeImportMissingPyflakesEnvironmentAttempts=1,targetCompile=0,targetRuntimeInvocation=0,exclusivePp=None),
        technicalMeasurementDelta=dict(newSourceOwnerCandidates=19,sourceRows=826,javaPaths=1789,registered=1651,registeredMain=965,totalMain=965,
          registeredTest=686,totalTest=824,unregisteredTest=138,remainingMultiOwner=120,remainingNoMainCp=18,
          verifiedSourceClosure=23,independentTestClassDeclarations=41,independentMainClassDeclarations=109,independentUniqueMainSourceFiles=50,
          catalogNegatives=9,mapperNegatives=8,neighbourInvariance=19,snapshotNegatives=6,
          productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,formalAccepted=0),
        sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1923_G13BatchData19_主関連責任結果.md'],
        tokenMeasurementIds=['3b0f1c9dd410b084f3b2c7529e4589aaf05ef101b40fd69b6ae24fe9c6dd7dab'],
        nextCommand='9480 publicdelta/save-push; fresh current-window remaining>10 then remaining138 source responsibilities or independent ordinary PGPT'),[
        ('PG9470-batch-data19-source-metadata-v2/manifest.json','03280b63db32bcc34f068ae109bff7c770bb08c63f44e16edce1020a16c2fb0f'),
        ('PG9472-batch-data19-source-post-v1/manifest.json','5957f49f6ebc509b4358e1d1ed9521d1c4980aa649fd0ca39da1fe7a22f6b5fe'),
        ('PG9474-batch-data19-source-join-v1/manifest.json','916f308c85f4b0465f2ef54bfe64b2bbb1529ecf57235a521fe3a67c9422e32c'),
        ('PG9476-batch-data19-snapshot-post-v1/manifest.json','0bdcb3ecd6a6b497fe2dd5db64db142540dccdf1ef9167163cc89d389abbdbe4')])
