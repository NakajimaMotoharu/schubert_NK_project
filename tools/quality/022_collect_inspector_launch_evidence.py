#!/usr/bin/env python3
"""PG-D-144/146: private launcher, deployment and Linux flock PT, not parent OS acceptance."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

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
POSTGRES_TRACES = {"PT-OPS-PGCFG-008.txt": b"isolated=true\nhostConfigurationChanged=false\nhbaReload=false\nrawDatabaseLogCopied=false\nconfigurationKeys=32\nhbaRules=16\n"}


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
     "ArtemisRoleReadinessClient", "ArtemisQueuePressureClient"))
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
                   "dev.codex.schubert.nk.batch.mq.ArtemisQueuePressureClientTest": "PT-OPS-MQ"}.get(cls, "PT-OPS-INBOX")
                  if deployment else "PT-DB-INBOX")
        methods.update({f"{prefix}-{i:03}": cls + "#" + name for i, name in enumerate(expected, start)})
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
    full = repo / "evidence/01_PT/008_NK-SCN-001/evidence/manifest.json"
    verified = json.loads(full.read_text())
    if verified["runId"] != run or verified["exitCode"] != 0:
        raise SystemExit("matching successful full reactor required")
    subprocess.run(["git", "diff", "--exit-code", verified["targetCommit"], "--", "src", "pom.xml",
                    "program/characterization", "tools/quality"], cwd=repo, check=True)
    target = repo / "src/schubert-nk-api/target"
    groups = DEPLOYMENT_GROUPS if args.deployment else GROUPS
    def module_for(cls):
        return {"dev.codex.schubert.nk.batch.platform.InspectorUnitSnapshotTest": "batch",
                "dev.codex.schubert.nk.batch.platform.InspectorUnitProbeTest": "batch",
                "dev.codex.schubert.nk.storage.ResourceScopeTest": "storage",
                "dev.codex.schubert.nk.storage.LinuxFileLockTest": "storage",
                "dev.codex.schubert.nk.storage.PrivateDirectoryEntryTest": "storage",
                "dev.codex.schubert.nk.storage.ChildDirectoryPublicationTest": "storage",
                "dev.codex.schubert.nk.storage.PrivateChildDirectoryTest": "storage",
                "dev.codex.schubert.nk.batch.file.InspectorEnvironmentPublisherTest": "batch",
                "dev.codex.schubert.nk.batch.platform.ConfigurationGroupResolverTest": "batch",
                "dev.codex.schubert.nk.batch.file.InspectorEnvironmentFilesTest": "batch",
                "dev.codex.schubert.nk.batch.file.MaintenanceFileLockTest": "batch",
                "dev.codex.schubert.nk.batch.platform.ApplicationStopGateTest": "batch",
                "dev.codex.schubert.nk.batch.platform.SystemctlStateSourceTest": "batch",
                "dev.codex.schubert.nk.batch.platform.InspectorRunEnvironmentTest": "batch",
                "dev.codex.schubert.nk.batch.platform.InspectorStaticEnvironmentTest": "batch",
                "dev.codex.schubert.nk.batch.file.InspectorEnvironmentReaderTest": "batch",
                "dev.codex.schubert.nk.batch.mq.ArtemisReadinessClientTest": "batch",
                "dev.codex.schubert.nk.batch.mq.ArtemisManagementReadinessClientTest": "batch",
                "dev.codex.schubert.nk.batch.mq.ArtemisAddressSettingsReadinessClientTest": "batch",
                "dev.codex.schubert.nk.batch.mq.ArtemisAcceptorReadinessClientTest": "batch",
                "dev.codex.schubert.nk.batch.mq.ArtemisRoleReadinessClientTest": "batch",
                "dev.codex.schubert.nk.batch.mq.ArtemisQueuePressureClientTest": "batch"}.get(cls, "api")
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
    evidence = repo / "evidence/01_PT" / directory
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
        sources += [repo / "src/schubert-nk-batch/src/main/java" / (s + ".java") for s in (*STOP_SUBJECTS, ENV_SUBJECT, CFG_SUBJECT, EFILE_SUBJECT, *PUBLISH_SUBJECTS, *NAMESPACE_SUBJECTS, *UNIT_SUBJECTS, *MQ_SUBJECTS)]
        sources += [repo / "src/deployment/postgresql" / name for name in ("postgresql.conf.template", "pg_hba.conf.template")]
        validate_postgres_ids((repo / "src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/database/PostgresDeploymentTest.java").read_text())
        sources += [repo / "src/schubert-nk-api/src/main/resources/db/provisioning/001_roles.sql",
                    repo / "src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/logging/ApiLogDatabaseFixture.java"]
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
            "systemd/optional/inbox-inspector-context-previous.conf", "systemd/optional/inbox-inspector-response-previous.conf")]
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
                     "037_NK-OPS-001_Artemis実効Queue実行結果.md"):
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
        manifest["staticAnalysisByModule"] = {m: verified["modules"][m]["spotbugs"] for m in ("api", "storage", "batch")}
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
    (evidence / "checksums.sha256").write_text("".join(digest(p) + "  " + str(p.relative_to(evidence)) + "\n"
        for p in sorted(evidence.rglob("*")) if p.is_file() and p.name != "checksums.sha256"))
    print(json.dumps({"runId": run, "tests": len(methods), "scopeResult": manifest["scopeResult"], "programComplete": False}))


if __name__ == "__main__":
    main()
