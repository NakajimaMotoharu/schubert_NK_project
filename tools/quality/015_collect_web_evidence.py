#!/usr/bin/env python3
"""Certify executed Web PT IDs against the verified full reactor; omit raw session and JVM data."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET

from pgpt_evidence_checksums import write_scope_checksums


def validate_session_resource_inventory(mapping):
    expected = {
        "PT-WEB-294": "dev.codex.schubert.nk.web.logging.JdbcWebSessionStoreTest#web294ProviderGetterFailureNeverBecomesInvalidRow",
        "PT-WEB-295": "dev.codex.schubert.nk.web.session.EncryptedWebSessionRepositoryTest#web295ProviderGetterFailureRollsBackWithoutDeletingSession",
        "PT-WEB-296": "dev.codex.schubert.nk.web.logging.JdbcWebSessionStoreTest#web296MalformedRowWithResultCloseFailureIsInfrastructureNotInvalidation",
        "PT-WEB-297": "dev.codex.schubert.nk.web.session.EncryptedWebSessionRepositoryTest#web297MalformedRowAndResultCloseFailureRollsBackWithoutDeletingSession",
        "PT-WEB-298": "dev.codex.schubert.nk.web.logging.JdbcWebSessionStoreTest#web298MalformedRowWithFatalResultClosePropagatesFatalWithoutInvalidation",
    }
    if mapping != expected:
        raise ValueError("Web session resource Test IDs are incomplete or inconsistent")


def validate_log_view_inventory(mapping):
    names = ("web286SuccessfulSnapshot", "web287Pagination", "web288QueryEncoding", "web289ResponseBinding", "web290InvalidFields", "web291NullRoleOwnership", "web292ClosedBeanAndEscaping", "web293ConcurrentViews")
    expected = {f"PT-WEB-{i:03}": "dev.codex.schubert.nk.web.view.LogSearchViewModelTest#" + name for i, name in enumerate(names, 286)}
    if mapping != expected:
        raise ValueError("Log view Test IDs are incomplete or inconsistent")


def validate_log_form_inventory(mapping):
    names = ("web278DefaultsAndFilters", "web279TextAndBinding", "web280Characters", "web281PageAndEnums", "web282Dates", "web283DateRange", "web284NullOwnershipAndRedaction", "web285ConcurrentBinding")
    expected = {f"PT-WEB-{i:03}": "dev.codex.schubert.nk.web.form.LogSearchFormTest#" + name for i, name in enumerate(names, 278)}
    if mapping != expected:
        raise ValueError("Log form Test IDs are incomplete or inconsistent")


def validate_log_results_inventory(mapping):
    names = ("web262CompleteRow", "web263OptionalFields", "web264PageBounds", "web265OrderingAndIdentity", "web266NullRoleAndOwnership", "web267ClosedBeansAndRedaction", "web268SyntheticHtmlEscaping", "web269ConcurrentProjection")
    expected = {f"PT-WEB-{i:03}": "dev.codex.schubert.nk.web.view.LogSearchResultsViewModelTest#" + name
                for i, name in enumerate(names, 262)}
    if mapping != expected:
        raise ValueError("log_results Test IDs are incomplete or inconsistent")


def validate_log_wire_inventory(mapping):
    names = ("web270Requests", "web271SuccessProfiles", "web272ErrorProfiles", "web273MalformedReplies", "web274CapabilitiesAndNull", "web275TransportFailures", "web276ConcurrentRequests", "web277OwnershipAndDiagnostics")
    expected = {f"PT-WEB-{i:03}": "dev.codex.schubert.nk.web.messaging.LogSearchWireClientTest#" + name
                for i, name in enumerate(names, 270)}
    if mapping != expected:
        raise ValueError("log_wire Test IDs are incomplete or inconsistent")


def validate_music_wire_inventory(mapping):
    names = ("web254Requests", "web255SuccessProfiles", "web256ErrorProfiles", "web257MalformedReplies",
             "web258CapabilitiesAndNull", "web259TransportFailures", "web260ConcurrentRequests", "web261OwnershipAndDiagnostics")
    expected = {f"PT-WEB-{i:03}": "dev.codex.schubert.nk.web.messaging.MusicWireClientTest#" + name
                for i, name in enumerate(names, 254)}
    if mapping != expected:
        raise ValueError("Music wire Test IDs are incomplete or inconsistent")


def validate_music_hierarchy_inventory(mapping):
    names = ("web246CategorySnapshot", "web247SectionSnapshot", "web248SizeAndCountBounds", "web249DuplicateAndSegment",
             "web250NullAndOwnership", "web251ClosedBeansAndRedaction", "web252SyntheticHtmlEscaping", "web253ConcurrentProjection")
    expected = {f"PT-WEB-{i:03}": "dev.codex.schubert.nk.web.view.MusicHierarchyViewModelTest#" + name
                for i, name in enumerate(names, 246)}
    if mapping != expected:
        raise ValueError("Music hierarchy Test IDs are incomplete or inconsistent")


def validate_animation_wire_inventory(mapping):
    names = ("web238AnimationRequests", "web239SuccessProfiles", "web240ErrorProfiles",
             "web241MalformedReplies", "web242CapabilitiesAndNull", "web243TransportFailures",
             "web244ConcurrentRequests", "web245OwnershipAndDiagnostics")
    expected = {f"PT-WEB-{i:03}": "dev.codex.schubert.nk.web.messaging.AnimationWireClientTest#" + name
                for i, name in enumerate(names, 238)}
    if mapping != expected:
        raise ValueError("Animation wire Test IDs are incomplete or inconsistent")


def validate_animation_view_inventory(mapping):
    names = ("web230AnimationMenuCounts", "web231MainGrouping", "web232OvaAndBounds", "web233RejectInconsistentGroups",
             "web234NullAndOwnership", "web235ClosedBeansAndRedaction", "web236SyntheticHtmlEscaping", "web237ConcurrentProjection")
    expected = {f"PT-WEB-{i:03}": "dev.codex.schubert.nk.web.view.AnimationViewModelTest#" + name
                for i, name in enumerate(names, 230)}
    if mapping != expected:
        raise ValueError("Animation view Test IDs are incomplete or inconsistent")


def validate_scenario_inventory(mapping):
    names = ("web166SixRequestsMatchIndependentWire", "web167SixSuccessResponsesDecodeWithoutRetainingSecrets",
             "web168ApprovedErrorsNeverExposeSuccessPayload", "web169MalformedUncorrelatedAndForeignResponsesReject",
             "web170InputAndConfigurationFaultsNeverSend", "web171TransportFailuresDoNotRetryOrLeakPending",
             "web172ConcurrentQueriesKeepContextsAndRepliesSeparate", "web173ResponseBoundsAndCallerOwnershipRemainExact")
    expected = {f"PT-WEB-{i:03}": "dev.codex.schubert.nk.web.messaging.ScenarioWireClientTest#" + name
                for i, name in enumerate(names, 166)}
    if mapping != expected:
        raise ValueError("Scenario Web Test IDs are incomplete or inconsistent")


def validate_page_inventory(mapping):
    names = ("web174EmptyAndSinglePage", "web175FirstMiddleAndLastPages",
             "web176MaximumWireBounds", "web177InvalidProjectionCombinations",
             "web178NullConfigurationAndRedaction", "web179IndependentParallelProjection",
             "web180JavaBeanDisplayContract", "web181ThymeleafSyntheticDom")
    expected = {f"PT-WEB-{i:03}": "dev.codex.schubert.nk.web.view.PageViewModelTest#" + name
                for i, name in enumerate(names, 174)}
    if mapping != expected:
        raise ValueError("Page Web Test IDs are incomplete or inconsistent")


def validate_hierarchy_inventory(mapping):
    names = ("web182GameDisplay", "web183RouteDisplay", "web184FileDisplay", "web185NullBoundaries", "web186PrefixBoundaries", "web187SnapshotOwnership", "web188ClosedBeanContract", "web189SyntheticEscaping", "web190ConcurrentProjection", "web191ListSizeBoundaries", "web192PreserveSourceOrder", "web193RedactedDiagnostics")
    expected = {f"PT-WEB-{i:03}": "dev.codex.schubert.nk.web.view.ScenarioHierarchyViewModelTest#" + name
                for i, name in enumerate(names, 182)}
    if mapping != expected:
        raise ValueError("Hierarchy Web Test IDs are incomplete or inconsistent")


def validate_detail_inventory(mapping):
    names = ("web194HeaderAndNavigation", "web195GroupingAndAudio", "web196EmptyAndBounds",
             "web197NullContracts", "web198NavigationPairs", "web199SequenceRejection",
             "web200EntryMetadataConsistency", "web201ImmutableSnapshot", "web202ClosedBeanContract",
             "web203SyntheticHtmlEscaping", "web204ConcurrentProjection", "web205RedactedDiagnostics")
    expected = {f"PT-WEB-{i:03}": "dev.codex.schubert.nk.web.view.ScenarioDetailViewModelTest#" + name
                for i, name in enumerate(names, 194)}
    if mapping != expected:
        raise ValueError("Detail Web Test IDs are incomplete or inconsistent")


def validate_search_inventory(mapping):
    names = ("web206LiteralRowsAndAudio", "web207PageBounds", "web208PageRecordMismatch",
             "web209AudioAndLineInvariants", "web210NullAndOwnership", "web211ClosedBeansAndRedaction",
             "web212SyntheticEscaping", "web213ConcurrentProjection")
    expected = {f"PT-WEB-{i:03}": "dev.codex.schubert.nk.web.view.ScenarioSearchResultsViewModelTest#" + name
                for i, name in enumerate(names, 206)}
    if mapping != expected:
        raise ValueError("Search result Web Test IDs are incomplete or inconsistent")


def validate_search_form_inventory(mapping):
    names = ("web214CanonicalRequest", "web215ByteBoundaries", "web216UnicodeAndEnums",
             "web217BindingAllowlist", "web218PageBoundaries", "web219InvalidCannotRequest",
             "web220NullOwnershipRedaction", "web221ConcurrentValidation")
    expected = {f"PT-WEB-{i:03}": "dev.codex.schubert.nk.web.form.ScenarioSearchFormTest#" + name
                for i, name in enumerate(names, 214)}
    if mapping != expected:
        raise ValueError("Search form Web Test IDs are incomplete or inconsistent")


def validate_search_view_inventory(mapping):
    names = ("web222SuccessfulSnapshot", "web223PaginationUrls", "web224QueryEncoding",
             "web225ResponseBindingAndBounds", "web226InvalidFieldDisplay", "web227NullAndOwnership",
             "web228ClosedBeansAndRedaction", "web229ConcurrentSnapshots")
    expected = {f"PT-WEB-{i:03}": "dev.codex.schubert.nk.web.view.ScenarioSearchViewModelTest#" + name
                for i, name in enumerate(names, 222)}
    if mapping != expected:
        raise ValueError("Search view Web Test IDs are incomplete or inconsistent")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    run = parser.parse_args().run_id
    if not run.startswith("PT-WEB-") or not all(c.isalnum() or c == "-" for c in run):
        raise SystemExit("invalid run ID")
    repo = Path(__file__).resolve().parents[2]
    verified = json.loads((repo / "evidence/01_PT/008_NK-SCN-001/evidence/manifest.json").read_text())
    if verified["runId"] != run or verified["exitCode"] != 0:
        raise SystemExit("collect the matching full verified reactor first")
    subprocess.run(["git", "diff", "--exit-code", verified["targetCommit"], "--", "src", "pom.xml",
                    "program/characterization", "tools/quality"], cwd=repo, check=True,
                   stdout=subprocess.DEVNULL)
    expected = {}
    groups = {
        "dev.codex.schubert.nk.web.session.WebSessionIdTest": (
            (1, "web001CanonicalIdsAndIndependentHashes"),
            (2, "web002NullLengthAlphabetAndUnusedBitsReject"),
            (3, "web003GenerationOwnsAndErasesRandomBuffers"),
            (4, "web004ConcurrentIdsAndHashesShareNoMutableDigest")),
        "dev.codex.schubert.nk.web.security.SavedRequestTargetTest": (
            (5, "web005SafeGetTargetsPreservePathAndQuery"),
            (6, "web006ExternalMalformedAndStateChangingTargetsReject"),
            (7, "web007Utf8LimitAndUnicodeBoundariesAreExact"),
            (8, "web008ConcurrentTargetsRemainIndependent")),
        "dev.codex.schubert.nk.web.session.SessionAttributeCodecTest": (
            (9, "web009AnonymousAndAuthenticatedGoldenJson"),
            (10, "web010PrincipalTokenAndCollectionInvariantsFailFast"),
            (11, "web011UnknownDuplicateNullAndTypesNeverDeserialize"),
            (12, "web012MalformedUtf8AndBoundedDocumentsRejectSafely"),
            (13, "web013UnicodeSavedTargetsAndTokenPurposesPreserveMeaning"),
            (14, "web014IndependentDecodeAcceptsOrderButRejectsInvalidValues"),
            (15, "web015ConcurrentAttributesHaveNoCrossSessionState")),
        "dev.codex.schubert.nk.web.session.SessionPayloadCodecTest": (
            (16, "web016IndependentEnvelopeAndDefensiveOwnership"),
            (17, "web017CurrentPreviousAndUnknownKeyFailClosed"),
            (18, "web018EnvelopeAndEveryAadFieldMutationReject"),
            (19, "web019AuthenticatedInvalidJsonAndSizeBoundariesReject"),
            (20, "web020NullConfigurationIdentityAndClosedLifetime"),
            (21, "web021ConcurrentNonceAndCallerMonitorIsolation"),
            (22, "web022ProviderAndRandomFailuresAreRedacted"),
            (23, "web023RotationKeysAndCloseAreSerialized")),
        "dev.codex.schubert.nk.web.logging.JdbcWebSessionStoreTest": (
            (24, "web024RoundTripCiphertextAndExplicitColumns"),
            (25, "web025CompareAndSwapNoResurrection"),
            (26, "web026CallerTransactionsRollbackFixation"),
            (27, "web027RoleIsolationAndConstraints"),
            (28, "web028NullRowAndConfigurationBoundaries"),
            (29, "web029EveryJdbcFailureIsRedactedAndResourcesClose"),
            (30, "web030InvalidDatabaseRowsFailClosed"),
            (31, "web031ConcurrentLocksAndVersionsStayConsistent"),
            (294, "web294ProviderGetterFailureNeverBecomesInvalidRow")),
        "dev.codex.schubert.nk.web.security.WebCsrfTokenTest": (
            (32, "web032GenerationMatchesIndependentHexAndErasesBuffers"),
            (33, "web033EveryAllowedLengthMatchesOnlyIdenticalToken"),
            (34, "web034MissingMalformedAndNullBoundariesStayRedacted"),
            (35, "web035ConcurrentGenerationAndMatchingStayIndependent")),
        "dev.codex.schubert.nk.web.session.EncryptedWebSessionRepositoryTest": (
            (36, "web036CreateReadRestartAndIdleAreEncrypted"),
            (37, "web037ExpiryAndCorruptRowsCommitInvalidation"),
            (38, "web038MutationPreservesCurrentAttributesAndSecurityIdentity"),
            (39, "web039LoginFixationIsAtomicAndPreservesAllowlist"),
            (40, "web040VersionRolloverPreservesCookieAndRejectsOldPk"),
            (41, "web041DatabaseCryptoAndCommitFailuresNeverGrantSession"),
            (42, "web042NullConfigurationAndIdentityInvariants"),
            (43, "web043ConcurrentReadMutateInvalidateNeverResurrect")),
        "dev.codex.schubert.nk.web.session.SpringWebSessionTest": (
            (44, "web044LifecycleRotateAndTouchPreserveIdentity"),
            (45, "web045ProjectionAndImmediatePersistenceAreClosed"),
            (46, "web046TokenDeltasPreserveConcurrentChanges"),
            (47, "web047RepositoryOwnershipExpiryAndFailuresReject"),
            (48, "web048ServletFilterCookiesRestartAndFixation"),
            (49, "web049ServletInvalidationAndStaleCommitNeverResurrect")),
        "dev.codex.schubert.nk.web.session.WebCsrfIntegrationTest": (
            (50, "web050RepositoryPersistsGeneratesAndInvalidates"),
            (51, "web051OnlySingleBodyParameterResolves"),
            (52, "web052EveryPostRejectsBeforeBusinessWithoutCsrf"),
            (53, "web053FixationExpiryFaultsAndConcurrentRequestsStayBound")),
        "dev.codex.schubert.nk.web.security.MqLoginClientTest": (
            (54, "web054RequestAndSuccessMatchIndependentWire"),
            (55, "web055ErrorProfilesRemainDistinct"),
            (56, "web056InputAndNullContractsNeverSendSecrets"),
            (57, "web057MalformedOrUncorrelatedRepliesNeverAuthenticate"),
            (58, "web058TransportFaultsDoNotBecomeBadCredentials"),
            (59, "web059ConcurrentLoginsKeepIdentityAndOwnership")),
        "dev.codex.schubert.nk.web.security.MqLoginContextProbeTest": (
            (60, "web060ProbeUsesFreshProtectedReadAndValidatesAllRecords"),
            (61, "web061ProbeRejectsMalformedAndFailedReplies"),
            (62, "web062ProbeNullFaultsAndConcurrentCallsStayIsolated")),
        "dev.codex.schubert.nk.web.security.MqAuthenticationProviderTest": (
            (63, "web063DetailsAndLockDelayAreBoundedAndRedacted"),
            (64, "web064FreshAuthenticationConsumesCredentialsAndUsesApiRole"),
            (65, "web065ReplayRequiresCurrentContextBeforeGrant"),
            (66, "web066FailureAndNullTypesNeverBecomeAuthentication"),
            (67, "web067ConcurrentProvidersNeverCrossCredentialsOrPrincipals")),
        "dev.codex.schubert.nk.web.session.SessionSecurityContextTest": (
            (68, "web068ClosedProjectionRejectsForeignAuthentication"),
            (69, "web069DeferredLoadAndCompatibilityRemainRequestScoped"),
            (70, "web070SaveOnlyChecksPersistedIdentityWithoutMutation"),
            (71, "web071StrategyFixatesOncePreservingApprovedAttributes"),
            (72, "web072NullConfigurationAndStorageFaultsFailClosed"),
            (73, "web073ConcurrentLoadAndStaleRequestsNeverResurrect"),
            (74, "web074RealHolderFilterRestoresAndClearsThreadContext"),
            (75, "web075ProviderFixationAndRestoreStayBoundAcrossRequests")),
        "dev.codex.schubert.nk.web.session.SessionSavedRequestTest": (
            (76, "web076AllScreenRoutesAndUtf8BoundariesAreExplicit"),
            (77, "web077UnsafeMethodsEndpointsAndSecretQueriesNeverSave"),
            (78, "web078EncryptedCacheContainsOnlyClosedGetProjection"),
            (79, "web079MatchingConsumesOnlyExactCurrentGetWithoutReplay"),
            (80, "web080NullInvalidSessionAndStorageFailuresAreRedacted"),
            (81, "web081ConcurrentSessionsAndStaleResponsesStayIsolated")),
        "dev.codex.schubert.nk.web.session.SessionFormLoginTest": (
            (82, "web082OnlyDirectLoopbackCaddyHeadersSupplyClientAddress"),
            (83, "web083ProxyNullFaultsAndConcurrentRequestsAreIsolated"),
            (84, "web084FormCreatesOnlyConsumableUntrustedCredentials"),
            (85, "web085MalformedAmbiguousFormsNeverReachAuthentication"),
            (86, "web086ActualCsrfProviderFixationAndHolderChainSucceeds"),
            (87, "web087CsrfAndAuthenticationFailuresNeverGrantOrReplay"),
            (88, "web088FactoryNullMatchingAndExceptionalLifecycleAreBounded"),
            (89, "web089ConcurrentLoginChainsKeepPrincipalsAndCookiesSeparate"),
            (90, "web090UnknownFormNamesAndEnumerationFaultsNeverAuthenticate")),
        "dev.codex.schubert.nk.web.security.WebSecurityHeaderTest": (
            (91, "web091EveryResponseGetsExactNonConflictingSecurityPolicy"),
            (92, "web092RealHeaderFilterWritesBeforeEveryCommitAndAfterReset"),
            (93, "web093NullAndResponseFaultContractsDoNotHideFailures"),
            (94, "web094ConcurrentResponsesHaveNoSharedMutableState")),
        "dev.codex.schubert.nk.web.logging.WebSecurityAuditTest": (
            (95, "web095AllSecurityEventsUseClosedIndependentJson"),
            (96, "web096InvalidEventMetadataNeverReachesLogger"),
            (97, "web097UnicodeAndSecretCanariesRemainOutsideAudit"),
            (98, "web098ClockAndLoggerFaultsNeverBecomeSuccessfulAudit"),
            (99, "web099RepeatedEventsHaveNoMutableJsonOrPrincipalRetention"),
            (100, "web100ConcurrentAuditEventsStayIndependent")),
        "dev.codex.schubert.nk.web.session.WebRequestSecurityTest": (
            (101, "web101ServerIdentityAndTrustedAddressReachOnlyCurrentRequest"),
            (102, "web102RedispatchReusesIdentityButRevalidatesTransport"),
            (103, "web103UntrustedProxyNeverTouchesSessionOrBusiness"),
            (104, "web104NullConfigurationAttributeAndResponseFaultsFailClosed"),
            (105, "web105CsrfDeniedHandlerIgnoresSecretExceptionsAndPreservesSession"),
            (106, "web106ActualCsrfFilterUsesProductionDeniedAudit"),
            (107, "web107DeniedHandlerNullContextAndLoggerFaultsNeverGrant"),
            (108, "web108ConcurrentSecurityRequestsDoNotShareContextOrAudit")),
        "dev.codex.schubert.nk.web.session.EmbeddedWebSecurityTest": (
            (109, "web109RealHttpSessionCsrfAndHeadersMatchContract(Path)"),
            (110, "web110RealErrorDispatchIsBoundedAndRedacted(Path)"),
            (111, "web111RealFormParameterMergingRejectsUnknownAndQueryCredentials(Path)"),
            (112, "web112ConcurrentRealHttpRequestsKeepCookiesAndAuditSeparate(Path)")),
        "dev.codex.schubert.nk.web.session.SessionLoginHandlerTest": (
            (113, "web113SuccessRedirectsOnlyToClosedSavedGet"),
            (114, "web114SuccessRejectsUnpersistedOrInvalidIdentity"),
            (115, "web115FailureAndLockPreserveCurrentRedirectContract"),
            (116, "web116InputServiceAndUnknownFailuresStayDistinct"),
            (117, "web117HandlerNullAndPublicFaultsNeverPretendSuccess"),
            (118, "web118ActualLoginFilterUsesProductionHandlers"),
            (119, "web119ConcurrentHandlerCallsKeepOutcomesSeparate"),
            (120, "web120SuccessResponseFailureDoesNotInventRollback")),
        "dev.codex.schubert.nk.web.security.WebAuthorizationFilterTest": (
            (121, "web121OnlyExplicitPublicResourcesAreAnonymous"),
            (122, "web122RoleMatrixProtectsAdminAndLogs"),
            (123, "web123FirewallAndRedispatchCannotBypassRole"),
            (124, "web124ConcurrentPoliciesHaveNoCrossRequestIdentity")),
        "dev.codex.schubert.nk.web.session.SessionAccessFailureTest": (
            (125, "web125AnonymousGetReturnsToLoginWithOnlySafeSavedRequest"),
            (126, "web126PostAjaxAndMediaNeverRedirectOrReplay"),
            (127, "web127RoleDenialKeepsPrincipalAndRedactsException"),
            (128, "web128NullStorageLoggerAndResponseFaultsRemainFailures"),
            (129, "web129ActualExceptionTranslationUsesEncryptedCacheAndRoleGate"),
            (130, "web130ConcurrentDenialsKeepRequestAndActorSeparate")),
        "dev.codex.schubert.nk.web.session.WebSecurityChainTest": (
            (131, "web131FactoryNullAndClosedComposition"),
            (132, "web132RealHttpLoginReturnsToSavedScreen"),
            (133, "web133RealHttpFailuresNeverGrantAuthentication"),
            (134, "web134RealHttpRoleAndErrorDispatchRemainBound"),
            (135, "web135FirewallRejectionRetainsSafeHeaders"),
            (136, "web136ConcurrentHttpChainsKeepSessionsAndAuditIsolated"),
            (137, "web137ServletPrincipalAndProgrammaticAuthStayClosed")),
        "dev.codex.schubert.nk.web.security.ClosedServletSecurityFilterTest": (
            (138, "web138ClosedPrincipalImplementsServletContract"),
            (139, "web139ProgrammaticAuthenticationCannotBypassCoordination"),
            (140, "web140NullForeignAndDownstreamFaultsStayClosed"),
            (141, "web141ConcurrentAndCrossThreadSnapshotsKeepOriginalActor")),
        "dev.codex.schubert.nk.web.session.MenuMvcTest": (
            (142, "web142MenuModelsPreserveRoleOrderAndClosedFields"),
            (143, "web143MenuBoundaryNullForeignAndModelFaultsReject"),
            (144, "web144MvcConfigurationIsExplicitUtf8AndClosed"),
            (145, "web145RealHttpMenuHasExactCardsAndLogoutCsrf"),
            (146, "web146HtmlEscapesIdentityAndServesOnlySafeResources"),
            (147, "web147ConcurrentMenuRenderingKeepsActorsAndCsrfSeparate")),
        "dev.codex.schubert.nk.web.session.ErrorMvcTest": (
            (148, "web148ErrorCatalogAndModelsAreClosed"),
            (149, "web149DisplaySnapshotAndCsrfRemainRequestScoped"),
            (150, "web150InfrastructureFailuresDoNotLoopOrHideOtherFaults"),
            (151, "web151ErrorControllerIgnoresUnsafeDiagnostics"),
            (152, "web152ErrorTemplatesRenderExactSafeDom"),
            (153, "web153RealHttpErrorsKeepStatusHeadersAndIdentity"),
            (154, "web154DatabaseFailureRendersWithoutReadingSessionAgain"),
            (155, "web155DeniedRequestsKeepOneAuditAndOriginalRequestId"),
            (156, "web156ForgedErrorDispatchNeverBypassesBusinessSecurity"),
            (157, "web157ConcurrentErrorRenderingKeepsRequestActorsSeparate")),
        "dev.codex.schubert.nk.web.session.ApiSessionInvalidTest": (
            (158, "web158ResultCodesHaveIndependentHttpClassification"),
            (159, "web159InvalidHandlerBoundariesNeverUseNativeSession"),
            (160, "web160InvalidHandlerUsesClosedNavigationAndAudit"),
            (161, "web161InvalidationClearsEncryptedSessionAndDisplay"),
            (162, "web162RealHttpExpiredGetReturnsToLogin"),
            (163, "web163RealHttpPostAjaxAndMediaNeverReplay"),
            (164, "web164InvalidationFaultsNeverClaimSuccessfulLogout"),
            (165, "web165ConcurrentAndStaleInvalidationCannotDeleteNewLogin")),
    }
    groups["dev.codex.schubert.nk.web.messaging.ScenarioWireClientTest"] = (
        (166, "web166SixRequestsMatchIndependentWire"),
        (167, "web167SixSuccessResponsesDecodeWithoutRetainingSecrets"),
        (168, "web168ApprovedErrorsNeverExposeSuccessPayload"),
        (169, "web169MalformedUncorrelatedAndForeignResponsesReject"),
        (170, "web170InputAndConfigurationFaultsNeverSend"),
        (171, "web171TransportFailuresDoNotRetryOrLeakPending"),
        (172, "web172ConcurrentQueriesKeepContextsAndRepliesSeparate"),
        (173, "web173ResponseBoundsAndCallerOwnershipRemainExact"))
    groups["dev.codex.schubert.nk.web.view.PageViewModelTest"] = (
        (174, "web174EmptyAndSinglePage"), (175, "web175FirstMiddleAndLastPages"),
        (176, "web176MaximumWireBounds"), (177, "web177InvalidProjectionCombinations"),
        (178, "web178NullConfigurationAndRedaction"), (179, "web179IndependentParallelProjection"),
        (180, "web180JavaBeanDisplayContract"), (181, "web181ThymeleafSyntheticDom"))
    groups["dev.codex.schubert.nk.web.view.ScenarioHierarchyViewModelTest"] = (
        (182, "web182GameDisplay"),
        (183, "web183RouteDisplay"),
        (184, "web184FileDisplay"),
        (185, "web185NullBoundaries"),
        (186, "web186PrefixBoundaries"),
        (187, "web187SnapshotOwnership"),
        (188, "web188ClosedBeanContract"),
        (189, "web189SyntheticEscaping"),
        (190, "web190ConcurrentProjection"),
        (191, "web191ListSizeBoundaries"),
        (192, "web192PreserveSourceOrder"),
        (193, "web193RedactedDiagnostics"),
    )
    groups["dev.codex.schubert.nk.web.view.ScenarioDetailViewModelTest"] = (
        (194, "web194HeaderAndNavigation"), (195, "web195GroupingAndAudio"), (196, "web196EmptyAndBounds"),
        (197, "web197NullContracts"), (198, "web198NavigationPairs"), (199, "web199SequenceRejection"),
        (200, "web200EntryMetadataConsistency"), (201, "web201ImmutableSnapshot"), (202, "web202ClosedBeanContract"),
        (203, "web203SyntheticHtmlEscaping"), (204, "web204ConcurrentProjection"), (205, "web205RedactedDiagnostics"))
    groups["dev.codex.schubert.nk.web.view.ScenarioSearchResultsViewModelTest"] = (
        (206, "web206LiteralRowsAndAudio"), (207, "web207PageBounds"), (208, "web208PageRecordMismatch"),
        (209, "web209AudioAndLineInvariants"), (210, "web210NullAndOwnership"),
        (211, "web211ClosedBeansAndRedaction"), (212, "web212SyntheticEscaping"), (213, "web213ConcurrentProjection"))
    groups["dev.codex.schubert.nk.web.form.ScenarioSearchFormTest"] = (
        (214, "web214CanonicalRequest"), (215, "web215ByteBoundaries"), (216, "web216UnicodeAndEnums"),
        (217, "web217BindingAllowlist"), (218, "web218PageBoundaries"), (219, "web219InvalidCannotRequest"),
        (220, "web220NullOwnershipRedaction"), (221, "web221ConcurrentValidation"))
    groups["dev.codex.schubert.nk.web.view.ScenarioSearchViewModelTest"] = (
        (222, "web222SuccessfulSnapshot"), (223, "web223PaginationUrls"), (224, "web224QueryEncoding"),
        (225, "web225ResponseBindingAndBounds"), (226, "web226InvalidFieldDisplay"),
        (227, "web227NullAndOwnership"), (228, "web228ClosedBeansAndRedaction"), (229, "web229ConcurrentSnapshots"))
    groups["dev.codex.schubert.nk.web.view.AnimationViewModelTest"] = (
        (230, "web230AnimationMenuCounts"), (231, "web231MainGrouping"), (232, "web232OvaAndBounds"),
        (233, "web233RejectInconsistentGroups"), (234, "web234NullAndOwnership"), (235, "web235ClosedBeansAndRedaction"),
        (236, "web236SyntheticHtmlEscaping"), (237, "web237ConcurrentProjection"))
    groups["dev.codex.schubert.nk.web.messaging.AnimationWireClientTest"] = (
        (238, "web238AnimationRequests"), (239, "web239SuccessProfiles"), (240, "web240ErrorProfiles"),
        (241, "web241MalformedReplies"), (242, "web242CapabilitiesAndNull"),
        (243, "web243TransportFailures"), (244, "web244ConcurrentRequests"), (245, "web245OwnershipAndDiagnostics"))
    groups["dev.codex.schubert.nk.web.view.MusicHierarchyViewModelTest"] = (
        (246, "web246CategorySnapshot"), (247, "web247SectionSnapshot"), (248, "web248SizeAndCountBounds"),
        (249, "web249DuplicateAndSegment"), (250, "web250NullAndOwnership"), (251, "web251ClosedBeansAndRedaction"),
        (252, "web252SyntheticHtmlEscaping"), (253, "web253ConcurrentProjection"))
    groups["dev.codex.schubert.nk.web.messaging.MusicWireClientTest"] = (
        (254, "web254Requests"), (255, "web255SuccessProfiles"), (256, "web256ErrorProfiles"),
        (257, "web257MalformedReplies"), (258, "web258CapabilitiesAndNull"), (259, "web259TransportFailures"),
        (260, "web260ConcurrentRequests"), (261, "web261OwnershipAndDiagnostics"))
    groups["dev.codex.schubert.nk.web.view.LogSearchResultsViewModelTest"] = ((262, "web262CompleteRow"), (263, "web263OptionalFields"), (264, "web264PageBounds"), (265, "web265OrderingAndIdentity"), (266, "web266NullRoleAndOwnership"), (267, "web267ClosedBeansAndRedaction"), (268, "web268SyntheticHtmlEscaping"), (269, "web269ConcurrentProjection"))
    groups["dev.codex.schubert.nk.web.messaging.LogSearchWireClientTest"] = ((270, "web270Requests"), (271, "web271SuccessProfiles"), (272, "web272ErrorProfiles"), (273, "web273MalformedReplies"), (274, "web274CapabilitiesAndNull"), (275, "web275TransportFailures"), (276, "web276ConcurrentRequests"), (277, "web277OwnershipAndDiagnostics"))
    groups["dev.codex.schubert.nk.web.form.LogSearchFormTest"] = ((278, "web278DefaultsAndFilters"), (279, "web279TextAndBinding"), (280, "web280Characters"), (281, "web281PageAndEnums"), (282, "web282Dates"), (283, "web283DateRange"), (284, "web284NullOwnershipAndRedaction"), (285, "web285ConcurrentBinding"))
    groups["dev.codex.schubert.nk.web.view.LogSearchViewModelTest"] = ((286, "web286SuccessfulSnapshot"), (287, "web287Pagination"), (288, "web288QueryEncoding"), (289, "web289ResponseBinding"), (290, "web290InvalidFields"), (291, "web291NullRoleOwnership"), (292, "web292ClosedBeanAndEscaping"), (293, "web293ConcurrentViews"))
    groups["dev.codex.schubert.nk.web.session.EncryptedWebSessionRepositoryTest"] += ((295, "web295ProviderGetterFailureRollsBackWithoutDeletingSession"),)
    groups["dev.codex.schubert.nk.web.logging.JdbcWebSessionStoreTest"] += ((296, "web296MalformedRowWithResultCloseFailureIsInfrastructureNotInvalidation"),)
    groups["dev.codex.schubert.nk.web.session.EncryptedWebSessionRepositoryTest"] += ((297, "web297MalformedRowAndResultCloseFailureRollsBackWithoutDeletingSession"),)
    groups["dev.codex.schubert.nk.web.logging.JdbcWebSessionStoreTest"] += ((298, "web298MalformedRowWithFatalResultClosePropagatesFatalWithoutInvalidation"),)
    methods, reports = [], {}
    for classname, cases in groups.items():
        expected.update({f"PT-WEB-{i:03d}": classname + "#" + name for i, name in cases})
        report = repo / "src/schubert-nk-web/target/surefire-reports" / ("TEST-" + classname + ".xml")
        suite = ET.parse(report).getroot()
        actual = suite.findall("testcase")
        if any(int(suite.get(key, "0")) for key in ("errors", "failures", "skipped")):
            raise SystemExit("nonpassing Web PT")
        if int(suite.get("tests", "0")) != len(actual):
            raise SystemExit("inconsistent Web PT count")
        clean = ET.Element("testsuite", {key: suite.get(key) for key in
                                        ("name", "time", "tests", "errors", "failures", "skipped")})
        for case in actual:
            if any(child.tag not in ("system-out", "system-err") for child in case):
                raise SystemExit("failed/skipped/flaky/rerun Web case")
            attributes = {key: case.get(key) for key in ("name", "classname", "time")}
            methods.append(attributes["classname"] + "#" + attributes["name"])
            ET.SubElement(clean, "testcase", attributes)
        ET.indent(clean)
        reports[report.name] = ET.ElementTree(clean)
    if set(methods) != set(expected.values()) or len(methods) != len(expected):
        raise SystemExit("Web Test IDs do not exactly cover executed methods")
    validate_session_resource_inventory({key: value for key, value in expected.items() if key in ("PT-WEB-294", "PT-WEB-295", "PT-WEB-296", "PT-WEB-297", "PT-WEB-298")})
    validate_scenario_inventory({key: value for key, value in expected.items() if "ScenarioWireClientTest#" in value})
    validate_page_inventory({key: value for key, value in expected.items() if "PageViewModelTest#" in value})
    validate_hierarchy_inventory({key: value for key, value in expected.items() if "ScenarioHierarchyViewModelTest#" in value})
    validate_detail_inventory({key: value for key, value in expected.items() if "ScenarioDetailViewModelTest#" in value})
    validate_search_inventory({key: value for key, value in expected.items() if "ScenarioSearchResultsViewModelTest#" in value})
    validate_search_form_inventory({key: value for key, value in expected.items() if "ScenarioSearchFormTest#" in value})
    validate_search_view_inventory({key: value for key, value in expected.items() if "ScenarioSearchViewModelTest#" in value})
    validate_animation_view_inventory({key: value for key, value in expected.items() if "AnimationViewModelTest#" in value})
    validate_animation_wire_inventory({key: value for key, value in expected.items() if "AnimationWireClientTest#" in value})
    validate_music_hierarchy_inventory({key: value for key, value in expected.items() if "MusicHierarchyViewModelTest#" in value})
    validate_music_wire_inventory({key: value for key, value in expected.items() if "MusicWireClientTest#" in value})
    validate_log_wire_inventory({key: value for key, value in expected.items() if "LogSearchWireClientTest#" in value})
    validate_log_results_inventory({key: value for key, value in expected.items() if "LogSearchResultsViewModelTest#" in value})
    validate_log_form_inventory({key: value for key, value in expected.items() if "LogSearchFormTest#" in value})
    validate_log_view_inventory({key: value for key, value in expected.items() if "LogSearchViewModelTest#" in value})
    evidence = repo / "evidence/01_PT/015_NK-WEB-001/evidence"
    for name in ("logs", "output", "coverage"):
        (evidence / name).mkdir(parents=True, exist_ok=True)
    for name, report in reports.items():
        report.write(evidence / "output" / name, encoding="UTF-8", xml_declaration=True)
    for name in ("001_NK-WEB-001_単体テスト仕様書.md", "002_NK-WEB-001_実行結果.md",
                 "003_NK-WEB-001_Scenario通信実行結果.md",
                 "004_NK-WEB-001_Page表示モデル単体テスト仕様書.md", "005_NK-WEB-001_Page表示モデル実行結果.md",
                 "006_NK-WEB-001_Scenario階層表示単体テスト仕様書.md", "007_NK-WEB-001_Scenario階層表示実行結果.md",
                 "008_NK-WEB-001_Scenario本文表示モデル単体テスト仕様書.md", "009_NK-WEB-001_Scenario本文表示モデル実行結果.md",
                 "010_NK-WEB-001_Scenario検索結果表示単体テスト仕様書.md", "011_NK-WEB-001_Scenario検索結果表示実行結果.md",
                 "012_NK-WEB-001_Scenario検索入力単体テスト仕様書.md", "013_NK-WEB-001_Scenario検索入力実行結果.md",
                 "014_NK-WEB-001_Scenario検索画面状態単体テスト仕様書.md", "015_NK-WEB-001_Scenario検索画面状態実行結果.md",
                 "016_NK-WEB-001_Animation一覧表示単体テスト仕様書.md", "017_NK-WEB-001_Animation一覧表示実行結果.md",
                 "018_NK-WEB-001_Animation通信単体テスト仕様書.md", "019_NK-WEB-001_Animation通信実行結果.md",
                 "020_NK-WEB-001_Music階層表示単体テスト仕様書.md", "021_NK-WEB-001_Music階層表示実行結果.md",
                 "022_NK-WEB-001_Music通信単体テスト仕様書.md", "023_NK-WEB-001_Music通信実行結果.md",
                 "024_NK-WEB-001_Log検索結果表示単体テスト仕様書.md", "025_NK-WEB-001_Log検索結果表示実行結果.md",
                 "026_NK-WEB-001_Log検索通信単体テスト仕様書.md", "027_NK-WEB-001_Log検索通信実行結果.md",
                 "028_NK-WEB-001_Log検索入力単体テスト仕様書.md", "029_NK-WEB-001_Log検索入力実行結果.md",
                 "030_NK-WEB-001_Log検索画面状態単体テスト仕様書.md", "031_NK-WEB-001_Log検索画面状態実行結果.md"):
        shutil.copyfile(evidence.parent / name, evidence / "logs" / name)
    for suffix in ("csv", "xml"):
        shutil.copyfile(repo / "src/schubert-nk-web/target/site/jacoco" / ("jacoco." + suffix),
                        evidence / "coverage" / ("web-jacoco." + suffix))
    manifest = {key: verified[key] for key in ("runId", "targetCommit", "branch", "startedAt", "completedAt",
                                              "exitCode", "command", "environment", "modules", "rawLogSha256")}
    manifest.update({
        "logViewExpected": "PG215/030/031/PT-WEB286..293/UI222,225/SS313: independent closed ADMIN snapshots, all filters/error messages, page0/100/101/201/clamp and request binding, percent URL literals, null/USER/ownership, bean allowlist/Spring HTML escaping/64 views.Not template/HTTP/NK gate.",
        "logViewSources": [{"path": relative, "sha256": hashlib.sha256((repo / relative).read_bytes()).hexdigest()}
                           for relative in (
            "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/view/LogSearchViewModel.java",
            "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/LogSearchViewModelTest.java")],
        "logFormExpected": "PG214/028/029/PT-WEB278..285/SSC073/UI222,225,235/SS313,352: independent8fields/defaults/enums/NFC/ASCIItrim/UTF8limits/control/surrogates/page/int bounds/strict JST literal dates/31day boundary/null/immutable/redaction/64 binds.No template/HTTP/NK gate completion.",
        "logFormSources": [{"path": relative, "sha256": hashlib.sha256((repo / relative).read_bytes()).hexdigest()}
                           for relative in (
            "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/form/LogSearchForm.java",
            "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/form/LogSearchFormTest.java")],
        "logResultsExpected": "PG212/024/025/PT-WEB262..269/UI225,235/SS313,323: independent fields/UTC OffsetDateTime literals/1024 optional combinations/page0..100/order/identity/null/ADMIN/ownership/closed beans/escaping/64 projections.Not form/template/HTTP/NK gate.",
        "logWireExpected": "PG213/026/027/PT-WEB270..277/UI232,234,235/SS311,312,321,323: independent LGS656/PAGED48/2088 vectors,all type/level,0/1/100,31day/page boundaries,all error/malformed/null/unknown/64 requests/erasure/ownership.No authorization or HTTP/NK gate completion.",
        "logSources": [{"path": relative, "sha256": hashlib.sha256((repo / relative).read_bytes()).hexdigest()}
                       for relative in (
            "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/view/LogSearchResultsViewModel.java",
            "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/LogSearchResultsViewModelTest.java",
            "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/LogSearchWireClient.java",
            "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/LogSearchWireClientTest.java")],
        "musicWireExpected": "PG210/022/023/PT-WEB254..261/UI232,235/SS311,312,321,323,352: independent MCT/MCS/MTR byte vectors,0/20/100/200 bounds,all error profiles,malformed/semantic/null/transport/unknown error,64 concurrent exchanges,buffer erasure and immutable redacted snapshots.No descriptor/retry/HTTP/live broker/NK gate certificate.",
        "musicWireSources": [{"path": relative, "sha256": hashlib.sha256((repo / relative).read_bytes()).hexdigest()}
                             for relative in (
            "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/MusicWireClient.java",
            "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/MusicWireClientTest.java")],
        "musicHierarchyExpected": "PG208/020/021/PT-WEB246..253/UI223,235/SS313,323: independent category/section names,order,sum,0/20/100 bounds and6-digit totals,count mismatch/duplicate/empty-dot rejection,null/ownership/closed beans/redaction,UTF8 literal URLs,synthetic escaped HTML,64 snapshots.Not actual template/HTTP/Music pair/stream/NK gate.",
        "musicHierarchySources": [{"path": relative, "sha256": hashlib.sha256((repo / relative).read_bytes()).hexdigest()}
                                 for relative in (
            "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/view/MusicCategoryViewModel.java",
            "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/view/MusicSectionViewModel.java",
            "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/MusicHierarchyViewModelTest.java")],
        "animationWireExpected": "PG206/PT-WEB238..245/UI232,235/SS311,312,321,322,323,352: independently assembled header/data/record bytes, ANM and MAIN/OVA capability, success/error profiles, malformed response/correlation/context/bounds, null, no retry,64 concurrent contexts, buffer erasure and immutable redacted result. Existing Scenario166..173 and HTTP regression retained. Not HTTP/MQ deployment/NK gate completion.",
        "animationWireSources": [{"path": relative, "sha256": hashlib.sha256((repo / relative).read_bytes()).hexdigest()}
                                 for relative in (
            "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/ProtectedReadWireClient.java",
            "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/ProtectedReadWireException.java",
            "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/AnimationWireClient.java",
            "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/AnimationWireClientTest.java")],
        "animationViewExpected": "PG204/PT-WEB230..237/016/017/UI223,235/SS313,323: independent menu count sum,main/SUBTRACK parent grouping and source main order,OVA order,0/50/51 bounds,all invalid category/parent/duplicates/zero size/empty-dot links,null/immutable/closed beans/redaction,percent-encoded literal URL,synthetic HTML and64 independent snapshots. No template/HTTP/stream/NK gate certificate.",
        "animationViewSources": [{"path": relative, "sha256": hashlib.sha256((repo / relative).read_bytes()).hexdigest()}
                                 for relative in (
            "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/view/AnimationMenuViewModel.java",
            "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/view/AnimationListViewModel.java",
            "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/AnimationViewModelTest.java")],
        "searchViewExpected": "PG200/PT-WEB222..229/014/015/UI222,223,234/SS313,323: independent Current candidate/order/display literals, fixed six-condition UTF8 percent encoded query vectors, first/middle/last/empty and clamped request binding,10/500 candidate limits, all closed field messages, invalid no-result/no-link state, null/immutable/closed bean/redaction/synthetic HTML and64 parallel snapshots. Not actual search template/controller/NK gate certificate.",
        "searchViewSources": [{"path": relative, "sha256": hashlib.sha256((repo / relative).read_bytes()).hexdigest()}
                              for relative in (
            "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/view/ScenarioSearchViewModel.java",
            "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/ScenarioSearchViewModelTest.java")],
        "searchFormExpected": "PG199/SSC072/PT-WEB214..221/012/013/UI222,223,234/SS313,352: independent NFC/UTF8 boundaries, exact seven names and duplicate rejection, four prohibited controls and malformed surrogates, enums, signed ASCII int page correction and overflow, immutable snapshots/null/redaction, invalid request prohibition and64 parallel validations. No HTTP/template/MQ connection certificate.",
        "searchFormSources": [{"path": relative, "sha256": hashlib.sha256((repo / relative).read_bytes()).hexdigest()}
                              for relative in (
            "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/form/ScenarioSearchForm.java",
            "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/form/ScenarioSearchFormTest.java")],
        "searchResultsExpected": "PG198/PT-WEB-206..213/010/011/UI223,234/SS313,323: independent literal display values, order, numeric scenario/audio URLs, page count boundaries, all eight audio presence combinations, null and immutable ownership, closed bean graph, synthetic HTML escaping and64 concurrent projections. Validated wire input only; no search form/controller/template or actual NK gate certificate.",
        "searchResultsSources": [{"path": relative, "sha256": hashlib.sha256((repo / relative).read_bytes()).hexdigest()}
                                 for relative in (
            "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/view/ScenarioSearchResultsViewModel.java",
            "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/ScenarioSearchResultsViewModelTest.java")],
        "detailViewExpected": "PG195/PT-WEB-194..205/008/009/UI223,234/SS313,333: independent literal header/navigation/audio grouping/order,0/200/10000 bounds,null,sequence/pair/metadata rejection,immutable snapshots,closed bean graph,synthetic escaping,64 concurrent projections and fixed redaction. Input already wire/file-verified. No controller/production detail template/large reader bootstrap/actual NK CHR certificate.",
        "detailViewSources": [{"path": relative, "sha256": hashlib.sha256((repo / relative).read_bytes()).hexdigest()}
                              for relative in (
            "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/view/ScenarioDetailViewModel.java",
            "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/ScenarioDetailViewModelTest.java")],
        "frameworkVersions": {"springMvc": "7.0.9", "thymeleafSpring6": "3.1.5.RELEASE", "jsoupTest": "1.23.2", "springSession": "4.1.1", "springWeb": "7.0.9", "springTest": "7.0.9", "springSecurityWeb": "7.1.1", "micrometerWeb": "1.17.1", "servletApi": "6.1 (Tomcat bundled)", "tomcatEmbedCore": "11.0.25", "commonsLoggingWeb": "1.4.0", "jspecifyWeb": "1.0.1", "sourceAndHashes": "documents/400_PGPT/420_環境/421_開発環境・toolchain構築記録.md sections5.7/5.8/5.9/5.10"},
        "programId": "NK-WEB-001", "programStatus": "IN_PROGRESS",
        "hierarchyExpected": "PG193/PT-WEB-182..193/006/007/UI223,234/SS313: immutable display-only projections of already validated game/route/file records; independent literal values/URLs/order, null/0/max/max+1, owned snapshots, closed getter graph, synthetic escaping,100 parallel calls and redaction. Limits10/50/500; no protocol/session retention. Not semantic wire validation, request binding, production templates/controller/HTTP/NK CHR.",
        "hierarchySources": [{"path": relative, "sha256": hashlib.sha256((repo / relative).read_bytes()).hexdigest()}
                             for relative in (
            "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/view/GameListViewModel.java",
            "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/view/RouteListViewModel.java",
            "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/view/ScenarioFileListViewModel.java",
            "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/ScenarioHierarchyViewModelTest.java")],
        "pageViewExpected": "PG192/PT-WEB-174..181/004/005/SS313 section6.1/UI222: independent literal 50/100 page fixtures, empty/single/first/middle/last/max, invalid projection and null/configuration rejection, 100 parallel checks, closed read-only JavaBean and synthetic Thymeleaf DOM. User input page correction remains upstream. Not production screens/controller/URLs/NK CHR.",
        "pageViewSources": [{"path": relative, "sha256": hashlib.sha256((repo / relative).read_bytes()).hexdigest()}
                            for relative in (
            "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/view/PageViewModel.java",
            "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/PageViewModelTest.java")],
        "scenarioWireExpected": "PG118/191, PT-WEB-166..173,001 section14.14/003: six independent UI234 request/response byte vectors,0/1/max records,I/F descriptors,all defined error profiles,mutated headers/data/records,100 concurrent correlations,timeout/interruption/capacity/no retry/buffer erasure. Synthetic sender and real correlation registry, not actual broker/controller/production bootstrap/NK CHR.",
        "scenarioWireSources": [{"path": relative, "sha256": hashlib.sha256((repo / relative).read_bytes()).hexdigest()}
                                for relative in (
            "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/ScenarioWireClient.java",
            "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/ScenarioWireException.java",
            "src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/ScenarioWireClientTest.java")],
        "tests": {"program": len(methods), "reactor": sum(m["tests"] for m in verified["modules"].values())},
        "testIdMethods": expected, "methods": methods,
        "inputAndExpected": "PT-WEB-001..008 / PG-D-093: synthetic 32-byte zero/sequence/FF CSPRNG data with independent Python base64/hashlib fixed vectors; canonical unpadded43-character base64url and raw-ASCII SHA256 lookup, temporary random/decode/hash arrays erased. Null/length/alphabet/padding/unused-bits negatives, provider failure and100 concurrent random IDs/per-call hashes. Explicit GET URL strings preserve path/query/Unicode and valid query escapes with no trim/decode; reject schemes/authority/fragment/malformed/control/dot-segments/encoded path delimiters and nonGET. Exact2047/2048/2049 UTF8-byte, malformed surrogate and100 independent query cases. toString and validation errors contain no values.",
        "actual": "All mapped independent assertion sets passed; no failed/skipped/flaky/not-run counted",
        "sessionSchemaExpected": "PT-WEB-009..015 / SSC-038 / PG-D-094: independently handwritten UTF8 JSON for anonymous/authenticated all-or-none principal, every optional combination, USER/ADMIN, ordered0/1/10 purpose-tagged UUIDs, canonical UTC timestamps, NFC64byte usernames, csrf64..128 and saved GET2048byte. Reject missing/duplicate/unknown/null/wrong types, invalid UTF8/BOM/trailing documents, noncanonical UUID/time and over16384byte/deep inputs. Immutable values/collection copies, fixed redacted exceptions without parser cause/suppressed and100 concurrent inputs. BUG-055 malformed loginAt/issuedAt reproduction followed by explicit DateTimeException conversion and regression.",
        "sessionEncryptionExpected": "PT-WEB-016..023 / SSC-039 / PG-D-095: independently handcrafted JSON/DataOutputStream seven-field LP AAD and JCE AES256-GCM full NKENC1 envelopes. DB UUID/hash/created_at microseconds bind row; every AAD field and envelope/nonce/tag/body mutation rejects. Current writes/previous reads/unknown key and DB-vs-envelope version mismatch, defensive key/ciphertext copies, nonce erasure, valid16384byte JSON and16436byte envelope limits, authenticated bad JSON/UTF8 reject. Null/config/closed negatives;100 distinct concurrent nonces and attributes; caller-monitor isolation; fixed provider/random failures with no diagnostic cause/suppressed; latch-controlled close serialization and restart/rotation.",
        "sessionStoreExpected": "PT-WEB-024..031 / SSC-040 / PG-D-096 / BUG-056 / YKT-051: isolated PostgreSQL18 with production Flyway/grants, independent nine-column metadata/SQL afterconditions, every ciphertext/key/time/TTL/version update field changed, row identity and expected-version predicates. Caller-owned read/write transactions, rollback/atomic old-delete and new-insert, stale CAS false and no resurrection. Web business-schema denial and all nine SQL NULL/DDL constraints; public null/time/precision/TTL/version limits; every JDBC operation/resource failure with fixed redacted exception. Invalid row/duplicate/null resource and non-unit update counts reject.100 row-locked updates retain all versions and CAS race has one winner. No production SQL/schema expectation is used as oracle.",
        "scope": "Web values/JSON/crypto/store/lifecycle/Spring Session, actual CsrfFilter/Holder/AuthenticationProcessingFilter, closed context/custom fixation/screen-only SavedRequest, Caddy numeric client resolver/form converter connected on Mock Servlet and loopback Tomcat11.0.25 plus isolated PostgreSQL; provider/current-context probe uses independent wire replies. Remaining denial/logout HTTP handlers, full audit/logger policy/entrypoint/role and all-request forwarded-origin/header configuration/API revoke queue/screens/actual API and JMS startup/actual NK Characterization remain required and incomplete; no IT/ST claim.",
        "requestContextExpected": "PT-WEB-101..108 / PG-D-108 / BUG-069 / YKT-061: server-generated UUID and validated Caddy numeric client in immutable request attribute, ignore external request ID, no new response header; redispatch preserves existing identity but revalidates transport/client. Invalid proxy stops before body/session/business and emits closed local PROXY denial/403 without untrusted IP/actor. Production CSRF denied handler ignores exception/parameters, preserves session/CSRF and writes CSRF local audit/403. Actual encrypted PostgreSQL Spring Session/Holder/CsrfFilter chain covers anonymous/USER/ADMIN valid-invalid CSRF, independent token and status/audit values; null/type/UUID/attribute/logger/response faults and100 concurrent request identities. Real container ERROR dispatch is additionally verified by PT109..112; final Host/origin, WARN logger config and full authorization remain separate gates.",
        "securityAuditExpected": "PT-WEB-095..100 / PG-D-107 / BUG-068 / YKT-060: closed six event catalog and Route enum, exact SS351 JSON key/value with route and HTTP_REQUEST targetType, UTC millis/config versions, only known principal username/role and trusted canonical IP; Login failures omit attempted username. No raw request/URL/query/body/context/Throwable input, lock0..900 only, all null/metadata/clock/logger faults, Unicode/escaping, 100 concurrent independent logger strings. API existing denial layout/targetType nonregression adds fixed DB assertions; no change to API source/oracles. Local logger PT does not certify HTTP wiring/backend or replace critical API DB audit.",
        "headerExpected": "PT-WEB-091..094 / PG-D-106: independent SS352 seven fixed header values, all status/method/HTML/error/media/static, overwrite conflicting/duplicate values with one safe value, no-store. Real deferred HeaderWriterFilter writes before error/redirect/flush/stream and writer close, after reset and exceptional exit. Public response faults propagate, null fails fast, no request-derived values, 100 concurrent independent responses. Mock Servlet PT, not deployed Caddy/server verification.",
        "formAllowlistExpected": "PT-WEB-090 / BUG-067 / YKT-059: only exact username/password/_csrf parameter names; unknown/empty/case variants/merged query names/null enumeration/null element/Servlet enumeration faults reject before provider with sends0 and no session. Existing CSRF token-only and empty SavedRequest projection responsibilities remain separate.",
        "formLoginExpected": "PT-WEB-082..089 / PG-D-105 / BUG-066 / YKT-058: numeric loopback transport peer before forwarded wrappers, one XFF literal and one https proto; reject nonloopback/hostname/scope/missing/multiple/chain/Forwarded/header-null/faults with fixed proxy exception. Converter accepts only UTF8 urlencoded POST /login, single nonempty username/password, no query credential/CSRF names, no standard raw-session details; provider consumes char[] on all outcomes. Real Spring Session/CSRF/Holder/AuthenticationProcessingFilter invokes configured provider then one custom fixation then closed context save and explicit PT handler.0000/0200 USER/ADMIN saved GET return and next-request restore, CSRF failures MQ0, bad/lock0..900/MQ/probe/form/proxy/DB distinct failures without grant/new cookie; nonmatching requests continue exactly once and controller/success/failure exceptions clear ThreadLocal.100 distinct usernames/passwords/contexts and random-cookie sessions under8 workers preserve each identity, old-row removal, pending0 and buffer erasure. Status/redirect callbacks are PT doubles, not final production handlers or full URL authorization.",
        "savedRequestExpected": "PT-WEB-076..081 / PG-D-104 / BUG-063..065 / YKT-057: UI221/SS313 literal screen GET families and relative query spelling, Japanese/2047/2048/2049byte limits. Reject unsafe methods/external/dot/encoded delimiter/unknown/login/error/static/media/AJAX, decoded case-insensitive secret query names and servlet URL-rewriting session carriers. Keep normal search values including query semicolons and question marks. Only String stored; ephemeral SavedRequest has GET/relative URL and empty cookie/header/locale/parameter projection, absent parameter null per Spring SPI. Matching only exact current GET consumes cache without replay wrapper/Host/header/body reconstruction. Configured encrypted repository marker/null/type/DB/key/Servlet faults fail closed.100 distinct real PG sessions preserve individual targets, Login fixation keeps approved CSRF/tokens, stale response never recreates deleted row. Existing generic safe-GET parser null/path/fragment branches independently regressed; no suppression or oracle relaxation.",
        "securityContextExpected": "PT-WEB-068..075 / SSC-044 / PG-D-103: public configured SessionRepositoryFilter marker binds exact encrypted repository; absent/foreign/native fallback rejects. Closed principal creates exact authenticated token with one correct ROLE and no credential/details. Reject foreign type/untrusted authentication/authority mutation/unknown stored type. Request-lazy one-load cache and stable generated flag,100 concurrent references/private monitor isolation, compatibility API and null faults. Ordinary save validates identity without extra write/grant/invalidation. Actual PG/Servlet strategy fixates once, fresh Cookie/UUID/CSRF, preserves SavedRequest/tokens; SQL/resource/key failures fixed and never successful HTTP, postcommit-close ambiguity not called rollback. Stale response never resurrects row. Actual Holder filter restores USER/ADMIN/anonymous and clears ThreadLocal on success/controller exception/restart/expiry/corruption. Independent UI232/234 Login0000 or0200+active GAM wire to real provider/strategy/save and next-request restore; revoked probe never grants. No final form/handler/Logout or actual NK CHR completion claim.",
        "authenticationProviderExpected": "PT-WEB-060..067 / SSC-043 / PG-D-102 / YKT-056: actual Spring7.1.1 provider accepts only exact unauthenticated UsernamePasswordAuthenticationToken with username String, consumed char[] and bounded numeric IP details established by trusted upstream.0000 maps API identity to SessionPrincipal/Principal.getName and exact ROLE_USER or ROLE_ADMIN;0101/input failures,0106 bounded0..900seconds,9000/transport remain distinct fixed exceptions without source diagnostic. Erase input credentials on success/error/type rejection.0200 must perform fresh IF-003 protected read, exact256byte request and fully validated265+272*n response with n0/1/10, matching layout/correlation/context and all record semantics.0102 never grants; failed/malformed probe fails unavailable. Original Login issue time remains immutable and original expiry is not misused as current idle expiry.100 concurrent probes and100 provider pairs use independent usernames/passwords/roles/contexts and200 fresh IDs without public-monitor dependence or pending leaks. Existing API current-context and admin role/status/password full-revocation PT are regressed; mock reply tests do not claim live dispatcher/HTTP completion.",
        "loginExchangeExpected": "PT-WEB-054..059 / PG-D-101 / BUG-060..061 / YKT-055..056: independent UI232/234 header and DATA offset vectors for exact640byte NFC/trim Login request, 688byte reply. USER/ADMIN,64byte username including lowercase-expanding Unicode,1..256byte password, numeric IPv4/IPv6 without DNS; consumed char array and delegated sender buffer zero.0000/0200 semantic and same username binding;0101/0106/9000 retain distinct validated error profile and bounded retry/message with no success-only filler mapping. Invalid layout/length/correlation/header/UTF8/role/context/time/code and leaked error fields reject. Every constructor/API null boundary; no send for invalid input, no retry for provider/timeout/capacity/interruption/clock/UUID failure, fixed cause-free failures and interrupt preservation.100 concurrent identities within client limit, pending0, no public monitor dependence. Reply is not a session grant;0200 retains original snapshot and requires later current-context validation in provider.",
        "csrfPostExpected": "PT-WEB-050..053 / PG-D-100: persistent CSRF repository generates via anonymous create or atomic session rotate; closed readonly existing token validation, null save invalidates only as an externally coordinated Logout step. load/save/generate null/wrong type/field/value and DB/key failures fail closed. Deferred request attributes, exactly one valid64..128 body parameter _csrf, no header alternative or decoded query _csrf key, duplicates/null/empty/malformed reject. Independent literal token/HTTP403/business count for every SS313 POST including Login/Logout/User four operations/create/question/cancel/delete. GET/HEAD pass this CSRF layer only; unsafe PUT/DELETE/PATCH remain protected. Old fixation/different-session/expired token reject,100 concurrent valid requests succeed without creating operation tokens. Audit callback is a fixed PT double, final production audit/security chain/logger configuration remain mandatory, not counted as complete.",
        "springSessionExpected": "PT-WEB-044..049 / SSC-042 / PG-D-099 / BUG-058..059 / YKT-053..054: closed principal/csrfToken/savedRequest/operationTokens projection with immediate persistence; generic cast localized and unknown/type/null/read-only security boundaries. Rotate preserves principal with fresh Cookie/UUID/CSRF, microsecond touch never reduces last access, fixed idle value. Request snapshot token deltas merge into current DB state;10 parallel add/remove, identical retry, UUID-metadata collisions including stale delete, max10 and no resurrection. Repository ownership/expiry/fault/close/private monitor isolation. Actual Spring filter/Mock Servlet sets opaque32byte SCHUBERT_NK_SESSION, Secure/HttpOnly/Lax/Path=/, no domain/persistent expiry/extra base64; restart/fixation/Logout/invalid cookie/response-before-commit stale save checks. Explicit path dot segments reject across value/JSON/session while normal dotted names and query dots remain unchanged.",
        "sessionLifecycleExpected": "PT-WEB-036..043 / SSC-041 / PG-D-098 / BUG-057 / YKT-052: isolated production-DDL PostgreSQL with independently constructed JSON/AAD/AES vectors and SQL afterconditions. Microsecond8h idle boundaries/backward clock/restart/key rotation; expiry/corrupt tag/key/schema/NULL invalidate only their row with mandatory deletion verified. Pure current-state mutation preserves principal and CSRF, max10 tokens; atomic Login fixation preserves SavedRequest/tokens even with previously absent CSRF; Cookie/UUID/CSRF and neighbour UUID collisions rollback. Version999999999 rollover preserves Cookie and attributes, renews DB UUID and rejects old-PK CAS. All lifecycle JDBC/resource/commit/rollback/close/random/crypto/config faults return fixed errors; postcommit close may commit and retry checks actual state, never assumes rollback.100 concurrent counter changes,10 concurrent token adds/removes and invalidate races retain state without resurrection. Constructor/API null contracts and no provider cause/suppressed disclosure.",
        "csrfValueExpected": "PT-WEB-032..035 / PG-D-097:32 CSPRNG bytes to independent fixed64hex vector and provider-failure buffer erasure. All persisted lengths64..128 with explicit same/different first/middle/last/length booleans; nullable submitted missing is false and malformed tokens reject. Valid secrets compare via MessageDigest.isEqual over fixed129byte length-plus-padding arrays, then erase.100 unique concurrent generated tokens and shared immutable matching; toString/cause/suppressed redacted. Value only, no claim of POST/filter/403/session wiring completion.",
"relatedBug": ["BUG-074", "BUG-073", "BUG-072", "BUG-071", "BUG-070", "BUG-069", "BUG-068", "BUG-067", "BUG-055", "BUG-056", "BUG-057", "BUG-058", "BUG-059", "BUG-060", "BUG-061", "BUG-062", "BUG-063", "BUG-064", "BUG-065", "BUG-066"], "relatedSsc": ["SSC-048", "SSC-047", "SSC-046", "SSC-038", "SSC-039", "SSC-040", "SSC-041", "SSC-042", "SSC-043", "SSC-044"], "relatedYkt": ["YKT-066", "YKT-065", "YKT-064", "YKT-063", "YKT-062", "YKT-061", "YKT-060", "YKT-059", "YKT-050", "YKT-051", "YKT-052", "YKT-053", "YKT-054", "YKT-055", "YKT-056", "YKT-057", "YKT-058"],
        "notRunCountedAsPass": 0,
        "apiSessionInvalidExpected": "PT-WEB-158..165 / PG-D-117 / SSC-048: exhaustive twelve approved ResultCode generic HTTP statuses from independent literal table; classification never substitutes for controller side effects. Trusted API0102 terminal handler requires exact configured encrypted repository marker, captures only closed actor for existing SESSION_EXPIRED INFO action/reason API_SESSION_INVALID, clears request display/CSRF and Holder, invalidates existing local session without new anonymous session/SavedRequest/revoke queue/API Logout. Normal GET302 fixed /login?session-expired; nonGET/AJAX/media401 without body replay. Shared unchanged UI221 navigation predicate. Null/foreign/native/type/getter/clear/invalidate/logger/response faults propagate, committed response still invalidates before fixed exception. Real PostgreSQL/Tomcat/Login/security/error MVC cookie expiry, SQL deletion/neighbour retention, DB failure before delete/commit yields503 anonymous error and no false deletion audit.100 independent expired sessions and ordered stale-request/new-Login fixation retain new row; all resources close. Explicit trusted API0102 endpoint double, not all business controllers/real NK CHR or Logout recovery completion.",
        "errorMvcExpected": "PT-WEB-148..157 / PG-D-116 / SSC-047 / BUG-074 / YKT-066: fixed independent status/message/UUID catalog and anonymous or closed display-only TopBar; actual Spring MVC/Thymeleaf/Tomcat errors400/401/403/404/405/409/416/429/503 with500/unknown mapped503 and direct missing status404. Internal ERROR exact /error routes after trusted Caddy/headers/server UUID and before business-only StrictHttpFirewall, without DB/JMS/session/native identity reread. Other dispatchers/paths remain in original single business security chain. Real prohibited TRACK common400, role and CSRF403 with one original request ID/audit, external POST/error405, proxy403 empty, DB failure before/after snapshot without recursion, lifecycle cleanup and context clearing on errors. Null/type/config/response/model faults, escaped DOM and100 concurrent actor/role/token/request ID isolation. Login GET remains a named fixture, full bootstrap/Logout/API0102/screens/actual NK CHR not certified.",
        "menuMvcExpected": "PT-WEB-142..147 / PG-D-115: actual Spring MVC7.0.9/Thymeleaf3.1.5.RELEASE with independent Current/UI223 title-description-URL lists; USER7/ADMIN9 order, schubert NK brand, username/role and common navigation. Closed immutable display-only models, null/foreign/model/configuration faults, no retained protocol/session objects. Real Tomcat/encrypted PostgreSQL/Login/security/DispatcherServlet GET root with exactly one hidden Logout CSRF and no native sessions,100 concurrent identities/roles/tokens. Jsoup test-only DOM assertions for escaped HTML-special username, no inline script/style/event/data attributes or raw context/password/cookie, safe stylesheet and unknown resources. Login/error are named test servlets here; Logout itself and full production bootstrap/all screens/actual NK CHR are not certified.",
        "securityCompositionExpected": "PT-WEB-131..141 / PG-D-113/114 / BUG-073 / YKT-065: actual single composite security chain on loopback Tomcat with PostgreSQL encrypted sessions and independent Login/replay/error wire responses. Anonymous saved GET, body CSRF, Login fixation, USER/ADMIN HTTP authorization, firewall/proxy/error dispatch,100 concurrent real HTTP sessions. Matching GET consumes SavedRequest; Servlet principal/name/FORM/exact roles are a closed immutable actor snapshot, not native container identity. Programmatic authenticate/login/logout always reject without changing persisted principal/CSRF; null/foreign/boundary/downstream faults and100 cross-thread snapshots verified. Synthetic terminal/error servlets only; full MVC/templates/runtime bootstrap/Logout recovery and actual NK Characterization are not complete.",
        "accessFailureExpected": "PT-WEB-125..130 / PG-D-112: normal anonymous GET302/login with only safe saved screen GET, nonGET/AJAX/media403 and no replay. Role403 keeps closed principal/session and emits only trusted ID/IP/actor/ROLE audit. New internal AUTHENTICATION_REQUIRED event uses existing AUTHORIZATION_DENIED action with UNAUTHENTICATED reason and no actor; old six event expectations unchanged. Actual encrypted PostgreSQL Session/Holder/CSRF/Login/ExceptionTranslation/Authorization sequence saves once, returns after Login, denies USER admin and allows ADMIN. Null/context/foreign principal/DB/attribute/logger/response faults, secret diagnostic getters not touched by handlers,100 concurrent outcomes/actors remain isolated. Final error HTML/logger/runtime/API0102 invalidation/owner checks remain separate gates.",
        "authorizationExpected": "PT-WEB-121..124 / PG-D-111: actual AuthorizationFilter and StrictHttpFirewall with six explicit public resource paths and SS352 exact method policy: Login GET/POST, assets/error GET/HEAD, internal ERROR/error across methods only, admin subtree and exact logs ADMIN-only, all other routes authenticated. Independent USER/ADMIN/anonymous matrix across methods, unknown static/suffix routes and forged role/query headers; path parameters/dot paths/double slash/encoded delimiter/firewall reject, percent-encoded admin letters stay admin-protected. Every dispatcher reauthorizes,100 concurrent principals/paths remain isolated without caller-monitor locking. Policy component only; final error view/full audit/runtime wiring and API owner revalidation remain separate gates.",
        "loginHandlerExpected": "PT-WEB-113..120 / PG-D-110 / SSC-046: persisted closed identity equality before local LOGIN_SUCCEEDED and302 to closed saved GET or root. No target/Referer or URL session rewriting. Current-compatible bad-credential302/login?error and lock302/login?locked with API retry0..900; form400/proxy403/service-storage-unknown503 stay distinct and do not increment Web counters. No diagnostic getters/form values/session creation on failure. Actual PostgreSQL Session/Holder/CSRF/provider/fixation chain with independent0000/0200/0101/0106/9000/transport-fault wire fixtures;100 parallel result/audit isolation, public null/attribute/logger/response faults, committed session remains confirmed after response failure without extra fixation or API Login. Full MVC/runtime chain and remaining-lock-time view are not certified here.",
        "embeddedHttpExpected": "PT-WEB-109..112 / PG-D-109 / BUG-070 / YKT-062: single Servlet API provider, real loopback Tomcat11.0.25 GET and POST with encrypted PostgreSQL Spring Session, independent Cookie/security headers/CSRF/form merge/status and error body. Native sessions and JSESSIONID absent. Untrusted proxy terminates403 with one audit/UUID and no session/error servlet; trusted CSRF uses one audit and original request ID on ERROR dispatch.100 independent sessions, cookies, CSRF and audit IDs remain separate under8 workers; all temporary HTTP resources close. Synthetic terminal/error servlets, not full MVC/production bootstrap/IT/ST.",
        "redaction": "Only allowlisted method names/timing/counters/coverage and metadata. No JVM properties/stdout/stderr, raw cookie/session/context/token/key or database dump.",
    })
    (evidence / "logs" / (run + "-summary.json")).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    manifest["files"] = [{"path": str(p.relative_to(evidence)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                         for p in sorted(evidence.rglob("*")) if p.is_file() and p.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    write_scope_checksums(evidence, manifest["files"])
    print(json.dumps({"runId": run, "tests": len(methods), "status": "SLICE_PASS / PROGRAM_IN_PROGRESS"}))


if __name__ == "__main__":
    main()
