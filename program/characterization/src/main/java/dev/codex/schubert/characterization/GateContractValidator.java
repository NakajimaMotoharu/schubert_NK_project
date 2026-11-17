package dev.codex.schubert.characterization;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.Predicate;
import java.util.stream.Stream;

/**
 * Machine assertions for UI 264 and SS 355.
 *
 * <p>Program: NK-CHR-001. Tests: PT-CHR-G01-* through PT-CHR-G06-*.
 */
final class GateContractValidator {
  private static final String HASH_SUFFIX = "Sha256";
  private static final String FIELD_CASE_ORDER = "caseOrder";
  private static final String FIELD_CURRENT_APPLICABLE_COUNT = "currentApplicableCount";
  private static final int CASE_GROUP_OFFSET = 4;
  private static final String FIELD_BASELINECOMMIT = "baselineCommit";
  private static final String FIELD_VERSION = "version";
  private static final String FIELD_CASES = "cases";
  private static final String FIELD_CURRENT = "current";
  private static final String FIELD_DEVICESCALEFACTOR = "deviceScaleFactor";
  private static final String FIELD_STATUS = "status";
  private static final String VALUE_PASS = "PASS";
  private static final String FIELD_EVIDENCE = "evidence";
  private static final String FIELD_ENVIRONMENT = "environment";

  private static final ObjectMapper JSON = new ObjectMapper();
  private static final Set<String> MODES = Set.of("difference", "required", "contract");
  private static final Set<String> SELECTOR_TYPES = Set.of("semantic", "header", "json-pointer");

  private GateContractValidator() {
    throw new AssertionError("GateContractValidator is a static tool");
  }

  static ValidationResult validate(
      Path projectRoot, Path firstRun, Path secondRun, Path comparisonReport)
      throws IOException, NoSuchAlgorithmException {
    Path resources = projectRoot.resolve("program/characterization/tests/resources");
    JsonNode contract = read(resources.resolve("cases/gate-contract.json"));
    JsonNode catalog = read(resources.resolve("cases/catalog.json"));
    JsonNode schema = read(resources.resolve("cases/schema.json"));
    JsonNode differences = read(resources.resolve("cases/dif-allowlist.json"));
    JsonNode browser = read(resources.resolve("browser/manifest.json"));
    JsonNode requirements = read(resources.resolve("cases/case-requirements.json"));
    JsonNode baselineManifest =
        read(projectRoot.resolve("program/characterization/baseline/current/manifest.json"));
    JsonNode sourceReport =
        read(projectRoot.resolve("program/characterization/reports/source-verification.json"));
    JsonNode firstInventory = readOptional(firstRun.resolve("inventory.json"));
    JsonNode secondInventory = readOptional(secondRun.resolve("inventory.json"));
    JsonNode preflight =
        read(projectRoot.resolve("program/characterization/reports/preflight.json"));
    JsonNode review =
        read(projectRoot.resolve("program/characterization/reports/review-record.json"));
    JsonNode comparison = read(comparisonReport);

    List<String> failures =
        new ArrayList<>(
            validateDefinitions(contract, catalog, schema, differences, browser, requirements));
    List<String> caseOrder = strings(contract.path(FIELD_CASE_ORDER));
    validateRun(firstRun, caseOrder, requirements, "run1", true, failures);
    validateRun(secondRun, caseOrder, requirements, "run2", true, failures);
    failures.addAll(
        validateEvidenceDocuments(
            comparison,
            sourceReport,
            firstInventory,
            secondInventory,
            contract.path("source"),
            preflight,
            review,
            contract.path(FIELD_BASELINECOMMIT).asText()));
    validateBaseline(
        projectRoot,
        projectRoot.resolve("program/characterization/baseline/current"),
        baselineManifest,
        contract,
        sourceReport,
        caseOrder,
        requirements,
        failures);

    Map<String, Object> metrics =
        gateMetrics(
            contract,
            differences,
            caseOrder.size(),
            regularFiles(
                    projectRoot.resolve("program/characterization/baseline/current"), path -> true)
                .size(),
            failures.size());
    return new ValidationResult(List.copyOf(failures), Map.copyOf(metrics));
  }

