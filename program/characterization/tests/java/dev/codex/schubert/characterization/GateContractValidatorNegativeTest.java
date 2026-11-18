package dev.codex.schubert.characterization;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.List;
import java.util.function.Consumer;
import java.util.stream.Stream;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

/** Negative fixtures for BUG-001/YKT-001. Program: NK-CHR-001. */
class GateContractValidatorNegativeTest {
  private static final String VERSION = "version";
  private static final String CASES = "cases";
  private static final String BAD_VALUE = "bad";
  private static final String CURRENT = "current";
  private static final String UNKNOWN = "unknown";
  private static final String HEIGHT = "height";
  private static final String UNKNOWN_CASE = "CHR-Z99";
  private static final String SELECTORS = "selectors";
  private static final String STATUS = "status";
  private static final String EVIDENCE = "evidence";
  private static final String FAILED = "FAIL";
  private static final String NOT_ARRAY = "not-array";
  private static final ObjectMapper JSON = new ObjectMapper();
  private static final Path SOURCE_ROOT =
      Path.of(System.getProperty("chr.unitProjectRoot")).toAbsolutePath().normalize();

  @TempDir Path temporaryDirectory;

  @Test
  void rejectsMalformedContractSchemaCatalogAndBrowser() throws Exception {
    Fixture fixture = fixture("contract-schema-catalog-browser");
    fixture.mutate(
        "program/characterization/tests/resources/cases/gate-contract.json",
        root -> {
          root.put(VERSION, 0);
          array(root, "gates").remove(5);
          ArrayNode cases = array(root, "caseOrder");
          cases.set(1, cases.get(0));
          cases.remove(23);
          array(root, "differenceIds").remove(15);
          root.put("baselineCommit", "invalid");
          root.put("baselineAggregateSha256", "invalid");
        });
    fixture.mutate(
        "program/characterization/tests/resources/cases/schema.json",
        root -> {
          root.put("$schema", "unsupported");
          root.put("type", "array");
          root.set("required", JSON.valueToTree(List.of(CASES)));
          ObjectNode cases = object(object(root, "properties"), CASES);
          cases.put("minItems", 23);
          cases.put("maxItems", 25);
          object(cases, "items").set("required", JSON.valueToTree(List.of("id")));
        });
    fixture.mutate(
        "program/characterization/tests/resources/cases/catalog.json",
        root -> {
          root.put(VERSION, 0);
          ArrayNode cases = array(root, CASES);
          for (int index = 0; index < 2; index++) {
            ObjectNode item = (ObjectNode) cases.get(index);
            item.put("id", "BAD");
            item.put("group", BAD_VALUE);
            item.put(CURRENT, BAD_VALUE);
            item.put("nk", BAD_VALUE);
          }
        });
    fixture.mutate(
        "program/characterization/tests/resources/browser/manifest.json",
        root -> {
          root.put("playwrightJava", "0");
          root.put("browser", UNKNOWN);
          root.put("browserRevision", 0);
          root.put("locale", "en-US");
          root.put("timezone", "UTC");
          object(root, "desktop").put("width", 1).put(HEIGHT, 1).put("deviceScaleFactor", 2);
          object(root, "mobile").put("width", 1).put(HEIGHT, 1).put("deviceScaleFactor", 2);
          root.set("fonts", JSON.createArrayNode());
          root.put("fontReady", UNKNOWN);
          root.put("colorScheme", "dark");
          root.put("reducedMotion", "no-preference");
        });

    assertFailures(
        fixture.validate(),
        "CONTRACT_VERSION",
        "CONTRACT_GATE_IDS",
        "CONTRACT_CASE_DUPLICATE",
        "CONTRACT_DIFFERENCE_COUNT",
        "CONTRACT_BASELINE_COMMIT",
        "CONTRACT_BASELINE_HASH",
        "SCHEMA_DRAFT",
        "SCHEMA_ROOT_TYPE",
        "SCHEMA_REQUIRED",
        "SCHEMA_MIN_ITEMS",
        "SCHEMA_MAX_ITEMS",
        "SCHEMA_CASE_REQUIRED",
        "CATALOG_VERSION",
        "CATALOG_DUPLICATE:BAD",
        "BROWSER_PLAYWRIGHT",
        "BROWSER_FONTS",
        "BROWSER_FONT_READY");
  }

