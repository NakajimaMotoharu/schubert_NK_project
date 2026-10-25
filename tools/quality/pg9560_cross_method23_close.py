"""Close23 existing method trace only; no file reassignment, TestID/coverage or PT inflation."""
from pathlib import Path
import trace_group_close as close

if __name__=='__main__':
    close.run(Path(__file__),'G13_CROSS_METHOD23_TRACE_V1',close.BASE/'PG9560-cross-method23-metrics-v1',
      close.BASE/'PG9562-cross-method23-public-delta-v1','a51bf765c198e2ecb3fc328356a92c13a888e1fa',dict(
        groupStartEstimatePp=dict(low=.5,base=2,high=6),groupCapPp=10,
        quotaBefore=dict(usedPercent=2,remainingPercent=98,resetsAt=1793513544),quotaAfter=dict(usedPercent=3,remainingPercent=97,resetsAt=1793513544),
        quotaBeforeObservedAtUTC='2026-10-25T07:02:26Z',quotaAfterObservedAtUTC='2026-10-25T07:10:03Z',sameQuotaWindow=True,observedSharedPp=1,
        attemptResult='23_EXISTING_TEST_METHODS_TO_26_CASE_FAMILIES_34_RELATIONS_AND_7_ACTUAL_MAIN_OWNER_ROLES_STATIC_ONLY_FILE_OWNERS_UNCHANGED',
        originalPlanEngineeringDelta=dict(item='INITIAL_CROSS_PROGRAM_METHOD_TESTID_REQUIREMENT_MAIN_ROLE_TRACE',wholeG13Accepted=False),
        additionalDiscoveries=dict(bugs=[],ykt=[]),
        sourceReauthentication=dict(filePrimaryOwnersReassigned=False,old956SourceRowsPreserved=True,oldSourceResultsTransferred=False,currentNormalSnapshotHashesExact=True),
        toolConstructionAndEnvironmentRework=dict(producerAttempts=1,producerRetries=0,helperCompilerInvocations=1,helperParseJvms=1,javapProcesses=2,targetCompile=0,targetRuntimeInvocation=0,exclusivePp=None),
        technicalMeasurementDelta=dict(newSourceOwnerCandidates=0,sourceRows=956,javaPaths=1789,registered=1781,registeredMain=965,totalMain=965,
          registeredTest=816,totalTest=824,unregisteredTest=8,existingMethodDeclarationsTraced=23,sourceFiles=2,
          existingDistinctCaseFamilies=26,methodCaseFamilyRelations=34,independentMainSubjects=7,syntaxVectors=7,
          methodMetadataCounterexamples=10,snapshotNegatives=6,productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,formalAccepted=0),
        sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1937_G13CrossMethod23_TestID・責任対応結果.md'],
        tokenMeasurementIds=['1fd233c2ce21ed35e5905b4865e5f217964865302d9b39763677202d3f1777b9'],
        nextCommand='9562 publicdelta/save-push; inspect scoped host runner and existing current-source evidence before necessary pure BorrowedJdbcFatal329 qualification or other independent ordinary PGPT'),[
        ('PG9554-cross-method23-source-ast-v1/manifest.json','1894885ded2b7d5bab5fc3ee741a8ea2bb0b1bc49665b5417c62158c01224f78'),
        ('PG9556-cross-method23-bytecode-post-v1/manifest.json','2cc03ca10c43b89096412104dc411de72e7d44a6390fb9f3c6e040e93c735fb1'),
        ('PG9558-cross-method23-snapshot-post-v1/manifest.json','3d73866a9c7027fd122824f067d6912f4ed58d3fcbab3e0b5591e40bec0d039b')])