  /**
   * SS355 / PT-CHR-METRIC001..006: pure report projection, never enumerates files or qualifies a
   * run.
   */
  static Map<String, Object> gateMetrics(
      JsonNode contract,
      JsonNode differences,
      int caseCount,
      int baselineFileCount,
      int failureCount) {
    if (contract == null || differences == null) {
      throw new IllegalArgumentException("metric documents are required");
    }
    if (caseCount < 0 || baselineFileCount < 0 || failureCount < 0) {
      throw new IllegalArgumentException("observed metric counts must be nonnegative");
    }
    Map<String, Object> metrics = new LinkedHashMap<>();
    if (contract.path(FIELD_CASE_ORDER).isArray()) {
      metrics.put("caseCount", caseCount);
    }
    if (integerEquals(contract.path(FIELD_CURRENT_APPLICABLE_COUNT), 23)) {
      metrics.put(FIELD_CURRENT_APPLICABLE_COUNT, 23);
    }
    if (differences.path("differences").isArray()) {
      metrics.put("differenceCount", differences.path("differences").size());
    }
    metrics.put("baselineFileCount", baselineFileCount);
    metrics.put("failureCount", failureCount);
    return Map.copyOf(metrics);
  }

  static boolean matchesBaselineFileCount(JsonNode contract, int actualCount) {
    if (contract == null || actualCount < 0) {
      throw new IllegalArgumentException("baseline count input is invalid");
    }
    return integerEquals(contract.path("baselineFileCount"), actualCount);
  }

  /**
   * PT-CHR-DEF-001..011 / SS355. Pure public-definition stage used by the full gate above.
   * Caller-frozen JSON only; no baseline, filesystem, capture, runtime or authority qualification.
   */
  static List<String> validateDefinitions(
      JsonNode contract,
      JsonNode catalog,
      JsonNode schema,
      JsonNode differences,
      JsonNode browser,
      JsonNode requirements) {
    for (JsonNode document :
        new JsonNode[] {contract, catalog, schema, differences, browser, requirements}) {
      if (document == null) throw new IllegalArgumentException("definition document is required");
    }
    List<String> failures = new ArrayList<>();
    validateContractShape(contract, failures);
    List<String> caseOrder = strings(contract.path(FIELD_CASE_ORDER));
    validateSchema(schema, failures);
    validateCatalog(catalog, caseOrder, failures);
    validateBrowser(browser, contract.path("browser"), failures);
    validateDifferences(differences, contract.path("differenceIds"), caseOrder, failures);
    validateRequirements(requirements, caseOrder, failures);
    return List.copyOf(failures);
  }

  private static void validateContractShape(JsonNode contract, List<String> failures) {
    require(contract.isObject(), "CONTRACT_NOT_OBJECT", failures);
    require(
        integerEquals(contract.path(FIELD_CURRENT_APPLICABLE_COUNT), 23),
        "CONTRACT_CURRENT_COUNT",
        failures);
    require(
        integerEquals(contract.path("baselineFileCount"), 27),
        "CONTRACT_BASELINE_FILE_COUNT",
        failures);
    require(
        CorrelatedLogEvidenceValidator.versionOne(contract.path(FIELD_VERSION)),
        "CONTRACT_VERSION",
        failures);
    require(
        strings(contract.path("gates"))
            .equals(List.of("CHR-G01", "CHR-G02", "CHR-G03", "CHR-G04", "CHR-G05", "CHR-G06")),
        "CONTRACT_GATE_IDS",
        failures);
    List<String> cases = strings(contract.path(FIELD_CASE_ORDER));
    require(cases.size() == 24, "CONTRACT_CASE_COUNT", failures);
    require(new HashSet<>(cases).size() == cases.size(), "CONTRACT_CASE_DUPLICATE", failures);
    require(
        strings(contract.path("differenceIds")).size() == 16,
        "CONTRACT_DIFFERENCE_COUNT",
        failures);
    require(
        contract.path(FIELD_BASELINECOMMIT).asText().matches("[0-9a-f]{7,40}"),
        "CONTRACT_BASELINE_COMMIT",
        failures);
    require(
        contract.path("baselineAggregateSha256").asText().matches("[0-9a-f]{64}"),
        "CONTRACT_BASELINE_HASH",
        failures);
  }

  private static void validateSchema(JsonNode schema, List<String> failures) {
    require(schema.isObject(), "SCHEMA_NOT_OBJECT", failures);
    require(
        "https://json-schema.org/draft/2020-12/schema".equals(schema.path("$schema").asText()),
        "SCHEMA_DRAFT",
        failures);
    require("object".equals(schema.path("type").asText()), "SCHEMA_ROOT_TYPE", failures);
    require(
        strings(schema.path("required")).equals(List.of(FIELD_VERSION, FIELD_CASES)),
        "SCHEMA_REQUIRED",
        failures);
    JsonNode cases = schema.path("properties").path(FIELD_CASES);
    require(integerEquals(cases.path("minItems"), 24), "SCHEMA_MIN_ITEMS", failures);
    require(integerEquals(cases.path("maxItems"), 24), "SCHEMA_MAX_ITEMS", failures);
    require(
        strings(cases.path("items").path("required"))
            .equals(List.of("id", "group", FIELD_CURRENT, "nk")),
        "SCHEMA_CASE_REQUIRED",
        failures);
  }

