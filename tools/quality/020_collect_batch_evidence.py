#!/usr/bin/env python3
"""PG-D-137: certify only executed batch repository PT; no process/backup completion claim."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET

from pgpt_evidence_checksums import write_scope_checksums

PAIR_CLASS = "dev.codex.schubert.nk.batch.repository.BackupStepRepositoryTest"
BATCH_TEST_COUNT = 550
EXPIRY_AUDIT_CLASS = "dev.codex.schubert.nk.batch.repository.ExpiryAuditRepositoryTest"
EXPIRY_AUDIT_METHODS = (
    "bat284StageIsInvisibleUntilCallerCommitAndKeepsExactCutoff",
    "bat285TerminalSuccessAndExactReplayCannotRewriteOldResult",
    "bat286RollbackUnknownAfterAndSameRunAttemptAreNeverGuessed",
    "bat287NullInvalidHandleAndTerminalAreRejectedWithoutMutation",
)

def validate_expiry_audit_suite(suite):
    return validate_group(suite, EXPIRY_AUDIT_CLASS, EXPIRY_AUDIT_METHODS, 284)
BATCH_RUNTIME_DEPENDENCY_CLASS = "dev.codex.schubert.nk.batch.bootstrap.BatchRuntimeDependencyTest"
BATCH_RUNTIME_DEPENDENCY_METHODS = ("bat283RuntimePostgresDriverAndScopeCanaries",)

def validate_batch_runtime_dependency_suite(suite):
    return validate_group(suite, BATCH_RUNTIME_DEPENDENCY_CLASS, BATCH_RUNTIME_DEPENDENCY_METHODS, 283)
COMPLETION_CLASS = "dev.codex.schubert.nk.batch.file.BackupBundleCompletionTest"
COMPLETION_METHODS = ("verifiedCommitAndReplay", "invalidFilesAndHandleBinding", "allReadAndDatabaseFailures", "sharedDeadlineAndInterrupt", "completionClockAndCommitUncertainty", "nullOwnershipAndFactory", "unknownFailuresAndResourceOwnership", "concurrentAndIndependentTrace")
COMPLETION_TRACES = {"PT-BAT-281-completion.txt": b"manifestSha256=bd608252091beeda64978c96a85107bd329c56f4222cb0a21c39b868af45c370\nfiles=4\nDB=1/1/0/26\nCONFIG=2/2/0/67\nend=2026-09-12T15:00:04.987654Z\nowner=SUCCESS\nnonowner=REJECTED\n"}

def validate_completion_suite(suite):
    return validate_group(suite, COMPLETION_CLASS, COMPLETION_METHODS, 274)

def validate_completion_traces(traces):
    if traces != COMPLETION_TRACES:
        raise ValueError("missing, extra or invalid independent backup completion trace")
BUNDLE_CLASS = "dev.codex.schubert.nk.batch.file.BackupBundlePublisherTest"
BUNDLE_METHODS = ("verifiedDurablePublication", "forceOrderAndRetainedInodes", "pendingContentAndMetadata", "finalManifestAndArtifactChecks", "forceSizeAndNullBoundaries", "everyIoFailure", "unknownAndCompoundFailures", "deadlineAcrossPhases", "interruptionAcrossPhases", "existingFinalAndMissingPending", "namespaceReplacement", "nullAndOwnerContracts", "concurrentPublication", "nativePortsAndFactory", "readonlyCompatibility", "independentBundleTrace")
BUNDLE_TRACES = {"PT-BAT-273-bundle.txt": b"964|bd608252091beeda64978c96a85107bd329c56f4222cb0a21c39b868af45c370\nforce=4|publish=1|sync=2\nio=301|clock=514\n"}

def validate_bundle_suite(suite):
    return validate_group(suite, BUNDLE_CLASS, BUNDLE_METHODS, 258)

def validate_bundle_traces(traces):
    if traces != BUNDLE_TRACES:
        raise ValueError("missing, extra or invalid independent bundle publication trace")

def validate_reactor(verified, run):
    if verified["runId"] != run or verified["exitCode"] != 0 or verified["modules"]["batch"]["tests"] != BATCH_TEST_COUNT:
        raise ValueError("matching verified full reactor required")

PUBLICATION_CLASS = "dev.codex.schubert.nk.batch.file.BackupManifestPublisherTest"
PUBLICATION_METHODS = ("independentGoldenPublication", "privateCreationOwnership", "rootAndChildAdmission", "metadataNullTypes", "filePermissionsAndLinks", "writeProgressBoundaries", "readbackAndIdentity", "namespaceReplacement", "collisionAndPartRetention", "everyIoFailure", "deadlineAndInterrupt", "compoundAndBufferWipe", "nullAndClosedContracts", "concurrentNoReplace", "nativeIoAndFactory", "independentPublicationTrace")
PUBLICATION_TRACES = {"PT-BAT-257-publication.txt": b"964|bd608252091beeda64978c96a85107bd329c56f4222cb0a21c39b868af45c370\ncreate=1|publish=1|sync=1\nio=79|clock=109\n"}

def validate_publication_suite(suite):
    return validate_group(suite, PUBLICATION_CLASS, PUBLICATION_METHODS, 242)

def validate_publication_traces(traces):
    if traces != PUBLICATION_TRACES:
        raise ValueError("missing, extra or invalid independent root manifest publication trace")
READER_CLASS = "dev.codex.schubert.nk.batch.file.BackupManifestReaderTest"
READER_METHODS = ("canonicalRootManifest", "nameAndFullHandleBinding", "directoryAndOwnerContracts", "manifestMetadataAndAcl", "rootAndChildRebinding", "manifestReplacementAndMutation", "sizeAndReadBoundaries", "canonicalByteRejection", "everyIoFailure", "closeFailurePrecedence", "timeAndInterrupt", "nullAndUnknownProviders", "borrowedRootAndClosed", "concurrentSerializedReaders", "readOnlyNativeAdapters", "independentTraceAndDownstream",)
READER_TRACES = {"PT-BAT-241-reader.txt": b"20260913-000002-12345678-9abc-def0-8123-456789abcdef\n90000|90001\n26|67\n964|bd608252091beeda64978c96a85107bd329c56f4222cb0a21c39b868af45c370\n"}

def validate_reader_suite(suite):
    return validate_group(suite, READER_CLASS, READER_METHODS, 226)

def validate_reader_traces(traces):
    if traces != READER_TRACES:
        raise ValueError("missing, extra or invalid independent root manifest reader trace")

PAIR_METHODS = ("runningAndCommittedPair", "fullHandleAndMissingRows", "statusCounterAndTimeMatrix", "atomicPairAndReplay", "databaseGuardsAndLocks", "everyJdbcFault", "nullAndUnknownFailures", "concurrentBindings",)
COMMIT_CLASS = "dev.codex.schubert.nk.batch.backup.BackupCommitServiceTest"
COMMIT_METHODS = ("commitAndExistingReceipt", "rollbackBothSteps", "uncertainCommitReplay", "connectionContract", "everyBoundaryFailure", "interruptionAfterCommit", "unknownPrimaryAndCleanup", "independentConnections",)
PAIR_ROWS = b"BACKUP_CONFIG|SUCCESS|2|2|0|67|2026-09-13 02:00:03.000000+00|true|true\nBACKUP_DB|SUCCESS|1|1|0|26|2026-09-13 02:00:03.000000+00|true|true\n"
PAIR_TRACES = {
    "PT-BAT-213-pair.txt": PAIR_ROWS,
    "PT-BAT-215-jdbc.txt": b"read=70\nnew=240\nreplay=70\ninjected=380\n",
    "PT-BAT-218-commit.txt": b"fresh_jdbc=246\nreplay_jdbc=76\n" + PAIR_ROWS,
    "PT-BAT-220-uncertain-false.txt": b"committed_before_failure=false\nretry_updates=2\n" + PAIR_ROWS,
    "PT-BAT-220-uncertain-true.txt": b"committed_before_failure=true\nretry_updates=0\n" + PAIR_ROWS,
}

def validate_pair_suite(suite):
    return validate_group(suite, PAIR_CLASS, PAIR_METHODS, 210)

def validate_commit_suite(suite):
    return validate_group(suite, COMMIT_CLASS, COMMIT_METHODS, 218)

def validate_pair_traces(traces):
    if traces != PAIR_TRACES:
        raise ValueError("missing, extra or invalid independent backup pair trace")

BACKUP_VALUE_CLASS = "dev.codex.schubert.nk.batch.backup.BackupManifestValuesTest"
ARTIFACT_CLASS = "dev.codex.schubert.nk.batch.file.BackupArtifactVerifierTest"
ARTIFACT_METHODS = ("trustedBundleAndManifestDigest", "completeFileSetAndCanonicalName", "directoryAndOwnerContracts", "perFileMetadataAndAcl", "rootAndChildRebinding", "eachFileReplacementAndMutation", "sizesShortLongAndZeroRead", "independentHashAndGoldenMismatch", "streamingBoundaryAndLargeFile", "everyIoFailure", "resourceClosureAndSuppression", "timeAndInterrupt", "providerNullRuntimeAndRedaction", "borrowedRootOwnershipAndClosed", "concurrentSerializedAccess", "readOnlyNoMutationInventory",)
ARTIFACT_GOLDEN = "{\"format\":\"NKBACKUP1\",\"database\":\"schubert_nk\",\"runId\":\"12345678-9abc-def0-8123-456789abcdef\",\"cutoff\":\"2026-09-12T15:00:00.000000Z\",\"startedAt\":\"2026-09-12T15:00:02.123456Z\",\"contentFinishedAt\":\"2026-09-12T15:00:03.654321Z\",\"databaseStep\":{\"id\":90000,\"attempt\":1,\"startedAt\":\"2026-09-12T15:00:00.000000Z\"},\"configurationStep\":{\"id\":90001,\"attempt\":1,\"startedAt\":\"2026-09-12T15:00:01.000000Z\"},\"versions\":{\"host\":\"nk-pt\",\"app\":\"0.1.0-SNAPSHOT\",\"schema\":\"020\",\"os\":\"Ubuntu-26.04.1\",\"jdk\":\"25.0.4\",\"postgresql\":\"18.6\",\"artemis\":\"2.56.0\",\"age\":\"1.2.1\"},\"recipientSha256\":\"0000000000000000000000000000000000000000000000000000000000000000\",\"files\":{\"schubert_nk.dump\":{\"size\":26,\"sha256\":\"9ae12cbba1c4e9e71419a38fde527ad49dac8ecd22d408173df80165d27d0aa9\"},\"config.tar\":{\"size\":35,\"sha256\":\"0793bedfb1288edbbf286aeda46ff08601492dc311bcc9ef352d5b76b4a0eb9a\"},\"credentials.tar.age\":{\"size\":32,\"sha256\":\"de5619301aab91cfd8872a1bd80b7f9c793bf01ca40fa38bfe2ac15ff93debb2\"}}}\n".encode("ascii")
ARTIFACT_TRACES = {"PT-BAT-194-digest.txt": b"964|bd608252091beeda64978c96a85107bd329c56f4222cb0a21c39b868af45c370\n"}

def validate_artifact_suite(suite):
    return validate_group(suite, ARTIFACT_CLASS, ARTIFACT_METHODS, 194)

def validate_artifact_traces(traces):
    if traces != ARTIFACT_TRACES:
        raise ValueError("missing, extra or invalid independently checked artifact digest")
BACKUP_VALUE_METHODS = ("completeIdentityAndDirectoryName", "fileDigestBoundsAndOverflow", "versionTokenBoundaries", "stepAndRunBinding", "timeAndPrecisionBoundaries", "nullAndRedaction", "immutableAccessors", "concurrentValueUse",)
BACKUP_CODEC_CLASS = "dev.codex.schubert.nk.batch.file.BackupManifestCodecTest"
BACKUP_CODEC_METHODS = ("independentCanonicalGolden", "allFieldsAndMaximumLengths", "structuralByteMutation", "noncanonicalScalarsAndDates", "missingUnknownDuplicateAndOrder", "sizeAndNullBoundaries", "inputOutputOwnership", "concurrentCanonicalRoundTrips",)
BACKUP_GOLDEN = "{\"format\":\"NKBACKUP1\",\"database\":\"schubert_nk\",\"runId\":\"12345678-9abc-def0-8123-456789abcdef\",\"cutoff\":\"2026-09-12T15:00:00.000000Z\",\"startedAt\":\"2026-09-12T15:00:02.123456Z\",\"contentFinishedAt\":\"2026-09-12T15:00:03.654321Z\",\"databaseStep\":{\"id\":90000,\"attempt\":1,\"startedAt\":\"2026-09-12T15:00:00.000000Z\"},\"configurationStep\":{\"id\":90001,\"attempt\":1,\"startedAt\":\"2026-09-12T15:00:01.000000Z\"},\"versions\":{\"host\":\"nk-pt\",\"app\":\"0.1.0-SNAPSHOT\",\"schema\":\"020\",\"os\":\"Ubuntu-26.04.1\",\"jdk\":\"25.0.4\",\"postgresql\":\"18.6\",\"artemis\":\"2.56.0\",\"age\":\"1.2.1\"},\"recipientSha256\":\"0000000000000000000000000000000000000000000000000000000000000000\",\"files\":{\"schubert_nk.dump\":{\"size\":1,\"sha256\":\"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\"},\"config.tar\":{\"size\":512,\"sha256\":\"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\"},\"credentials.tar.age\":{\"size\":200,\"sha256\":\"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc\"}}}\n".encode("ascii")

def validate_backup_value_suite(suite):
    return validate_group(suite, BACKUP_VALUE_CLASS, BACKUP_VALUE_METHODS, 178)

def validate_backup_codec_suite(suite):
    return validate_group(suite, BACKUP_CODEC_CLASS, BACKUP_CODEC_METHODS, 186)

def validate_backup_traces(traces):
    if traces != {"PT-BAT-186-manifest.json": BACKUP_GOLDEN}:
        raise ValueError("missing, extra or invalid independent backup manifest")


ATOMIC_VALUE_CLASS = "dev.codex.schubert.nk.batch.repository.CleanupStepValuesTest"
ATOMIC_VALUE_METHODS = ("kindStepMapping", "successfulChunkContracts", "rejectionAndDeferredContracts", "summaryCountsAndCompletion", "counterOverflowAndBounds", "nullAndRedaction", "immutableValues", "concurrentValues",)

def validate_atomic_value_suite(suite):
    return validate_group(suite, ATOMIC_VALUE_CLASS, ATOMIC_VALUE_METHODS, 154)

ATOMIC_REPOSITORY_CLASS = "dev.codex.schubert.nk.batch.repository.CleanupStepRepositoryTest"
ATOMIC_REPOSITORY_METHODS = ("actualSevenKindsAndStepTotals", "borrowedStateAndMapping", "nullAndProjection", "allJdbcFailures", "rejectionReasonsAndUnknownTotals", "utcFullHandle", "interruptRuntimeAndResourceOwnership", "concurrentTransactionsAndRollback",)

def validate_atomic_repository_suite(suite):
    return validate_group(suite, ATOMIC_REPOSITORY_CLASS, ATOMIC_REPOSITORY_METHODS, 162)

ATOMIC_SERVICE_CLASS = "dev.codex.schubert.nk.batch.cleanup.StepCleanupServiceTest"
ATOMIC_SERVICE_METHODS = ("allKindsCompleteAndPersistedCounts", "multiChunkResumeAndSharedStep", "lockBackupAndForeignKeyDeferral", "transactionFaultsAndUnknownCommit", "timeoutInterruptAndClockWrap", "counterContinuityAndOverflow", "connectionStateRestorationAndNulls", "concurrencyAndIndependentTrace",)

def validate_atomic_service_suite(suite):
    return validate_group(suite, ATOMIC_SERVICE_CLASS, ATOMIC_SERVICE_METHODS, 170)

ATOMIC_TRACES = {
    "PT-BAT-162-seven-kinds.txt": b"NOTIFICATIONS=1|1|END\nQUESTIONS=1|1|END\nSESSIONS=3|3|END\nOUTBOX=2|2|END\nBATCH_RUNS=1|1|END\nINBOX_PROGRESS=2|1|END\nLOG_PROGRESS=3|1|END\n",
    "PT-BAT-165-jdbc.txt": b"repository=53\nfault_positions=53\ndouble_close_pairs=3\n",
    "PT-BAT-171-chunks.txt": b"sessions=1001\nchunks=1000|1|0\nservice_jdbc=171\nresume_delta=0\n",
    "PT-BAT-173-jdbc.txt": b"positive_end=115\nfault_positions=115\ncommit_response_unknown=stored1|resume_delta0\n",
    "PT-BAT-177-service.txt": b"NOTIFICATIONS=RUNNING|1|1|0|0|true\nQUESTIONS=RUNNING|1|1|0|0|true\nSESSIONS=RUNNING|3|3|0|0|true\nOUTBOX=RUNNING|2|2|0|0|true\nBATCH_RUNS=RUNNING|1|1|0|0|true\nINBOX_PROGRESS=RUNNING|2|2|0|0|true\nLOG_PROGRESS=RUNNING|3|3|0|0|true\n",
}

def validate_atomic_traces(traces):
    if traces != ATOMIC_TRACES:
        raise ValueError("missing, extra or invalid independent atomic cleanup trace")


METHODS = (
    "runIdentityBoundaries", "countInvariants", "cleanupAllowlist", "rejectionAndProgressContracts",
    "emptyCleanupAndExplicitTransaction", "heldLogsAndDurableRead", "rollbackSavepointAndResume",
    "backupAndAdvisoryRejection", "exactLimitsAndNullInputs", "rowProjectionFailures",
    "progressProjectionFailures", "jdbcFailuresRemainRedacted", "roleIsolationAndNoInboxBypass",
    "timezoneAndCutoffIdentity", "lockedLogsDoNotAdvance", "retentionAndResourceOwnership",
    "moduleDependencyBoundary",
)
STEP_VALUE_CLASS = "dev.codex.schubert.nk.batch.repository.BatchStepValuesTest"
STEP_VALUE_METHODS = ("closedStepsAndBackupPolicy", "attemptIdentityAndBounds", "terminalStatesAndReasonMatrix", "counterAndStatusBoundaries", "temporalContractAndBusinessDay", "nullContractsAndRedaction", "immutableValueSemantics", "independentConcurrentValues",)
STEP_REPOSITORY_CLASS = "dev.codex.schubert.nk.batch.repository.BatchRunRepositoryTest"
STEP_REPOSITORY_METHODS = ("firstAttemptAndTerminalStates", "ordinarySuccessSkipsByBusinessDate", "backupAlwaysRunsAndAttemptLimit", "explicitAbandonedRecovery", "foreignRunningAndRootIdentity", "exactFinishReplay", "handleIdentityAndMissingRows", "rollbackAndUnknownCommit", "historicalUtcAndFixedRunDay", "clockRegressionPreservesRows", "parentTransactionAndLock", "historyProjectionAndNulls", "jdbcFailurePositions", "interruptionAndRuntime", "concurrentOwnersAndRowLocks", "independentSqlInventoryAndGrants",)
STEP_TRACES = {
    "PT-BAT-138-terminals.txt": b"BACKUP_DB=SUCCESS|5|3|0|9|NULL|NULL\nBACKUP_CONFIG=WARNING|5|2|0|8|PROTECTED_RECORDS|protected records retained\nCLEAN_NOTIFICATION=FAILED|6|2|4|0|DATABASE_FAILURE|batch database operation failed\nCLEAN_QUESTION=SKIPPED|0|0|0|0|BACKUP_UNAVAILABLE|verified backup unavailable\nCLEAN_SESSION=SUCCESS|5|3|0|9|NULL|NULL\nCLEAN_INBOX_OUTBOX=WARNING|5|2|0|8|PROTECTED_RECORDS|protected records retained\nCLEAN_LOG=FAILED|6|2|4|0|DATABASE_FAILURE|batch database operation failed\nCLEAN_BATCH_RUN=SKIPPED|0|0|0|0|BACKUP_UNAVAILABLE|verified backup unavailable\nCLEAN_TRANSFER=SUCCESS|5|3|0|9|NULL|NULL\nCLEAN_EXPIRY=WARNING|5|2|0|8|PROTECTED_RECORDS|protected records retained\n",
    "PT-BAT-150-jdbc.txt": b"empty=57/57/2\nhistory=70/70/2\nskip=70/70/2\nrecover=80/80/2\nfinish=50/50/2\nreplay=72/72/2\n",
}


def validate_step_traces(traces):
    if traces != STEP_TRACES:
        raise ValueError("missing, extra or invalid independently specified batch step trace")


def validate_step_value_suite(suite):
    return validate_group(suite, STEP_VALUE_CLASS, STEP_VALUE_METHODS, 130)


def validate_step_repository_suite(suite):
    return validate_group(suite, STEP_REPOSITORY_CLASS, STEP_REPOSITORY_METHODS, 138)


CLASS = "dev.codex.schubert.nk.batch.repository.CleanupRepositoryTest"
SUMMARY_CLASS = "dev.codex.schubert.nk.batch.repository.InspectionSummaryRepositoryTest"
SUMMARY_METHODS = ("summaryValueInvariants", "realBoundedRead", "parentStateAndLock", "projectionAndNull",
                   "allJdbcFailurePositions", "historicalUtcIdentity", "freshVisibilityAndBorrowing", "interruptAndRuntime")
ATTEMPT_CLASS = "dev.codex.schubert.nk.batch.cleanup.InspectionAttemptTest"
ATTEMPT_METHODS = ("matchingSuccessAndWarning", "zeroAndResumedAttemptCounts", "completedBaselineImmutability",
                   "countRegressionAndOverflow", "runIdentityAndMissingEnd", "receiptCodesAndNulls",
                   "redactionAndValueOwnership", "independentConcurrentObservations")
REFERENCES_CLASS = "dev.codex.schubert.nk.batch.repository.RunReferenceRepositoryTest"
REFERENCES_METHODS = ("referenceValueInvariants", "realReferenceRead", "transactionAndLockContracts",
                      "projectionAndNullContracts", "jdbcFailureMatrix", "interruptionAndRuntime",
                      "rollbackAndFreshVisibility", "independentConcurrentConnections")
LOG_METHODS = (
    "emptyAndCompletedRuns", "heldPrefixAndLargeChunks", "resumedAttemptCounts", "sessionLockOwnership",
    "backupAndRowLockStop", "timeBoundaryAndClockWrap", "interruptsRemainSet", "rollbackAndUncertainCommit",
    "restorationAndUnlockFailures", "invalidInputsAndProjections", "summaryInvariants", "failuresLeaveNoFalseSuccess",
)
LOG_CLASS = "dev.codex.schubert.nk.batch.cleanup.LogCleanupServiceTest"
HANDOFF_CLASS = "dev.codex.schubert.nk.batch.cleanup.InspectorLockHandoffTest"
HANDOFF_METHODS = ("actualTransactionHandoff", "preconditionsAndReentrantLock", "callbackFailuresAndNull",
                   "reacquisitionConflict", "jdbcFailureMatrix", "invalidResultMatrix",
                   "stateChangesAndInterrupts", "concurrentGapCompetition",
                   "callbackIdentitySurvivesReacquisitionSqlFailure")
DURABLE_CLASS = "dev.codex.schubert.nk.batch.file.DurableRecordFilesTest"
LIFECYCLE_CLASS = "dev.codex.schubert.nk.batch.file.MaintenanceRunFilesTest"
LIFECYCLE_METHODS = ("newRunPublication", "resumeActive", "resumeOrphanAnchor", "resumePendingBegin",
                     "resumeCompletedHistory", "completedActiveRecovery", "completeSuccessAndWarning",
                     "completionRetryAndMismatch", "noImplicitNewIdentity", "malformedGraphReferences",
                     "ambiguousPendingStates", "inventoryUnknownAndPartial", "namespacePermissions",
                     "namespaceReplacement", "recordReplacementDuringScan", "listingAndIoFailures",
                     "rootAcquisitionAndCloseFailures", "startCrashBoundaries", "resumeCrashBoundaries",
                     "completionCrashBoundaries", "nullAndClosedContracts", "interruptionAndRuntime",
                     "concurrentScopeOwnership", "fixedFactoryAndReopen")
RETIREMENT_RECORD_CLASS = "dev.codex.schubert.nk.batch.file.MaintenanceRetirementRecordsTest"
RETIREMENT_RECORD_METHODS = ("literalMarkerAndPlanHash", "temporalAndCountInvariants", "nullAndOwnership", "malformedMarkerBytes", "markerAliases", "boundedStorageRecords", "planNameBinding", "concurrentCanonicalRecords")
RETIREMENT_CLASS = "dev.codex.schubert.nk.batch.file.MaintenanceRunRetirementTest"
RETIREMENT_METHODS = ("candidatesAndProtectedRuns", "strictAgeAndLatestCompletion", "referenceCombinations", "missingAndContradictoryIdentity", "newRetirementPreservesOtherRuns", "preMarkerPlanRecovery", "markerOriginalRecovery", "metadataOnlyRecovery", "planCompletenessAndDigest", "namespaceAndForeignArtifacts", "referenceReappearanceAndDbFaults", "publicationAndDeletionCrashes", "everyIoFailurePreservesState", "scopeNullAndInterruption", "concurrentAndClosedScope", "resourceCloseAndDigestFailure")
REVIEWED_STATIC_DIAGNOSTICS = (
    {"method": "MaintenanceRunFiles.create", "id": "DMI_HARDCODED_ABSOLUTE_FILENAME", "match": "EXACT", "reason": "UI251/SS343 require fixed Linux /var", "owner": "NK-BAT-001 PG", "reviewAt": "PG gate or OS/path/SS change", "testId": "PT-BAT-081", "coverageExcluded": False},)
DURABLE_METHODS = ("literalReads", "newPublication", "sameRecordReuse", "expectedRetirement",
                   "nameContentAndNull", "metadataAndFilesystems", "boundedChannels",
                   "namespaceAndReplacement", "allReadFailures", "allWriteRetireFailures",
                   "interruptionsAndUnknownRuntime", "concurrencyAndNative")
RECORD_CLASS = "dev.codex.schubert.nk.batch.file.MaintenanceRecordsTest"
RECORD_METHODS = ("literalRecords", "identityTemporalBoundaries", "malformedSources", "scalarAliases",
                  "completionInvariants", "nullContracts", "ownershipAndRedaction", "concurrentUse")
RECORD_TRACES = {
    "PT-BAT-038-anchor.txt": b"NKRUN1\n12345678-9abc-def0-8123-456789abcdef\n2026-09-12T04:05:06.123456Z\n",
    "PT-BAT-038-activation.txt": b"NKACT1\n12345678-9abc-def0-8123-456789abcdef\n2026-09-12T04:05:06.123456Z\nfedcba98-7654-3210-8fed-cba987654321\n",
    "PT-BAT-038-completion-0.txt": b"NKDONE1\n12345678-9abc-def0-8123-456789abcdef\n2026-09-12T04:05:06.123456Z\nfedcba98-7654-3210-8fed-cba987654321\n2026-09-12T05:06:07.234567Z\n0\n",
    "PT-BAT-038-completion-10.txt": b"NKDONE1\n12345678-9abc-def0-8123-456789abcdef\n2026-09-12T04:05:06.123456Z\nfedcba98-7654-3210-8fed-cba987654321\n2026-09-12T05:06:07.234567Z\n10\n"}
OPS_CLASSES = {"dev.codex.schubert.nk.batch.file.MaintenanceFileLockTest",
               "dev.codex.schubert.nk.batch.mq.ArtemisReadinessClientTest",
               "dev.codex.schubert.nk.batch.mq.ArtemisManagementReadinessClientTest",
               "dev.codex.schubert.nk.batch.mq.ArtemisAddressSettingsReadinessClientTest",
               "dev.codex.schubert.nk.batch.mq.ArtemisAcceptorReadinessClientTest",
               "dev.codex.schubert.nk.batch.mq.ArtemisRoleReadinessClientTest",
               "dev.codex.schubert.nk.batch.mq.ArtemisQueuePressureClientTest",
               "dev.codex.schubert.nk.batch.mq.ArtemisExpiryManagementAuthorizationTest",
               "dev.codex.schubert.nk.batch.mq.ArtemisExpiryPurgeClientTest",
               "dev.codex.schubert.nk.batch.mq.ArtemisStartupObservationTest",
               "dev.codex.schubert.nk.batch.platform.ApplicationStopGateTest",
               "dev.codex.schubert.nk.batch.platform.SystemctlStateSourceTest",
               "dev.codex.schubert.nk.batch.platform.InspectorRunEnvironmentTest",
               "dev.codex.schubert.nk.batch.platform.InspectorStaticEnvironmentTest",
               "dev.codex.schubert.nk.batch.file.InspectorEnvironmentReaderTest",
               "dev.codex.schubert.nk.batch.file.InspectorEnvironmentPublisherTest",
               "dev.codex.schubert.nk.batch.platform.ConfigurationGroupResolverTest",
               "dev.codex.schubert.nk.batch.file.InspectorEnvironmentFilesTest",
               "dev.codex.schubert.nk.batch.platform.InspectorUnitSnapshotTest",
               "dev.codex.schubert.nk.batch.platform.InspectorUnitProbeTest"}
DURABLE_TRACES = {
    "PT-BAT-047-anchor.txt": RECORD_TRACES["PT-BAT-038-anchor.txt"],
    "PT-BAT-047-active.txt": RECORD_TRACES["PT-BAT-038-activation.txt"],
    "PT-BAT-047-begin.txt": RECORD_TRACES["PT-BAT-038-activation.txt"],
    "PT-BAT-047-done-10.txt": RECORD_TRACES["PT-BAT-038-completion-10.txt"]}
LIFECYCLE_NAMES = (b"attempts/fedcba98-7654-3210-8fed-cba987654321.begin\n"
                   b"attempts/fedcba98-7654-3210-8fed-cba987654321.done\n"
                   b"runs/12345678-9abc-def0-8123-456789abcdef.run\n")
LIFECYCLE_TRACES = {
    "PT-BAT-058-anchor.txt": RECORD_TRACES["PT-BAT-038-anchor.txt"],
    "PT-BAT-058-begin.txt": RECORD_TRACES["PT-BAT-038-activation.txt"],
    "PT-BAT-058-active.txt": RECORD_TRACES["PT-BAT-038-activation.txt"],
    "PT-BAT-064-done-0.txt": RECORD_TRACES["PT-BAT-038-completion-0.txt"],
    "PT-BAT-064-done-10.txt": RECORD_TRACES["PT-BAT-038-completion-10.txt"],
    "PT-BAT-064-names-0.txt": LIFECYCLE_NAMES,
    "PT-BAT-064-names-10.txt": LIFECYCLE_NAMES}


RETIREMENT_TRACES = {
    "PT-BAT-090-marker.txt": b"NKRET1\n12345678-9abc-def0-8123-456789abcdef\n2025-01-01T00:00:00.000000Z\n2025-01-02T00:00:00.000000Z\n2026-02-06T00:00:00.000001Z\n1\na5bf8bfabd8dbcc640bae2c4aa19c1e3387e43cb1a96cc3d9951be048a4a4065\n",
    "PT-BAT-090-maximum.txt": b"NKRET1\n12345678-9abc-def0-8123-456789abcdef\n2025-01-01T00:00:00.000000Z\n2025-01-02T00:00:00.000000Z\n2026-02-06T00:00:00.000001Z\n2147483647\na5bf8bfabd8dbcc640bae2c4aa19c1e3387e43cb1a96cc3d9951be048a4a4065\n",
    "PT-BAT-099-two-activation-marker.txt": b"NKRET1\n12345678-9abc-def0-8123-456789abcdef\n2025-01-01T00:00:00.000000Z\n2025-01-03T00:00:00.000000Z\n2026-02-07T00:00:00.000001Z\n2\ne6ff18dc21a10852fe4de7e8606fe0ad005c8e242bdc535ea8d391dd052528de\n",
    "PT-BAT-102-marker.txt": b"NKRET1\n12345678-9abc-def0-8123-456789abcdef\n2025-01-01T00:00:00.000000Z\n2025-01-02T00:00:00.000000Z\n2026-02-06T00:00:00.000001Z\n1\na5bf8bfabd8dbcc640bae2c4aa19c1e3387e43cb1a96cc3d9951be048a4a4065\n",
    "PT-BAT-102-phases.txt": b"phase0:\nattempts/fedcba98-7654-3210-8fed-cba987654321.begin\nattempts/fedcba98-7654-3210-8fed-cba987654321.done\nruns/12345678-9abc-def0-8123-456789abcdef.run\nphase1:\nattempts/fedcba98-7654-3210-8fed-cba987654321.begin\nattempts/fedcba98-7654-3210-8fed-cba987654321.done\nattempts/fedcba98-7654-3210-8fed-cba987654321.plan\nruns/12345678-9abc-def0-8123-456789abcdef.run\nphase2:\n12345678-9abc-def0-8123-456789abcdef.retire\nattempts/fedcba98-7654-3210-8fed-cba987654321.begin\nattempts/fedcba98-7654-3210-8fed-cba987654321.done\nattempts/fedcba98-7654-3210-8fed-cba987654321.plan\nruns/12345678-9abc-def0-8123-456789abcdef.run\nphase3:\n12345678-9abc-def0-8123-456789abcdef.retire\nattempts/fedcba98-7654-3210-8fed-cba987654321.begin\nattempts/fedcba98-7654-3210-8fed-cba987654321.plan\nruns/12345678-9abc-def0-8123-456789abcdef.run\nphase4:\n12345678-9abc-def0-8123-456789abcdef.retire\nattempts/fedcba98-7654-3210-8fed-cba987654321.plan\nruns/12345678-9abc-def0-8123-456789abcdef.run\nphase5:\n12345678-9abc-def0-8123-456789abcdef.retire\nattempts/fedcba98-7654-3210-8fed-cba987654321.plan\nphase6:\n12345678-9abc-def0-8123-456789abcdef.retire\nphase7:\n",
}


RETIREMENT_IO_TRACE = b"{acl=1075, attributes=1075, close=854, create=2, filesystem=1075, force=2, namesClose=54, namesHasNext=138, namesIterator=54, namesNext=84, namesOpen=54, openDirectory=477, openEntry=324, openRead=57, openRoot=53, openWriter=2, publish=2, read=114, readClose=57, readSize=114, readonly=1075, sync=13, unlink=5, write=2, writeSize=4, writerClose=2}"


def validate_retirement_io(value):
    if value != RETIREMENT_IO_TRACE:
        raise ValueError("invalid independently counted retirement IO inventory")


def validate_retirement_traces(traces):
    if traces != RETIREMENT_TRACES:
        raise ValueError("missing, extra or invalid independent retirement trace")


def select_program_suites(suites):
    # PG-D-147/148: shared module, distinct Program IDs; no unknown/missing/duplicate class.
    expected = {CLASS, LOG_CLASS, HANDOFF_CLASS, RECORD_CLASS, DURABLE_CLASS, LIFECYCLE_CLASS, REFERENCES_CLASS,
                RETIREMENT_RECORD_CLASS, RETIREMENT_CLASS, SUMMARY_CLASS, ATTEMPT_CLASS, STEP_VALUE_CLASS, STEP_REPOSITORY_CLASS, ATOMIC_VALUE_CLASS, ATOMIC_REPOSITORY_CLASS, ATOMIC_SERVICE_CLASS, BACKUP_VALUE_CLASS, BACKUP_CODEC_CLASS, ARTIFACT_CLASS, PAIR_CLASS, COMMIT_CLASS, READER_CLASS, *OPS_CLASSES}
    expected.add(BATCH_RUNTIME_DEPENDENCY_CLASS)
    expected.add(PUBLICATION_CLASS)
    expected.add(BUNDLE_CLASS)
    expected.add(COMPLETION_CLASS)
    expected.add(EXPIRY_AUDIT_CLASS)
    if len(suites) != len(expected) or {s.get("name") for s in suites} != expected:
        raise ValueError("unmapped or missing shared batch module class")
    return [s for s in suites if s.get("name") not in OPS_CLASSES]


def validate_suite(suite):
    return validate_group(suite, CLASS, METHODS, 1)


def validate_summary_suite(suite):
    return validate_group(suite, SUMMARY_CLASS, SUMMARY_METHODS, 114)


def validate_attempt_suite(suite):
    return validate_group(suite, ATTEMPT_CLASS, ATTEMPT_METHODS, 122)


def validate_log_suite(suite):
    return validate_group(suite, LOG_CLASS, LOG_METHODS, 18)


def validate_handoff_suite(suite):
    methods = validate_group(suite, HANDOFF_CLASS, HANDOFF_METHODS, 30)
    methods["PT-BAT-282"] = methods.pop("PT-BAT-038")
    return methods


def validate_record_suite(suite):
    return validate_group(suite, RECORD_CLASS, RECORD_METHODS, 38)


def validate_durable_suite(suite):
    return validate_group(suite, DURABLE_CLASS, DURABLE_METHODS, 46)


def validate_lifecycle_suite(suite):
    return validate_group(suite, LIFECYCLE_CLASS, LIFECYCLE_METHODS, 58)


def validate_references_suite(suite):
    return validate_group(suite, REFERENCES_CLASS, REFERENCES_METHODS, 82)


def validate_retirement_record_suite(suite):
    return validate_group(suite, RETIREMENT_RECORD_CLASS, RETIREMENT_RECORD_METHODS, 90)


def validate_retirement_suite(suite):
    return validate_group(suite, RETIREMENT_CLASS, RETIREMENT_METHODS, 98)


def validate_record_traces(traces):
    if traces != RECORD_TRACES:
        raise ValueError("missing, extra or invalid independently checked run record trace")


def validate_durable_traces(traces):
    if traces != DURABLE_TRACES:
        raise ValueError("missing, extra or invalid independently checked durable record trace")


def validate_lifecycle_traces(traces):
    if traces != LIFECYCLE_TRACES:
        raise ValueError("missing, extra or invalid independently checked lifecycle trace")


def validate_group(suite, cls, expected, start):
    cases = suite.findall("testcase")
    names = [c.get("name") for c in cases]
    if (suite.get("name") != cls or suite.get("tests") != str(len(expected))
            or any(int(suite.get(k, "0")) for k in ("failures", "errors", "skipped"))
            or len(names) != len(set(names)) or set(names) != set(expected)
            or any(c.get("classname") != cls or
                   any(child.tag not in ("system-out", "system-err") for child in c) for c in cases)):
        raise ValueError("batch PT inventory or execution is not certifiable")
    return {f"PT-BAT-{i:03}": cls + "#" + name for i, name in enumerate(expected, start)}


def validate_reports(suites):
    validators = {CLASS: validate_suite, LOG_CLASS: validate_log_suite,
                  HANDOFF_CLASS: validate_handoff_suite, RECORD_CLASS: validate_record_suite,
                  DURABLE_CLASS: validate_durable_suite, LIFECYCLE_CLASS: validate_lifecycle_suite,
                  REFERENCES_CLASS: validate_references_suite,
                  RETIREMENT_RECORD_CLASS: validate_retirement_record_suite,
                  RETIREMENT_CLASS: validate_retirement_suite,
                  SUMMARY_CLASS: validate_summary_suite, ATTEMPT_CLASS: validate_attempt_suite,
                  STEP_VALUE_CLASS: validate_step_value_suite, STEP_REPOSITORY_CLASS: validate_step_repository_suite,
                  ATOMIC_VALUE_CLASS: validate_atomic_value_suite, ATOMIC_REPOSITORY_CLASS: validate_atomic_repository_suite, ATOMIC_SERVICE_CLASS: validate_atomic_service_suite, BACKUP_VALUE_CLASS: validate_backup_value_suite, BACKUP_CODEC_CLASS: validate_backup_codec_suite, ARTIFACT_CLASS: validate_artifact_suite, PAIR_CLASS: validate_pair_suite, COMMIT_CLASS: validate_commit_suite, READER_CLASS: validate_reader_suite}
    validators[BATCH_RUNTIME_DEPENDENCY_CLASS] = validate_batch_runtime_dependency_suite
    validators[PUBLICATION_CLASS] = validate_publication_suite
    validators[BUNDLE_CLASS] = validate_bundle_suite
    validators[COMPLETION_CLASS] = validate_completion_suite
    validators[EXPIRY_AUDIT_CLASS] = validate_expiry_audit_suite
    if len(suites) != len(validators) or {s.get("name") for s in suites} != set(validators):
        raise ValueError("unmapped or missing batch test class")
    methods = {}
    for suite in suites:
        validator = validators[suite.get("name")]
        methods.update(validator(suite))
    return methods


def ownership_description(total, program):
    # BUG-153/YKT-119: observed totals have one source; this is reporting, not the PT oracle.
    return (f"Batch module{total} PT = NK-BAT-001{program} + NK-OPS-001{total - program}. "
            "Full module coverage includes both; OPS IDs are certified separately by022/018_NK-OPS-001. "
            "No duplicate PT credit.")


def read_batch_reports(target):
    reports = [ET.parse(path).getroot() for path in sorted((target / "surefire-reports").glob("TEST-*.xml"))]
    case_count = 0
    for suite in reports:
        cases = suite.findall("testcase")
        if (suite.tag != "testsuite" or any(int(suite.get(key, "0")) for key in ("failures", "errors", "skipped"))
                or len(cases) != int(suite.get("tests", "-1"))
                or any(child.tag not in ("system-out", "system-err") for case in cases for child in case)):
            raise ValueError("nonpassing or inconsistent Batch JUnit report")
        case_count += len(cases)
    if case_count != BATCH_TEST_COUNT:
        raise ValueError("Batch JUnit total does not match the fixed collector inventory")
    return reports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    parser.add_argument("--preflight", action="store_true", help="check the Batch roster without writing evidence")
    args = parser.parse_args()
    run = args.run_id
    if not run.startswith("PT-WEB-") or not all(c.isalnum() or c == "-" for c in run):
        raise SystemExit("invalid run ID")
    repo = Path(__file__).resolve().parents[2]
    target = repo / "src/schubert-nk-batch/target"
    if args.preflight:
        methods = validate_reports(select_program_suites(read_batch_reports(target)))
        print(json.dumps({"runId": run, "batchTests": BATCH_TEST_COUNT,
                          "programTests": len(methods), "writesEvidence": False}))
        return
    full = repo / "evidence/01_PT/008_NK-SCN-001/evidence/manifest.json"
    verified = json.loads(full.read_text())
    validate_reactor(verified, run)
    subprocess.run(["git", "diff", "--exit-code", verified["targetCommit"], "--", "src", "pom.xml",
                    "program/characterization", "tools/quality"], cwd=repo, check=True)
    methods = validate_reports(select_program_suites(read_batch_reports(target)))
    evidence = repo / "evidence/01_PT/017_NK-BAT-001/evidence"
    for folder in ("output", "coverage", "logs"):
        (evidence / folder).mkdir(parents=True, exist_ok=True)
    completion_root = target / "backup-completion-traces"
    completion_traces = {str(p.relative_to(completion_root)): p.read_bytes() for p in completion_root.rglob("*") if p.is_file()}
    validate_completion_traces(completion_traces)
    for folder, values in (("input/backup-completion", COMPLETION_TRACES), ("output/backup-completion", completion_traces)):
        (evidence / folder).mkdir(parents=True, exist_ok=True)
        for name, content in values.items():
            (evidence / folder / name).write_bytes(content)
    bundle_root = target / "backup-bundle-traces"
    bundle_traces = {str(p.relative_to(bundle_root)): p.read_bytes() for p in bundle_root.rglob("*") if p.is_file()}
    validate_bundle_traces(bundle_traces)
    for folder, values in (("input/backup-bundle", BUNDLE_TRACES), ("output/backup-bundle", bundle_traces)):
        (evidence / folder).mkdir(parents=True, exist_ok=True)
        for name, content in values.items():
            (evidence / folder / name).write_bytes(content)
    publication_root = target / "backup-publication-traces"
    publication_traces = {str(p.relative_to(publication_root)): p.read_bytes() for p in publication_root.rglob("*") if p.is_file()}
    validate_publication_traces(publication_traces)
    for folder, values in (("input/backup-publication", PUBLICATION_TRACES), ("output/backup-publication", publication_traces)):
        (evidence / folder).mkdir(parents=True, exist_ok=True)
        for name, content in values.items():
            (evidence / folder / name).write_bytes(content)
    reader_root = target / "backup-reader-traces"
    reader_traces = {str(p.relative_to(reader_root)): p.read_bytes() for p in reader_root.rglob("*") if p.is_file()}
    validate_reader_traces(reader_traces)
    for folder, values in (("input/backup-reader", READER_TRACES), ("output/backup-reader", reader_traces)):
        destination = evidence / folder
        destination.mkdir(parents=True, exist_ok=True)
        for name, value in values.items():
            (destination / name).write_bytes(value)
    for audit_name in ("048_NK-BAT-001_root_manifest資源横展開.md", "049_NK-BAT-001_file資源解放横展開PT.md", "050_NK-BAT-001_namespace資源解放横展開PT.md", "051_NK-OPS-001_Systemctl資源解放横展開PT.md", "052_NK-OPS-001_group資源解放横展開PT.md", "053_NK-BAT-001_root_manifest公開単体テスト仕様書.md", "055_NK-BAT-001_bundle確定単体テスト仕様書.md", "057_NK-BAT-001_bundle元inode横展開.md", "058_NK-BAT-001_Log_SQL資源横展開仕様.md", "059_NK-BAT-001_Log_SQL資源横展開結果.md", "060_NK-BAT-001_読取Repository資源横展開仕様.md", "061_NK-BAT-001_読取Repository資源横展開結果.md", "062_NK-BAT-001_CleanupRepository資源横展開仕様.md", "063_NK-BAT-001_CleanupRepository資源横展開結果.md", "064_NK-BAT-001_CleanupStep資源横展開仕様.md", "065_NK-BAT-001_CleanupStep資源横展開結果.md", "066_NK-BAT-001_BackupStep資源横展開仕様.md", "067_NK-BAT-001_BackupStep資源横展開結果.md", "068_NK-BAT-001_BatchRun資源横展開仕様.md", "069_NK-BAT-001_BatchRun資源横展開結果.md"):
        audit = repo / "evidence/01_PT/017_NK-BAT-001" / audit_name
        shutil.copyfile(audit, evidence / "logs" / audit.name)
    for completion_audit in ("070_NK-BAT-001_backup検証確定caller単体テスト仕様書.md", "071_NK-BAT-001_backup検証確定caller実行結果.md"):
        shutil.copyfile(repo / "evidence/01_PT/017_NK-BAT-001" / completion_audit, evidence / "logs" / completion_audit)
    for retirement_audit in ("072_NK-BAT-001_全IO位置試験の独立並列実行仕様.md", "073_NK-BAT-001_全IO位置試験の独立並列実行結果.md"):
        shutil.copyfile(repo / "evidence/01_PT/017_NK-BAT-001" / retirement_audit, evidence / "logs" / retirement_audit)
    pair_root = target / "backup-step-traces"
    pair_traces = {str(p.relative_to(pair_root)): p.read_bytes() for p in pair_root.rglob("*") if p.is_file()}
    validate_pair_traces(pair_traces)
    for folder, values in (("input/backup-pair", PAIR_TRACES), ("output/backup-pair", pair_traces)):
        destination = evidence / folder
        destination.mkdir(parents=True, exist_ok=True)
        for name, value in values.items():
            (destination / name).write_bytes(value)
    shutil.copyfile(repo / "evidence/01_PT/017_NK-BAT-001/045_NK-BAT-001_backup両step横展開.md",
                    evidence / "logs/BUG-191-194-YKT-151-153.md")
    artifact_root = target / "backup-artifact-traces"
    artifact_traces = {str(p.relative_to(artifact_root)): p.read_bytes() for p in artifact_root.rglob("*") if p.is_file()}
    validate_artifact_traces(artifact_traces)
    artifact_fixture = repo / "src/schubert-nk-batch/src/test/resources/backup/artifact-manifest.json"
    if artifact_fixture.read_bytes() != ARTIFACT_GOLDEN:
        raise ValueError("independent backup artifact fixture changed")
    for folder, values in (("input/backup-artifact", {"PT-BAT-194-manifest.json": ARTIFACT_GOLDEN}),
                           ("output/backup-artifact", artifact_traces)):
        destination = evidence / folder
        destination.mkdir(parents=True, exist_ok=True)
        for name, value in values.items():
            (destination / name).write_bytes(value)
    shutil.copyfile(repo / "evidence/01_PT/017_NK-BAT-001/040_NK-BAT-001_backup実体検証横展開.md",
                    evidence / "logs/BUG-184-185-186-YKT-145-146.md")
    backup_root = target / "backup-manifest-traces"
    backup_traces = {str(p.relative_to(backup_root)): p.read_bytes() for p in backup_root.rglob("*") if p.is_file()}
    validate_backup_traces(backup_traces)
    fixture = repo / "src/schubert-nk-batch/src/test/resources/backup/manifest-golden.json"
    if fixture.read_bytes() != BACKUP_GOLDEN:
        raise ValueError("independent backup manifest fixture changed")
    for folder, values in (("input/backup-manifest", {"PT-BAT-186-manifest.json": BACKUP_GOLDEN}),
                           ("output/backup-manifest", backup_traces)):
        destination = evidence / folder
        destination.mkdir(parents=True, exist_ok=True)
        for name, value in values.items():
            (destination / name).write_bytes(value)
    shutil.copyfile(repo / "evidence/01_PT/017_NK-BAT-001/037_NK-BAT-001_backup_manifest横展開.md",
                    evidence / "logs/BUG-182-183-YKT-143-144.md")
    atomic_root = target / "atomic-cleanup-traces"
    atomic_traces = {str(p.relative_to(atomic_root)): p.read_bytes() for p in atomic_root.rglob("*") if p.is_file()}
    validate_atomic_traces(atomic_traces)
    for folder, values in (("input/atomic-cleanup", ATOMIC_TRACES), ("output/atomic-cleanup", atomic_traces)):
        destination = evidence / folder
        destination.mkdir(parents=True, exist_ok=True)
        for name, value in values.items():
            (destination / name).write_bytes(value)
    shutil.copyfile(repo / "evidence/01_PT/017_NK-BAT-001/032_NK-BAT-001_cleanup証跡横展開.md", evidence / "logs/BUG-179-YKT-140.md")
    shutil.copyfile(repo / "src/schubert-nk-api/src/test/resources/maintenance/step-cleanup-fixture.sql", evidence / "input/atomic-cleanup/step-cleanup-fixture.sql")
    trace_root = target / "maintenance-record-traces"
    step_root = target / "batch-step-traces"
    step_traces = {str(p.relative_to(step_root)): p.read_bytes() for p in step_root.rglob("*") if p.is_file()}
    validate_step_traces(step_traces)
    for folder, values in (("input/batch-step", STEP_TRACES), ("output/batch-step", step_traces)):
        destination = evidence / folder
        destination.mkdir(parents=True, exist_ok=True)
        for name, value in values.items():
            (destination / name).write_bytes(value)
    shutil.copyfile(repo / "evidence/01_PT/017_NK-BAT-001/025_NK-BAT-001_step試験横展開.md", evidence / "logs/BUG-176-178-YKT-137-139.md")
    traces = {str(p.relative_to(trace_root)): p.read_bytes() for p in trace_root.rglob("*") if p.is_file()}
    validate_record_traces(traces)
    durable_root = target / "durable-record-traces"
    durable_traces = {str(p.relative_to(durable_root)): p.read_bytes()
                      for p in durable_root.rglob("*") if p.is_file()}
    validate_durable_traces(durable_traces)
    lifecycle_root = target / "run-lifecycle-traces"
    lifecycle_traces = {str(p.relative_to(lifecycle_root)): p.read_bytes()
                        for p in lifecycle_root.rglob("*") if p.is_file()}
    validate_lifecycle_traces(lifecycle_traces)
    retirement_root = target / "run-retirement-traces"
    retirement_traces = {str(p.relative_to(retirement_root)): p.read_bytes()
                         for p in retirement_root.rglob("*") if p.is_file()}
    validate_retirement_traces(retirement_traces)
    retirement_io = (target / "run-retirement-io-inventory.txt").read_bytes()
    validate_retirement_io(retirement_io)
    for folder, values in (("input/run-retirement", RETIREMENT_TRACES), ("output/run-retirement", retirement_traces)):
        destination = evidence / folder
        destination.mkdir(parents=True, exist_ok=True)
        for name, value in values.items():
            (destination / name).write_bytes(value)
    for folder, value in (("input/run-retirement", RETIREMENT_IO_TRACE), ("output/run-retirement", retirement_io)):
        (evidence / folder / "PT-BAT-110-io.txt").write_bytes(value)
    for folder, values in (("input/run-lifecycle", LIFECYCLE_TRACES), ("output/run-lifecycle", lifecycle_traces)):
        destination = evidence / folder
        destination.mkdir(parents=True, exist_ok=True)
        for name, value in values.items():
            (destination / name).write_bytes(value)
    for folder, values in (("input/durable-records", DURABLE_TRACES), ("output/durable-records", durable_traces)):
        destination = evidence / folder
        destination.mkdir(parents=True, exist_ok=True)
        for name, value in values.items():
            (destination / name).write_bytes(value)
    for folder, values in (("input/maintenance-records", RECORD_TRACES), ("output/maintenance-records", traces)):
        destination = evidence / folder
        destination.mkdir(parents=True, exist_ok=True)
        for name, value in values.items():
            (destination / name).write_bytes(value)
    sanitized = ET.Element("testsuite", name="NK-BAT-001", tests=str(len(methods)), failures="0", errors="0", skipped="0")
    for test_id, method in methods.items():
        ET.SubElement(sanitized, "testcase", id=test_id, classname=method.split("#")[0], name=method.split("#")[1], result="PASS")
    ET.ElementTree(sanitized).write(evidence / "output/results.xml", encoding="utf-8", xml_declaration=True)
    for suffix in ("csv", "xml"):
        shutil.copyfile(target / ("site/jacoco/jacoco." + suffix), evidence / ("coverage/batch-jacoco." + suffix))
    summary = {"runId": run, "targetCommit": verified["targetCommit"], "tests": len(methods),
               "failed": 0, "errors": 0, "skipped": 0,
               "coverage": verified["modules"]["batch"]["coverage"],
               "staticAnalysis": verified["modules"]["batch"]["spotbugs"],
               "result": "PASS_REPOSITORY_LOG_HANDOFF_RECORDS_AND_RUN_RETIREMENT_ONLY", "programComplete": False}
    (evidence / "logs" / (run + "-summary.json")).write_text(json.dumps(summary, indent=2) + "\n")
    manifest = {key: verified[key] for key in ("runId", "targetCommit", "branch", "startedAt", "completedAt",
                 "exitCode", "command", "environment", "modules", "rawLogSha256")}
    manifest.update({
        "programId": "NK-BAT-001", "scopeResult": "PASS_REPOSITORY_LOG_HANDOFF_RECORDS_AND_RUN_RETIREMENT_ONLY",
        "programComplete": False, "testIdMethods": methods,
        "sharedModuleOwnership": ownership_description(verified["modules"]["batch"]["tests"], len(methods)),
        "fullReactorManifest": "../../008_NK-SCN-001/evidence/manifest.json",
        "fullReactorManifestSha256": hashlib.sha256(full.read_bytes()).hexdigest(),
        "related": ["PG-D-137", "PG-D-138", "SSC-051", "BUG-104", "YKT-092", "BUG-109", "BUG-110", "BUG-111", "YKT-096", "YKT-097", "BUG-112", "YKT-098", "BUG-014", "YKT-012", "BUG-145", "YKT-113"],
        "fixture": "Isolated PostgreSQL18 with real Flyway and five denied roles; literal public log rows, fixed UUID/time, explicit parent transactions and public JDBC fault probes. No deployed credentials or data.",
        "oracle": "001/PT-BAT-001..017: independent8 function names/limits and3 reasons; held2+eligible1 gives2/0/2 then1/1/0 thenEND, run cumulative3/1/2; rollback/savepoint/reconnect/lock do not lose or duplicate counts; UTC/JST/NewYork epoch1789603200 and90day microsecond boundary; no parent connection commit/rollback/close/config mutation; all typed-null/row-count/SQL-stage failures reject; dependency allowlist.",
        "logServiceOracle": "003/PT018..029: held10000 then eligible1 yields three committed chunks and cumulative10001/1/10000; resume initial2/0/2 yields attempt1/1/0; derive initial cumulative by first committed cumulative minus its same-TX chunk; parent reentrant session lock retained, own acquisition released; first/late backup and row locks stop;30min/interrupt/wrap; rollback failure never enables implicit commit; unknown commit/recovery, every JDBC and resource failure, invalid counts/continuity reject before commit; only complete committed/restored/unlocked summary returns0/10.",
        "limitations": "No OS flock, actual backup verification, dedicated main, unit, whole-morning orchestrator, or IT/ST certificate. Repository observations require caller commit; LogCleanupService owns chunk transactions but borrows the parent connection.",
        "sourceFiles": [{"path": str(p.relative_to(repo)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                        for p in sorted((repo / "src/schubert-nk-batch").glob("src/**/*.java"))] +
                       [{"path": "src/schubert-nk-batch/pom.xml", "sha256": hashlib.sha256((repo / "src/schubert-nk-batch/pom.xml").read_bytes()).hexdigest()}],
    })
    manifest["logServiceOracle"] += " BUG145/YKT113: BAT026 crosses real foreign-connection lock contention with result/statement/both close faults, and TIME_LIMIT/INTERRUPTED/BACKUP_GATE with both unlock close faults. All typed failures have zero cause/suppressed after closure; primary reason, interruption and caller connection ownership are preserved; no deletion on lock rejection."
    manifest["related"] += ["PG-D-150", "SSC-049", "BUG-146", "YKT-114"]
    manifest["handoffOracle"] = "005/PT-BAT-030..037: parent single session lock -> child dedicated-role transaction lock -> parent nonblocking reacquire; repeated handoff preserves exact one acquisition. Missing/shared/two-int/reentrant/state/interrupt/null reject, every observed JDBC occurrence and each of5 scalar missing/duplicate/null/flipped/null-resource faults reject, resources close and provider diagnostics stay absent. Child IOException fixed, unexpected Runtime/Error identity preserved, null result never succeeds. A competing real connection/thread in the gap prevents parent success without waiting/force unlock."
    manifest["limitations"] += " InspectorLockHandoff only supplies the borrowed-connection synchronous handoff boundary. Caller must retain OS lock, admit backup/stopped applications/run, confirm child process termination before callback return, avoid sharing parent connection, verify receipts/progress, and dispose parent connection after failure. Actual oneshot and OS/backup orchestration remain unverified."
    manifest["related"] += ["PG-D-156", "SSC-055"]
    manifest["recordOracle"] = "007/PT-BAT-038..045: hand-written ASCII anchor72/activation109/done140 or141 bytes; nil/max UUID, UTC0001/9999 and microseconds, Asia/Tokyo civil date boundaries,0/10 only. Each fixed magic/delimiter byte mutated to all other byte values; aliases, leap normalization, scalar errors, malformed/null and wrong model reject. Valid different identity remains different data, not authentication. Completion invariants, caller-owned arrays, redacted values and64 independent activations use literal field/byte oracles."
    manifest["related"] += ["PG-D-157"]
    manifest["durableRecordOracle"] = "009/PT-BAT-046..057: independent literal records and real private inode/no-replace/fsync with synthetic root admission. Borrowed-root canonical name-to-content binding; bounded read, same-content reuse only, expected-inode retirement, every independently counted native/IO occurrence fails closed and releases owned resources; namespace replacement, metadata/ACL/filesystem, null, invalid IO, interruption and concurrency. No partial-file overwrite or automatic cleanup."
    manifest["related"] += ["PG-D-158", "BUG-159", "BUG-160", "BUG-161", "BUG-162", "YKT-124", "YKT-125", "YKT-126"]
    manifest["lifecycleOracle"] = "011/PT-BAT-058..081: fixed six-root namespace and scope-bound session, complete unfiltered canonical inventory, original-inode snapshots through whole-graph scan, anchor/begin/done/active consistency and unique pending run. Literal start/resume/complete and crash states, no new cutoff on resume, immutable prior completion, same-byte recovery force/directory sync and absent retirement re-sync, independently counted native/IO fault locations, null/closed/interrupt/runtime and concurrency. Root admission is synthetic over actual local inodes; parent OS lock and legacy DB uniqueness are caller obligations."
    manifest["reviewedStaticDiagnostics"] = list(REVIEWED_STATIC_DIAGNOSTICS)
    manifest["related"] += ["PG-D-159", "BUG-163", "BUG-164", "BUG-165", "BUG-166", "YKT-127"]
    manifest["runReferencesOracle"] = "013/BAT082..089: immutable4boolean/3flag OR/inconsistent-empty rejection; realPG reads and fixed UUID/cutoff; explicit read-write READ COMMITTED, own DB advisory required; all16 independently counted JDBC calls including all4 NULL columns and both close failures, missing/duplicate/null resource reject after closure. Initial/final interrupt retained, unknown runtime/NPE not normal, connection ownership/config untouched, fresh rollback and separate-owner concurrent connections. Observation alone never authorizes GC or substitutes for parent lock continuity."
    manifest["related"] += ["PG-D-160", "SSC-056", "PG-D-161", "BUG-171", "BUG-172", "BUG-173", "BUG-174", "YKT-132", "YKT-133", "YKT-134", "YKT-135"]
    manifest["retirementIoFaultPositions"] = 6768
    manifest["related"] += ["PG-D-163", "SSC-055", "BUG-176", "BUG-177", "BUG-178", "YKT-137", "YKT-138", "YKT-139"]
    manifest["parentStepOracle"] = "021/023 BAT130..153: 10 closed steps, fixed immutable handle and 4 terminal statuses/11 reasons; borrowed explicit RW READ_COMMITTED connection, self-db run identity guard before/after. Max99 ordered history, same-run explicit abandonment only, nonbackup daily success skip and backup always rerun. Exact full-handle terminal replay only; no implicit commit/rollback. Independent historical UTC/SQL and 399 JDBC fault positions plus6 double-close pairs, actual rollback/ownership/advisory/row-lock concurrency and all null/invalid projections. Parent child/OS/root/backup orchestration remains incomplete."
    manifest["related"] += ["PG-D-164", "SSC-057", "BUG-179", "YKT-140", "BUG-180", "YKT-141", "BUG-181", "YKT-142"]
    manifest["related"] += ["PG-D-165", "SSC-058", "BUG-182", "BUG-183", "YKT-143", "YKT-144"]
    manifest["related"] += ["PG-D-166", "SSC-059", "BUG-184", "BUG-185", "BUG-186", "YKT-145", "YKT-146"]
    manifest["related"] += ["PG-D-168", "SSC-061", "BUG-191", "BUG-192", "BUG-193", "BUG-194", "YKT-151", "YKT-152", "YKT-153"]
    manifest["related"] += ["PG-D-169", "PG-D-170", "SSC-062", "SSC-063", "BUG-195", "YKT-154", "BUG-196", "YKT-155", "BUG-197", "YKT-156"]
    manifest["related"] += ["PG-D-171", "PG-D-172", "PG-D-173", "PG-D-174", "BUG-198", "YKT-157"]
    manifest["rootManifestReaderOracle"] = "046 BAT226..241: canonical root-owned MANIFEST with full caller step identity; independent964-byte vector and reader result trace. Real held inode/positive-progress bounded4097-byte buffer, metadata/ACL/device/rebinding, all38 I/O and63 clock/interrupt positions, all close scopes/unknown compound and zeroed buffers. Root/backup UID admission remains synthetic; no backup creation or parent completion claim. BUG195 direct scopes repaired, broader YKT154 candidates remain open as enumerated in048."
    manifest["backupPairOracle"] = "041/043 BAT210..225: independent14-column two-row identity/counters/UTC microsecond ends; borrowed RW READ_COMMITTED and advisory owner. Both RUNNING or exact both SUCCESS only; atomic DB+CONFIG completion, rollback and uncertain commit replay without double update. Independently counted repository70/240/70=380 SQL fault positions and service246 positions/interrupt points; unknown primary/cleanup130 compound cases across Backup60+Step70 plus2 original counterexamples. Every owned JDBC resource closes, parent connection remains borrowed; null/Error/Runtime and concurrent isolated connections tested."
    manifest["limitations"] += " Backup pair completion requires caller-trusted root manifest, continuous OS/root/artifact verification. No manifest authentication, dump/tar/age creation, seven-generation retention or whole-parent completion."
    manifest["backupArtifactOracle"] = "038/BAT194..209: independent964byte manifest and public26/35/32byte inputs; actual returned manifest digest, canonical exact4 entries, held inode and final rebinding,0700/0600 owner/device/link/ACL/RW, streaming65535/65536/65537/196613byte fixed SHA256, all123 fallible IO positions and207 clock boundaries. Safe resource closure, read-only unchanged bytes/metadata, null/unknown exception ownership, 64serialized callers. BUG186 final-clock interrupt also rechecked by Log/Step/Inspection executor regression."
    manifest["limitations"] += " BackupArtifactVerifier checks real local held inode/bytes against caller-trusted claims under synthetic root/owner security admission in PT. It is not backup creation, valid pg_dump/tar/age, trusted DB binding, seven-generation retention, parent success or deployed root/NAS verification."
    manifest["backupManifestOracle"] = "033/035 BAT178..193: independent 965-byte canonical JSON/SHA256, immutable nine-field claims and complete two-step binding, microsecond UTC and IANA historical name literals, positive three-file counts/overflow, bounded nonsecret version tokens, exact LF/schema/order, all965 positions mutated with tilde/NUL/nonASCII, null/ownership/64concurrency. Claimed digest metadata only: no actual backup/restore/DB success authorization."
    manifest["sourceFiles"].append({"path": str(fixture.relative_to(repo)), "sha256": hashlib.sha256(fixture.read_bytes()).hexdigest()})
    manifest["atomicCleanupOracle"] = "026/028/030 BAT154..177: seven non-Log kinds and immutable full step handle/counts. V020 DELETE and stored totals atomic; caller transaction repository, service commits bounded1000 chunks. Independent53 repository JDBC failure positions and115 service positions/3 double-close pairs, 1000/1/0 actual chunks, unknown commit resume rereads stored totals; locks/backups never false-END, FK question deferral only. Negative/null/time-wrap/interrupt/continuity/rollback-restoration/runtime and concurrency. Actual output trace independent from fixed collector literal (BUG179/YKT140). Not parent orchestration."
    manifest["atomicCleanupJdbcFaultPositions"] = {"repository": 53, "service": 115, "doubleClosePairs": 3}
    manifest["sourceFiles"].append({"path": "src/schubert-nk-api/src/test/resources/maintenance/step-cleanup-fixture.sql", "sha256": hashlib.sha256((repo / "src/schubert-nk-api/src/test/resources/maintenance/step-cleanup-fixture.sql").read_bytes()).hexdigest()})
    manifest["related"] += ["PG-D-175", "SSC-064", "BUG-199"]
    manifest["related"] += ["PG-D-176", "PG-D-177", "SSC-065", "SSC-066", "BUG-200", "BUG-201", "BUG-202", "BUG-203", "BUG-204", "YKT-158", "YKT-159", "YKT-160"]
    manifest["related"] += ["PG-D-178", "BUG-205", "YKT-161"]
    manifest["related"] += ["PG-D-179", "BUG-206", "YKT-162"]
    manifest["related"] += ["PG-D-180"]
    manifest["related"] += ["PG-D-181", "BUG-207", "YKT-163"]
    manifest["related"] += ["PG-D-182"]
    manifest["related"] += ["PG-D-183"]
    manifest["related"] += ["PG-D-184", "SSC-067"]
    manifest["related"] += ["PG-D-185"]
    manifest["related"] += ["PG-D-239", "BUG-234", "YKT-186"]
    manifest["batchRuntimeDependencyOracle"] = "074/PT-BAT-283: SS341/342 independent Batch process JDBC42.7.13 runtime exactly once; test/compile/system/missing scope, old version and duplicate/absent dependency mutations rejected. Maven runtime-only classpath observed separately. No Batch launcher, credential or actual DB login certificate."
    manifest["related"] += ["PG-D-249", "SSC-077", "SSC-078", "BUG-237", "BUG-238", "YKT-188", "YKT-189"]
    manifest["expiryAuditOracle"] = "076/PT-BAT-284..287: V022 exact UTC microsecond stage, before/target/estimated bytes and unknown after, parent-borrowed transaction with independently observed pre/post commit visibility. Same-run attempt2, rollback, exact terminal replay, field-by-field malformed projection, full-handle/cutoff mismatch and SQL/close/null faults are rejected without raw diagnostics. Repository never commits or removes broker messages; durable parent stage and terminal commit remain mandatory."
    manifest["retirementExecution"] = "072/073 BAT110: unchanged independent26-operation/6768-position oracle, fixed4 workers with independent PG clusters/connections and thread-owned native fixtures. Every injection/fixed failure/resource release assertion retained; exact completed position set and zero duplicates. Three extra clusters stopped after worker completion; no JUnit/component increase or production change."
    manifest["backupCompletionOracle"] = "070/071 BAT274..281: root reader and full artifact verifier precede DB pair completion; independent 161 IO and274 shared clock observations, every IO/deadline/interrupt position, actual PG18 rollback/uncertain commit/replay and fixed microsecond end. Borrowed root and connection; caller supplies continuous exclusion/stopped actors/terminated generation child. No actual archive generation, retention or whole-parent completion claim."
    manifest["batchRunResourceOracle"] = "068/069 BAT151: eight SQL-classified resource scopes,272 compounds plus two null Statement and original provider/same-throwable regressions. History/insert/replay68 each,abandon/finish34 each; scoped fault counts, actual close/live0 and independent snapshots after caller rollback. Provider IAE oracle clarified by prior SSC063/BUG206; malformed projection expectations unchanged. Existing399 fault positions and recovery/skip/replay/related services rerun, no new JUnit/component count."
    manifest["backupStepResourceOracle"] = "066/067 BAT216: pair-only two JDBC scopes,68 independent compounds and original same-throwable regression. SQL-only catch unchanged including provider IAE identity. Exact acquired/unacquired close counts/live0, borrowed connection unchanged and independent RUNNING pair SQL after caller rollback; existing repository/commit16 PT. No new JUnit/component count."
    manifest["cleanupStepResourceOracle"] = "064/065 BAT168: two cleanup-only JDBC scopes and68 independent compounds plus provider/same-throwable regressions. Preserve null-resource SQL contract, narrow pure model validation, exact close/live/injection counters, unchanged borrowed connection and admin SQL rollback oracle. Existing repository/service16 tests rerun, no new JUnit/component count."
    manifest["cleanupResourceOracle"] = "062/063 BAT012: execute/progress four JDBC scopes,136 compound cases plus original provider/same-throwable regressions and four null-resource contract checks. Direct finally close, narrow pure counts/enum validation, exact live/close counters, borrowed connection unchanged and independent empty Log/progress SQL after caller rollback. Log225 and readonly136 compounds rerun; no added JUnit or component count."
    manifest["readOnlyResourceOracle"] = "060/061 BAT087,121: four JDBC release boundaries/136 compound cases plus four original counterexamples; SQL only is known, provider IAE/runtime/NPE/fatal preserve identity, model validation alone becomes fixed SQL failure. Direct finally close, live resources zero, exact owned close counts and no borrowed connection mutation. Log225 compounds also rerun; remaining repositories not certified by this scope."
    manifest["logResourceOracle"] = "058/059 BAT026: five owned SQL/lease release boundaries,225 compound and close-only cases; known SQL/repository/stop reasons versus unknown runtime/NPE/fatal, same throwable identity, fixed secondary, exact acquired-resource close counts, borrowed connection preservation and independent lock reacquisition after caller disposal. Direct JDBC finally close, no added static suppression. Transaction recovery and other repository scopes are separate."
    manifest["backupBundleOracle"] = "055/057 BAT258..273: trusted pending four-file byte/inode/hash verification, held-file force and close, child sync, no-replace directory publication/parent sync, final root reader and full artifact verification. Immutable original directory and four-file identity proof retained across phases rejects same-byte inode replacement (BUG204/YKT160). Independent964-byte manifest and26/35/32 archive vectors;301 I/O observations,514 shared-clock observations without phase budget reset. Synthetic root admission; no actual archive generation, DB success, retention or whole-parent claim."
    manifest["rootManifestPublicationOracle"] = "053 BAT242..257: new-only private0600 held inode, independent964-byte golden, write/force/close/readback/no-replace/directory sync/rebinding; 79 IO and109 clock observations. Synthetic root UID over real Linux FD, not archive generation, final bundle rename, DB success or retention."
    manifest["parentStepJdbcFaultPositions"] = 399
    manifest["parentSummaryOracle"] = "017/BAT114..121: borrowed autoCommit=true RW READ_COMMITTED connection; self DB lock only; no config/commit/close mutations. Missing is Optional.empty, 4 nonnull columns/one row maximum. Independent 16/11 JDBC calls with every SQL fault and both closes, fresh actual PG commit/rollback and historical UTC literal vectors; null/invalid counts/interrupt/runtime reject."
    manifest["inspectionAttemptOracle"] = "019/BAT122..129: same-run END and receipt0/10 match cumulative protection; all3 counts nondecreasing, prior END immutable; handwritten (5,2,3)->(9,5,4) delta(4,3,1), prior completed WARNING stays10 even delta0, MAX/null/identity/receipt/64 parallel vectors. Not a fresh child/OS/backup/step certificate."
    manifest["retirementOracle"] = "015/BAT090..113: literal NKRET1 195..204 bytes and independent one/two-activation SHA256 vectors; full canonical plan count/hash retained through original done/begin/anchor deletion, original-directory durability barriers BEFORE any plan/marker disposal, metadata-only recovery, strict latest-completion400day age, actual PG18 V018 three-reference combinations/identity/query failures, target-only active/pending protection and other-run preservation. Full namespace/graph, bounded record ownership, every native IO occurrence, crash/close/null/interruption/concurrency, no unknown part repair or recursive deletion."
    manifest["limitations"] += " The file scope establishes fixed-namespace, record lifecycle and limited400day retirement under caller exclusion, not actual OS-lock continuity, parent/child lifecycle or whole-morning orchestration. No actual reboot or root deployment."
    manifest["files"] = [{"path": str(p.relative_to(evidence)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                         for p in sorted(evidence.rglob("*")) if p.is_file() and p.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    write_scope_checksums(evidence, manifest["files"])
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
