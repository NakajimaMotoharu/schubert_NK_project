#!/usr/bin/env python3
"""Certify only executed NK-MED-001 methods against a verified full reactor, with no raw logs."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    run = parser.parse_args().run_id
    if not run.startswith("PT-MED-") or not all(c.isalnum() or c == "-" for c in run):
        raise SystemExit("invalid run ID")
    repo = Path(__file__).resolve().parents[2]
    verified = json.loads((repo / "evidence/01_PT/008_NK-SCN-001/evidence/manifest.json").read_text())
    if verified["runId"] != run or verified["exitCode"] != 0:
        raise SystemExit("collect the matching full verified reactor first")
    subprocess.run(["git", "diff", "--exit-code", verified["targetCommit"], "--", "src", "pom.xml",
                    "program/characterization", "tools/quality"], cwd=repo, check=True,
                   stdout=subprocess.DEVNULL)
    prefix = "dev.codex.schubert.nk.web.media."
    expected = {
        "PT-MED-001": prefix + "HttpByteRangeParserTest#literalRangesPreserveFirstSpecAndOneMebibyteCap",
        "PT-MED-002": prefix + "HttpByteRangeParserTest#invalidGrammarBoundsAndArithmeticNeverSelectBytes",
        "PT-MED-003": prefix + "HttpByteRangeParserTest#nullAndConstructedSelectionsKeepInvariants",
        "PT-MED-004": prefix + "HttpByteRangeParserTest#oneHundredConcurrentParsesHaveNoSharedState",
        "PT-MED-005": prefix + "ContentDispositionFactoryTest#literalHeadersEncodeUtf8WithoutRawMetadata",
        "PT-MED-006": prefix + "MediaBodyStreamerTest#exactIntervalsUseBoundedWritesAndLeaveResourcesOpen(Path)",
        "PT-MED-007": prefix + "MediaBodyStreamerTest#nullBoundsAndIoFailuresDoNotClaimCompleteTransfer",
        "PT-MED-026": prefix + "DescriptorFileResolverTest#med026ApprovedAssetsUseVerifiedRetainedReadOnlyChannels",
        "PT-MED-027": prefix + "MediaRangeServiceTest#med027GetStatusHeadersAndBytesMatchLiteralIntervals",
        "PT-MED-028": prefix + "MediaRangeServiceTest#med028HeadAndDownloadNeverApplyForbiddenBodyOrRange",
        "PT-MED-029": prefix + "MediaRangeServiceTest#med029DescriptorBindingRejectsBeforeFileAndPermit",
        "PT-MED-030": prefix + "MediaRangeServiceTest#med030TwentyStreamsRejectTwentyFirstAndRecoverAllPermits",
        "PT-MED-031": prefix + "MediaRangeServiceTest#med031IoFailuresReleasePermitsWithoutSecondResponse",
        "PT-MED-032": prefix + "MediaRangeServiceTest#med032OneHundredCallsHaveIndependentPositionsAndHeaders",
        "PT-MED-037": prefix + "MediaResponseDecoderTest#med037ThreeRequestsBindAllApprovedSuccessfulDescriptors",
        "PT-MED-038": prefix + "MediaResponseDecoderTest#med038ErrorProfilesKeepCodesWithoutFabricatedDescriptors",
        "PT-MED-039": prefix + "MediaResponseDecoderTest#med039MalformedAndMismatchedRepliesNeverAuthorizeFiles",
        "PT-MED-040": prefix + "MediaResponseDecoderTest#med040ConcurrentDecodeOwnsBytesAndIsolatesRequests",
    }
    query = "dev.codex.schubert.nk.api.persistence.MediaRepositoryTest#"
    expected.update({
        "PT-MED-008": query + "animationMenuCountsStoredCategoriesWithoutFilesystem",
        "PT-MED-009": query + "animationRowsPreserveParentAndDisplayOrder",
        "PT-MED-010": query + "musicGroupsUseApprovedCategoryAndSectionOrder",
        "PT-MED-011": query + "musicTracksReadFrozenPairsAndLogicalIdTies",
        "PT-MED-012": query + "everyListCapacityRejectsTruncationAndCloseDowngrades",
        "PT-MED-013": query + "nullContractsAndJdbcMetadataFailuresRemainRedacted",
        "PT-MED-014": query + "concurrentReadersNeverMutateOrAcquireRowLocks",
        "PT-MED-015": query + "audioAndMusicMetadataUseCanonicalIdsAndAllApprovedFormats",
        "PT-MED-016": query + "videoMetadataIncludesOpeningAndDisplayFields",
        "PT-MED-017": query + "descriptorNullDatabaseAndMetadataFaultsNeverBecomeMissing",
        "PT-MED-036": query + "med036DecodedRequestsDispatchAllEightStoredQueries",
    })
    request = "dev.codex.schubert.nk.api.application.media.MediaRequestTest#"
    expected.update({
        "PT-MED-033": request + "med033CanonicalFactoriesNormalizeOwnAndEraseBytes",
        "PT-MED-034": request + "med034EightLayoutsHaveIndependentCanonicalFingerprints",
        "PT-MED-035": request + "med035MalformedNullAndUnknownRequestsNeverReachQueries",
    })
    storage = "dev.codex.schubert.nk.storage."
    storage_cases = {
        "PT-MED-018": storage + "OwnedTransferDirectoryTest#med018ExistingAssetChildrenAndEntriesRetainReadOnlyInodes",
        "PT-MED-019": storage + "OwnedTransferDirectoryTest#med019AssetNameNullOpenAndCloseFaultsNeverEscapeOwnership",
        "PT-MED-020": storage + "StorageAttributeGuardTest#med020LargeAssetSizesKeepTransferLimitAndUnixGuards",
        "PT-MED-021": storage + "ExistingFileAccessTest#med021NestedAndLargeAssetsReadExactBytesAndCloseChannels",
        "PT-MED-022": storage + "ExistingFileAccessTest#med022NullSizeAndSegmentContractsFailBeforeContentRead",
        "PT-MED-023": storage + "ExistingFileAccessTest#med023LinksMissingAndWrongUnixAttributesNeverExposeContent",
        "PT-MED-024": storage + "ExistingFileAccessTest#med024OpenReadAttributeAndCloseFailuresAreRedactedAndOwned",
        "PT-MED-025": storage + "ExistingFileAccessTest#med025ConcurrentAndReplacedNamesRetainIndependentInodes",
    }
    expected.update(storage_cases)
    asset = "dev.codex.schubert.nk.api.file."
    expected.update({
        "PT-MED-041": asset + "AssetChecksumManifestTest#med041LiteralManifestsPreserveApprovedPathsAndHashes",
        "PT-MED-042": asset + "AssetChecksumManifestTest#med042MalformedAndMismatchedCountsNeverPublishPartialCatalog",
        "PT-MED-043": asset + "AssetChecksumManifestTest#med043PartialReadsIoFailuresAndHashMismatchesRemainRedacted",
        "PT-MED-044": asset + "AssetChecksumManifestTest#med044ConcurrentMatchesOwnImmutableInput",
        "PT-MED-045": asset + "AssetManifestLoaderTest#med045HeldManifestLoadsWithoutReopeningOrMutatingNames",
        "PT-MED-046": asset + "AssetManifestLoaderTest#med046NullLinksAttributesAndIoFaultsFailClosed",
        "PT-MED-047": asset + "HeldMediaFileInspectorTest#med047ApprovedFilesRequireManifestAndExactPhysicalSize",
        "PT-MED-048": asset + "HeldMediaFileInspectorTest#med048MissingHashPathsAndPhysicalFaultsNeverBecomeNotFound",
        "PT-MED-049": asset + "HeldMediaFileInspectorTest#med049ConcurrentInspectionsRetainRootOwnership",
    })
    methods, clean_reports = [], {}
    reports = list((repo / "src/schubert-nk-web/target/surefire-reports").glob("TEST-" + prefix + "*.xml"))
    reports.extend((repo / "src/schubert-nk-api/target/surefire-reports").glob("TEST-dev.codex.schubert.nk.api.persistence.MediaRepositoryTest.xml"))
    reports.extend((repo / "src/schubert-nk-api/target/surefire-reports").glob("TEST-dev.codex.schubert.nk.api.application.media.MediaRequestTest.xml"))
    reports.extend((repo / "src/schubert-nk-api/target/surefire-reports").glob("TEST-" + asset + "*.xml"))
    reports.extend((repo / "src/schubert-nk-storage/target/surefire-reports").glob("TEST-dev.codex.schubert.nk.storage.*.xml"))
    for report in sorted(reports):
        suite = ET.parse(report).getroot()
        cases = suite.findall("testcase")
        if any(int(suite.get(k, "0")) for k in ("errors", "failures", "skipped")) or len(cases) != int(suite.get("tests")):
            raise SystemExit("nonpassing/inconsistent media suite")
        if suite.get("name", "").startswith(storage):
            cases = [case for case in cases if case.get("classname", "") + "#" + case.get("name", "") in storage_cases.values()]
            if not cases:
                continue
        clean = ET.Element("testsuite", {k: suite.get(k) for k in ("name", "time", "tests", "errors", "failures", "skipped")})
        clean.set("tests", str(len(cases)))
        for case in cases:
            if any(child.tag not in ("system-out", "system-err") for child in case):
                raise SystemExit("failed/skipped/flaky/rerun media case")
            attrs = {k: case.get(k) for k in ("name", "classname", "time")}
            methods.append(attrs["classname"] + "#" + attrs["name"])
            ET.SubElement(clean, "testcase", attrs)
        ET.indent(clean)
        clean_reports[report.name] = ET.ElementTree(clean)
    if len(methods) != len(expected) or set(methods) != set(expected.values()):
        raise SystemExit("media Test IDs do not exactly cover executed methods")
    evidence = repo / "evidence/01_PT/009_NK-MED-001/evidence"
    for folder in ("logs", "output", "coverage"):
        (evidence / folder).mkdir(parents=True, exist_ok=True)
    for name, report in clean_reports.items():
        report.write(evidence / "output" / name, encoding="UTF-8", xml_declaration=True)
    for module, directory in (("api", "src/schubert-nk-api"), ("web", "src/schubert-nk-web"), ("protocol", "src/schubert-nk-protocol"), ("storage", "src/schubert-nk-storage")):
        for suffix in ("csv", "xml"):
            shutil.copyfile(repo / directory / "target/site/jacoco" / ("jacoco." + suffix),
                            evidence / "coverage" / (module + "-jacoco." + suffix))
    manifest = {k: verified[k] for k in ("runId", "targetCommit", "branch", "startedAt", "completedAt",
                                         "exitCode", "command", "environment", "modules", "rawLogSha256")}
    manifest.update({
        "programId": "NK-MED-001", "programStatus": "IN_PROGRESS",
        "tests": {"program": len(methods), "reactor": sum(m["tests"] for m in verified["modules"].values())},
        "testIdMethods": expected, "methods": methods, "actual": f"All {len(methods)} mapped independent assertion sets passed",
        "inputAndExpected": "001 PT specification and exact testIdMethods at targetCommit: SS333 literal Range intervals/416 and 1MiB cap, literal UTF-8 percent header strings, independently patterned bytes and exact array slices; real PostgreSQL synthetic VIDEO/MUSIC/audio rows and independent UI235 16/8/928/72/136/1312/1024/1808-byte vectors for five lists/menu and three descriptor metadata queries, all approved formats/modes, scoped IDs, bounded counts and immutable/read-only/fault postconditions. SSC028 uses literal three-byte retained inodes, independent Unix attribute maps including 48MB+/N12 maximum/Long.MAX, strict single segments and counted FD close/fault/no-mutation checks. Production is never used to generate expected values.",
        "scope": "Range/header/bounded copy, five menu/list and three descriptor DB metadata queries, shared complete retained segment walk/Unix/size-before-after/scoped-channel, Web descriptor-file adapter and internal response-port delivery of 200/206/416/HEAD/download with 20 immediate permits and request binding. Explicit header maps and exact independently patterned body slices, latch-held 20/21 rejection and all-permit recovery, redacted I/O failures/no second response and 100 independent deliveries passed. This is not a registered/authenticated HTTP endpoint or manifest/hash check. Auth/Inbox/manifest/MQ-to-HTTP connection/full startup/client-abort classification/actual NK CHR remain unimplemented or unconnected. Selected eight Storage methods overlap Scenario's module regression and are not additive to reactor count.",
        "requestIdentity": "SSC-029 all eight UI235 literal request vectors, explicit ordered field names/type-version and independent LP/JCA HMAC; direct dispatch through the same decoded values to all eight real PostgreSQL queries; CanonicalField factory NFC/copy/zero and Scenario existing canonical regressions. Final authentication/Inbox/response capture is still separate.",
        "responseVerification": "SSC-030: manually assembled UI232/235 header/DATA bytes for all seven formats, both success profiles and all error fillers. Original request layout/correlation, constant-time 64-byte context and type/ID/disposition binding, invalid data/length/UTF8/NFC/video fields and 100 concurrent decodes passed. No separate response MAC/key/property exists in the approved protocol; API request HMAC and Web transport/request binding remain distinct responsibilities. Actual API/MQ/HTTP registration is pending.",
        "assetIntegrity": "PG-D-078 / PT-MED-041..049: strict immutable checksum subset, SHA256(abc) literal, seven formats, NFC/512-byte/255-byte bounds, 59627 synthetic entries, malformed UTF8/byte-vs-character regression, exact count/duplicate/hash64-position/IO rejection. Real retained manifests and asset abc files with Unix guards, name replacement, symlink/hardlink/size and before/after/open/read/close failures, native FD ownership/no write/repair and 100 concurrent inspections passed. No real master contents committed. This completes the manifest/file adapter slice, not its startup/API/Inbox registration; full migration metadata and content-hash inventory remain separate.",
        "relatedBug": ["BUG-042"], "relatedSsc": ["SSC-028", "SSC-029", "SSC-030"], "crossProgramRegressions": ["BUG-040/YKT-036 in 003 manifest", "BUG-042/YKT-037 in logs/BUG-042-YKT-037.md"],
        "notRunCountedAsPass": 0, "redaction": "JUnit names/timing/counters only; no properties/stdout/stderr or raw logs/paths/credentials/master content.",
    })
    (evidence / "logs" / (run + "-summary.json")).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    manifest["files"] = [{"path": str(p.relative_to(evidence)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                         for p in sorted(evidence.rglob("*")) if p.is_file() and p.name not in ("manifest.json", "checksums.sha256")]
    (evidence / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    (evidence / "checksums.sha256").write_text("".join(hashlib.sha256(p.read_bytes()).hexdigest() + "  " + str(p.relative_to(evidence)) + "\n"
                                                     for p in sorted(evidence.rglob("*")) if p.is_file() and p.name != "checksums.sha256"))
    print(json.dumps({"runId": run, "tests": len(methods), "status": "SLICE_PASS / PROGRAM_IN_PROGRESS"}))


if __name__ == "__main__":
    main()