  private static void validateCatalog(
      JsonNode catalog, List<String> expectedOrder, List<String> failures) {
    require(catalog.isObject(), "CATALOG_NOT_OBJECT", failures);
    require(
        CorrelatedLogEvidenceValidator.versionOne(catalog.path(FIELD_VERSION)),
        "CATALOG_VERSION",
        failures);
    JsonNode cases = catalog.path(FIELD_CASES);
    require(cases.isArray(), "CATALOG_CASES_NOT_ARRAY", failures);
    List<String> actualOrder = new ArrayList<>();
    Set<String> ids = new HashSet<>();
    for (JsonNode item : cases) {
      String id = item.path("id").asText();
      actualOrder.add(id);
      if (!ids.add(id)) {
        failures.add("CATALOG_DUPLICATE:" + id);
      }
      require(id.matches("CHR-[A-Z][0-9]{2}"), "CATALOG_ID:" + id, failures);
      require(
          expectedGroup(id).equals(item.path("group").asText()), "CATALOG_GROUP:" + id, failures);
      String expectedCurrent = "CHR-N01".equals(id) ? "NK_ONLY" : "RUN";
      require(
          expectedCurrent.equals(item.path(FIELD_CURRENT).asText()),
          "CATALOG_CURRENT:" + id,
          failures);
      require("RUN".equals(item.path("nk").asText()), "CATALOG_NK:" + id, failures);
    }
    require(expectedOrder.equals(actualOrder), "CATALOG_ORDER", failures);
  }

  private static String expectedGroup(String id) {
    if (id.length() <= CASE_GROUP_OFFSET) {
      return "";
    }
    return switch (id.charAt(CASE_GROUP_OFFSET)) {
      case 'A' -> "Authentication";
      case 'U' -> "Common UI";
      case 'S' -> "Scenario";
      case 'M' -> "Media";
      case 'L' -> "Log";
      case 'E' -> "Error";
      case 'N' -> "New feature";
      case 'O' -> "Operation";
      default -> "";
    };
  }

  private static void validateBrowser(JsonNode browser, JsonNode expected, List<String> failures) {
    require(
        expected.path("playwrightJava").asText().equals(browser.path("playwrightJava").asText()),
        "BROWSER_PLAYWRIGHT",
        failures);
    require(
        expected.path("browser").asText().equals(browser.path("browser").asText()),
        "BROWSER_NAME",
        failures);
    require(
        matchingInteger(expected.path("browserRevision"), browser.path("browserRevision")),
        "BROWSER_REVISION",
        failures);
    require(
        expected.path("locale").asText().equals(browser.path("locale").asText()),
        "BROWSER_LOCALE",
        failures);
    require(
        expected.path("timezone").asText().equals(browser.path("timezone").asText()),
        "BROWSER_TIMEZONE",
        failures);
    require(
        matchingInteger(expected.path("desktopWidth"), browser.path("desktop").path("width"))
            && matchingInteger(
                expected.path("desktopHeight"), browser.path("desktop").path("height")),
        "BROWSER_DESKTOP_VIEWPORT",
        failures);
    require(
        matchingInteger(expected.path("mobileWidth"), browser.path("mobile").path("width"))
            && matchingInteger(
                expected.path("mobileHeight"), browser.path("mobile").path("height")),
        "BROWSER_MOBILE_VIEWPORT",
        failures);
    require(
        matchingInteger(
                expected.path(FIELD_DEVICESCALEFACTOR),
                browser.path("desktop").path(FIELD_DEVICESCALEFACTOR))
            && matchingInteger(
                expected.path(FIELD_DEVICESCALEFACTOR),
                browser.path("mobile").path(FIELD_DEVICESCALEFACTOR)),
        "BROWSER_DEVICE_SCALE",
        failures);
    require(!strings(browser.path("fonts")).isEmpty(), "BROWSER_FONTS", failures);
    require(
        "document.fonts.status=loaded".equals(browser.path("fontReady").asText()),
        "BROWSER_FONT_READY",
        failures);
    require("light".equals(browser.path("colorScheme").asText()), "BROWSER_COLOR_SCHEME", failures);
    require(
        "reduce".equals(browser.path("reducedMotion").asText()),
        "BROWSER_REDUCED_MOTION",
        failures);
  }

  private static boolean integerEquals(JsonNode value, int expected) {
    return value.isIntegralNumber() && value.canConvertToInt() && value.intValue() == expected;
  }

