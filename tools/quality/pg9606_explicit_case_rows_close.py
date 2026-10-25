"""Close a reference-candidate group, distinguishing BUG1752 rework from product acceptance."""
from pathlib import Path
import trace_group_close as close

if __name__=='__main__':
    close.run(Path(__file__),'G13_EXPLICIT_CASE_ROW_JOIN_V1',close.BASE/'PG9606-explicit-case-rows-metrics-v2',
      close.BASE/'PG9608-explicit-case-rows-public-delta-v2','268850069a86e0d36d1928e7bb1331b1d1242dec',dict(
        groupStartEstimatePp=dict(low=.5,base=3,high=8),groupCapPp=10,
        quotaBefore=dict(usedPercent=5,remainingPercent=95,resetsAt=1793513544),quotaAfter=dict(usedPercent=5,remainingPercent=95,resetsAt=1793513544),
        quotaBeforeObservedAtUTC='2026-10-25T08:35:08Z',quotaAfterObservedAtUTC='2026-10-25T08:47:19Z',sameQuotaWindow=True,observedSharedPp=0,
        attemptResult='859_UNIQUE_EXISTING_SPEC_ROW_CANDIDATES_NOT_ORACLE_QUALIFICATION_BUG1752_V2_ALL_ROW_REPAIR_VERIFIED',
        originalPlanEngineeringDelta=dict(item='EXISTING_SPEC_ROW_REFERENCE_CANDIDATES',wholeG13Accepted=False),
        additionalDiscoveries=dict(bugs=['BUG-1752'],ykt=['YKT-1503'],unqualifiedOriginalPreserved=True),
        sourceReauthentication=dict(currentSourceUnchanged=True,oldSourceResultsTransferred=False,filePrimaryOwnersReassigned=False),
        toolConstructionAndEnvironmentRework=dict(originalPostExit=1,originalPostSuccessManifest=False,
          producerVersionAttempts=2,postVersionAttempts=2,initialV2UnusedImportLintFailureBeforeExecution=1,
          changedSourceDocRefRows=3618,changedSelectedSpecRows=445,exclusivePp=None),
        technicalMeasurementDelta=dict(newSourceOwnerCandidates=0,sourceRows=956,javaPaths=1789,registered=1781,unregisteredTest=8,
          ordinaryMethodDeclarations=5622,corpusSpecDocuments=1188,uniqueSourceDocRefCandidates=44,uniqueGlobalCandidates=815,
          multipleSpecRowCandidates=75,explicitDocRefMismatch=13,noMatchingExplicitRow=2397,noStrictMethodNameToken=2278,
          literalEdgeVectors=13,additionalDocRefVectors=8,metadataCounterexamples=8,productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,formalAccepted=0),
        sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1948_G13ExplicitCaseRows_v2結果・未確定範囲.md'],
        tokenMeasurementIds=['2e3fbe42791b022a785829af9df9bf88fa88e888626a102f20c4cfb182b844a1'],
        nextCommand='9608 publicdelta/save-push; make BUG1752 fix commit concrete, then source-explicit method/oracle review or other permitted PGPT'),[
        ('PG9602-explicit-case-row-candidates-v2/manifest.json','f4fa3e3fe68ef3343c20a7e8cbc8c128918f32cb10bad3b9634a90efe587d3ba'),
        ('PG9604-explicit-case-row-post-v2/manifest.json','24a6202625e1e76c6f070254d630330525438f34bb3a915ed4d9778563c08092'),
        ('PG9604-explicit-case-row-post-v2/correction-post.safe.json','28a911908a04dc287fef9b390703e42e6df99de8e8498e0c634ebc887c1d6ca8')])
