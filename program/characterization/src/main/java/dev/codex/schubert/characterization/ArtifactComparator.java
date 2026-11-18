package dev.codex.schubert.characterization;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.BooleanNode;
import com.fasterxml.jackson.databind.node.IntNode;
import com.fasterxml.jackson.databind.node.NullNode;
import com.fasterxml.jackson.databind.node.TextNode;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;
import java.util.stream.Stream;
import org.jspecify.annotations.Nullable;

/** Narrow DIF oracle for normalized Current baseline and NK artifacts. SS 355 §8, §12. */
public final class ArtifactComparator {
  private static final String VALUE_PASS = "PASS";

  private static final String MODE_DIFFERENCE = "difference";
  private static final String MODE_CONTRACT = "contract";
  private static final String LOGIN_CASE = "CHR-A01";
  private static final String BRAND_DIFFERENCE = "DIF-001";
  private static final String EMPTY_MESSAGE_DIFFERENCE = "DIF-008";
  private static final String EMPTY_SEARCH_CASE = "CHR-S04";
  private static final String CACHE_DIFFERENCE = "DIF-011";
  private static final String RANGE_DIFFERENCE = "DIF-012";
  private static final String RANGE_STATUS_POINTER = "/invalidRange/status";
  private static final String GAME_CHANGE_DIFFERENCE = "DIF-013";
  private static final String GAME_CHANGE_CASE = "CHR-S02";
  private static final String GAME_CHANGE_FALLBACK = "javascriptDisabledSubmitButton";
  private static final String ERROR_CASE = "CHR-E01";
  private static final List<String> ERROR_NON_DISCLOSURE =
      List.of("secretLeak", "absolutePathLeak", "exceptionClassLeak");
  private static final String RESTART_DIFFERENCE = "DIF-014";
  private static final String SESSION_DIFFERENCE = "DIF-016";
  private static final String SESSION_CASE = "CHR-A02";
  private static final String LOGIN_TITLE = "CHR-A01:/title";
  private static final String CURRENT_BRAND = "schubert";
  private static final String NK_BRAND = "schubert NK";
  private static final String CONFIGURED_SESSIONS = "configuredMaximumSessions";
  private static final IntNode MAX_ACTIVE_SESSIONS = IntNode.valueOf(2);
  private static final List<JsonNode> INVALID_RANGE_STATUS =
      List.of(IntNode.valueOf(500), IntNode.valueOf(416));
  // UI264 and SS355 §8: treat only these exact case fields as the approved change.
  private static final Map<String, Map<String, List<JsonNode>>> FIXED_EXPECTATIONS =
      Map.of(
          BRAND_DIFFERENCE,
          Map.of(
              LOGIN_TITLE,
              textPair("schubert - ログイン", "schubert NK - ログイン"),
              "CHR-U01:/brand",
              textPair(CURRENT_BRAND, NK_BRAND),
              "CHR-U02:/titles/0",
              textPair(CURRENT_BRAND, NK_BRAND),
              "CHR-U02:/titles/1",
              textPair("schubert - 検索", "schubert NK - 検索")),
          EMPTY_MESSAGE_DIFFERENCE,
          Map.of(EMPTY_SEARCH_CASE + ":/emptyVisibleText", textPair("", "該当するデータはありません")),
          CACHE_DIFFERENCE,
          Map.of(
              "CHR-O01:/cacheControl",
              textPair("no-cache, no-store, max-age=0, must-revalidate", "no-store")),
          RANGE_DIFFERENCE,
          Map.of(
              "CHR-M04:/invalidRange/status",
              INVALID_RANGE_STATUS,
              "CHR-M04:/invalidRange/contentRange",
              textPair("bytes 999999999999-84084291/84084292", "bytes */84084292"),
              "CHR-M07:/invalidRange/status",
              INVALID_RANGE_STATUS,
              "CHR-M07:/invalidRange/contentRange",
              textPair("bytes 999999999999-3388626/3388627", "bytes */3388627")),
          GAME_CHANGE_DIFFERENCE,
          Map.of(
              GAME_CHANGE_CASE + ":/gameOnchange",
              List.of(TextNode.valueOf("this.form.submit()"), NullNode.getInstance())),
          RESTART_DIFFERENCE,
          Map.of(
              "CHR-O01:/sessionAfterRestart", textPair("redirect-login", "authenticated"),
              "CHR-O01:/sessionInvalidated", List.of(BooleanNode.TRUE, BooleanNode.FALSE)),
          SESSION_DIFFERENCE,
          Map.of(
              "CHR-A02:/observedActiveSessionCount",
                  List.of(IntNode.valueOf(3), MAX_ACTIVE_SESSIONS),
              "CHR-A02:/oldestSessionInvalidated", List.of(BooleanNode.FALSE, BooleanNode.TRUE),
              "CHR-A02:/sessionActiveOldestToNewest/0",
                  List.of(BooleanNode.TRUE, BooleanNode.FALSE),
              "CHR-A02:/sessionRedirectsOldestToNewest/0",
                  textPair("/", "/login?session-expired")));
  private static final ObjectMapper JSON = new ObjectMapper();
  private static final Set<String> MODES = Set.of(MODE_DIFFERENCE, "required", MODE_CONTRACT);