  private static boolean matchingInteger(JsonNode expected, JsonNode actual) {
    return expected.isIntegralNumber()
        && expected.canConvertToInt()
        && expected.intValue() > 0
        && integerEquals(actual, expected.intValue());
  }

  private static void validateDifferences(
      JsonNode catalog,
      JsonNode expectedIdsNode,
      List<String> expectedCases,
      List<String> failures) {
    require(
        CorrelatedLogEvidenceValidator.versionOne(catalog.path(FIELD_VERSION)),
        "DIF_VERSION",
        failures);
    JsonNode differences = catalog.path("differences");
    require(differences.isArray(), "DIF_NOT_ARRAY", failures);
    List<String> ids = new ArrayList<>();
    Set<String> fields = new HashSet<>();
    for (JsonNode difference : differences) {
      String id = difference.path("id").asText();
      ids.add(id);
      require(fields.add(difference.path("field").asText()), "DIF_DUPLICATE_FIELD:" + id, failures);
      require(MODES.contains(difference.path("mode").asText()), "DIF_MODE:" + id, failures);
      require(
          SELECTOR_TYPES.contains(difference.path("selectorType").asText()),
          "DIF_SELECTOR_TYPE:" + id,
          failures);
      List<String> cases = strings(difference.path(FIELD_CASES));
      require(!cases.isEmpty(), "DIF_CASES_EMPTY:" + id, failures);
      require(new HashSet<>(cases).size() == cases.size(), "DIF_CASES_DUPLICATE:" + id, failures);
      for (String caseId : cases) {
        require(expectedCases.contains(caseId), "DIF_UNKNOWN_CASE:" + id + ":" + caseId, failures);
      }
      List<String> selectors = strings(difference.path("selectors"));
      require(!selectors.isEmpty(), "DIF_SELECTOR_EMPTY:" + id, failures);
      require(
          new HashSet<>(selectors).size() == selectors.size(),
          "DIF_SELECTOR_DUPLICATE:" + id,
          failures);
      for (String selector : selectors) {
        require(
            !selector.isBlank()
                && !selector.contains("*")
                && !selector.contains("..")
                && !selector.contains("$"),
            "DIF_SELECTOR_WILDCARD:" + id,
            failures);
      }
      require(!difference.path(FIELD_CURRENT).asText().isBlank(), "DIF_CURRENT:" + id, failures);
      require(!difference.path("nk").asText().isBlank(), "DIF_NK:" + id, failures);
    }
    require(strings(expectedIdsNode).equals(ids), "DIF_ID_SEQUENCE", failures);
    JsonNode pathContract = findDifference(differences, "DIF-015");
    require(
        expectedCases.equals(strings(pathContract.path(FIELD_CASES))),
        "DIF-015_CASE_COVERAGE",
        failures);
  }

  private static JsonNode findDifference(JsonNode differences, String id) {
    for (JsonNode item : differences) {
      if (id.equals(item.path("id").asText())) {
        return item;
      }
    }
    return JSON.createObjectNode();
  }

  private static void validateRequirements(
      JsonNode requirements, List<String> expectedCases, List<String> failures) {
    require(
        CorrelatedLogEvidenceValidator.versionOne(requirements.path(FIELD_VERSION)),
        "REQ_VERSION",
        failures);
    JsonNode byCase = requirements.path("requirements");
    require(byCase.isObject(), "REQ_NOT_OBJECT", failures);
    List<String> actualCases = new ArrayList<>();
    byCase.fieldNames().forEachRemaining(actualCases::add);
    require(expectedCases.equals(actualCases), "REQ_CASE_ORDER", failures);
    for (String caseId : expectedCases) {
      List<String> keys = strings(byCase.path(caseId));
      require(
          keys.contains("caseId") && keys.contains(FIELD_STATUS), "REQ_CORE:" + caseId, failures);
      require(new HashSet<>(keys).size() == keys.size(), "REQ_DUPLICATE:" + caseId, failures);
    }
    JsonNode supplemental = requirements.path("supplementalChecks");
    require(supplemental.isObject(), "REQ_SUPPLEMENTAL_NOT_OBJECT", failures);
    supplemental
        .properties()
        .forEach(
            entry -> {
              require(
                  expectedCases.contains(entry.getKey()),
                  "REQ_SUPPLEMENTAL_CASE:" + entry.getKey(),
                  failures);
              List<String> checks = strings(entry.getValue());
              require(!checks.isEmpty(), "REQ_SUPPLEMENTAL_EMPTY:" + entry.getKey(), failures);
              require(
                  new HashSet<>(checks).size() == checks.size(),
                  "REQ_SUPPLEMENTAL_DUPLICATE:" + entry.getKey(),
                  failures);
            });
    JsonNode nkOnly = requirements.path("nkOnlySupplementalChecks");
    require(nkOnly.isObject(), "REQ_NK_ONLY_NOT_OBJECT", failures);
    nkOnly
        .properties()
        .forEach(
            entry -> {
              require(
                  expectedCases.contains(entry.getKey()),
                  "REQ_NK_ONLY_CASE:" + entry.getKey(),
                  failures);
              for (String check : strings(entry.getValue())) {
                require(
                    strings(supplemental.path(entry.getKey())).contains(check),
                    "REQ_NK_ONLY_UNKNOWN:" + entry.getKey() + ":" + check,
                    failures);
              }
            });
  }