  @Test
  void rejectsUnknownCatalogGroupAndSecondaryViewportMismatches() throws Exception {
    Fixture fixture = fixture("catalog-browser-secondary");
    fixture.mutate(
        "program/characterization/tests/resources/cases/catalog.json",
        root -> {
          ObjectNode item = (ObjectNode) array(root, CASES).get(23);
          item.put("id", UNKNOWN_CASE);
          item.put("group", "Operation");
          item.put(CURRENT, "NK_ONLY");
        });
    fixture.mutate(
        "program/characterization/tests/resources/browser/manifest.json",
        root -> {
          object(root, "desktop").put(HEIGHT, 1);
          object(root, "mobile").put(HEIGHT, 1).put("deviceScaleFactor", 2);
        });
    assertFailures(
        fixture.validate(),
        "CATALOG_GROUP:CHR-Z99",
        "CATALOG_CURRENT:CHR-Z99",
        "CATALOG_ORDER",
        "BROWSER_DESKTOP_VIEWPORT",
        "BROWSER_MOBILE_VIEWPORT",
        "BROWSER_DEVICE_SCALE");
  }

  @Test
  void rejectsBroadAndMalformedDifferenceRules() throws Exception {
    Fixture fixture = fixture("differences");
    fixture.mutate(
        "program/characterization/tests/resources/cases/dif-allowlist.json",
        root -> {
          root.put(VERSION, 0);
          ArrayNode differences = array(root, "differences");
          ObjectNode first = (ObjectNode) differences.get(0);
          first.put("mode", "wildcard");
          first.put("selectorType", "xpath-all");
          first.set(CASES, JSON.createArrayNode());
          first.set(SELECTORS, JSON.createArrayNode());
          first.put(CURRENT, "");
          first.put("nk", "");
          ObjectNode second = (ObjectNode) differences.get(1);
          second.put("field", first.path("field").asText());
          second.set(CASES, JSON.valueToTree(List.of("CHR-L01", "CHR-L01", UNKNOWN_CASE)));
          second.set(SELECTORS, JSON.valueToTree(List.of("same", "same")));
          ((ObjectNode) differences.get(2)).set(SELECTORS, JSON.valueToTree(List.of("")));
          ((ObjectNode) differences.get(3)).set(SELECTORS, JSON.valueToTree(List.of("all*")));
          ((ObjectNode) differences.get(4)).set(SELECTORS, JSON.valueToTree(List.of("a..b")));
          ((ObjectNode) differences.get(5)).set(SELECTORS, JSON.valueToTree(List.of("$.all")));
          ((ObjectNode) differences.get(14)).put("id", "DIF-X15");
        });
    assertFailures(
        fixture.validate(),
        "DIF_VERSION",
        "DIF_MODE:DIF-001",
        "DIF_SELECTOR_TYPE:DIF-001",
        "DIF_CASES_EMPTY:DIF-001",
        "DIF_SELECTOR_EMPTY:DIF-001",
        "DIF_CURRENT:DIF-001",
        "DIF_NK:DIF-001",
        "DIF_DUPLICATE_FIELD:DIF-002",
        "DIF_CASES_DUPLICATE:DIF-002",
        "DIF_UNKNOWN_CASE:DIF-002:CHR-Z99",
        "DIF_SELECTOR_DUPLICATE:DIF-002",
        "DIF_SELECTOR_WILDCARD:DIF-003",
        "DIF_SELECTOR_WILDCARD:DIF-004",
        "DIF_SELECTOR_WILDCARD:DIF-005",
        "DIF_SELECTOR_WILDCARD:DIF-006",
        "DIF_ID_SEQUENCE",
        "DIF-015_CASE_COVERAGE");
  }

  /** PT-CHR-DEF077: the approved legacy HTTP path is a single semantic contract. */
  @Test
  void rejectsOtherValidMetadataValuesForTheLegacyPathContract() throws Exception {
    List<List<String>> changes =
        List.of(
            List.of("mode", "difference"),
            List.of("field", "unrelated.field"),
            List.of("selectorType", "header"),
            List.of(SELECTORS, "other.path"));
    int index = 0;
    for (List<String> change : changes) {
      Fixture sample = fixture("path-contract-" + ++index);
      sample.mutate(
          "program/characterization/tests/resources/cases/dif-allowlist.json",
          root -> {
            ObjectNode pathContract = (ObjectNode) array(root, "differences").get(14);
            String property = change.getFirst();
            String changed = change.getLast();
            if (SELECTORS.equals(property)) {
              pathContract.putArray(SELECTORS).add(changed);
            } else {
              pathContract.put(property, changed);
            }
          });
      assertFailures(sample.validate(), "DIF-015_CONTRACT_SHAPE");
    }
  }

