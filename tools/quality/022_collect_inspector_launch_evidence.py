#!/usr/bin/env python3
"""PG-D-144/146: private launcher, deployment and Linux flock PT, not parent OS acceptance."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from pgpt_evidence_checksums import write_scope_checksums
from pgpt_evidence_destination import evidence_output_root
import bootstrap_ownership

PREFIX = "dev.codex.schubert.nk.api.maintenance."
GROUPS = (
    (PREFIX + "InspectorLaunchConfigurationTest", 221,
     ("validConfiguration", "missingUnknownAndArguments", "scalarBoundaries", "versionAndSnapshotContracts")),
    (PREFIX + "InspectorLauncherTest", 225,
     ("successWarningAndFailureStatus", "expectedFailuresAndRedaction", "nativeFactoryFailure",
      "receiptAndOutputFailure", "nullContracts", "mainAndFatalHandler", "concurrentInvocations", "actualJvmEntry")),
)
DEPLOYMENT_GROUPS = (("dev.codex.schubert.nk.storage.ResourceScopeTest", 1, ("successfulOwnership", "knownIoFailures", "unknownBodyFailures", "knownBodyUnknownCleanup", "unknownCompoundFailures", "nullAndNullableContracts", "nestedScopes", "concurrentScopes")), (PREFIX + "InspectorDeploymentTest", 1,
    ("renderedShellCheck", "statusMapping", "malformedReceipts", "argumentsAndPlaceholders",
     "realMainBridge", "baseUnitAndSyntax", "previousProfiles", "releaseClasspathAndIsolation")),
    ("dev.codex.schubert.nk.storage.LinuxFileLockTest", 1,
     ("nativeRoundTrip", "externalFlockInteroperability", "fcntlIsNotFlock", "callbackFailureAndClose",
      "nativeErrorsAndFlags", "inputAndPlatformContracts", "concurrentSingleWinner", "retainedInodeAndDescriptorLifetime")),
    ("dev.codex.schubert.nk.batch.file.MaintenanceFileLockTest", 1,
     ("admittedRealLock", "contentionAndIndependentInvocations", "rootAndFilesystemPolicy", "inodeAndAttributePolicy",
      "replacementAndPostconditions", "ioAndCloseFailures", "constructorAndNativeBoundary", "fixedProvisioningContract")),
    ("dev.codex.schubert.nk.batch.platform.ApplicationStopGateTest", 1,
     ("literalAndOrder", "nonStoppedStates", "malformedFields", "byteAndNullContracts",
      "gateOrderAndFreshReads", "interruptAndFailure", "concurrentChecks", "factoryAndContracts")),
    ("dev.codex.schubert.nk.batch.platform.SystemctlStateSourceTest", 9,
     ("fixedCommandAndSuccess", "commandFailure", "timeoutAndTermination", "interruptedWait",
      "outputBoundaries", "closeFailures", "nativeEnvironmentAndRead", "nullAndRuntimeContracts")),
    ("dev.codex.schubert.nk.batch.platform.InspectorRunEnvironmentTest", 1,
     ("independentGolden", "mutationAndRunBinding", "boundariesNullAndOwnership", "concurrentUse")),
    ("dev.codex.schubert.nk.batch.platform.InspectorStaticEnvironmentTest", 1,
     ("canonicalFixtures", "sourceAndSyntaxRejection", "urlBoundaries", "versionBoundaries", "sizeNullAndRedaction", "concurrentValidation")),
    ("dev.codex.schubert.nk.batch.file.InspectorEnvironmentReaderTest", 1,
     ("staticReadAndBoundaries", "runReadAndBinding", "permissionAndFilesystem", "metadataAndNull",
      "boundedReadsAndMutation", "inodeReplacementAndOwnership", "ioFaultsAndRedaction", "concurrentAndConstructor")),
    ("dev.codex.schubert.nk.storage.PrivateDirectoryEntryTest", 1,
     ("nativePrivateCreation", "atomicNoReplace", "scopedOwnership", "nameAndNullContracts",
      "faultAndUncertainOutcomes", "retainedNamespace", "concurrentSinglePublication", "unsupportedAndNativeArguments")),
    ("dev.codex.schubert.nk.batch.file.InspectorEnvironmentPublisherTest", 1,
     ("createAndRetire", "sameRunAndDifferentRun", "privatePartCollisions", "permissionsAndNull",
      "boundedWrites", "replacementsAndRetention", "createFailureMatrix", "reuseFailureMatrix",
      "retireFailureMatrix", "interruptionAndRuntime", "concurrentInvocations", "nativeAndConstructor")),
    ("dev.codex.schubert.nk.batch.platform.ConfigurationGroupResolverTest", 1,
     ("canonicalByteBoundaries", "malformedAndNull", "ownedCommandAndExit", "timeoutInterruptAndTermination",
      "stdioFailureMatrix", "sourceBufferAndNoLeak", "concurrentLookup", "nativeFactory")),
    ("dev.codex.schubert.nk.batch.file.InspectorEnvironmentFilesTest", 1,
     ("prepareCallbackRetire", "callbackFailureRetention", "namespaceAndStaticIdentity", "permissionsAndAccounts",
      "allOpenCloseFailures", "lateFailureAndInterruption", "concurrentScopes", "constructorAndFactory")),
    ("dev.codex.schubert.nk.batch.platform.InspectorUnitSnapshotTest", 1,
     ("strictGolden", "propertyInventory", "byteBoundaries", "scalarBounds",
      "quiescentStates", "freshReceipt", "immutabilityAndNull", "concurrentSnapshots")),
    ("dev.codex.schubert.nk.batch.platform.InspectorUnitProbeTest", 9,
     ("fixedCommands", "stableTerminalAndReceipt", "unstableAndNonempty", "commandFailures",
      "boundedOutputAndTimeout", "interruptions", "allResourceFailures", "nativeEnvironmentAndConcurrency")))
SCOPE_SUBJECT = "dev/codex/schubert/nk/storage/ResourceScope"
DEPLOYMENT_GROUPS += (("dev.codex.schubert.nk.storage.ChildDirectoryPublicationTest", 1,
    ("nativeDirectoryPublication", "noReplaceAndSourceType", "nameNullAndClosed", "everyNativeFailure",
     "uncertainPublication", "compoundFailures", "retainedParentCapability", "concurrentNoReplace")),)
FLOCK_SUBJECT = "dev/codex/schubert/nk/storage/LinuxFileLock"
DEPLOYMENT_GROUPS += (("dev.codex.schubert.nk.storage.PrivateChildDirectoryTest", 1,
    ("nativePrivateCreation", "existingEntriesPreserved", "nameNullAndClosed", "everyNativeFailure",
     "compoundFailures", "retainedParentCapability", "unsupportedAdapter", "concurrentNewOnly")),)
PRIVATE_SUBJECTS = tuple("dev/codex/schubert/nk/storage/" + name for name in
    ("DirectoryCalls", "LinuxDirectoryCalls", "OwnedTransferDirectory"))
DEPLOYMENT_GROUPS += (("dev.codex.schubert.nk.api.database.PostgresDeploymentTest", 1,
    ("literalConfiguration", "nativeConfiguration", "literalHba", "nativeHba", "roleTimeouts",
     "invalidConfiguration", "invalidHba", "isolationAndEvidence")),)
DEPLOYMENT_GROUPS += (("dev.codex.schubert.nk.batch.mq.ArtemisReadinessClientTest", 1,
    ("opsMq001ActualBrokerHasSixDurableAnycastPairs", "opsMq002MissingLiveQueueFailsWithoutRecreation",
     "opsMq003EveryAddressAndQueueMismatchFailsClosed", "opsMq004NullProviderFaultAndBorrowedConcurrentSession")),)
DEPLOYMENT_GROUPS += (("dev.codex.schubert.nk.batch.mq.ArtemisManagementReadinessClientTest", 5,
    ("opsMq005ReadsActualBrokerWithoutChangingOrClosingBorrowedSession",
     "opsMq006EveryApprovedValueIsCheckedAndDiskBoundaryIsStrict",
     "opsMq007NullMalformedAndProviderFailureAreRedactedWithoutSessionOwnership",
     "opsMq008ProductionOpsRoleCanReadEffectiveManagementValues",
     "opsMq009MissingManagementReplyIsBoundedAndInterruptIsRestored")),)
DEPLOYMENT_GROUPS += (("dev.codex.schubert.nk.batch.mq.ArtemisAddressSettingsReadinessClientTest", 10,
    ("opsMq010ReadsSixEffectiveSettingsWithOpsRole",
     "opsMq011RejectsEveryCommonAndCapacityDriftAndMissingValues",
     "opsMq012RejectsNullMalformedUnknownAndProviderFailures")),)
DEPLOYMENT_GROUPS += (("dev.codex.schubert.nk.batch.mq.ArtemisAcceptorReadinessClientTest", 13,
    ("opsMq013RealLoopbackCoreAcceptorAndOpsOnlyManagement",
     "opsMq014RejectsEveryAcceptorFieldDriftAndExtraListener",
     "opsMq015NullMalformedStartedAndProviderFailuresAreRedacted")),)
DEPLOYMENT_GROUPS += (("dev.codex.schubert.nk.batch.mq.ArtemisRoleReadinessClientTest", 16,
    ("opsMq016LiveEffectiveSevenRoleMatchesAndApplicationDenial",
     "opsMq017RejectsEachPermissionDriftMissingExcessRoleAndMalformedProjection",
     "opsMq018NullMalformedProviderAndEncoderFailuresAreRedacted")),)
DEPLOYMENT_GROUPS += (("dev.codex.schubert.nk.batch.mq.ArtemisQueuePressureClientTest", 19,
    ("opsMq019LiveSixEmptyQueueMetricsAndApplicationDenial",
     "opsMq020EveryCountAndByteBoundaryIncludingDlqAlert",
     "opsMq021NullInvalidMetricsAndProviderFaultAreRedacted")),)
DEPLOYMENT_GROUPS += (("dev.codex.schubert.nk.batch.mq.ArtemisExpiryManagementAuthorizationTest", 22,
    ("opsMq022MaintenanceCanOnlyInspectAndRemoveSelectedExpiryMessages",)),)
DEPLOYMENT_GROUPS += (("dev.codex.schubert.nk.batch.mq.ArtemisExpiryPurgeClientTest", 23,
    ("opsMq023FixedCutoffCountAndByteReconciliationWithoutCallerSelector",
     "opsMq024RejectsEveryCounterDriftOverflowAndProviderFailure",
     "opsMq025RejectsMissingMalformedOrUnboundedManagementSelector",
     "opsMq026RealBrokerRemovesOnlyActualExpiredMessage",
     "opsMq027RejectsUnstagedOrDriftedObservationBeforeRemove",
     "opsMq028StrictSevenDayCutoffRetainsSubmillisecondPrecision")),)
DEPLOYMENT_GROUPS += (("dev.codex.schubert.nk.batch.mq.ArtemisStartupObservationTest", 29,
    ("opsMq029OrderedReadOnlyObservation", "opsMq030FailClosedAndNoLaterChecks",
     "opsMq031MalformedPressureAndFatalContracts")),)
DEPLOYMENT_GROUPS += ((PREFIX + "ApplicationServiceUnitTest", 1,
    ("apiDependencyCredentialAndResourceContract", "webDependencyCredentialAndResourceContract",
     "noSecretInEnvironmentOrShellAndNoAutomaticWritableEscalation",
     "renderedSyntaxIsAcceptedWithoutStartingService")),)
DEPLOYMENT_GROUPS += (("dev.codex.schubert.nk.api.bootstrap.ApiJdbcPoolTest", 1,
    ("opsDbpool001RealRoleAndFixedConfiguration", "opsDbpool002EightBorrowersAndNinthTimeout",
     "opsDbpool003NullAndUnavailableFailBeforeReady")),
    ("dev.codex.schubert.nk.web.bootstrap.WebJdbcPoolTest", 4,
    ("opsDbpool004RealRoleAndFixedConfiguration", "opsDbpool005TwoBorrowersAndThirdTimeout",
     "opsDbpool006NullAndUnavailableFailBeforeReady")))
DEPLOYMENT_GROUPS += (("dev.codex.schubert.nk.api.bootstrap.ApiNonSecretConfigTest", 1,
    ("opsApiCfg001IndependentDefaultsAndCanonicalHash", "opsApiCfg002LayeredNonSecretOverridesAndScalarTypes",
     "opsApiCfg003YamlsRejectDuplicateUnknownSecretAndStructures", "opsApiCfg004AllFixedKeysUrlsAndRootsFailClosed",
     "opsApiCfg005NullUnknownAndConcurrentDeterminism", "opsApiCfg006ShippedTemplatesMatchApprovedDefaults")),)
DEPLOYMENT_GROUPS += (("dev.codex.schubert.nk.web.bootstrap.WebNonSecretConfigTest", 1,
    ("opsWebCfg001IndependentDefaultsAndCanonicalHash", "opsWebCfg002LayeredRangesAndScalarTypes",
     "opsWebCfg003RejectMalformedUnknownSecretAndDecodedValues", "opsWebCfg004FixedKeysPortsTimeoutsCountsAndRoots",
     "opsWebCfg005NullUnknownAndConcurrentDeterminism", "opsWebCfg006ShippedTemplatesMatchApprovedDefaults",
     "opsWebCfg007ExplicitDbMqSourcesAndNegativeBoundaries")),)
DEPLOYMENT_GROUPS += (("dev.codex.schubert.nk.storage.ServiceConfigFilesTest", 1,
    ("opsCfgfile001FixedNamesAndIndependentBytes", "opsCfgfile002MissingSymlinkAndNonRegularAreRejected",
     "opsCfgfile003LengthEncodingAndModeBoundaries", "opsCfgfile004RootAndFileIdentityPolicy",
     "opsCfgfile005IndependentAttributeMutationMatrix", "opsCfgfile006NullConcurrentAndOwnedCloseFailure",
     "opsCfgfile007MidReadFaultsAndInodeDrift")),)
DEPLOYMENT_GROUPS += (("dev.codex.schubert.nk.storage.ServiceCredentialLocationTest", 1,
    ("opsCredloc001AcceptsPrivateAbsoluteLocationWithoutOtherEnvironmentRetention",
     "opsCredloc002RejectsMissingEmptyRelativeAndRoot",
     "opsCredloc003RejectsAliasTraversalAndControlBytes", "opsCredloc004BoundsAndNullContracts",
     "opsCredloc005ConcurrentFreshMapsDoNotChangeSnapshot")),)
DEPLOYMENT_GROUPS += (("dev.codex.schubert.nk.storage.ServiceCredentialIdTest", 1,
    ("opsCredid001ApiExactlyFiveRequiredIds", "opsCredid002WebExactlyFiveRequiredIds",
     "opsCredid003ServicesAreDisjointAndImmutable", "opsCredid004NullServiceRejected")),)
DEPLOYMENT_GROUPS += (("dev.codex.schubert.nk.api.bootstrap.ApiConfigurationLoaderTest", 1,
    ("opsApiLoad001FixedServiceAndLayerOrder", "opsApiLoad002SourceAndParserFailuresStayDistinct",
     "opsApiLoad003NullContractsAndProductionFactory", "opsApiLoad004ConcurrentFreshReads",
     "opsApiLoad005EnvironmentIsExactBeforeFileRead")),
    ("dev.codex.schubert.nk.web.bootstrap.WebConfigurationLoaderTest", 1,
    ("opsWebLoad001FixedServiceAndLayerOrder", "opsWebLoad002SourceAndParserFailuresStayDistinct",
     "opsWebLoad003NullContractsAndProductionFactory", "opsWebLoad004ConcurrentFreshReads",
     "opsWebLoad005EnvironmentIsExactBeforeFileRead")))
DEPLOYMENT_GROUPS += (("dev.codex.schubert.nk.api.bootstrap.ApiStartupInputsTest", 1,
    ("opsApiInput001CombinesIndependentFixedInputs", "opsApiInput002MissingPrivateLocationStopsBeforeSourceRead",
     "opsApiInput003SourceFailureAndConfigAdmissionStayDistinct", "opsApiInput004NullContracts")),
    ("dev.codex.schubert.nk.web.bootstrap.WebStartupInputsTest", 1,
    ("opsWebInput001CombinesIndependentFixedInputs", "opsWebInput002MissingPrivateLocationStopsBeforeSourceRead",
     "opsWebInput003SourceFailureAndConfigAdmissionStayDistinct", "opsWebInput004NullContracts")))
DEPLOYMENT_GROUPS += (("dev.codex.schubert.nk.api.file.ServiceCredentialReaderTest", 1,
    ("opsCredread001AllFixedIdsReturnOwnedExactBytes",
     "opsCredread002RejectsCrossServiceAndNullBeforeIo",
     "opsCredread003MissingSymlinkAndNonregularFailClosed",
     "opsCredread004RootAndAclAdmissionBeforeContent",
     "opsCredread005KeyPasswordSizeMetadataAndDeviceBoundaries",
     "opsCredread006ReadSizeCloseAndRootDriftFailuresEraseBuffer",
     "opsCredread007EntryCloseAndBorrowedRootLifetime",
     "opsCredread008ConcurrentIndependentOwnedReads",
     "opsCredread009DbAndMqPasswordDecodeWithOwnedCopies",
     "opsCredread010SixKeysDecodeCanonicalCurrentMaterial",
     "opsCredread011KindServiceAndNullRejectBeforeIo",
     "opsCredread012MalformedContentErasesOwnedBytesAndRedacts")),)
DEPLOYMENT_GROUPS += (("dev.codex.schubert.nk.api.maintenance.ServiceDatabaseAdmissionTest", 1,
    ("opsDbadmit001ExactApiAndWebRolesOnIsolatedPg",
     "opsDbadmit002WrongRoleTransactionAndReadonlyRejectWithoutOwningConnection",
     "opsDbadmit003RowsNullMismatchDuplicateAndSqlFaultsFailClosed",
     "opsDbadmit004StrictUrlAndNullContracts")),)
DEPLOYMENT_GROUPS += (("dev.codex.schubert.nk.api.file.ServiceCredentialSetTest", 1,
    ("opsCredset001FiveFixedMaterialsPerServiceAreOwnedAndClosed",
     "opsCredset002WrongIdNullAndClosedStateReject",
     "opsCredset003MissingMalformedAndUncheckedFailureClearPartial",
     "opsCredset004ConcurrentIndependentLoads",
     "opsCredset005CallerMonitorCannotDelaySecretCopyOrClose")),)
DEPLOYMENT_GROUPS += (("dev.codex.schubert.nk.api.bootstrap.ApiProcessMainTest", 1,
    ("opsApiMain001AdmissionBeforeAssemblyAndUnwiredNativeRefusal", "opsApiMain002FailuresAndUnknownRemainNonSuccess",
     "opsApiMain003FatalDiagnosticIsFixed", "opsApiMain004ActualExternalMainRejectsMissingConfigAndArgv")),
    ("dev.codex.schubert.nk.web.bootstrap.WebProcessMainTest", 1,
    ("opsWebMain001AdmissionBeforeAssemblyAndUnwiredNativeRefusal", "opsWebMain002FailuresAndUnknownRemainNonSuccess",
     "opsWebMain003FatalDiagnosticIsFixed", "opsWebMain004ActualExternalMainRejectsMissingConfigAndArgv")))
DEPLOYMENT_GROUPS += (("dev.codex.schubert.nk.api.bootstrap.ServiceDatabaseSourceTest", 1,
    ("opsDbsource001BothFixedRolesAndInputErasure", "opsDbsource002EveryPhysicalPoolConnectionIsAdmitted",
     "opsDbsource003NullProviderWrongRoleAndSqlFailuresCloseBeforeRefusal",
     "opsDbsource004UnknownAndCompoundFailuresPreserveIdentity",
     "opsDbsource005OptionsNullUrlSizeAndConstructorFailureErasure",
     "opsDbsource006ConcurrentConnectionsAndPrivateMonitor")),
    ("dev.codex.schubert.nk.api.file.ServiceProcessResourcesTest", 1,
    ("opsApiRes001RealFiveMaterialsAndAdmittedPoolOwnedScope",
     "opsApiRes002CallbackAndPoolCloseCompoundFailuresDoNotReturnSuccess",
     "opsApiRes003PartialAcquisitionFailureClearsPasswordAndMaterials",
     "opsApiRes004MissingMalformedAndAclFailureNeverCreatesDatabase",
     "opsApiRes005NullAndNativeFactoryBoundaries", "opsApiRes006IndependentConcurrentScopes",
     "opsWebRes001WebOnlyFiveMaterialsTechnicalRoleAndTwoConnectionCeiling")))
DEPLOYMENT_GROUPS += (
    ("dev.codex.schubert.nk.storage.LinuxProcessExecTest", 1, ("opsExec001LiteralVectorsAndArenaLifetime", "opsExec002EveryNativeReturnIsRedactedFailure", "opsExec003InputNullAndPathContracts", "opsExec004VectorAndStringBoundaries", "opsExec005PlatformAndSymbolContracts", "opsExec006UnknownFailureIdentityAndArenaClose", "opsExec007ConcurrentInputsRemainIndependent", "opsExec008ActualReplacementKeepsPidAndOnlyPreparedEnvironment")),
    ("dev.codex.schubert.nk.storage.LinuxExecDescriptorsTest", 1, ("opsXfd001ExactlyTwoFlagsRestoredInReverseOrder", "opsXfd002EveryNativeFailureAndPartialTransition", "opsXfd003IoAndUnknownBodyPreserveOwnership", "opsXfd004CompoundCleanupUnknownPriority", "opsXfd005NullDescriptorAndBoundaryContracts", "opsXfd006PlatformAndSymbolContracts", "opsXfd007ConcurrentDisjointCapabilities", "opsXfd008RealExecInheritsSameFlockUntilProcessExit")),
    ("dev.codex.schubert.nk.storage.LinuxSealedProofTest", 1, ("opsSeal001LiteralBytesFlagsOrderAndScopedClose", "opsSeal002AllCreationSyscallFailuresAndCleanup", "opsSeal003ReadSealEmptyOversizeAndNativeErrors", "opsSeal004BoundaryAndPartialIoIndependentVector", "opsSeal005NullAndPlatformContracts", "opsSeal006UnknownCompoundAndAllOwnedClose", "opsSeal007RealMemfdModeSealsAndMutationRefusal", "opsSeal008NativeConcurrentProofsNeverMix")),
    ("dev.codex.schubert.nk.storage.LinuxHostDirectoryCallsTest", 1, ("opsHost001FixedKernelAnchorAndNativeFlags", "opsHost002NoFollowChildrenAndOwnedCloseForwardOnly", "opsHost003EveryMutationRefusedWithoutDelegation", "opsHost004UidGateAndNativeFailureNeverFallBack", "opsHost005UnknownFailuresKeepIdentityAndArenaClosed", "opsHost006NullPlatformAndSymbolContracts", "opsHost007ActualOrdinaryUidCannotOpenHostAnchor", "opsHost008ConcurrentScopesKeepOnlyOwnPointers")),
    ("dev.codex.schubert.nk.storage.LinuxStartupAdmissionTest", 1, ("childfd001RootSealsImmediateCloexecAndEarlyProofClose", "childfd002EveryDescriptorInputAndNullContractBeforeOwnership", "childfd003BothFdInitialFlagsAllSyscallsAndReadonlyAccess", "childfd004EveryTypedAttributeRootModeLinkSizeAndUnsignedIdentity", "childfd005PayloadNullSizeIoAndProofCloseBeforeCallback", "childfd006UnknownAndCompoundFailurePriorityAndOneClose", "childfd007ConcurrentReadyAndOuterCleanupConsumeAExactlyOnce", "childfd008NativeFactoryBindingsAndOrdinaryUidCannotForgeRootMetadata")),
    ("dev.codex.schubert.nk.batch.file.StartupAdmissionFileTest", 1, ("admissionLock001TwoViewsSameOfdAndReadonlyPrivate", "admissionLock002ContentionAndCrossViewMismatch", "admissionLock003EveryTypedMetadataAndBoundaryRejected", "admissionLock004PhysicalSymlinkReplacementAndNoRepair", "admissionLock005AllIoAndCloseFaultsReleaseEveryOwner", "admissionLock006CompoundUnknownCleanupIsNeverDowngraded", "admissionLock007ConcurrentSingleWinnerAndReusableAfterRelease", "admissionLock008FactoryNullAndActualNioContracts")),
    ("dev.codex.schubert.nk.batch.platform.RootStartupContextTest", 1, ("rootctx001LiteralContextAndTwoObservations", "rootctx002RootProcInitBootAndInvocationDomains", "rootctx003StatStartBoundaryAndPidNamespaceBinding", "rootctx004EveryManagerPropertyAndCgroupRefused", "rootctx005AsciiBoundsNullAndObservationDrift", "rootctx006FixedSystemBusQueryAndAllProcessResults", "rootctx007NativeStreamsFaultsAndUnknownPriority", "rootctx008NativeKernelReadsAndOrdinaryUidRefusal")),
    ("dev.codex.schubert.nk.bootstrap.StartupProofFrameTest", 1, ("proof001IndependentGoldenAndExplicitFieldOrdering", "proof002EveryMissingExtraDuplicateAndNoncanonicalRow", "proof003AsciiByteSizeAndEveryNullContract", "proof004NumericLowerUpperOverflowAndCanonicalDecimals", "proof005StrictSortedGroupsAndInvalidGroupBoundary", "proof006ServiceBootEpochInvocationAndDigestDomains", "proof007ImmutableInputSnapshotAndByteOwnership", "proof008ConcurrentIndependentImmutableFrames")),
    ("dev.codex.schubert.nk.bootstrap.FixedServiceIdentityTest", 1, ("serviceid001BothFixedAccountsExplicitRequiredGroups", "serviceid002EveryFixedRowMalformedMissingAliasAndShadowMarker", "serviceid003UidGidBoundariesAndCanonicalDecimal", "serviceid004PrimaryMismatchDuplicateGroupsAndImplicitMembershipIgnored", "serviceid005ByteNullAndImmutableValueInvariant", "serviceid006NativeQueryTimeoutExitInterruptAndNoInheritedSecrets", "serviceid007EveryOwnedCloseAndUnknownFailurePreserved", "serviceid008ConcurrentLiteralVectorsAndNativeUnprovisionedRejection")),
    ("dev.codex.schubert.nk.bootstrap.ChildStartupContextTest", 1, ("childctx001IndependentGoldenBindingsAndBothUnits", "childctx002EnvironmentMissingAliasNullAndDescriptorBounds", "childctx003EveryAttestedFieldAndNativeIdentityMismatch", "childctx004KernelBoundariesCapabilitiesAndImmutableSnapshots", "childctx005MalformedKernelStatBootPidAndByteInputs", "childctx006EveryStatusMissingDuplicateBoundsAndMalformedValue", "childctx007NullUnknownFailureAndConcurrency", "childctx008NativeProcOnlyDoesNotGrantAuthority")),
)
DEPLOYMENT_GROUPS += (
    ("dev.codex.schubert.nk.batch.platform.BackupArchiveProcessTest", 1, ("fixedCommandAndEnvironment", "inputAndNullContracts", "statusDeadlineAndCancellation", "everyStreamFailureAndCompoundOwnership", "encryptedPipelineIsNotPlaintextArtifact", "actorGatesAndDatabaseListFailure", "concurrentIndependentScopes", "actualNativePublicTarAndBuilder")),
    ("dev.codex.schubert.nk.batch.file.BackupDatabaseCopyTest", 1, ("literalCreationErasureAndBorrowing", "boundaryAndNullContracts", "metadataSecurityAndNamespace", "everyIoPositionAndProgress", "callbackFailureAndRetainedCapability", "erasureAndNameBindings", "repeatedCollisionAndConcurrentRoots", "nativePrivateTmpfsPublicBytes")),
    ("dev.codex.schubert.nk.batch.platform.BackupWorkerRequestTest", 1, ("literalCanonicalAndIndependentDirectory", "dateAndMicroBoundaries", "everyNullAndValueInvariant", "missingExtraAndFixedFieldOrder", "asciiAndBoundedBytes", "uuidAndTimestampNoncanonical", "ownedByteMutationDoesNotMutateRecord", "concurrentIndependentConsumption")),
    ("dev.codex.schubert.nk.batch.platform.BackupUnitTerminationTest", 1, ("bterm001ColdAndPresentStableNamespace", "bterm002EveryPlacementByteAndField", "bterm003EveryMetadataAndFilesystemCondition", "bterm004MissingOnlyAtExactLeafAndDriftRefused", "bterm005AllAcquisitionIoUnknownAndCloseCompounds", "bterm006InterruptAndIndependentParallelInstances", "bterm007FixedQueryProjectionAndNioPort", "bterm008MorningContextAndNativeFactoryFailClosed")),
    ("dev.codex.schubert.nk.batch.platform.MaintenanceStopSnapshotTest", 1, ("mstop001FixedNamesAndIndependentTerminalVectors", "mstop002MissingDuplicateUnknownAndSeparators", "mstop003ByteBoundsNullAndOriginalOwnership", "mstop004FixedPlacementAndNonTerminalStates", "mstop005InvocationAndUnsignedTimestampDomains", "mstop006AbaAndAllFieldChangesStayUnmatched", "mstop007IndependentParallelAndNoAmbientAuthorization")),
    ("dev.codex.schubert.nk.batch.platform.MaintenanceUnitTerminationTest", 1, ("mterm001AllFixedColdAndPresentLeaves", "mterm002UnboundBusyAndNestedProcessRefused", "mterm003AbaCurrentNamespaceAndWrongActor", "mterm004EveryIoUnknownAndClosePosition", "mterm005NullContractsAndAllOwnedMaterials", "mterm006InterruptAndIndependentParallel", "mterm007NativeFixedQueriesAndMaterials", "mterm008NativeFactoryAndOrdinaryHostRefusal")),
    ("dev.codex.schubert.nk.batch.platform.MaintenanceUnitStopPolicyTest", 1, ("mpol001AllEightFixedPolicyAndOrderIndependent", "mpol002MissingDuplicateUnknownAndLineStructure", "mpol003ByteAndNullBounds", "mpol004WrongIdLoadKillAndAutomaticSigkillRefused", "mpol005FixedNativeQueryAndAllProcessOwners", "mpol006KnownUnknownNullAndInterrupts", "mpol007IndependentParallelAndNoStopAuthority")),
    ("dev.codex.schubert.nk.batch.platform.MaintenanceUnitStopClientTest", 1, ("mclient001FixedEightNamesPolicyBeforeExactCommand", "mclient002PolicyAndRootRefusalIssueNoClient", "mclient003ClientNonzeroAndOwnerCloseNeverSucceeds", "mclient004TimeoutRetainsLiveProcessAndReapsSameOwner", "mclient005EveryCloseGetterAndUnknownFailurePoisoned", "mclient006StartAndPostContextUnknownAreNotStopSuccess", "mclient007InterruptionKeepsOwnerWithoutAutomaticKill", "mclient008FactoryNullActorAndHarmlessNativeProcessPort")),
    ("dev.codex.schubert.nk.batch.platform.ArtemisServiceUnitTest", 1, ("artunit001RealFixedDependencyIdentityAndInstance", "artunit002PrivateHashedCredentialIsFixedReadOnlyMount", "artunit003ExactStopAndResourceLimits", "artunit004HardeningAndNoHostSecretMutation")),
    ("dev.codex.schubert.nk.batch.file.RootBatchCredentialReaderTest", 1, ("literalUtf8AndOwnedBuffers", "nullAndFixedName", "everyMetadataAndPolicyBoundary", "allIoAndUnknownPositionsCloseExactlyOnce", "progressSizeAndIndependentCodecNegatives", "mutationAndInterruption", "sharedOwnerConcurrentIndependentMaterial", "nativePortPublicFileOnlyAndWrongActor")),
    ("dev.codex.schubert.nk.batch.repository.MorningDatabaseSessionTest", 1, ("fixedUrlRootConstructorAndNullContracts", "literalAdmissionAndSessionLifetime", "roleRecoveryNullAndLockRejections", "allAdmissionResourceFailuresAndUnknownIdentity", "compoundUnknownAndNullMethodBoundaries", "interruptionAndForeignThreadCannotUseBorrowedSession", "actualBothBackupBeginsAreCommittedTogether", "actualCommitAmbiguityNeverReturnsHandles")),
    ("dev.codex.schubert.nk.batch.file.BackupWorkerRequestFilesTest", 1, ("literalPublicationReadAndRetirement", "nullActorAndPrivateMetadata", "collisionMissingAndFixedNameOnly", "allIoPositionsAndProgress", "sourceCanonicalAndOriginalBinding", "unknownCompoundAndInterrupt", "parallelBorrowedScopesAndNoRepair", "namespaceReadAndRetireUncertainty")),
    ("dev.codex.schubert.nk.batch.file.BackupDatabaseWorkerTest", 1, ("literalRequestDumpAndFullClose", "selfAndUnitAdmissionBeforePrivateIo", "nullBoundariesAndSecretOwnerBeforeAcquisition", "rootMetadataAndOutputBinding", "everyAcquisitionIoAndUnknownFailureCloses", "postconditionsAndCompoundCloseFailure", "newOnlyReplayAndIndependentParallelJobs", "fixedNativeEntryRefusalAndRedactedDiagnostic")),
    ("dev.codex.schubert.nk.api.file.BackupRequestCredentialLoaderTest", 1, ("literalAndOwnedCopy", "boundedSource", "fixedNameMissingAndNoFallback", "everyIoFailureClears", "namespaceAndSecurityFailures", "symlinkAndHardLinkRefused", "closeFailureAndNullContracts", "independentConcurrentCopies")),
    ("dev.codex.schubert.nk.api.file.BackupCredentialLoaderTest", 1, ("literalAndOwnedCopy", "boundedSource", "fixedNameMissingAndNoFallback", "everyIoFailureClears", "namespaceAndSecurityFailures", "symlinkAndHardLinkRefused", "closeFailureAndNullContracts", "independentConcurrentCopies")),
    ("dev.codex.schubert.nk.batch.file.StartupPermitFilesTest", 1, ("originalsAndPublicationOrder", "missingCorruptAndWrongBindings", "metadataAndSecurityMatrix", "everyOwnedIoFaultAndUncertainPublication", "inodeChangesAndNoRepair", "interruptionNullAndUnknownIdentity", "concurrentSinglePublication", "nativeIoAndBorrowedLifetime")),
    ("dev.codex.schubert.nk.batch.file.StartupPermitRecordsTest", 1, ("literalRecords", "syntaxFailures", "identityAndHashFailures", "stateTransitions", "issuedBinding", "cutoffContract", "nullAndOwnership", "concurrentSnapshots")),
    ("dev.codex.schubert.nk.bootstrap.StartupReleaseManifestTest", 1, ("release001ActualBytesFixedGoldenAndNoExportedOwner", "release002SelectorCanonicalBoundariesAndNonfollowTargets", "release003EveryTypedAttributeOwnerModeLinkAndAclRejection", "release004NamespaceAndMetadataChangesAtEveryRecheck", "release005ReadLengthEofBoundaryAndIoFailures", "release006EveryAcquisitionCloseFailureAndUnknownPriority", "release007NullInvariantUnsignedMetadataAndConcurrency", "release008NativeReaderDoesNotBypassOwnershipGate")),
    ("dev.codex.schubert.nk.bootstrap.ServiceStartupAdmissionTest", 1, ("startadmit001MandatoryOrderBeforeBusinessAndReady", "startadmit002MissingInvalidAndUntrustedDescriptorsHaveFactoryZero", "startadmit003MalformedRootProofIsRedactedAndNeverObservesBusiness", "startadmit004IndependentBindingsAndChangedKernelRefuseFactory", "startadmit005EveryObservationFailureAndUnknownIdentity", "startadmit006BusinessFailureCleansBeforeFinalAAndCloseNotSuccess", "startadmit007NullConstructorHashAndDescriptorNames", "startadmit008ConcurrentScopesAndNativeFailureNoBusiness")),
)
DEPLOYMENT_GROUPS += (("dev.codex.schubert.nk.api.maintenance.SchemaHistoryAdmissionTest", 1,
    ("opsSchema001ExactFixedQueryAndBorrowedOwner", "opsSchema002EveryColumnMissingExtraAndFailedRow",
     "opsSchema003ExpectedRowInvariantBoundaries", "opsSchema004ExpectedProfileOrderingAndDefensiveCopy",
     "opsSchema005NullProviderSqlExceptionsAndAllOwnership", "opsSchema006KnownUnknownCloseMatrixAndSameThrowable",
     "opsSchema007InterruptBeforeAndAfterNeverAccepts", "opsSchema008IndependentConcurrentOwners")),)
DEPLOYMENT_GROUPS += (
    ("dev.codex.schubert.nk.bootstrap.ReleaseApprovalTest", 1, ("approval001IndependentLiteral", "approval002VersionBoundaries", "approval003NullAndDigestContracts", "approval004ByteBoundsAndNonAscii", "approval005CanonicalOrderAndKeys", "approval006DefensiveCopies", "approval007ParallelOwners", "approval008HeaderAndFixedProfile")),
    ("dev.codex.schubert.nk.batch.file.RootReleaseApprovalReaderTest", 1, ("approvalRead001FixedLiteralAndClosedOwners", "approvalRead002NullAndNoFallback", "approvalRead003AllMetadataContracts", "approvalRead004EveryIoFaultAndCompoundIdentity", "approvalRead005ReadProgressAndCanonicalMaterial", "approvalRead006NamespaceAndHeldInodeChanges", "approvalRead007InterruptRootAndParallel", "approvalRead008NativePortAndRealContextRefusal")),
    ("dev.codex.schubert.nk.bootstrap.ReleaseSignatureVerifierTest", 1, ("sign001IndependentRfcVectors", "sign002MessageSignatureAndWrongKey", "sign003DerAndNullContracts", "sign004MaterialBoundaries", "sign005SnapshotAndErasedOwnedBuffers", "sign006KnownCryptoFailureIsRedacted", "sign007UnknownFailureIdentityAndErasure", "sign008ConcurrentNativeProviderAndMalformedPoint")),
    ("dev.codex.schubert.nk.bootstrap.ReleaseInventoryTest", 1, ("bomProfile001IndependentLiteralClaims", "bomProfile002FixedKeysTypesAndOrder", "bomProfile003ByteUtf8AndDocumentBounds", "bomProfile004StrictNumbersAndBoundaryValues", "bomProfile005ArtifactLexicalAndNullContracts", "bomProfile006DependencyContractsAndCopies", "bomProfile007RequiredPayloadAndOrdering", "bomProfile008ManagementSelfHashAndAncestorConflicts", "bomProfile009RegisteredLibCompleteSetAndCommonBytes", "bomProfile010SharedVersionsAndRequiredRoles", "bomProfile011SqlNamesRanksAndSchemaVersion", "bomProfile012IntegerNullableAndColumnContracts", "bomProfile013DefensiveInputAndCollections", "bomProfile014CollectionCapsAndExactPositiveBoundaries", "bomProfile015AllMetadataScalarContracts", "bomProfile016IndependentConcurrentParsers")),
    ("dev.codex.schubert.nk.bootstrap.ReleasePayloadVerificationTest", 1, ("fullBom001IndependentLiteralAndAllOwners", "fullBom002ByteInventoryAndNullContracts", "fullBom003ReadonlyAndNamespace", "fullBom004AcquisitionNullAndIo", "fullBom005IndependentSqlVectorsAndEmbeddedAgreement", "fullBom006ThinLayoutAndSharedShadow", "fullBom007IndependentConcurrentScopes", "fullBom008EveryRetainedOwnerAndUntrustedDigest")),
    ("dev.codex.schubert.nk.batch.platform.RootReleaseAdmissionTest", 1, ("rootBom001ClosedLoaderAndFreshBeforeEverySchema", "rootBom002NoPublicClaimsOrBooleanAuthority", "rootBom003EveryMetadataAndNullField", "rootBom004CloseOrChangedRootCannotMint", "rootBom005ActorAndSchemaFailureBeforeBegin", "rootBom006CurrentReloadAndInterruption", "rootBom007FixedOsVectors", "rootBom008IndependentConcurrentOwners")),
)
RUNTIME_SUBJECTS = (
    ("bootstrap", "dev/codex/schubert/nk/bootstrap/ReleasePayloadVerification"),
    ("batch", "dev/codex/schubert/nk/batch/platform/RootReleaseAdmission"),
    ("bootstrap", "dev/codex/schubert/nk/bootstrap/ReleaseApproval"),
    ("batch", "dev/codex/schubert/nk/batch/file/RootReleaseApprovalReader"),
    ("bootstrap", "dev/codex/schubert/nk/bootstrap/ReleaseSignatureVerifier"),
    ("bootstrap", "dev/codex/schubert/nk/bootstrap/ReleaseInventory"),
    ("bootstrap", "dev/codex/schubert/nk/api/bootstrap/SchemaHistoryAdmission"),
    ("bootstrap", "dev/codex/schubert/nk/api/bootstrap/JdbcAdmissionFailures"),
    ("batch", "dev/codex/schubert/nk/batch/platform/BackupArchiveProcess"),
    ("batch", "dev/codex/schubert/nk/batch/platform/BackupWorkerRequest"),
    ("batch", "dev/codex/schubert/nk/batch/file/BackupWorkerRequestFiles"),
    ("batch", "dev/codex/schubert/nk/batch/file/BackupDatabaseWorker"),
    ("batch", "dev/codex/schubert/nk/batch/platform/BackupUnitTermination"),
    ("batch", "dev/codex/schubert/nk/batch/platform/FixedUnitCgroupNamespace"),
    ("batch", "dev/codex/schubert/nk/batch/platform/MaintenanceUnit"),
    ("batch", "dev/codex/schubert/nk/batch/platform/MaintenanceStopSnapshot"),
    ("batch", "dev/codex/schubert/nk/batch/platform/MaintenanceUnitTermination"),
    ("batch", "dev/codex/schubert/nk/batch/platform/MaintenanceUnitStopPolicy"),
    ("batch", "dev/codex/schubert/nk/batch/platform/MaintenanceUnitStopClient"),
    ("batch", "dev/codex/schubert/nk/batch/file/RootBatchCredentialReader"),
    ("batch", "dev/codex/schubert/nk/batch/repository/MorningDatabaseSession"),
    ("batch", "dev/codex/schubert/nk/batch/file/BackupDatabaseCopy"),
    ("batch", "dev/codex/schubert/nk/batch/file/StartupPermitFiles"),
    ("batch", "dev/codex/schubert/nk/batch/file/StartupPermitRecords"),
    ("bootstrap", "dev/codex/schubert/nk/bootstrap/StartupReleaseManifest"),
    ("bootstrap", "dev/codex/schubert/nk/bootstrap/ServiceStartupAdmission"),
    ("storage", "dev/codex/schubert/nk/storage/LinuxProcessExec"),
    ("storage", "dev/codex/schubert/nk/storage/LinuxExecDescriptors"),
    ("storage", "dev/codex/schubert/nk/storage/LinuxSealedProof"),
    ("storage", "dev/codex/schubert/nk/storage/LinuxHostDirectoryCalls"),
    ("storage", "dev/codex/schubert/nk/storage/LinuxStartupAdmission"),
    ("batch", "dev/codex/schubert/nk/batch/file/StartupAdmissionFile"),
    ("batch", "dev/codex/schubert/nk/batch/platform/RootStartupContext"),
    ("bootstrap", "dev/codex/schubert/nk/bootstrap/StartupProofFrame"),
    ("bootstrap", "dev/codex/schubert/nk/bootstrap/FixedServiceIdentity"),
    ("bootstrap", "dev/codex/schubert/nk/bootstrap/ChildStartupContext"),
                    ("api", "dev/codex/schubert/nk/api/bootstrap/ServiceDatabaseSource"),
                    ("api", "dev/codex/schubert/nk/api/file/ServiceProcessResources"),
                    ("api", "dev/codex/schubert/nk/api/bootstrap/ApiProcessMain"),
                    ("web", "dev/codex/schubert/nk/web/bootstrap/WebProcessMain"),
                    ("api", "dev/codex/schubert/nk/api/bootstrap/ApiJdbcPool"),
                    ("web", "dev/codex/schubert/nk/web/bootstrap/WebJdbcPool"),
                    ("api", "dev/codex/schubert/nk/api/bootstrap/ApiNonSecretConfig"),
                    ("web", "dev/codex/schubert/nk/web/bootstrap/WebNonSecretConfig"),
                    ("storage", "dev/codex/schubert/nk/storage/ServiceConfigFiles"),
                    ("storage", "dev/codex/schubert/nk/storage/ServiceCredentialLocation"),
                    ("storage", "dev/codex/schubert/nk/storage/ServiceCredentialId"),
                    ("api", "dev/codex/schubert/nk/api/bootstrap/ApiConfigurationLoader"),
                    ("web", "dev/codex/schubert/nk/web/bootstrap/WebConfigurationLoader"),
                    ("api", "dev/codex/schubert/nk/api/bootstrap/ApiStartupInputs"),
                    ("web", "dev/codex/schubert/nk/web/bootstrap/WebStartupInputs"),
                    ("api", "dev/codex/schubert/nk/api/file/InspectorCredentialLoader"),
                    ("api", "dev/codex/schubert/nk/api/maintenance/InspectorCredentialAccess"),
                    ("api", "dev/codex/schubert/nk/api/file/ServiceCredentialReader"),
                    ("api", "dev/codex/schubert/nk/api/file/ServiceCredentialException"),
                    ("api", "dev/codex/schubert/nk/api/bootstrap/ServiceDatabaseAdmission"),
                    ("api", "dev/codex/schubert/nk/api/file/ServiceCredentialSet"))
POSTGRES_TRACES = {"PT-OPS-PGCFG-008.txt": b"isolated=true\nhostConfigurationChanged=false\nhbaReload=false\nrawDatabaseLogCopied=false\nconfigurationKeys=32\nhbaRules=16\n"}


def module_for(cls):
    if cls in bootstrap_ownership.BOOTSTRAP_TEST:
        return "bootstrap"
    for module in ("api", "web", "batch", "storage"):
        if cls.startswith("dev.codex.schubert.nk." + module + "."):
            return module
    raise ValueError("unknown PT module")


def validate_postgres_traces(traces):
    if traces != POSTGRES_TRACES:
        raise ValueError("missing, extra or invalid PostgreSQL deployment trace")


def validate_postgres_ids(source):
    ids = re.findall(r'@DisplayName\(\s*"(PT-OPS-PGCFG-\d{3})\b', source)
    if len(ids) != 8 or set(ids) != {f"PT-OPS-PGCFG-{i:03}" for i in range(1, 9)}:
        raise ValueError("missing, duplicate or inconsistent PostgreSQL source Test IDs")

LOCK_SUBJECT = "dev/codex/schubert/nk/batch/file/MaintenanceFileLock"
STOP_SUBJECTS = tuple("dev/codex/schubert/nk/batch/platform/" + name for name in
    ("ApplicationUnit", "StopGateFailure", "StopGateException", "UnitStateParser", "ApplicationStopGate", "SystemctlStateSource", "ProcessResourceScope"))
ENV_SUBJECT = "dev/codex/schubert/nk/batch/platform/InspectorRunEnvironment"
CFG_SUBJECT = "dev/codex/schubert/nk/batch/platform/InspectorStaticEnvironment"
EFILE_SUBJECT = "dev/codex/schubert/nk/batch/file/InspectorEnvironmentReader"
PUBLISH_SUBJECTS = tuple("dev/codex/schubert/nk/batch/file/" + name for name in
    ("EnvironmentInodePolicy", "InspectorEnvironmentPublisher"))
NAMESPACE_SUBJECTS = ("dev/codex/schubert/nk/batch/platform/ConfigurationGroupResolver",
                      "dev/codex/schubert/nk/batch/file/InspectorEnvironmentFiles")
UNIT_SUBJECTS = tuple("dev/codex/schubert/nk/batch/platform/" + name for name in
    ("InspectorUnitSnapshot", "InspectorUnitProbe", "ProcessResourceScope"))
MQ_SUBJECTS = tuple("dev/codex/schubert/nk/batch/mq/" + name for name in
    ("ArtemisReadinessClient", "ArtemisReadinessException",
     "ArtemisManagementReadinessClient", "ArtemisManagementReadinessException",
     "ArtemisAddressSettingsReadinessClient", "ArtemisAcceptorReadinessClient",
     "ArtemisRoleReadinessClient", "ArtemisQueuePressureClient", "ArtemisStartupObservation"))
UNIT_TRACES = {
    "PT-OPS-UNIT-001-state.txt": b"quiescent=true\nreceipt=10\nsameInvocationReceipt=none\n",
    "PT-OPS-UNIT-010-receipt-0.txt": b"receipt=0\ncommands=3\n",
    "PT-OPS-UNIT-010-receipt-10.txt": b"receipt=10\ncommands=3\n"}
UNIT_GOLDEN_SHA256 = "2170fc2e71a4ba50519bc2f123d0bf75fcc46adab033645b7b68b5c513c345f6"

def validate_unit_traces(traces):
    if traces != UNIT_TRACES:
        raise ValueError("missing, additional or incorrect Inspector unit observation trace")

def validate_unit_golden(data):
    if len(data) != 373 or hashlib.sha256(data).hexdigest() != UNIT_GOLDEN_SHA256:
        raise ValueError("incorrect independent Inspector unit state fixture")

SUBJECTS = tuple("dev/codex/schubert/nk/api/maintenance/" + c
                 for c in ("InspectorLaunchConfiguration", "InspectorLauncher"))
TRACES = {"renderedShellCheck": 3, "statusMapping": 9, "malformedReceipts": 29,
          "argumentsAndPlaceholders": 3, "realMainBridge": 1, "baseUnitAndSyntax": 1, "previousProfiles": 4}
REVIEWED_STATIC_DIAGNOSTICS = (
    {"method": "MaintenanceFileLock.create", "id": "DMI_HARDCODED_ABSOLUTE_FILENAME", "match": "EXACT", "reason": "UI251/SS341/343 require fixed Linux /run", "owner": "NK-OPS-001 PG", "reviewAt": "PG gate or OS/path/SS change", "testId": "PT-OPS-LOCK-007", "coverageExcluded": False},
    {"method": "InspectorEnvironmentFiles.create", "id": "DMI_HARDCODED_ABSOLUTE_FILENAME", "match": "EXACT", "reason": "UI251/SS343 require fixed Linux /etc and /run", "owner": "NK-OPS-001 PG", "reviewAt": "PG gate or OS/path/SS change", "testId": "PT-OPS-NS-008", "coverageExcluded": False},
    {"method": "MaintenanceRunFiles.create", "id": "DMI_HARDCODED_ABSOLUTE_FILENAME", "match": "EXACT", "reason": "UI251/SS343 require fixed Linux /var", "owner": "NK-BAT-001 PG", "reviewAt": "PG gate or OS/path/SS change", "testId": "PT-BAT-081", "coverageExcluded": False})

# BUG-153/YKT-119: current limitations, not an accumulation of stale milestones.
UNVERIFIED_PARENT_GATES = (
    "OS lock continuity and child termination",
    "durable authoritative run and parent lifecycle", "real backup artifact and full cleanup callers",
    "actual root systemd credential deployment", "actual NK characterization and IT/ST")
DEPLOYMENT_LIMITATIONS = (
    "Scope covers private launcher, wrapper/unit syntax, low-level flock, borrowed-root admission/read/publish, "
    "read-only application stop observations, canonical environment bytes and fixed namespace/NSS callback lifetime. Java coverage is not a shell percentage; "
    "shell decisions use recorded traces. Root UID/GID/tmpfs admission is synthetic over isolated real inodes; "
    "no privileged deployed service acceptance. Flock executes amd64 libc; aarch64 is ABI selection only and "
    "CLOEXEC is checked at the call boundary, not by inherited-FD inspection. Systemctl timeout tests use a process "
    "fault port, not a stalled manager or TERM-ignoring descendant. Borrowed-root publisher requires caller-held "
    "OS lock, stable namespace and terminal child; its success proves none of those. Failed unpublished parts "
    "remain for controlled operational reconciliation. Fixed factory admission uses synthetic root metadata in PT; "
    "actual getent on this unprovisioned host verifies missing-group rejection, not a deployed positive lookup. "
    "Remaining gates: " + "; ".join(UNVERIFIED_PARENT_GATES) + ".")


def validate_reports(suites, deployment=False):
    groups = DEPLOYMENT_GROUPS if deployment else GROUPS
    if len(suites) != len(groups) or {s.get("name") for s in suites} != {g[0] for g in groups}:
        raise ValueError("missing or unmapped launcher/deployment class")
    methods = {}
    for cls, start, expected in groups:
        suite = next(s for s in suites if s.get("name") == cls)
        cases = suite.findall("testcase")
        names = [c.get("name") for c in cases]
        if (suite.get("tests") != str(len(expected))
                or any(int(suite.get(k, "0")) for k in ("failures", "errors", "skipped"))
                or len(names) != len(set(names)) or set(names) != set(expected)
                or any(c.get("classname") != cls or any(child.tag not in ("system-out", "system-err")
                   for child in c) for c in cases)):
            raise ValueError("launcher/deployment PT inventory or status is not certifiable")
        prefix = ({"dev.codex.schubert.nk.storage.ResourceScopeTest": "PT-OPS-RSCOPE",
                   "dev.codex.schubert.nk.storage.LinuxFileLockTest": "PT-OPS-FLOCK",
                   "dev.codex.schubert.nk.storage.LinuxProcessExecTest": "PT-OPS-EXEC",
                   "dev.codex.schubert.nk.storage.LinuxExecDescriptorsTest": "PT-OPS-XFD",
                   "dev.codex.schubert.nk.storage.LinuxSealedProofTest": "PT-OPS-SEAL",
                   "dev.codex.schubert.nk.storage.LinuxHostDirectoryCallsTest": "PT-OPS-HOST",
                   "dev.codex.schubert.nk.storage.LinuxStartupAdmissionTest": "PT-OPS-CHILDFD",
                   "dev.codex.schubert.nk.batch.file.StartupAdmissionFileTest": "PT-OPS-ADMISSIONLOCK",
                   "dev.codex.schubert.nk.batch.platform.RootStartupContextTest": "PT-OPS-ROOTCTX",
                   "dev.codex.schubert.nk.bootstrap.StartupProofFrameTest": "PT-OPS-PROOF",
                   "dev.codex.schubert.nk.bootstrap.FixedServiceIdentityTest": "PT-OPS-SERVICEID",
                   "dev.codex.schubert.nk.bootstrap.ChildStartupContextTest": "PT-OPS-CHILDCTX",
                   "dev.codex.schubert.nk.bootstrap.StartupReleaseManifestTest": "PT-OPS-RELEASE",
                   "dev.codex.schubert.nk.bootstrap.ServiceStartupAdmissionTest": "PT-OPS-STARTADMIT",
                   "dev.codex.schubert.nk.batch.file.StartupPermitRecordsTest": "PT-OPS-PERMITREC",
                   "dev.codex.schubert.nk.batch.file.StartupPermitFilesTest": "PT-OPS-PERMITFILE",
                   "dev.codex.schubert.nk.batch.platform.BackupArchiveProcessTest": "PT-OPS-ARCHPROC",
                   "dev.codex.schubert.nk.batch.file.BackupDatabaseCopyTest": "PT-OPS-DBCP",
                   "dev.codex.schubert.nk.batch.platform.BackupWorkerRequestTest": "PT-OPS-BREQ",
                   "dev.codex.schubert.nk.batch.platform.BackupUnitTerminationTest": "PT-OPS-BTERM",
                   "dev.codex.schubert.nk.batch.platform.MaintenanceStopSnapshotTest": "PT-OPS-MSTOP",
                   "dev.codex.schubert.nk.batch.platform.MaintenanceUnitTerminationTest": "PT-OPS-MTERM",
                   "dev.codex.schubert.nk.batch.platform.MaintenanceUnitStopPolicyTest": "PT-OPS-MPOL",
                   "dev.codex.schubert.nk.batch.platform.MaintenanceUnitStopClientTest": "PT-OPS-MCLIENT",
                   "dev.codex.schubert.nk.batch.platform.ArtemisServiceUnitTest": "PT-OPS-ARTUNIT",
                   "dev.codex.schubert.nk.batch.file.RootBatchCredentialReaderTest": "PT-OPS-RBCR",
                   "dev.codex.schubert.nk.batch.repository.MorningDatabaseSessionTest": "PT-OPS-MDB",
                   "dev.codex.schubert.nk.batch.file.BackupWorkerRequestFilesTest": "PT-OPS-BREQFILE",
                   "dev.codex.schubert.nk.batch.file.BackupDatabaseWorkerTest": "PT-OPS-BWORK",
                   "dev.codex.schubert.nk.api.file.BackupRequestCredentialLoaderTest": "PT-OPS-BREQUESTCRED",
                   "dev.codex.schubert.nk.api.file.BackupCredentialLoaderTest": "PT-OPS-BACKCRED",
                   "dev.codex.schubert.nk.batch.file.MaintenanceFileLockTest": "PT-OPS-LOCK",
                   "dev.codex.schubert.nk.batch.platform.ApplicationStopGateTest": "PT-OPS-STOP",
                   "dev.codex.schubert.nk.batch.platform.SystemctlStateSourceTest": "PT-OPS-STOP",
                   "dev.codex.schubert.nk.batch.platform.InspectorRunEnvironmentTest": "PT-OPS-ENV",
                   "dev.codex.schubert.nk.batch.platform.InspectorStaticEnvironmentTest": "PT-OPS-CFG",
                   "dev.codex.schubert.nk.batch.file.InspectorEnvironmentReaderTest": "PT-OPS-EFILE",
                   "dev.codex.schubert.nk.storage.PrivateDirectoryEntryTest": "PT-OPS-PFILE",
                   "dev.codex.schubert.nk.storage.ChildDirectoryPublicationTest": "PT-OPS-PDIR",
                   "dev.codex.schubert.nk.storage.PrivateChildDirectoryTest": "PT-OPS-CDIR",
                   "dev.codex.schubert.nk.api.database.PostgresDeploymentTest": "PT-OPS-PGCFG",
                   "dev.codex.schubert.nk.batch.file.InspectorEnvironmentPublisherTest": "PT-OPS-PUB",
                   "dev.codex.schubert.nk.batch.platform.ConfigurationGroupResolverTest": "PT-OPS-GID",
                   "dev.codex.schubert.nk.batch.file.InspectorEnvironmentFilesTest": "PT-OPS-NS",
                   "dev.codex.schubert.nk.batch.platform.InspectorUnitSnapshotTest": "PT-OPS-UNIT",
                   "dev.codex.schubert.nk.batch.platform.InspectorUnitProbeTest": "PT-OPS-UNIT",
                   "dev.codex.schubert.nk.batch.mq.ArtemisReadinessClientTest": "PT-OPS-MQ",
                   "dev.codex.schubert.nk.batch.mq.ArtemisManagementReadinessClientTest": "PT-OPS-MQ",
                   "dev.codex.schubert.nk.batch.mq.ArtemisAddressSettingsReadinessClientTest": "PT-OPS-MQ",
                   "dev.codex.schubert.nk.batch.mq.ArtemisAcceptorReadinessClientTest": "PT-OPS-MQ",
                   "dev.codex.schubert.nk.batch.mq.ArtemisRoleReadinessClientTest": "PT-OPS-MQ",
                   "dev.codex.schubert.nk.batch.mq.ArtemisQueuePressureClientTest": "PT-OPS-MQ",
                   "dev.codex.schubert.nk.batch.mq.ArtemisExpiryManagementAuthorizationTest": "PT-OPS-MQ",
                   "dev.codex.schubert.nk.batch.mq.ArtemisExpiryPurgeClientTest": "PT-OPS-MQ",
                   "dev.codex.schubert.nk.batch.mq.ArtemisStartupObservationTest": "PT-OPS-MQ",
                   PREFIX + "ApplicationServiceUnitTest": "PT-OPS-SVC",
                   "dev.codex.schubert.nk.api.bootstrap.ApiJdbcPoolTest": "PT-OPS-DBPOOL",
                   "dev.codex.schubert.nk.web.bootstrap.WebJdbcPoolTest": "PT-OPS-DBPOOL",
                   "dev.codex.schubert.nk.api.bootstrap.ApiNonSecretConfigTest": "PT-OPS-API-CFG",
                   "dev.codex.schubert.nk.web.bootstrap.WebNonSecretConfigTest": "PT-OPS-WEB-CFG",
                   "dev.codex.schubert.nk.storage.ServiceConfigFilesTest": "PT-OPS-CFGFILE",
                   "dev.codex.schubert.nk.storage.ServiceCredentialLocationTest": "PT-OPS-CREDLOC",
                   "dev.codex.schubert.nk.storage.ServiceCredentialIdTest": "PT-OPS-CREDID",
                   "dev.codex.schubert.nk.api.bootstrap.ApiConfigurationLoaderTest": "PT-OPS-API-LOAD",
                   "dev.codex.schubert.nk.web.bootstrap.WebConfigurationLoaderTest": "PT-OPS-WEB-LOAD",
                   "dev.codex.schubert.nk.api.bootstrap.ApiStartupInputsTest": "PT-OPS-API-INPUT",
                   "dev.codex.schubert.nk.web.bootstrap.WebStartupInputsTest": "PT-OPS-WEB-INPUT",
                   "dev.codex.schubert.nk.api.file.ServiceCredentialReaderTest": "PT-OPS-CREDREAD",
                   "dev.codex.schubert.nk.api.maintenance.ServiceDatabaseAdmissionTest": "PT-OPS-DBADMIT",
                   "dev.codex.schubert.nk.api.maintenance.SchemaHistoryAdmissionTest": "PT-OPS-SCHEMA",
                   "dev.codex.schubert.nk.bootstrap.ReleaseApprovalTest": "PT-OPS-APPROVAL",
                   "dev.codex.schubert.nk.batch.file.RootReleaseApprovalReaderTest": "PT-OPS-APPROVALREAD",
                   "dev.codex.schubert.nk.bootstrap.ReleaseSignatureVerifierTest": "PT-OPS-SIGN",
                   "dev.codex.schubert.nk.bootstrap.ReleaseInventoryTest": "PT-OPS-BOMPROFILE",
                   "dev.codex.schubert.nk.bootstrap.ReleasePayloadVerificationTest": "PT-OPS-FULLBOM",
                   "dev.codex.schubert.nk.batch.platform.RootReleaseAdmissionTest": "PT-OPS-ROOTBOM",
                   "dev.codex.schubert.nk.api.file.ServiceCredentialSetTest": "PT-OPS-CREDSET",
                   "dev.codex.schubert.nk.api.bootstrap.ApiProcessMainTest": "PT-OPS-API-MAIN",
                   "dev.codex.schubert.nk.api.bootstrap.ServiceDatabaseSourceTest": "PT-OPS-DBSOURCE",
                   "dev.codex.schubert.nk.api.file.ServiceProcessResourcesTest": "PT-OPS-API-RES",
                   "dev.codex.schubert.nk.web.bootstrap.WebProcessMainTest": "PT-OPS-WEB-MAIN"}.get(cls, "PT-OPS-INBOX")
                  if deployment else "PT-DB-INBOX")
        methods.update({("PT-OPS-WEB-RES-001" if name == "opsWebRes001WebOnlyFiveMaterialsTechnicalRoleAndTwoConnectionCeiling" else f"{prefix}-{i:03}"): cls + "#" + name for i, name in enumerate(expected, start)})
    return methods


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    parser.add_argument("--deployment", action="store_true")
    args = parser.parse_args()
    run = args.run_id
    if not run.startswith("PT-WEB-") or not all(c.isalnum() or c == "-" for c in run):
        raise SystemExit("invalid run ID")
    repo = Path(__file__).resolve().parents[2]
    full = evidence_output_root(repo) / "008_NK-SCN-001/evidence/manifest.json"
    verified = json.loads(full.read_text())
    if verified["runId"] != run or verified["exitCode"] != 0:
        raise SystemExit("matching successful full reactor required")
    subprocess.run(["git", "diff", "--exit-code", verified["targetCommit"], "--", "src", "pom.xml",
                    "program/characterization", "tools/quality"], cwd=repo, check=True)
    target = repo / "src/schubert-nk-api/target"
    groups = DEPLOYMENT_GROUPS if args.deployment else GROUPS
    methods = validate_reports([ET.parse(repo / ("src/schubert-nk-" + module_for(g[0])) / "target/surefire-reports" / ("TEST-" + g[0] + ".xml")).getroot()
                                for g in groups], args.deployment)
    coverage = {}
    for cls in ET.parse(target / "site/jacoco/jacoco.xml").getroot().iter("class"):
        name = cls.get("name")
        if any(name == s or name.startswith(s + "$") for s in SUBJECTS):
            coverage[name] = {c.get("type"): {"missed": int(c.get("missed")), "covered": int(c.get("covered"))}
                             for c in cls.findall("counter")}
    if not set(SUBJECTS).issubset(coverage) or any(c["missed"] for v in coverage.values() for c in v.values()):
        raise SystemExit("missing or incomplete launcher coverage")
    if args.deployment:
        for original_module, subject in RUNTIME_SUBJECTS:
            module = bootstrap_ownership.owner(subject)
            for cls in ET.parse(repo / ("src/schubert-nk-" + module) / "target/site/jacoco/jacoco.xml").getroot().iter("class"):
                name = cls.get("name")
                if name == subject or name.startswith(subject + "$"):
                    coverage[name] = {c.get("type"): {"missed": int(c.get("missed")), "covered": int(c.get("covered"))}
                                     for c in cls.findall("counter")}
        if not {subject for _, subject in RUNTIME_SUBJECTS}.issubset(coverage) or any(c["missed"] for v in coverage.values() for c in v.values()):
            raise SystemExit("missing or incomplete API/Web runtime coverage")
        for module, subject in (("storage", SCOPE_SUBJECT), ("storage", FLOCK_SUBJECT), ("batch", LOCK_SUBJECT),
                                *(("storage", s) for s in PRIVATE_SUBJECTS),
                                *(("batch", s) for s in (*STOP_SUBJECTS, ENV_SUBJECT, CFG_SUBJECT, EFILE_SUBJECT, *PUBLISH_SUBJECTS, *NAMESPACE_SUBJECTS, *UNIT_SUBJECTS, *MQ_SUBJECTS))):
            for cls in ET.parse(repo / ("src/schubert-nk-" + module) / "target/site/jacoco/jacoco.xml").getroot().iter("class"):
                name = cls.get("name")
                if name == subject or name.startswith(subject + "$"):
                    coverage[name] = {c.get("type"): {"missed": int(c.get("missed")), "covered": int(c.get("covered"))}
                                     for c in cls.findall("counter")}
        if not {SCOPE_SUBJECT, FLOCK_SUBJECT, *PRIVATE_SUBJECTS, LOCK_SUBJECT, *STOP_SUBJECTS, ENV_SUBJECT, CFG_SUBJECT, EFILE_SUBJECT, *PUBLISH_SUBJECTS, *NAMESPACE_SUBJECTS, *UNIT_SUBJECTS, *MQ_SUBJECTS}.issubset(coverage) or any(c["missed"] for v in coverage.values() for c in v.values()):
            raise SystemExit("missing or incomplete parent boundary coverage")
    directory = "018_NK-OPS-001/evidence" if args.deployment else "004_NK-DAT-001/evidence/inspector-launch"
    evidence = evidence_output_root(repo) / directory
    evidence.mkdir(parents=True, exist_ok=True)
    program = "NK-OPS-001" if args.deployment else "NK-DAT-001"
    sanitized = ET.Element("testsuite", name=program + "-inspector-launch", tests=str(len(methods)), failures="0", errors="0", skipped="0")
    for test_id, method in methods.items():
        ET.SubElement(sanitized, "testcase", id=test_id, classname=method.split("#")[0], name=method.split("#")[1], result="PASS")
    ET.ElementTree(sanitized).write(evidence / "results.xml", encoding="utf-8", xml_declaration=True)
    sources = [repo / "src/schubert-nk-api/src/main/java" / (s + ".java") for s in SUBJECTS]
    sources += [repo / ("src/schubert-nk-" + module_for(g[0])) / "src/test/java" / (g[0].replace(".", "/") + ".java") for g in groups]
    sources += [repo / "src/schubert-nk-api/pom.xml"]
    if args.deployment:
        sources += [repo / ("src/schubert-nk-" + bootstrap_ownership.owner(subject)) / "src/main/java" / (subject + ".java")
                    for module, subject in RUNTIME_SUBJECTS]
        sources += [repo / "src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/NonSecretConfigSource.java"]
        sources += [bootstrap_ownership.source(repo, "dev.codex.schubert.nk.api.file.InspectorCredentialLoaderTest", test=True)]
        sources += [repo / "src/schubert-nk-bootstrap/pom.xml", repo / "tools/quality/bootstrap_ownership.py"]
        sources += [repo / "src/schubert-nk-web/pom.xml"]
        sources += [repo / "src/deployment/config" / name
                    for name in ("common.yml.template", "api.yml.template", "web.yml.template",
                                 "api.env.template", "web.env.template")]
        sources += [repo / "src/schubert-nk-batch/src/main/java" / (s + ".java") for s in (*STOP_SUBJECTS, ENV_SUBJECT, CFG_SUBJECT, EFILE_SUBJECT, *PUBLISH_SUBJECTS, *NAMESPACE_SUBJECTS, *UNIT_SUBJECTS, *MQ_SUBJECTS)]
        sources += [repo / "src/deployment/postgresql" / name for name in ("postgresql.conf.template", "pg_hba.conf.template")]
        validate_postgres_ids((repo / "src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/database/PostgresDeploymentTest.java").read_text())
        sources += [repo / "src/schubert-nk-api/src/main/resources/db/provisioning/001_roles.sql",
                    bootstrap_ownership.source(repo, "dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture", test=True),
                    bootstrap_ownership.source(repo, "dev.codex.schubert.nk.api.maintenance.MaintenanceJdbcProbe", test=True)]
        postgres_root = target / "postgres-deployment-traces"
        postgres_traces = {str(p.relative_to(postgres_root)): p.read_bytes() for p in postgres_root.rglob("*") if p.is_file()}
        validate_postgres_traces(postgres_traces)
        for name, data in postgres_traces.items():
            destination = evidence / "output/postgresql" / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
        sources += [repo / "src/schubert-nk-storage/src/main/java" / (s + ".java") for s in PRIVATE_SUBJECTS]
        sources += [repo / "src/schubert-nk-storage/src/main/java" / (SCOPE_SUBJECT + ".java"),
                    repo / "src/schubert-nk-storage/src/main/java" / (FLOCK_SUBJECT + ".java"),
                    repo / "src/schubert-nk-storage/pom.xml",
                    repo / "src/schubert-nk-batch/src/main/java" / (LOCK_SUBJECT + ".java"),
                    repo / "src/schubert-nk-batch/pom.xml",
                    repo / "src/deployment/artemis/etc/broker.xml",
                    repo / "src/deployment/tmpfiles/schubert-nk-maintenance.conf"]
        sources += [repo / "src/deployment" / p for p in (
            "operations/inbox-inspector.sh.template", "config/inbox-inspector.env.template", "systemd/schubert-nk-inbox-inspector.service",
            "systemd/optional/inbox-inspector-context-previous.conf", "systemd/optional/inbox-inspector-response-previous.conf",
            "systemd/schubert-nk-api.service.template", "systemd/schubert-nk-web.service.template")]
        unit_root = repo / "src/schubert-nk-batch/target/inspector-unit-traces"
        unit_traces = {str(p.relative_to(unit_root)): p.read_bytes() for p in unit_root.rglob("*") if p.is_file()}
        validate_unit_traces(unit_traces)
        unit_input = repo / "src/schubert-nk-batch/src/test/resources/inspector/unit-golden.txt"
        validate_unit_golden(unit_input.read_bytes())
        sources += [unit_input, repo / "src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/InspectorUnitProbeFixture.java"]
        for relative, data in unit_traces.items():
            destination = evidence / "output/unit" / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
        destination = evidence / "input/unit-golden.txt"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(unit_input.read_bytes())
        audit = repo / "evidence/01_PT/018_NK-OPS-001/025_NK-OPS-001_Inspector終端観測横展開.md"
        destination = evidence / "logs/025_NK-OPS-001_Inspector終端観測横展開.md"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(audit.read_bytes())
        for name in ("031_NK-OPS-001_private子directory単体テスト仕様書.md", "032_NK-OPS-001_private子directory実行結果.md"):
            (evidence / "logs" / name).write_bytes((repo / "evidence/01_PT/018_NK-OPS-001" / name).read_bytes())
        for name in ("033_NK-OPS-001_PostgreSQL配備設定単体テスト仕様書.md", "034_NK-OPS-001_PostgreSQL配備設定実行結果.md",
                     "035_NK-OPS-001_shell診断混線再試験.md",
                     "036_NK-OPS-001_Artemis実効Queue単体テスト仕様書.md",
                     "037_NK-OPS-001_Artemis実効Queue実行結果.md",
                     "038_NK-OPS-001_Artemis起動前観測単体テスト仕様書.md",
                     "039_NK-OPS-001_Artemis起動前観測実行結果.md",
                     "056_NK-OPS-001_WebAPI_service単体テスト仕様書.md",
                     "057_NK-OPS-001_WebAPI_service実行結果.md",
                     "058_NK-OPS-001_WebAPI_DBpool単体テスト仕様書.md",
                     "059_NK-OPS-001_WebAPI_DBpool実行結果.md",
                     "060_NK-OPS-001_API非秘密設定単体テスト仕様書.md",
                     "061_NK-OPS-001_API非秘密設定実行結果.md",
                     "062_NK-OPS-001_Web非秘密設定単体テスト仕様書.md",
                     "063_NK-OPS-001_Web非秘密設定実行結果.md",
                     "064_NK-OPS-001_固定設定実file読取単体テスト仕様書.md",
                     "065_NK-OPS-001_固定設定実file読取実行結果.md",
                     "066_NK-OPS-001_API設定読取結線単体テスト仕様書.md",
                     "067_NK-OPS-001_API設定読取結線実行結果.md",
                     "068_NK-OPS-001_Web設定読取結線単体テスト仕様書.md",
                     "069_NK-OPS-001_Web設定読取結線実行結果.md"):
            (evidence / "logs" / name).write_bytes((repo / "evidence/01_PT/018_NK-OPS-001" / name).read_bytes())
        trace_root = target / "inspector-deployment"
        expected_paths = {f"{method}/{i:03}.json" for method, count in TRACES.items() for i in range(1, count + 1)}
        if {str(p.relative_to(trace_root)) for p in trace_root.rglob("*") if p.is_file()} != expected_paths:
            raise SystemExit("incomplete deployment execution trace inventory")
        for relative in sorted(expected_paths):
            data = json.loads((trace_root / relative).read_text())
            if data["method"] != relative.split("/")[0] or set(data) != {"method", "command", "exitCode", "stdout", "stderr"}:
                raise SystemExit("invalid deployment trace")
            destination = evidence / "logs" / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(json.dumps(data, indent=2) + "\n")
    manifest = {k: verified[k] for k in ("runId", "targetCommit", "branch", "startedAt", "completedAt", "exitCode", "command", "environment", "rawLogSha256")}
    manifest.update({
        "programId": program, "scopeResult": "PASS_DEPLOYMENT_AND_PARENT_BOUNDARIES_ONLY" if args.deployment else "PASS_PRIVATE_LAUNCHER_ONLY",
        "programComplete": False, "testIdMethods": methods, "failed": 0, "errors": 0, "skipped": 0,
        "classCoverage": coverage, "staticAnalysis": verified["modules"]["api"]["spotbugs"],
        "fullReactorManifest": ("../../" if args.deployment else "../../../") + "008_NK-SCN-001/evidence/manifest.json",
        "fullReactorManifestSha256": digest(full), "related": ["QA-046", "UIC-006", "SSC-049", "SSC-053", "PG-D-144", "BUG-136", "BUG-137", "YKT-107", "BUG-014", "YKT-012"],
        "fixture": "Public environment/path/UUID/time/version/receipt vectors only. Fresh real JVM negative tests. OPS uses fixed fake Java and local static unit syntax verification; no host manager/service/credential changes.",
        "oracle": "051/PT221..232: bounded nonsecret canonical input, missing/null/unknown rejection, no parsing diagnostics, exact ASCII receipt after owned resource closure, 0/10/50/70 mapping, unexpected runtime escape/fixed fatal message, native admission negatives,64 independent invocations. 018/PT001..008: fixed receipt byte matrix and JVM exit override; all base directives and4 selected previous-key profiles; actual sh/ShellCheck/systemd-analyze with recorded outputs; release classpath/JDBC runtime/Java25 flags.",
        "limitations": "Java coverage belongs to launcher, not a shell percentage. Parent OS flock/inactive/backup/run binding, root-owned environment validation/publication, actual unit credential provisioning and timeout/TERM behavior, full batch, NK CHR and IT/ST are NOT certified.",
        "sourceFiles": [{"path": str(p.relative_to(repo)), "sha256": digest(p)} for p in sources],
    })
    if args.deployment:
        manifest["staticAnalysisByModule"] = {m: verified["modules"][m]["spotbugs"] for m in ("api", "bootstrap", "web", "storage", "batch")}
        manifest["related"] += ["PG-D-146", "PG-D-147", "PG-D-148", "BUG-140", "YKT-110", "BUG-141", "YKT-111", "BUG-142", "YKT-112", "BUG-143", "YKT-113", "BUG-144", "BUG-145"]
        manifest["reviewedStaticDiagnostics"] = list(REVIEWED_STATIC_DIAGNOSTICS)
        manifest["fixture"] += " FLOCK uses isolated retained regular files, real libc and util-linux2.41.3 with narrow native fault ports. No host lockfile, UID or service mutation."
        manifest["oracle"] += " 003/PT-OPS-FLOCK-001..008: independent flock exit20 while Java holds and Java empty while external holds; fcntl does not conflict; one of32 wins; retained original inode remains locked after path replacement; errno11 alone is contention; fixed open flags0x80000/flock6, close once and IO diagnostic redaction."
        manifest["oracle"] += " 005/PT-OPS-LOCK-001..008: MaintenanceFileLock connects held directories/inode and real flock, requires euid0, root:root0755 directories, root:root0600 empty single-link file, RW tmpfs/access ACL absent, same device and re-open identity before/after callback. All native open/close positions and attributes/FS/ACL faults, null/runtime failure,32 simultaneous requests, no repair and fixed3 boot-only tmpfiles entries are checked."
        manifest["oracle"] += " 007/PT-OPS-STOP-001..016: independent ASCII seven-property vectors, exact loaded/inactive/dead/no Job/zero PID admission; missing/duplicate/unknown/control/1024+1/null rejection; fixed API then Web fresh reads; interrupts preserved and64 concurrent invocations; fixed systemctl argv/5-second wait/1025-byte read; all three stdio close failures crossed with normal/exit/timeout/oversize/read/interrupt; child-only TERM and no force kill; empty inherited environment replaced with exact five nonsecret variables; actual unprovisioned host not-found states rejected."
        manifest["related"] += ["PG-D-149"]
        manifest["related"] += ["BUG-157", "YKT-122"]
        manifest["oracle"] += " BUG157/STOP016: null Process and all three getter runtime/null failures, already-acquired stdio closed exactly once before escape; no wait/read after invalid acquisition, alive lookup child TERM only. GID005 independently regresses the other production Process owner."
        manifest["oracle"] += " 009/PT-OPS-ENV-001..004: SS343 independent two-line ASCII golden; every byte changed to each other possible byte, missing/extra/duplicate/quoted/CRLF/unknown-key input, all128 UUID bit changes and +/-1 microsecond fail exact run binding; years0001/9999, null, caller-owned fresh arrays and64 concurrent results are independently checked."
        manifest["related"] += ["PG-D-151"]
        manifest["oracle"] += " 011/PT-OPS-CFG-001..006: fixed static DB/version two-line ASCII grammar before Map parsing; literal rendered template, port1/65535 and database1/63, version1/16 and unique list65535/65536, wrong source/duplicate/unknown/alias/quotes/controls/high-byte/oversize/null rejection, fixed redaction and64 concurrent checks. Independent SS values, no production-generated expected."
        manifest["related"] += ["PG-D-152", "BUG-147", "YKT-115", "BUG-148", "BUG-149"]
        manifest["oracle"] += " 013/PT-OPS-EFILE-001..008: real retained inode/channel reads with synthetic root/GID/local-FS metadata; exact source and run bytes, metadata types/modes/owner/group/link/size/device/ACL/FS before IO, max+1 bounded EOF and size/identity/time rechecks, same-name replacement rejection, explicit nine-key null/type matrix, every IO/owned-close occurrence, compound raw IO diagnostics stripped,64 reads and start/mid/final interrupts preserved. No source-derived expected or reflection into private production state."
        manifest["related"] += ["PG-D-153", "BUG-150", "YKT-116"]
        manifest["oracle"] += " 015/PT-OPS-PFILE-001..008: real libc CREATE_NEW/NOFOLLOW/0600 and unchanged0640, literal content/mode/link oracle; inode ownership across name replacement, callback/close failures, null/invalid/closed rejection, no-replace publication and sync uncertainty without undo, one of32 concurrent publications with31 retained losers, unsupported default fails without mutation. Shared storage full-class coverage is from the full regression; these8 PT belong only to OPS."
        manifest["related"] += ["PG-D-154", "BUG-151", "YKT-117", "BUG-152", "YKT-118", "BUG-153", "YKT-119"]
        manifest["oracle"] += " 017/PT-OPS-PUB-001..012: literal run bytes and0600 inode conditions, shared EFILE policy, CREATE_NEW plus native no-replace/fsync, bounded writes/readback, same-run re-force/reuse, different-run rejection, preexisting part preservation, same-run retirement with only initial ENOENT idempotence; independent full new/reuse/retire IO occurrence inventories, compound close diagnostics stripped, interrupts preserved, unknown runtime escape and32 serialized callers."
        manifest["related"] += ["PG-D-155", "BUG-154", "BUG-155", "YKT-120", "BUG-156", "YKT-121"]
        manifest["oracle"] += " BUG155/GID008: real isolated pipe4096 with literal65536-byte success,65537 oversize, nonzero exit, timeout and interruption; owned virtual reader drains during process wait, all tasks terminate before zeroing. BUG156/GID005: checked IO is fixed, unknown runtime becomes fixed IllegalStateException without raw cause, Error remains failure."
        manifest["oracle"] += " 019/PT-OPS-GID-001..008/NS-001..008: fixed getent group schubert with three-variable cleared environment,5s/65537-byte bounds, literal unsigned GID/source rejection, owned stdio/zeroed opaque bytes,64 independent lookups. Fixed five-root namespace lifetime with independent account lookup, real inode replacement for every ancestor/static source, stable source/run checks before and after one terminal callback, normal-only retire, all native/IO close occurrence faults, interrupts and32 serialized lifetimes. No target-derived expected GID or secret values."
        manifest["related"] += ["PG-D-170", "SSC-063", "BUG-195", "YKT-154", "BUG-196", "YKT-155", "BUG-197", "YKT-156"]
        manifest["oracle"] += " 027/PT-OPS-RSCOPE-001..008: explicit single close before return, null ownership contracts, nullable callback, known I/O reasons, unknown identity, same-throwable/body-cleanup precedence, nested release order and64 concurrent scopes. UNIT015 and native inode/flock callers independently regress compound failures. Broader YKT154 candidates remain open in017/048."
        manifest["related"] += ["PG-D-167", "SSC-060", "BUG-187", "BUG-188", "BUG-189", "BUG-190", "YKT-147", "YKT-148", "YKT-149", "YKT-150"]
        manifest["oracle"] += " 021/023/PT-OPS-UNIT-001..016: independent 373-byte eighteen-property ASCII golden; canonical uint32/uint64 and InvocationID, all fields missing/duplicate/unknown and numerical/byte boundaries. Fresh receipt0/10 only after stable state-process-state triple and exact empty GetUnitProcesses vector; PID/job alone never enough. Fixed argv/env5,5-second bounded command wait and2049/10-byte reads,11 native operation fault/interrupt positions, three cleanup by three primary compound failures with positive injection/suppressed counts, close-once and zeroed bytes,64 concurrent probes. Actual host checks only reject unprovisioned unit; no startup/termination ownership proof."
        manifest["related"] += ["PG-D-223"]
        manifest["oracle"] += " 036/PT-OPS-MQ-001..004: actual isolated Artemis Core live queries for six literal Address/Queue pairs, missing Queue denial without recreation, each address/queue attribute mutation and provider faults, borrowed session and32 concurrent reads. This is topology only; journal/disk/ACL/settings/thresholds/Expiry purge and production credentials remain mandatory."
        manifest["oracle"] += " 038/PT-OPS-MQ-005..009: isolated live Artemis Core management reads for broker name/persistence/NIO/journal sizing/global memory/duplicate cache/disk bound; independent SS321 literal mutation matrix, 89.9999/90% boundary, null/malformed/provider failure, borrowed-session/no secret leakage. Authenticated nk_ops ephemeral reply Address/Queue succeeds and is removed; nk_api cannot create or query management. Synthetic no-reply proves 2000ms receive/close and checked interrupt flag restoration. Journal recovery error, acceptor, full ACL/address settings/Queue thresholds, Expiry purge and production credential provisioning remain mandatory."
        manifest["related"] += ["PG-D-237", "QA-041", "QA-042", "UIC-001", "UIC-002"]
        manifest["related"] += ["PG-D-240", "PG-D-241", "PG-D-242", "QA-042", "UIC-002", "SSC-075", "YKT-185"]
        manifest["acceptorOracle"] = "042/PT-OPS-MQ-013..015: live Ops Core management getAcceptorsAsJSON plus acceptor.core started; exactly one Netty/tcp/127.0.0.1/61616/CORE and empty extras, app role denied; null/missing/extra/wildcard/AMQP/provider redacted. Not journal recovery, all roles, Queue threshold or full startup."
        manifest["roleOracle"] = "044/PT-OPS-MQ-016..018: live Ops getRolesAsJSON for SS321 six business matches plus management namespace; exact role names and 12 boolean permissions, every permission flip/missing/extra/unknown/malformed/provider redacted, app management denied. JAAS user provisioning and all other startup gates remain separate."
        manifest["queuePressureOracle"] = "046/PT-OPS-MQ-019..021: live six-Queue Ops messageCount/persistentSize, independent SS321 count/byte 70/90 boundary-1/equals/+1 and DLQ one-message alert; missing/negative/type/provider redacted, app role denied. No startup policy or Expiry purge claimed."
        manifest["startupObservationOracle"] = "038/PT-OPS-MQ-029..031: fixed topology→broker→settings→acceptor→roles→six pressure order; any ordinary failure stops later probes with fixed redaction, fatal identity escapes, nullable/missing/extra pressure rejected, borrowed Ops session never closed. This is a read-only observation, not journal recovery, credential provenance, Expiry maintenance or a startup go/no-go."
        manifest["related"] += ["PG-D-269", "PT-OPS-SVC-001..004"]
        manifest["serviceUnitOracle"] = "056/PT-OPS-SVC-001..004/SSC-079/BUG-253/YKT-191: SS342/343 independent API/Web dependency, explicit schubert supplementary group for UI243 release/config 0750/0640 while retaining schubert-read and API schubert-web, five private LoadCredential IDs each, service identity, readonly/write separation, exact JVM resources/hardening and no secret environment/shell; rendered syntax verified with test-only /bin/true and no host manager mutation. Actual OS account group provisioning/file admission, Java entry, credential distribution/DB/JMS/readiness and NK capture are unverified."
        manifest["related"] += ["PG-D-274", "SSC-079", "BUG-253", "YKT-191"]
        manifest["related"] += ["PG-D-271", "PT-OPS-DBPOOL-001..006"]
        manifest["databasePoolOracle"] = "058/PT-OPS-DBPOOL-001..006: two isolated PostgreSQL18 clusters with production DDL roles, SQL current_user/database and cross-schema 42501 denial; HikariCP7.1.0 API max8/min2 and Web max2/min1 with 3000ms wait, actual 8+1/2+1 borrowing, return/reuse, null and unavailable startup rejection. Credential/URL admission, external process and NK capture remain unverified."
        manifest["related"] += ["PG-D-272", "BUG-251", "PT-OPS-API-CFG-001..006"]
        manifest["apiNonSecretConfigOracle"] = "060/PT-OPS-API-CFG-001..006: independent SS343 sorted UTF-8 key=value LF SHA-256 vector and shipped common/api YAML; defaults→common→API merge, six fixed broker addresses, loopback URL bounds, separated absolute roots, unknown/duplicate/secret/alias/multiple-document/type/placeholder/decoded-empty/newline/16KiB rejection and32 deterministic concurrent parses. File identity, env and credential layers and external process readiness are not certified."
        manifest["related"] += ["PG-D-273", "PT-OPS-WEB-CFG-001..006"]
        manifest["webNonSecretConfigOracle"] = "062/PT-OPS-WEB-CFG-001..006: independent SS343 15-key sorted UTF-8 key=value LF SHA-256 vector and shipped common/web YAML; defaults→common→Web merge, fixed session/max-range/loopback, port distinctness, reply 100..2000ms, wait/max/streams bounds, separated absolute roots, unknown/duplicate/secret/alias/multiple-document/type/placeholder/decoded-empty/newline/16KiB rejection and32 deterministic concurrent parses. File identity, env and credential layers and external process readiness are not certified."
        manifest["related"] += ["PG-D-275", "BUG-254", "BUG-255", "PT-OPS-CFGFILE-001..007"]
        manifest["serviceConfigFileOracle"] = "064/PT-OPS-CFGFILE-001..007: independent literal common/api/web UTF-8 bytes; fixed names and root:schubert 0750 / file0640 single-link metadata, same device and held-inode before/after, 1..16384-byte bounds, symlink/nonregular/missing/invalid UTF-8/identity drift and injected mid-read faults, null/concurrent/owned-close checks. Actual account/ACL/filesystem/env/credential/cross-file atomic rollout, Java process integration and readiness are unverified."
        manifest["related"] += ["PG-D-276", "PT-OPS-API-LOAD-001..004", "PT-OPS-WEB-LOAD-001..004"]
        manifest["configLoaderOracle"] = "066/068: independent common DEBUG and API/Web fixed service layer vectors; exact API or Web read once, parser result, source checked failure identity vs fixed malformed YAML, null contracts and32 fresh concurrent reads. Immutable production factory uses fixed ServiceConfigFiles. Actual external Java main/OS/credential/DB/JMS/readiness and NK CHR are unverified."
        manifest["related"] += ["PG-D-277", "SSC-080", "BUG-256", "YKT-192", "PT-OPS-API-LOAD-005", "PT-OPS-WEB-LOAD-005"]
        manifest["environmentOracle"] = "056/PT-OPS-SVC-001/002 and066/068 LOAD005: independent exact single ASCII LF `SCHUBERT_NK_CONFIG_DIR=/etc/schubert-nk` for both required EnvironmentFile templates, fixed path and namespace map admission before source read, missing/other path/lowercase alias/unknown secret-like key rejection without value exposure. systemd manager actual root:service0600 deployment and external Java main remain unverified."
        manifest["related"] += ["PG-D-278", "PT-OPS-CREDLOC-001..005"]
        manifest["credentialLocationOracle"] = "070/PT-OPS-CREDLOC-001..005: independent systemd CREDENTIALS_DIRECTORY nonsecret map admission, absolute normalized nonroot 1..4096-char path, missing/empty/relative/root/case alias/traversal/control/null rejection, unrelated environment nonretention and 32 concurrent fresh-map results. No inode/owner/ACL/readonly/credential byte admission, external main or OS distribution is claimed."
        manifest["related"] += ["PG-D-279", "PT-OPS-API-INPUT-001..004", "PT-OPS-WEB-INPUT-001..004"]
        manifest["startupInputsOracle"] = "072/074: API/Web each receives fixed nonsecret YAML source and systemd CREDENTIALS_DIRECTORY in one nonsecret startup boundary; independent literal DEBUG/config/Path, missing credential location before source IO, checked source failure identity vs fixed invalid config, null contracts and separate immutable result. Does not read a credential, create DB/JMS or launch an external process."
        manifest["related"] += ["PG-D-280", "SSC-081", "PT-OPS-CREDID-001..004"]
        manifest["credentialIdOracle"] = "076/PT-OPS-CREDID-001..004: independent SS342/343 literal API and Web five LoadCredential IDs, password vs fixed-key kind, disjoint service identity, immutable allowlists and null rejection. No credential byte read or OS distribution is claimed."
        manifest["related"] += ["PG-D-281", "SSC-081", "PT-OPS-CREDREAD-001..008"]
        manifest["credentialReaderOracle"] = "078/PT-OPS-CREDREAD-001..008: borrowed retained directory, fixed service ID and existing strict Inspector inode/ACL/readonly admission reused; independent synthetic ten ID bytes, password/key 1..65536/54..69 bounds, same-device, missing/symlink/nonregular/cross-service rejection, root/file drift and IO/entry-close faults, buffer erasure and32 fresh concurrent reads. Test metadata is explicitly synthetic; no actual root/systemd credential distribution, secret format codec, DB/JMS or external process is claimed."
        manifest["related"] += ["PG-D-282", "SSC-081", "PT-OPS-CREDREAD-009..012"]
        manifest["credentialMaterialOracle"] = "080/PT-OPS-CREDREAD-009..012: DB/MQ strict UTF-8 password and six fixed current AES/HMAC keys use established independent Inspector parsers. Explicit test-owned raw arrays are all zero after success and format failure; typed kind/cross-service/null reject before IO; returned material owns destroyable password/key copies. Non-secret synthetic vectors only. This does not establish live secret distribution, DB/MQ driver copy destruction or external process readiness."
        manifest["related"] += ["PG-D-283", "SSC-082", "PT-OPS-DBADMIT-001..004"]
        manifest["databaseAdmissionOracle"] = "082/PT-OPS-DBADMIT-001..004: isolated real PostgreSQL API/Web roles and fixed SELECT current_user/session_user/current_database/recovery, literal loopback URL boundaries, admin/cross-role/transaction/read-only/null/row/SQL/resource-close faults, fixed redacted SQLState08001. Borrowed connection remains caller-owned; actual production DataSource/pool/main readiness is not claimed."
        manifest["related"] += ["PG-D-284", "SSC-081", "BUG-258", "BUG-259", "YKT-194", "PT-OPS-CREDSET-001..005"]
        manifest["credentialSetOracle"] = "084/PT-OPS-CREDSET-001..005: each service fixed five ID order and two Kind enum values, synthetic strict password/key bytes, owned material copies and close, null/kind/cross-service/closed rejection, missing/malformed/unchecked Runtime/Error after partial acquisition, operation buffers erased, 32 independent loads and external caller monitor cannot delay copy/close via private lock. No actual systemd root distribution, DB/MQ driver or external main is claimed."
        manifest["webStaticAnalysis"] = verified["modules"]["web"]["spotbugs"]
        manifest["oracle"] += " 040/PT-OPS-MQ-010..012: authenticated live Core getAddressSettingsAsJSON for all six SS321 business addresses, independent fixed capacity/paging/DLQ/Expiry/retry/auto-create/metric oracle, every checked field mutation/missing/null/malformed/provider failure, borrowed session and temporary reply cleanup. Unknown address resolves Artemis fallback and is rejected by full six-value verifier; raw management reply is not existence proof. Journal recovery, acceptor, full role matrix, Queue thresholds, Expiry purge and production credentials remain mandatory."
        manifest["limitations"] = DEPLOYMENT_LIMITATIONS + " Inspector unit observation is read-only and necessary, not proof of parent-start delivery ordering, callback lifetime, fresh startup ownership or deployed child termination."

        manifest["unverifiedParentGates"] = list(UNVERIFIED_PARENT_GATES)
        manifest["deploymentCoverage"] = {
            "class": "not applicable", "method": "not applicable",
            "basis": "Every executable statement and decision outcome in the hashed shell template has an asserting test and recorded sh -x trace; no code is excluded. Unit is declarative, validated by independent exact directive map, not JaCoCo.",
            "decisions": {"argument count zero/nonzero": "PT004 and PT002", "placeholder absent/present": "PT001/PT004",
                          "JVM success/failure and dot/exclamation marker": "PT002", "hex converter success/failure": "PT002 test-only fixed executable fault",
                          "receipt cases0/10/50/70/default including NUL at all16 positions": "PT002/PT003"},
            "profiles": {"none": 3, "context": 4, "response": 4, "both": 5},
            "tools": {"ShellCheck": "0.11.0", "systemd-analyze": "259.5-0ubuntu3.4", "shell": "/bin/sh", "od": "uutils coreutils0.8.0"},
        }
    if args.deployment:
        manifest["related"] = manifest.get("related", []) + ["PG-D-176", "SSC-065", "PG-D-186", "SSC-068"]
        manifest["related"] += ["PG-D-187", "SSC-069", "BUG-208", "BUG-209", "YKT-164", "YKT-165"]
        manifest["postgresConfigurationOracle"] = "033/034 PGCFG-001..008: independent32-directive map and native PostgreSQL18 -C normalized units/enum/string; exact16 ordered HBA rules and native pg_hba_file_rules with finally restoration/no reload; six roles18 timeouts plus inspector2 unchanged, invalid configuration/HBA canaries. Declarative coverage is complete inventory, not Java percentage. Isolated fixture only, no host deployment or universal primary error MESSAGE redaction claim."
        manifest["privateChildOracle"] = "031/032 CDIR001..008: new-only mkdirat0700, retained NOFOLLOW child, child then parent sync before FD ownership transfer; actual mode/inode/owner and empty namespace, collision preservation, null/closed/native arguments, all four native body fault positions and40 compound cleanup combinations, unsupported default no mutation, retained parent and eight contenders/one winner. Borrowed parent, partial preservation, no chmod/chown/repair. Caller authenticates backup owner/namespace under exclusion; not archive generation or backup success."
        manifest["directoryPublicationOracle"] = "029/PT-OPS-PDIR001..008: retained parent, existing NOFOLLOW directory, same-parent RENAME_NOREPLACE then sync/one child close; literal bytes/inode, all4 native failure positions, compound unknown identity, uncertain final preservation, original parent capability and eight concurrent contenders. Caller exclusion/backup authenticity remain separate."
    manifest["files"] = [{"path": str(p.relative_to(evidence)), "sha256": digest(p)} for p in sorted(evidence.rglob("*"))
                         if p.is_file() and p.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    write_scope_checksums(evidence, manifest["files"])
    print(json.dumps({"runId": run, "tests": len(methods), "scopeResult": manifest["scopeResult"], "programComplete": False}))


if __name__ == "__main__":
    main()