  private ArtifactComparator() {
    throw new AssertionError("ArtifactComparator is a static tool");
  }

  public static ComparisonResult compare(
      Path projectRoot, Path currentArtifacts, Path nkArtifacts, Path observationsFile)
      throws IOException {
    requireInput(projectRoot, "projectRoot");
    requireInput(currentArtifacts, "currentArtifacts");
    requireInput(nkArtifacts, "nkArtifacts");
    requireInput(observationsFile, "observationsFile");
    if (!Files.isDirectory(currentArtifacts, LinkOption.NOFOLLOW_LINKS)
        || !Files.isDirectory(nkArtifacts, LinkOption.NOFOLLOW_LINKS)
        || !Files.isRegularFile(observationsFile, LinkOption.NOFOLLOW_LINKS)) {
      throw new IllegalArgumentException("artifact directories and observation file are required");
    }

    JsonNode catalog =
        JSON.readTree(
            projectRoot
                .resolve("program/characterization/tests/resources/cases/catalog.json")
                .toFile());
    JsonNode allowlist =
        JSON.readTree(
            projectRoot
                .resolve("program/characterization/tests/resources/cases/dif-allowlist.json")
                .toFile());
    JsonNode observations = JSON.readTree(observationsFile.toFile());
    List<String> failures = new ArrayList<>();
    // QA-051/SS355 §8.1: legacy DIF claims alone cannot establish correlated CHR-L01 evidence.
    failures.addAll(
        CorrelatedLogEvidenceValidator.validateCompleteL01(
            observations.path("correlatedLogEvidence")));

    Set<String> expectedCases = new LinkedHashSet<>();
    for (JsonNode item : catalog.path("cases")) {
      String id = item.path("id").asText();
      require(expectedCases.add(id), "CATALOG_DUPLICATE:" + id, failures);
      require("RUN".equals(item.path("nk").asText()), "CATALOG_NK:" + id, failures);
    }
    require(expectedCases.size() == 24, "CATALOG_CASE_COUNT", failures);

    Map<String, Path> currentFiles = artifactFiles(currentArtifacts, failures, "CURRENT");
    Map<String, Path> nkFiles = artifactFiles(nkArtifacts, failures, "NK");
    compareSets(expectedCases, currentFiles.keySet(), "CURRENT", failures);
    compareSets(expectedCases, nkFiles.keySet(), "NK", failures);

    Map<String, JsonNode> currentByCase = new TreeMap<>();
    Map<String, JsonNode> nkByCase = new TreeMap<>();
    Set<String> rawDifferences = new TreeSet<>();
    int comparedCases = 0;
    for (String caseId : expectedCases) {
      if (!currentFiles.containsKey(caseId) || !nkFiles.containsKey(caseId)) continue;
      JsonNode current = JSON.readTree(currentFiles.get(caseId).toFile());
      JsonNode nk = JSON.readTree(nkFiles.get(caseId).toFile());
      currentByCase.put(caseId, current);
      nkByCase.put(caseId, nk);
      require(
          caseId.equals(current.path("caseId").asText()), "CURRENT_CASE_ID:" + caseId, failures);
      require(caseId.equals(nk.path("caseId").asText()), "NK_CASE_ID:" + caseId, failures);
      require(
          VALUE_PASS.equals(current.path("status").asText()), "CURRENT_STATUS:" + caseId, failures);
      require(VALUE_PASS.equals(nk.path("status").asText()), "NK_STATUS:" + caseId, failures);
      if (SESSION_CASE.equals(caseId)) {
        require(
            MAX_ACTIVE_SESSIONS.equals(current.path(CONFIGURED_SESSIONS)),
            "CURRENT_SESSION_LIMIT",
            failures);
        require(
            MAX_ACTIVE_SESSIONS.equals(nk.path(CONFIGURED_SESSIONS)), "NK_SESSION_LIMIT", failures);
      }
      if (GAME_CHANGE_CASE.equals(caseId)) {
        require(
            BooleanNode.TRUE.equals(current.path(GAME_CHANGE_FALLBACK)),
            "CURRENT_GAME_CHANGE_FALLBACK",
            failures);
        require(
            BooleanNode.TRUE.equals(nk.path(GAME_CHANGE_FALLBACK)),
            "NK_GAME_CHANGE_FALLBACK",
            failures);
      }
      if (ERROR_CASE.equals(caseId)) {
        for (String field : ERROR_NON_DISCLOSURE) {
          require(
              BooleanNode.FALSE.equals(current.path(field)),
              "CURRENT_ERROR_DISCLOSURE:" + field,
              failures);
          require(
              BooleanNode.FALSE.equals(nk.path(field)), "NK_ERROR_DISCLOSURE:" + field, failures);
        }
      }
      collectDifferences(caseId, "", current, nk, rawDifferences);
      comparedCases++;
    }

    JsonNode logArtifacts = observations.path("correlatedLogArtifacts");
    require(
        logArtifacts.isObject()
            && logArtifacts.size() == 2
            && logArtifacts.path("current").equals(currentByCase.get("CHR-L01"))
            && logArtifacts.path("nk").equals(nkByCase.get("CHR-L01")),
        "LOG_PROJECTION_ARTIFACT_BINDING",
        failures);

    Map<String, JsonNode> rules = new LinkedHashMap<>();
    for (JsonNode rule : allowlist.path("differences")) {
      String id = rule.path("id").asText();
      require(rules.putIfAbsent(id, rule) == null, "DIF_DUPLICATE:" + id, failures);
    }
    require(rules.size() == 16, "DIF_RULE_COUNT", failures);
    require(
        CorrelatedLogEvidenceValidator.versionOne(observations.path("version")),
        "OBSERVATION_VERSION",
        failures);
    require(observations.path("observations").isArray(), "OBSERVATIONS_NOT_ARRAY", failures);

    Set<String> usedRules = new TreeSet<>();
    Set<String> claimedDifferences = new HashSet<>();
    Set<String> observationKeys = new HashSet<>();
    Set<String> pendingFixedObservations = new TreeSet<>();
    for (Map<String, List<JsonNode>> expectations : FIXED_EXPECTATIONS.values()) {
      pendingFixedObservations.addAll(expectations.keySet());
    }
    int observationCount = 0;
    for (JsonNode observation : observations.path("observations")) {
      observationCount++;
      String id = observation.path("id").asText();
      String caseId = observation.path("caseId").asText();
      String field = observation.path("field").asText();
      String mode = observation.path("mode").asText();
      String selectorType = observation.path("selectorType").asText();
      String selector = observation.path("selector").asText();
      String pointer = observation.path("jsonPointer").asText();
      String observationKey = id + ":" + caseId + ":" + pointer;
      boolean valid = true;
      valid &=
          require(
              observationKeys.add(observationKey),
              "OBSERVATION_DUPLICATE:" + observationKey,
              failures);
      JsonNode rule = rules.get(id);
      valid &= require(rule != null, "OBSERVATION_UNKNOWN_DIF:" + id, failures);
      valid &=
          require(expectedCases.contains(caseId), "OBSERVATION_UNKNOWN_CASE:" + caseId, failures);
      valid &= require(validPointer(pointer), "OBSERVATION_POINTER:" + observationKey, failures);
      valid &=
          require(
              observation.has("expectedCurrent"),
              "OBSERVATION_CURRENT_MISSING:" + observationKey,
              failures);
      valid &=
          require(
              observation.has("expectedNk"), "OBSERVATION_NK_MISSING:" + observationKey, failures);
      boolean comparable =
          rule != null
              & currentByCase.containsKey(caseId)
              & nkByCase.containsKey(caseId)
              & validPointer(pointer);
      if (!comparable) {
        continue;
      }
      valid &=
          require(
              strings(rule.path("cases")).contains(caseId),
              "OBSERVATION_CASE_SCOPE:" + observationKey,
              failures);
      valid &=
          require(
              field.equals(rule.path("field").asText()),
              "OBSERVATION_FIELD:" + observationKey,
              failures);
      valid &=
          require(
              mode.equals(rule.path("mode").asText()) && MODES.contains(mode),
              "OBSERVATION_MODE:" + observationKey,
              failures);
      valid &=
          require(
              selectorType.equals(rule.path("selectorType").asText()),
              "OBSERVATION_SELECTOR_TYPE:" + observationKey,
              failures);
      valid &=
          require(
              strings(rule.path("selectors")).contains(selector),
              "OBSERVATION_SELECTOR:" + observationKey,
              failures);

      JsonNode actualCurrent = currentByCase.get(caseId).at(pointer);
      JsonNode actualNk = nkByCase.get(caseId).at(pointer);
      String differenceKey = key(caseId, pointer);
      if (ERROR_CASE.equals(caseId) && ERROR_NON_DISCLOSURE.contains(pointer.substring(1))) {
        failures.add("OBSERVATION_ERROR_DISCLOSURE_FIELD:" + observationKey);
        valid = false;
      }
      // L01 has its own log projection. The empty search field is specific to S04.
      Map<String, List<JsonNode>> fixed =
          EMPTY_MESSAGE_DIFFERENCE.equals(id) && !EMPTY_SEARCH_CASE.equals(caseId)
              ? null
              : FIXED_EXPECTATIONS.get(id);
      if (fixed != null) {
        valid &=
            checkFixed(id, caseId, fixed.get(differenceKey), actualCurrent, actualNk, failures);
      }
      if (RANGE_DIFFERENCE.equals(id)) {
        String requiredSelector = RANGE_STATUS_POINTER.equals(pointer) ? "status" : "content-range";
        valid &= require(requiredSelector.equals(selector), "OBSERVATION_RANGE_SELECTOR", failures);
      }
      valid &=
          require(
              !actualCurrent.isMissingNode(),
              "OBSERVATION_CURRENT_POINTER:" + observationKey,
              failures);
      valid &=
          require(!actualNk.isMissingNode(), "OBSERVATION_NK_POINTER:" + observationKey, failures);
      valid &=
          require(
              actualCurrent.equals(observation.path("expectedCurrent")),
              "OBSERVATION_CURRENT_VALUE:" + observationKey,
              failures);
      valid &=
          require(
              actualNk.equals(observation.path("expectedNk")),
              "OBSERVATION_NK_VALUE:" + observationKey,
              failures);

      boolean changed = rawDifferences.contains(differenceKey);
      if (MODE_DIFFERENCE.equals(mode)) {
        valid &= require(changed, "OBSERVATION_DIFFERENCE_REQUIRED:" + observationKey, failures);
      }
      if (MODE_CONTRACT.equals(mode)) {
        valid &= require(!changed, "OBSERVATION_CONTRACT_CHANGED:" + observationKey, failures);
      }
      // BUG2812: invalid observations must never consume an otherwise unregistered drift.
      if (changed) {
        valid &=
            require(
                !claimedDifferences.contains(differenceKey),
                "OBSERVATION_OVERLAP:" + differenceKey,
                failures);
        if (valid) claimedDifferences.add(differenceKey);
      }
      if (valid) usedRules.add(id);
      if (valid && fixed != null) pendingFixedObservations.remove(differenceKey);
    }

    for (String target : pendingFixedObservations) {
      failures.add(missingObservation(target));
    }
    List<String> unregistered =
        rawDifferences.stream().filter(key -> !claimedDifferences.contains(key)).toList();
    unregistered.forEach(value -> failures.add("UNREGISTERED_DIFF:" + value));
    List<String> unused = rules.keySet().stream().filter(id -> !usedRules.contains(id)).toList();
    unused.forEach(value -> failures.add("UNUSED_DIF:" + value));
    List<String> used = List.copyOf(usedRules);
    return new ComparisonResult(
        failures.isEmpty() ? VALUE_PASS : "FAIL",
        expectedCases.size(),
        comparedCases,
        rawDifferences.size(),
        observationCount,
        used,
        unused,
        unregistered,
        List.copyOf(failures));
  }