  private static void validateRun(
      Path runRoot,
      List<String> expectedCases,
      JsonNode requirements,
      String label,
      boolean requireSupplemental,
      List<String> failures)
      throws IOException, NoSuchAlgorithmException {
    Path artifactRoot = runRoot.resolve("artifacts");
    List<String> actualCases = caseIds(artifactRoot);
    require(expectedCases.equals(actualCases), label + "_CASE_COVERAGE", failures);
    Set<String> rejected =
        Set.of("FAIL", "FAILED", "FLAKY", "SKIP", "SKIPPED", "DISABLED", "NOT_RUN");
    for (String caseId : expectedCases) {
      Path artifact = artifactRoot.resolve(caseId + ".json");
      if (!Files.isRegularFile(artifact, LinkOption.NOFOLLOW_LINKS)) {
        failures.add(label + "_MISSING:" + caseId);
        continue;
      }
      JsonNode item = read(artifact);
      require(caseId.equals(item.path("caseId").asText()), label + "_CASE_ID:" + caseId, failures);
      String status = item.path(FIELD_STATUS).asText();
      require(VALUE_PASS.equals(status), label + "_STATUS:" + caseId, failures);
      require(!rejected.contains(status), label + "_REJECTED_STATUS:" + caseId, failures);
      for (String key : strings(requirements.path("requirements").path(caseId))) {
        require(
            item.has(key) && !item.path(key).isNull(),
            label + "_KEY:" + caseId + ":" + key,
            failures);
      }
    }
    Path screenshots = runRoot.resolve("screenshots");
    List<Path> screenshotFiles =
        regularFiles(
            screenshots,
            path -> ArtifactComparator.requiredArtifactFileName(path).endsWith(".png"));
    require(screenshotFiles.size() == 2, label + "_SCREENSHOT_COUNT", failures);
    require(
        Files.isRegularFile(screenshots.resolve("CHR-U01-desktop.png")),
        label + "_SCREENSHOT_DESKTOP",
        failures);
    require(
        Files.isRegularFile(screenshots.resolve("CHR-U01-mobile.png")),
        label + "_SCREENSHOT_MOBILE",
        failures);
    if (Files.isRegularFile(artifactRoot.resolve("CHR-U01.json"))
        && Files.isRegularFile(screenshots.resolve("CHR-U01-desktop.png"))
        && Files.isRegularFile(screenshots.resolve("CHR-U01-mobile.png"))) {
      JsonNode u01 = read(artifactRoot.resolve("CHR-U01.json"));
      require(
          sha256(screenshots.resolve("CHR-U01-desktop.png"))
              .equals(u01.path("desktopScreenshotSha256").asText()),
          label + "_SCREENSHOT_DESKTOP_HASH",
          failures);
      require(
          sha256(screenshots.resolve("CHR-U01-mobile.png"))
              .equals(u01.path("mobileScreenshotSha256").asText()),
          label + "_SCREENSHOT_MOBILE_HASH",
          failures);
    }
    if (requireSupplemental) {
      validateSupplemental(runRoot.resolve("supplemental.json"), requirements, label, failures);
    }
  }

  private static void validateSupplemental(
      Path report, JsonNode requirements, String label, List<String> failures) throws IOException {
    JsonNode checks = readOptional(report).path("checks");
    requirements
        .path("supplementalChecks")
        .properties()
        .forEach(
            entry -> {
              for (String check : strings(entry.getValue())) {
                JsonNode result = checks.path(entry.getKey()).path(check);
                String value = result.path(FIELD_STATUS).asText();
                boolean nkOnlyAllowed =
                    strings(requirements.path("nkOnlySupplementalChecks").path(entry.getKey()))
                        .contains(check);
                require(
                    VALUE_PASS.equals(value) || (nkOnlyAllowed && "NK_ONLY".equals(value)),
                    label + "_SUPPLEMENTAL:" + entry.getKey() + ":" + check,
                    failures);
                require(
                    result.path(FIELD_EVIDENCE).isObject()
                        && !result.path(FIELD_EVIDENCE).isEmpty(),
                    label + "_SUPPLEMENTAL_EVIDENCE:" + entry.getKey() + ":" + check,
                    failures);
              }
            });
  }