  @Test
  void rejectsIncompleteRequirementMatrix() throws Exception {
    Fixture fixture = fixture("requirements");
    fixture.mutate(
        "program/characterization/tests/resources/cases/case-requirements.json",
        root -> {
          root.put(VERSION, 0);
          ObjectNode requirements = object(root, "requirements");
          requirements.set("CHR-A01", JSON.valueToTree(List.of("caseId", "caseId")));
          requirements.set("CHR-A02", JSON.valueToTree(List.of(STATUS)));
          requirements.remove("CHR-O01");
          ObjectNode supplemental = object(root, "supplementalChecks");
          supplemental.set("CHR-A02", JSON.createArrayNode());
          supplemental.set(
              "CHR-A03", JSON.valueToTree(List.of("unsafe-post-denied", "unsafe-post-denied")));
          supplemental.set(UNKNOWN_CASE, JSON.valueToTree(List.of(UNKNOWN)));
          ObjectNode nkOnly = object(root, "nkOnlySupplementalChecks");
          nkOnly.set(UNKNOWN_CASE, JSON.valueToTree(List.of(UNKNOWN)));
          nkOnly.set("CHR-E01", JSON.valueToTree(List.of("not-defined")));
        });
    assertFailures(
        fixture.validate(),
        "REQ_VERSION",
        "REQ_CASE_ORDER",
        "REQ_CORE:CHR-A01",
        "REQ_DUPLICATE:CHR-A01",
        "REQ_CORE:CHR-A02",
        "REQ_SUPPLEMENTAL_EMPTY:CHR-A02",
        "REQ_SUPPLEMENTAL_DUPLICATE:CHR-A03",
        "REQ_SUPPLEMENTAL_CASE:CHR-Z99",
        "REQ_NK_ONLY_CASE:CHR-Z99",
        "REQ_NK_ONLY_UNKNOWN:CHR-E01:not-defined");
  }

  @Test
  void rejectsMissingFailedAndIncompleteRunArtifacts() throws Exception {
    Fixture fixture = fixture("run-artifacts");
    Files.delete(fixture.firstRun().resolve("artifacts/CHR-A01.json"));
    Files.delete(fixture.firstRun().resolve("screenshots/CHR-U01-desktop.png"));
    fixture.mutateRun(
        false,
        "artifacts/CHR-A02.json",
        root -> root.put("caseId", "CHR-X00").put(STATUS, "SKIPPED"));
    fixture.mutateRun(
        false,
        "artifacts/CHR-A03.json",
        root -> {
          root.remove("logoutMethod");
          root.putNull("missingCsrfStatus");
        });
    fixture.mutateRun(
        false,
        "artifacts/CHR-U01.json",
        root -> root.put("mobileScreenshotSha256", "0".repeat(64)));
    fixture.mutateRun(
        true,
        "supplemental.json",
        root -> {
          ObjectNode checks = object(root, "checks");
          ObjectNode ip = object(object(checks, "CHR-A02"), "ip-limit-observed-not-hardcoded");
          ip.put(STATUS, "NK_ONLY");
          ip.set(EVIDENCE, JSON.createObjectNode());
          ObjectNode csrf = object(object(checks, "CHR-A03"), "unsafe-post-denied");
          csrf.put(STATUS, FAILED);
          csrf.put(EVIDENCE, "invalid");
        });
    assertFailures(
        fixture.validate(),
        "run1_MISSING:CHR-A01",
        "run1_SCREENSHOT_COUNT",
        "run1_SCREENSHOT_DESKTOP",
        "run2_CASE_ID:CHR-A02",
        "run2_STATUS:CHR-A02",
        "run2_REJECTED_STATUS:CHR-A02",
        "run2_KEY:CHR-A03:logoutMethod",
        "run2_KEY:CHR-A03:missingCsrfStatus",
        "run2_SCREENSHOT_MOBILE_HASH",
        "run1_SUPPLEMENTAL:CHR-A02:ip-limit-observed-not-hardcoded",
        "run1_SUPPLEMENTAL_EVIDENCE:CHR-A02:ip-limit-observed-not-hardcoded",
        "run1_SUPPLEMENTAL:CHR-A03:unsafe-post-denied",
        "run1_SUPPLEMENTAL_EVIDENCE:CHR-A03:unsafe-post-denied");
  }