  private static List<JsonNode> textPair(String current, String nk) {
    return List.of(TextNode.valueOf(current), TextNode.valueOf(nk));
  }

  private static String missingObservation(String target) {
    if (LOGIN_TITLE.equals(target)) return "LOGIN_TITLE_DIF_REQUIRED";
    if (target.startsWith("CHR-U0")) return "BRAND_DIF_REQUIRED:" + target;
    return "FIXED_DIF_REQUIRED:" + target;
  }

  private static boolean checkFixed(
      String id,
      String caseId,
      @Nullable List<JsonNode> pair,
      JsonNode current,
      JsonNode nk,
      List<String> failures) {
    String prefix = "OBSERVATION_FIXED_";
    if (BRAND_DIFFERENCE.equals(id)) {
      prefix = LOGIN_CASE.equals(caseId) ? "OBSERVATION_LOGIN_TITLE_" : "OBSERVATION_BRAND_";
    }
    if (pair == null) {
      failures.add(prefix + "POINTER");
      return false;
    }
    boolean currentMatches = require(pair.getFirst().equals(current), prefix + "CURRENT", failures);
    boolean nkMatches = require(pair.getLast().equals(nk), prefix + "NK", failures);
    return currentMatches && nkMatches;
  }

  private static void requireInput(Path value, String label) {
    if (value == null) throw new IllegalArgumentException(label + " is required");
  }