  /**
   * Metadata consistency only (SS355 / PT-CHR-META001..009); no collection, permission, source
   * ownership, actual approval or physical baseline qualification occurs in this stage.
   */
  static List<String> validateEvidenceDocuments(
      JsonNode comparison,
      JsonNode sourceReport,
      JsonNode firstInventory,
      JsonNode secondInventory,
      JsonNode expectedSource,
      JsonNode preflight,
      JsonNode review,
      String baselineCommit) {
    for (JsonNode document :
        new JsonNode[] {
          comparison,
          sourceReport,
          firstInventory,
          secondInventory,
          expectedSource,
          preflight,
          review
        }) {
      if (document == null) throw new IllegalArgumentException("evidence document is required");
    }
    if (baselineCommit == null)
      throw new IllegalArgumentException("baseline reference is required");
    List<String> failures = new ArrayList<>();
    validateComparison(comparison, failures);
    validateSource(sourceReport, firstInventory, expectedSource, "run1", failures);
    validateSource(sourceReport, secondInventory, expectedSource, "run2", failures);
    require(firstInventory.equals(secondInventory), "INVENTORY_REPEAT_DIFF", failures);
    validatePreflight(preflight, failures);
    validateReview(review, baselineCommit, failures);
    return List.copyOf(failures);
  }

  private static void validateComparison(JsonNode comparison, List<String> failures) {
    require(VALUE_PASS.equals(comparison.path(FIELD_STATUS).asText()), "COMPARE_STATUS", failures);
    require(integerEquals(comparison.path("firstFileCount"), 28), "COMPARE_FIRST_COUNT", failures);
    require(
        integerEquals(comparison.path("secondFileCount"), 28), "COMPARE_SECOND_COUNT", failures);
    require(
        comparison.path("missing").isArray() && comparison.path("missing").isEmpty(),
        "COMPARE_MISSING",
        failures);
    require(
        comparison.path("extra").isArray() && comparison.path("extra").isEmpty(),
        "COMPARE_EXTRA",
        failures);
    require(
        comparison.path("changed").isArray() && comparison.path("changed").isEmpty(),
        "COMPARE_CHANGED",
        failures);
  }

  private static void validateSource(
      JsonNode sourceReport,
      JsonNode inventoryReport,
      JsonNode expected,
      String label,
      List<String> failures) {
    require(VALUE_PASS.equals(sourceReport.path(FIELD_STATUS).asText()), "SOURCE_STATUS", failures);
    for (String field :
        List.of(
            "sourceFileCount",
            "sourceAggregateSha256",
            "documentFileCount",
            "documentAggregateSha256",
            "masterFileCount",
            "masterBytes")) {
      require(
          (field.endsWith(HASH_SUFFIX)
              ? matchingHash(expected.path(field), sourceReport.path(field))
              : matchingCount(expected.path(field), sourceReport.path(field))),
          "SOURCE_VALUE:" + field,
          failures);
    }
    require(
        sourceReport.path("masterSymlinks").isArray()
            && sourceReport.path("masterSymlinks").isEmpty(),
        "SOURCE_SYMLINKS",
        failures);
    require(
        VALUE_PASS.equals(inventoryReport.path(FIELD_STATUS).asText()),
        label + "_INVENTORY_STATUS",
        failures);
    for (String field :
        List.of(
            "scenarioFileCount",
            "scenarioEntryCount",
            "audioMetadataCount",
            "audioLinkCount",
            "videoCount",
            "musicCount")) {
      require(
          matchingCount(expected.path(field), inventoryReport.path(field)),
          label + "_INVENTORY_VALUE:" + field,
          failures);
    }
  }

  private static void validatePreflight(JsonNode preflight, List<String> failures) {
    require(VALUE_PASS.equals(preflight.path(FIELD_STATUS).asText()), "PREFLIGHT_STATUS", failures);
    require(
        preflight.path("failures").isArray() && preflight.path("failures").isEmpty(),
        "PREFLIGHT_FAILURES",
        failures);
    require(
        "0600".equals(preflight.path("credentialPermission").asText()),
        "PREFLIGHT_CREDENTIAL",
        failures);
    require(
        strings(preflight.path("hostAllowlist")).equals(List.of("localhost", "127.0.0.1")),
        "PREFLIGHT_HOSTS",
        failures);
    require(
        atLeastLong(preflight.path("freeBytes"), 20L * 1024 * 1024 * 1024),
        "PREFLIGHT_DISK",
        failures);
  }