  @ParameterizedTest
  @ValueSource(strings = {FAILED, "FAILED", "FLAKY", "SKIP", "SKIPPED", "DISABLED", "NOT_RUN"})
  void rejectsEveryNonPassExecutionStatus(String rejectedStatus) throws Exception {
    Fixture fixture =
        fixture("rejected-status-" + rejectedStatus.toLowerCase(java.util.Locale.ROOT));
    fixture.mutateRun(false, "artifacts/CHR-A02.json", root -> root.put(STATUS, rejectedStatus));
    assertFailures(fixture.validate(), "run2_STATUS:CHR-A02", "run2_REJECTED_STATUS:CHR-A02");
  }

  @Test
  void rejectsMissingScreenshotDirectoriesAndOptionalReports() throws Exception {
    Fixture fixture = fixture("missing-directories");
    deleteTree(fixture.firstRun().resolve("screenshots"));
    deleteTree(fixture.secondRun().resolve("artifacts"));
    Files.delete(fixture.secondRun().resolve("supplemental.json"));
    assertFailures(
        fixture.validate(),
        "run1_SCREENSHOT_COUNT",
        "run1_SCREENSHOT_DESKTOP",
        "run1_SCREENSHOT_MOBILE",
        "run2_CASE_COVERAGE",
        "run2_MISSING:CHR-A01",
        "run2_SUPPLEMENTAL:CHR-A02:ip-limit-observed-not-hardcoded");
  }

  @Test
  void rejectsComparisonSourceInventoryPreflightAndReviewFailures() throws Exception {
    Fixture fixture = fixture("reports");
    fixture.mutate(
        "program/characterization/reports/current-repeat-comparison.json",
        root -> {
          root.put(STATUS, FAILED);
          root.put("firstFileCount", 27);
          root.put("secondFileCount", 29);
          root.put("missing", NOT_ARRAY);
          root.set("extra", JSON.valueToTree(List.of("extra")));
          root.set("changed", JSON.valueToTree(List.of("changed")));
        });
    fixture.mutate(
        "program/characterization/reports/source-verification.json",
        root -> {
          root.put(STATUS, FAILED);
          root.put("sourceFileCount", 0);
          root.put("sourceAggregateSha256", BAD_VALUE);
          root.put("documentFileCount", 0);
          root.put("documentAggregateSha256", BAD_VALUE);
          root.put("masterFileCount", 0);
          root.put("masterBytes", 0);
          root.put("masterSymlinks", NOT_ARRAY);
        });
    fixture.mutateRun(
        true,
        "inventory.json",
        root -> {
          root.put(STATUS, FAILED);
          root.put("scenarioFileCount", 0);
          root.put("scenarioEntryCount", 0);
          root.put("audioMetadataCount", 0);
          root.put("audioLinkCount", 0);
          root.put("videoCount", 0);
          root.put("musicCount", 0);
        });
    fixture.mutate(
        "program/characterization/reports/preflight.json",
        root -> {
          root.put(STATUS, FAILED);
          root.put("failures", NOT_ARRAY);
          root.put("credentialPermission", "INVALID");
          root.set("hostAllowlist", JSON.valueToTree(List.of("external")));
          root.put("freeBytes", 1);
        });
    fixture.mutate(
        "program/characterization/reports/review-record.json",
        root -> {
          root.put(STATUS, "REJECTED");
          root.put("baselineCommit", BAD_VALUE);
          root.put("reviewerRole", "");
          root.put(EVIDENCE, NOT_ARRAY);
          object(root, "checks")
              .properties()
              .forEach(entry -> ((ObjectNode) root.path("checks")).put(entry.getKey(), false));
        });
    assertFailures(
        fixture.validate(),
        "COMPARE_STATUS",
        "COMPARE_FIRST_COUNT",
        "COMPARE_SECOND_COUNT",
        "COMPARE_MISSING",
        "COMPARE_EXTRA",
        "COMPARE_CHANGED",
        "SOURCE_STATUS",
        "SOURCE_VALUE:sourceFileCount",
        "SOURCE_SYMLINKS",
        "run1_INVENTORY_STATUS",
        "run1_INVENTORY_VALUE:scenarioFileCount",
        "INVENTORY_REPEAT_DIFF",
        "PREFLIGHT_STATUS",
        "PREFLIGHT_FAILURES",
        "PREFLIGHT_CREDENTIAL",
        "PREFLIGHT_HOSTS",
        "PREFLIGHT_DISK",
        "REVIEW_STATUS",
        "REVIEW_COMMIT",
        "REVIEW_ROLE",
        "REVIEW_EVIDENCE",
        "REVIEW_CHECK:currentSourceUnchanged");
  }