  /** Lexical name boundary shared by artifact readers; it performs no filesystem operation. */
  static String requiredArtifactFileName(Path path) {
    if (path == null) throw new IllegalArgumentException("artifact path is required");
    Path name = path.getFileName();
    if (name == null) throw new IllegalArgumentException("artifact entry must have a name");
    return name.toString();
  }

  private static Map<String, Path> artifactFiles(Path root, List<String> failures, String target)
      throws IOException {
    Map<String, Path> files = new TreeMap<>();
    return CharacterizationIoScope.acquire(
        () -> Files.list(root),
        Stream::close,
        paths -> {
          for (Path path : paths.toList()) {
            if (Files.isSymbolicLink(path)) {
              failures.add(target + "_SYMLINK:" + path.getFileName());
            } else if (Files.isRegularFile(path, LinkOption.NOFOLLOW_LINKS)
                && requiredArtifactFileName(path).endsWith(".json")) {
              String id = requiredArtifactFileName(path).replaceFirst("\\.json$", "");
              files.put(id, path);
            }
          }
          return files;
        });
  }

  private static void compareSets(
      Set<String> expected, Set<String> actual, String target, List<String> failures) {
    expected.stream()
        .filter(id -> !actual.contains(id))
        .forEach(id -> failures.add(target + "_MISSING:" + id));
    actual.stream()
        .filter(id -> !expected.contains(id))
        .forEach(id -> failures.add(target + "_EXTRA:" + id));
  }