  private static void validateReview(
      JsonNode review, String baselineCommit, List<String> failures) {
    require("APPROVED".equals(review.path(FIELD_STATUS).asText()), "REVIEW_STATUS", failures);
    require(
        baselineCommit.equals(review.path(FIELD_BASELINECOMMIT).asText()),
        "REVIEW_COMMIT",
        failures);
    require(
        review.path("reviewerRole").isTextual()
            && !review.path("reviewerRole").asText("").isBlank(),
        "REVIEW_ROLE",
        failures);
    require(
        review.path(FIELD_EVIDENCE).isArray() && review.path(FIELD_EVIDENCE).size() >= 3,
        "REVIEW_EVIDENCE",
        failures);
    JsonNode checks = review.path("checks");
    for (String name :
        List.of(
            "currentSourceUnchanged",
            "currentMasterUnchanged",
            "repeatDiffZero",
            "secretScanZero",
            "qaThrough044Resolved",
            "uicThrough004Completed")) {
      require(
          checks.path(name).isBoolean() && checks.path(name).booleanValue(),
          "REVIEW_CHECK:" + name,
          failures);
    }
  }

  private static boolean matchingCount(JsonNode expected, JsonNode actual) {
    return expected.isIntegralNumber()
        && expected.canConvertToLong()
        && expected.longValue() >= 0
        && actual.isIntegralNumber()
        && actual.canConvertToLong()
        && actual.longValue() == expected.longValue();
  }

  private static boolean matchingHash(JsonNode expected, JsonNode actual) {
    return expected.isTextual()
        && expected.asText("").matches("[0-9a-f]{64}")
        && actual.isTextual()
        && expected.asText("").equals(actual.asText(""));
  }

  private static boolean atLeastLong(JsonNode actual, long minimum) {
    return actual.isIntegralNumber() && actual.canConvertToLong() && actual.longValue() >= minimum;
  }

  /**
   * SS355 / PT-CHR-BMETA001..008: manifest items only, never opens a baseline or qualifies origin.
   */
  static List<String> validateBaselineMetadata(JsonNode manifest, JsonNode sourceReport) {
    if (manifest == null || sourceReport == null) {
      throw new IllegalArgumentException("baseline metadata document is required");
    }
    List<String> failures = new ArrayList<>();
    require(FIELD_CURRENT.equals(manifest.path("target").asText()), "BASELINE_TARGET", failures);
    require(integerEquals(manifest.path("caseCount"), 24), "BASELINE_CASE_COUNT", failures);
    require(
        integerEquals(manifest.path("screenshotFileCount"), 2),
        "BASELINE_SCREENSHOT_COUNT",
        failures);
    require(integerEquals(manifest.path("differenceCount"), 16), "BASELINE_DIF_COUNT", failures);
    require(
        matchingHash(
            sourceReport.path("sourceAggregateSha256"), manifest.path("sourceAggregateSha256")),
        "BASELINE_SOURCE_HASH",
        failures);
    require(
        matchingHash(
            sourceReport.path("documentAggregateSha256"), manifest.path("documentAggregateSha256")),
        "BASELINE_DOCUMENT_HASH",
        failures);
    require(
        matchingCount(sourceReport.path("masterFileCount"), manifest.path("masterFileCount")),
        "BASELINE_MASTER_COUNT",
        failures);
    require(
        matchingCount(sourceReport.path("masterBytes"), manifest.path("masterBytes")),
        "BASELINE_MASTER_BYTES",
        failures);
    require(
        "25.0.4".equals(manifest.path(FIELD_ENVIRONMENT).path("javaVersion").asText("")),
        "BASELINE_JAVA",
        failures);
    require(
        integerEquals(manifest.path(FIELD_ENVIRONMENT).path("browserRevision"), 1187),
        "BASELINE_BROWSER",
        failures);
    require(
        "ja-JP".equals(manifest.path(FIELD_ENVIRONMENT).path("locale").asText("")),
        "BASELINE_LOCALE",
        failures);
    require(
        "Asia/Tokyo".equals(manifest.path(FIELD_ENVIRONMENT).path("timezone").asText("")),
        "BASELINE_TIMEZONE",
        failures);
    return List.copyOf(failures);
  }