  @Test
  void rejectsAlteredBaselineManifestTreeAndCommit() throws Exception {
    Fixture fixture = fixture("baseline");
    fixture.mutate(
        "program/characterization/baseline/current/manifest.json",
        root -> {
          root.put("target", "nk");
          root.put("caseCount", 23);
          root.put("screenshotFileCount", 1);
          root.put("differenceCount", 15);
          root.put("sourceAggregateSha256", BAD_VALUE);
          root.put("documentAggregateSha256", BAD_VALUE);
          root.put("masterFileCount", 0);
          root.put("masterBytes", 0);
          ObjectNode environment = object(root, "environment");
          environment.put("javaVersion", "0");
          environment.put("browserRevision", 0);
          environment.put("locale", "en-US");
          environment.put("timezone", "UTC");
          root.put("gateCommit", "not-a-commit");
        });
    fixture.mutate(
        "program/characterization/tests/resources/cases/gate-contract.json",
        root -> {
          root.put("baselineFileCount", 0);
          root.put("baselineAggregateSha256", "0".repeat(64));
        });
    assertFailures(
        fixture.validate(),
        "BASELINE_TARGET",
        "BASELINE_CASE_COUNT",
        "BASELINE_SCREENSHOT_COUNT",
        "BASELINE_DIF_COUNT",
        "BASELINE_SOURCE_HASH",
        "BASELINE_DOCUMENT_HASH",
        "BASELINE_MASTER_COUNT",
        "BASELINE_MASTER_BYTES",
        "BASELINE_JAVA",
        "BASELINE_BROWSER",
        "BASELINE_LOCALE",
        "BASELINE_TIMEZONE",
        "BASELINE_FILE_COUNT",
        "BASELINE_TREE_HASH",
        "BASELINE_GATE_COMMIT");
  }

  @Test
  void rejectsNonEmptyCompositeReportsAndMissingMobileScreenshot() throws Exception {
    Fixture fixture = fixture("composite-secondary");
    Files.delete(fixture.firstRun().resolve("screenshots/CHR-U01-mobile.png"));
    fixture.mutate(
        "program/characterization/reports/current-repeat-comparison.json",
        root -> {
          root.set("missing", JSON.valueToTree(List.of("missing")));
          root.put("extra", NOT_ARRAY);
          root.put("changed", NOT_ARRAY);
        });
    fixture.mutate(
        "program/characterization/reports/source-verification.json",
        root -> root.set("masterSymlinks", JSON.valueToTree(List.of("link"))));
    fixture.mutate(
        "program/characterization/reports/preflight.json",
        root -> root.set("failures", JSON.valueToTree(List.of("failure"))));
    fixture.mutate(
        "program/characterization/reports/review-record.json",
        root -> root.set(EVIDENCE, JSON.valueToTree(List.of("one"))));
    assertFailures(
        fixture.validate(),
        "run1_SCREENSHOT_MOBILE",
        "COMPARE_MISSING",
        "COMPARE_EXTRA",
        "COMPARE_CHANGED",
        "SOURCE_SYMLINKS",
        "PREFLIGHT_FAILURES",
        "REVIEW_EVIDENCE");
  }

