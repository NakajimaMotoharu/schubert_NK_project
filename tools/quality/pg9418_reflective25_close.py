"""Close exact25 static source responsibilities and measurement corrections, not runtime PT."""
from pathlib import Path
import trace_group_close as close

if __name__=='__main__':
    close.run(Path(__file__),'G13_REFLECTIVE25_SOURCE_ONLY_V1',close.BASE/'PG9418-reflective25-metrics-v1',
      close.BASE/'PG9420-reflective25-public-delta-v1','32750903d7c1bf9600392df5d7d6906b297ead0f',dict(
        groupStartEstimatePp=dict(low=.5,base=2,high=5),groupCapPp=10,
        quotaBefore=dict(usedPercent=66,remainingPercent=34,resetsAt=1793382075),quotaAfter=dict(usedPercent=66,remainingPercent=34,resetsAt=1793382075),
        quotaBeforeObservedAtUTC='2026-10-25T05:03:13Z',quotaAfterObservedAtUTC='2026-10-25T05:17:08Z',sameQuotaWindow=True,observedSharedPp=0,
        attemptResult='25_EXACT_STATIC_SOURCE_LABELS_REGISTERED_RUNTIME_REFLECTION_HOLDS_RETAINED; REMAIN256',
        failureIds=['BUG-1749','BUG-1750'],retryCause='FULL_PATH_SOURCE_SELECTION_REMEDY_AFTER_BASENAME_COLLISION; UNIT_LABEL_CORRECTION_WITHOUT_TOOL_REPLAY; NO_SECURITY_RETRY',
        originalPlanEngineeringDelta=dict(item='EXACT25_SOURCE_RESPONSIBILITIES_RUNTIME_UNCERTAINTY_RETAINED',wholeG13Accepted=False),
        additionalDiscoveries=dict(toolBugs=['BUG-1749','BUG-1750'],ykt=['YKT-1500','YKT-1501'],measurementCorrectionEvent='PGPT-20261008-2148'),
        sourceReauthentication=dict(old683CanonicalRelatedAndRuntimeFieldsPreserved=True,oldSourceResultsTransferred=False,normalCurrentSourceHashesExact=True),
        toolConstructionAndEnvironmentRework=dict(producerAttempts=2,failedSourceSelection=1,sourceSelectionVectors=5,measurementUnitVectors=4,
          targetCompile=0,targetRuntimeInvocation=0,exclusivePp=None),
        technicalMeasurementDelta=dict(newSourceOwnerCandidates=25,sourceRows=708,javaPaths=1789,registered=1533,registeredMain=965,totalMain=965,
          registeredTest=568,totalTest=824,unregisteredTest=256,independentTestClassMetadata=62,independentMainClassDeclarations=63,
          independentUniqueMainSourceFiles=49,verifiedSourceClosure=29,runtimeUncertaintyRetainedSources=25,
          catalogNegatives=8,mapperNegatives=8,neighbourInvariance=25,snapshotNegatives=6,
          productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,formalAccepted=0),
        sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1913_G13Reflective25_静的責任・保留維持結果.md'],
        tokenMeasurementIds=['0f5c3848055deff1cdc2b82365fa131b2c3e4ee68904afb34735e0767c87dd62'],
        nextCommand='9420 public scan/save-push; remaining205 multi-primary and51 resource-only source responsibilities then independent PG/PT'),[
        ('PG9410-reflective25-source-metadata-v2/manifest.json','3a091fd42596d8529b93c65147a7045e82824c049d5d507ca024eac08f6d8f13'),
        ('PG9412-reflective25-source-post-v1/manifest.json','3744825998125a964bcd0029d5af61fffb0f30f1afd95e05706ce7e8e1581071'),
        ('PG9413-trace-measurement-units-v1/manifest.json','65c642b762583ecd680b7bd6be7ab1b1afd59c610dfebbc2e8479b5f8166c5a0'),
        ('PG9414-reflective25-source-join-v1/manifest.json','c9d1ddfbf5a0766430221a57e837278155289d39fe5c2d64b076972345125b46'),
        ('PG9416-reflective25-snapshot-post-v1/manifest.json','b2da3eaae3ce414ce48ac84545d66355c9a3bfa76996f7d4d7beafe76158ebdb')])
