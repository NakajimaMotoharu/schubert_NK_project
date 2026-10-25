"""Record a declaration denominator, never claim thousands of unexecuted tests passed."""
from pathlib import Path
import trace_group_close as close

if __name__=='__main__':
    close.run(Path(__file__),'G13_CURRENT_TEST_METHOD_INVENTORY_V1',close.BASE/'PG9594-current-test-method-metrics-v1',
      close.BASE/'PG9596-current-test-method-public-delta-v1','46f627a51eaf16b825cb3ea7dff8acaadc774ecb',dict(
        groupStartEstimatePp=dict(low=.5,base=3,high=8),groupCapPp=10,
        quotaBefore=dict(usedPercent=5,remainingPercent=95,resetsAt=1793513544),quotaAfter=dict(usedPercent=5,remainingPercent=95,resetsAt=1793513544),
        quotaBeforeObservedAtUTC='2026-10-25T08:24:40Z',quotaAfterObservedAtUTC='2026-10-25T08:29:54Z',sameQuotaWindow=True,observedSharedPp=0,
        attemptResult='824_SOURCE_1910_TEST_CLASSES_5622_ORDINARY_DECLARATIONS_EXACT_BOUND_NOT_EXECUTED_REPEATED1_UNQUALIFIED',
        originalPlanEngineeringDelta=dict(item='CURRENT_METHOD_TRACE_DENOMINATOR_AND_BYTE_ANNOTATION_BINDING',wholeG13Accepted=False),
        additionalDiscoveries=dict(bugs=[],ykt=[],otherAnnotationDeclarations=1),
        sourceReauthentication=dict(currentNormalSnapshotHashesExact=True,filePrimaryOwnersReassigned=False,oldSourceResultsTransferred=False),
        toolConstructionAndEnvironmentRework=dict(producerAttempts=1,independentPostAttempts=1,helperCompilerInvocations=2,helperReadJvms=2,targetCompile=0,targetRuntimeInvocation=0,exclusivePp=None),
        technicalMeasurementDelta=dict(newSourceOwnerCandidates=0,sourceRows=956,javaPaths=1789,registered=1781,unregisteredTest=8,
          testSourceFiles=824,physicalTestClasses=1910,sourceOrdinaryDeclarations=5622,independentExactDeclarationBindings=5622,
          unmatchedKeys=0,declarationsWithFileOwner=5599,declarationsWithExistingCross23MethodTrace=23,otherTestAnnotationDeclarations=1,
          astVectors=7,classFileVectors=6,metadataCounterexamples=8,productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,formalAccepted=0),
        sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1945_G13TestMethodInventory_現source分母結果.md'],
        tokenMeasurementIds=['848abb597269f6d131c565e97cf586cace9b421c7ceab93a9568c3eed5b66501'],
        nextCommand='9596 publicdelta/save-push; explicit Program TestID/oracle joins against existing specifications, not new PT counts'),[
        ('PG9590-current-test-method-inventory-v1/manifest.json','0ecd6877f4666d4cd42d15b4af80d1a18681403766be221377bb842998906a9e'),
        ('PG9592-current-test-method-post-v1/manifest.json','d73ffe203a58ca9fab7f19f0b4baa7b2588fb25ad7e13c75c0c6411f5a719a18')])