  private static void collectDifferences(
      String caseId, String pointer, JsonNode current, JsonNode nk, Set<String> differences) {
    if (current.equals(nk)) return;
    if (current.isObject() && nk.isObject()) {
      Set<String> names = new TreeSet<>();
      current.propertyStream().forEach(entry -> names.add(entry.getKey()));
      nk.propertyStream().forEach(entry -> names.add(entry.getKey()));
      names.forEach(
          name ->
              collectDifferences(
                  caseId,
                  pointer + "/" + escape(name),
                  current.path(name),
                  nk.path(name),
                  differences));
      return;
    }
    if (current.isArray() && nk.isArray()) {
      int size = Math.max(current.size(), nk.size());
      for (int index = 0; index < size; index++) {
        collectDifferences(
            caseId, pointer + "/" + index, current.path(index), nk.path(index), differences);
      }
      return;
    }
    differences.add(key(caseId, pointer));
  }

  private static String escape(String name) {
    return name.replace("~", "~0").replace("/", "~1");
  }

  private static String key(String caseId, String pointer) {
    return caseId + ":" + pointer;
  }

  private static boolean validPointer(String pointer) {
    return pointer.startsWith("/")
        && !pointer.contains("*")
        && !pointer.contains("..")
        && !pointer.endsWith("/");
  }

  private static List<String> strings(JsonNode values) {
    List<String> result = new ArrayList<>();
    values.forEach(value -> result.add(value.asText()));
    return result;
  }

  private static boolean require(boolean condition, String failure, List<String> failures) {
    if (!condition) failures.add(failure);
    return condition;
  }

  public record ComparisonResult(
      String status,
      int expectedCaseCount,
      int comparedCaseCount,
      int rawDifferenceCount,
      int observationCount,
      List<String> usedDifferences,
      List<String> unusedDifferences,
      List<String> unregisteredDifferences,
      List<String> failures) {
    public ComparisonResult {
      usedDifferences = List.copyOf(usedDifferences);
      unusedDifferences = List.copyOf(unusedDifferences);
      unregisteredDifferences = List.copyOf(unregisteredDifferences);
      failures = List.copyOf(failures);
    }

    public boolean passed() {
      return VALUE_PASS.equals(status);
    }
  }
}