  @Test
  void acceptsActualBaselineCommitAndRejectsMissingBaselineDirectories() throws Exception {
    Fixture actualCommit = fixture("actual-commit");
    actualCommit.mutate(
        "program/characterization/baseline/current/manifest.json",
        root -> root.put("gateCommit", "843de94"));
    GateContractValidator.ValidationResult actualCommitResult = actualCommit.validate();
    assertFalse(actualCommitResult.failures().contains("BASELINE_GATE_COMMIT"));

    Fixture missing = fixture("missing-baseline");
    deleteTree(missing.root().resolve("program/characterization/baseline/current/artifacts"));
    deleteTree(missing.root().resolve("program/characterization/baseline/current/screenshots"));
    assertFailures(
        missing.validate(),
        "BASELINE_FILE_COUNT",
        "BASELINE_TREE_HASH",
        "baseline_CASE_COVERAGE",
        "baseline_MISSING:CHR-A01",
        "baseline_SCREENSHOT_COUNT");
  }

  private Fixture fixture(String name) throws IOException {
    Path root = temporaryDirectory.resolve(name);
    copyTree(
        SOURCE_ROOT.resolve("program/characterization/tests/resources"),
        root.resolve("program/characterization/tests/resources"));
    copyTree(
        SOURCE_ROOT.resolve("program/characterization/baseline/current"),
        root.resolve("program/characterization/baseline/current"));
    Path reports = root.resolve("program/characterization/reports");
    Files.createDirectories(reports.resolve(CURRENT));
    for (String report :
        List.of(
            "source-verification.json",
            "preflight.json",
            "review-record.json",
            "current-repeat-comparison.json")) {
      Files.copy(
          SOURCE_ROOT.resolve("program/characterization/reports").resolve(report),
          reports.resolve(report),
          StandardCopyOption.COPY_ATTRIBUTES);
    }
    copyTree(
        SOURCE_ROOT.resolve("program/characterization/reports/current/pgpt-gate-20260901-05"),
        reports.resolve("current/run1"));
    copyTree(
        SOURCE_ROOT.resolve("program/characterization/reports/current/pgpt-gate-20260901-06"),
        reports.resolve("current/run2"));
    return new Fixture(root, reports.resolve("current/run1"), reports.resolve("current/run2"));
  }

  private static void assertFailures(
      GateContractValidator.ValidationResult result, String... expected) {
    assertFalse(result.passed());
    for (String failure : expected) {
      assertTrue(
          result.failures().contains(failure),
          () -> "missing " + failure + " in " + result.failures());
    }
  }

  private static ObjectNode object(ObjectNode parent, String name) {
    JsonNode value = parent.path(name);
    if (!(value instanceof ObjectNode object)) {
      throw new IllegalStateException("not an object: " + name);
    }
    return object;
  }

  private static ArrayNode array(ObjectNode parent, String name) {
    JsonNode value = parent.path(name);
    if (!(value instanceof ArrayNode array)) {
      throw new IllegalStateException("not an array: " + name);
    }
    return array;
  }

  private static void copyTree(Path source, Path destination) throws IOException {
    try (Stream<Path> paths = Files.walk(source)) {
      for (Path path : paths.sorted().toList()) {
        Path target = destination.resolve(source.relativize(path).toString());
        if (Files.isDirectory(path)) {
          Files.createDirectories(target);
        } else {
          Files.copy(path, target, StandardCopyOption.COPY_ATTRIBUTES);
        }
      }
    }
  }

  private static void deleteTree(Path root) throws IOException {
    if (!Files.exists(root)) return;
    try (Stream<Path> paths = Files.walk(root)) {
      for (Path path : paths.sorted((left, right) -> right.compareTo(left)).toList()) {
        Files.delete(path);
      }
    }
  }

  private record Fixture(Path root, Path firstRun, Path secondRun) {
    GateContractValidator.ValidationResult validate() throws Exception {
      return GateContractValidator.validate(
          root,
          firstRun,
          secondRun,
          root.resolve("program/characterization/reports/current-repeat-comparison.json"));
    }

    void mutate(String relative, Consumer<ObjectNode> mutation) throws IOException {
      mutate(root.resolve(relative), mutation);
    }

    void mutateRun(boolean first, String relative, Consumer<ObjectNode> mutation)
        throws IOException {
      mutate((first ? firstRun : secondRun).resolve(relative), mutation);
    }

    private static void mutate(Path path, Consumer<ObjectNode> mutation) throws IOException {
      ObjectNode value = (ObjectNode) JSON.readTree(path.toFile());
      mutation.accept(value);
      JSON.writerWithDefaultPrettyPrinter().writeValue(path.toFile(), value);
    }
  }
}