  private static void validateBaseline(
      Path projectRoot,
      Path baselineRoot,
      JsonNode manifest,
      JsonNode contract,
      JsonNode sourceReport,
      List<String> caseOrder,
      JsonNode requirements,
      List<String> failures)
      throws IOException, NoSuchAlgorithmException {
    failures.addAll(validateBaselineMetadata(manifest, sourceReport));
    List<Path> files = regularFiles(baselineRoot, path -> true);
    require(matchesBaselineFileCount(contract, files.size()), "BASELINE_FILE_COUNT", failures);
    require(
        aggregateHash(projectRoot, files).equals(contract.path("baselineAggregateSha256").asText()),
        "BASELINE_TREE_HASH",
        failures);
    String gateCommit = manifest.path("gateCommit").asText();
    boolean anchoredLegacy =
        "commit-containing-this-manifest".equals(gateCommit)
            && "843de94".equals(contract.path(FIELD_BASELINECOMMIT).asText());
    boolean actualCommit = gateCommit.equals(contract.path(FIELD_BASELINECOMMIT).asText());
    require(anchoredLegacy || actualCommit, "BASELINE_GATE_COMMIT", failures);
    validateRun(baselineRoot, caseOrder, requirements, "baseline", false, failures);
  }

  private static List<String> caseIds(Path artifactRoot) throws IOException {
    if (!Files.isDirectory(artifactRoot)) {
      return List.of();
    }
    return CharacterizationIoScope.acquire(
        () -> Files.list(artifactRoot),
        Stream::close,
        files -> {
          return files
              .filter(
                  path ->
                      ArtifactComparator.requiredArtifactFileName(path)
                          .matches("CHR-[A-Z][0-9]{2}\\.json"))
              .map(path -> ArtifactComparator.requiredArtifactFileName(path).replace(".json", ""))
              .sorted((left, right) -> Integer.compare(caseOrder(left), caseOrder(right)))
              .toList();
        });
  }

  private static int caseOrder(String id) {
    int group = "AUSMLENO".indexOf(id.charAt(CASE_GROUP_OFFSET));
    return group * 100 + Integer.parseInt(id.substring(5));
  }

  private static List<Path> regularFiles(Path root, Predicate<Path> filter) throws IOException {
    if (!Files.isDirectory(root)) {
      return List.of();
    }
    return CharacterizationIoScope.acquire(
        () -> Files.walk(root),
        Stream::close,
        paths -> {
          return paths
              .filter(path -> Files.isRegularFile(path, LinkOption.NOFOLLOW_LINKS))
              .filter(filter)
              .toList();
        });
  }

  private static String aggregateHash(Path root, List<Path> files)
      throws IOException, NoSuchAlgorithmException {
    List<Path> sorted =
        files.stream()
            .sorted(
                (left, right) ->
                    compareUtf8(
                        root.relativize(left).toString().replace('\\', '/'),
                        root.relativize(right).toString().replace('\\', '/')))
            .toList();
    MessageDigest aggregate = MessageDigest.getInstance("SHA-256");
    for (Path file : sorted) {
      String relative = root.relativize(file).toString().replace('\\', '/');
      aggregate.update((sha256(file) + "  " + relative + "\n").getBytes(StandardCharsets.UTF_8));
    }
    return java.util.HexFormat.of().formatHex(aggregate.digest());
  }

  private static int compareUtf8(String left, String right) {
    return Arrays.compareUnsigned(
        left.getBytes(StandardCharsets.UTF_8), right.getBytes(StandardCharsets.UTF_8));
  }

  static String sha256(Path file) throws IOException, NoSuchAlgorithmException {
    if (file == null) throw new IllegalArgumentException("hash source is required");
    MessageDigest digest = MessageDigest.getInstance("SHA-256");
    CharacterizationIoScope.acquire(
        () -> Files.newInputStream(file),
        java.io.InputStream::close,
        input -> {
          byte[] buffer = new byte[1024 * 1024];
          for (int read = input.read(buffer); read >= 0; read = input.read(buffer)) {
            digest.update(buffer, 0, read);
          }
          return Boolean.TRUE;
        });
    return java.util.HexFormat.of().formatHex(digest.digest());
  }

  private static JsonNode read(Path path) throws IOException {
    return JSON.readTree(path.toFile());
  }

  private static JsonNode readOptional(Path path) throws IOException {
    return Files.isRegularFile(path) ? read(path) : JSON.createObjectNode();
  }

  private static List<String> strings(JsonNode node) {
    if (!node.isArray()) {
      return List.of();
    }
    List<String> values = new ArrayList<>();
    node.forEach(value -> values.add(value.asText()));
    return List.copyOf(values);
  }

  private static void require(boolean condition, String failure, List<String> failures) {
    if (!condition) {
      failures.add(failure);
    }
  }

  record ValidationResult(List<String> failures, Map<String, Object> metrics) {
    boolean passed() {
      return failures.isEmpty();
    }
  }
}
