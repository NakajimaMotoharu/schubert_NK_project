package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** PT-MIG-MUSICPAIR001..026; hand-written pair/shadow oracles, independent distance matrix. */
final class MusicMigrationPairingTest {
  private static final String DIAGNOSTIC = "migration music pairing input is invalid";
  private static final String CAT_TITLE = "cat";
  private static final String ALPHA = "Alpha";
  private static final String ALPHA_INST = "Alpha inst";
  private static final String ALPHA_PAIR = "Alpha|alpha|a|z";
  private static final String DECORATED = "A　_B＿C!！+＋^[]【】()（）.,.．・'’`´-";
  private static final String PATH_A = "a";
  private static final String PATH_Z = "z";
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;

  @Test
  void emptyGroupHasNoPairsOrShadowedPaths() {
    var result = new MusicMigrationPairing().plan(Map.of());
    assertEquals(List.of(), result.pairs());
    assertEquals(List.of(), result.shadowedPaths());
  }

  @Test
  void exactMainAndInstrumentalHaveOnePair() {
    pairs(tracks(PATH_A, ALPHA, PATH_Z, ALPHA_INST), ALPHA_PAIR);
  }

  @Test
  void unmatchedMainKeepsTheInstrumentalPlaceholder() {
    pairs(tracks(PATH_A, ALPHA), "Alpha|alpha|a|-");
  }

  @Test
  void unmatchedInstrumentalKeepsTheMainPlaceholder() {
    pairs(tracks(PATH_Z, ALPHA_INST), "Alpha|alpha|-|z");
  }

  @Test
  void currentCaseInsensitiveSubstringRoleIncludesInstinct() {
    pairs(tracks(PATH_A, "INSTINCT"), "INSTINCT|instinct|-|a");
    pairs(tracks(PATH_Z, "Beta INSTRUMENT"), "Beta|beta|-|z");
  }

  @Test
  void numericPrefixRequiresTheOriginalFollowingWhitespace() {
    pairs(tracks(PATH_A, "12-34 Alpha"), "Alpha|alpha|a|-");
    pairs(tracks(PATH_A, "12-34Alpha"), "12-34Alpha|1234alpha|a|-");
  }

  @Test
  void currentHalfFullWidthAndUnclosedAnnotationsAndSuffixAreRetained() {
    for (var title :
        List.of("Echo (inst) trailing", "Echo（INST）tail", "Echo (instrument", "Echo inst variant"))
      pairs(tracks(PATH_A, title), "Echo|echo|-|a");
  }

  @Test
  void onlyTheExactCurrentPunctuationSetIsRemovedFromKeys() {
    pairs(tracks(PATH_A, DECORATED), DECORATED + "|abc|a|-");
    pairs(tracks(PATH_A, "A、B。"), "A、B。|a、b。|a|-");
  }

  @Test
  void oneEditInsertDeleteSubstituteAndEmptySidesHaveIndependentOracles() {
    pairs(tracks(PATH_A, "abc", PATH_Z, "abx inst"), "abc|abc|a|z");
    pairs(tracks(PATH_A, "abc", PATH_Z, "ab inst"), "abc|abc|a|z");
    pairs(tracks(PATH_A, "ab", PATH_Z, "abc inst"), "ab|ab|a|z");
    pairs(tracks(PATH_A, "!", PATH_Z, "A inst"), "!||a|z");
    pairs(tracks(PATH_A, "A", PATH_Z, " inst"), "A|a|a|z");
  }

  @Test
  void distanceTwoRemainsAnAcceptedFuzzyPair() {
    pairs(tracks(PATH_A, "abcd", PATH_Z, "abxy inst"), "abcd|abcd|a|z");
  }

  @Test
  void distanceThreeLeavesBothUnmatched() {
    pairs(tracks(PATH_A, "abc", PATH_Z, "xyz inst"), "abc|abc|a|-", "xyz|xyz|-|z");
    pairs(tracks(PATH_A, "😀a", PATH_Z, "xb inst"), "😀a|😀a|a|-", "xb|xb|-|z");
  }

  @Test
  void exactKeyWinsOverAnEarlierCloseInstrumental() {
    pairs(
        tracks("m", CAT_TITLE, PATH_A, "bat inst", PATH_Z, "cat inst"),
        "cat|cat|m|z",
        "bat|bat|-|a");
  }

  @Test
  void closestDistanceWinsOverAnEarlierDistanceTwo() {
    pairs(
        tracks("m", CAT_TITLE, PATH_A, "batx inst", PATH_Z, "cut inst"),
        "cat|cat|m|z",
        "batx|batx|-|a");
  }

  @Test
  void equalDistanceUsesTheFirstDisplayPath() {
    pairs(
        tracks("m", CAT_TITLE, PATH_Z, "cut inst", PATH_A, "bat inst"),
        "cat|cat|m|a",
        "cut|cut|-|z");
  }

  @Test
  void consumedInstrumentalCannotBeReusedByTheNextMain() {
    pairs(tracks("m", CAT_TITLE, "n", "cats", PATH_A, "bat inst"), "cat|cat|m|a", "cats|cats|n|-");
  }

  @Test
  void mainRowsPrecedeUnmatchedInstrumentalsInTheirOwnPathOrders() {
    pairs(
        tracks("m", ALPHA, PATH_Z, "Zulu", "b", "Unrelated inst", "y", "Other inst"),
        "Alpha|alpha|m|-",
        "Zulu|zulu|z|-",
        "Unrelated|unrelated|-|b",
        "Other|other|-|y");
  }

  @Test
  void mapInsertionOrderDoesNotReplaceUnicodeCodepointPathOrder() {
    pairs(tracks("😀", "Two", "\ue000", "One"), "One|one|\ue000|-", "Two|two|😀|-");
    pairs(tracks(PATH_Z, ALPHA_INST, PATH_A, ALPHA), ALPHA_PAIR);
  }

  @Test
  void collisionsOverwriteValuesKeepFirstKeyPositionAndReportBothShadowedPaths() {
    var result =
        new MusicMigrationPairing()
            .plan(
                tracks(
                    PATH_A, ALPHA, "b", "Beta", "c", "ALPHA", "d", ALPHA_INST, "e", "ALPHA INST"));
    assertEquals(List.of("ALPHA|alpha|c|e", "Beta|beta|b|-"), canonical(result));
    assertEquals(List.of(PATH_A, "d"), result.shadowedPaths());
  }

  @Test
  void emptyDerivedKeyIsPreservedWithoutClaimingDatabaseRepresentability() {
    pairs(tracks(PATH_A, "!!!", "b", "(inst)"), "!!!||a|b");
  }

  @Test
  void nullableInputMapAndItsKeysAndValuesUseFixedDiagnostics() {
    reject(null);
    var input = new LinkedHashMap<@Nullable String, @Nullable String>();
    input.put(null, ALPHA);
    reject(input);
    input.clear();
    input.put(PATH_A, null);
    reject(input);
  }

  @Test
  void relativePathGrammarDoesNotRepairUnsafeInputs() {
    for (var path : List.of("/a", "a/", "a\\b", "a//b", "./a", "a/../b", "a/./b"))
      reject(tracks(path, ALPHA));
  }

  @Test
  void malformedUnicodeNonNfcControlsAndEmptyTextAreRejectedAtBothBoundaries() {
    for (var value : List.of("", "e\u0301", "\ud800", "\udc00", "a\n", "a\u007f")) {
      reject(tracks(value, ALPHA));
      reject(tracks(PATH_A, value));
    }
  }

  @Test
  void utf8ByteBoundsIncludeSupplementaryCharactersWithoutTruncation() {
    String path = "😀".repeat(128);
    String title = "あ".repeat(85) + "a";
    var result = new MusicMigrationPairing().plan(tracks(path, title));
    assertEquals(path, result.pairs().get(0).mainDisplayPath().orElseThrow());
    assertEquals(title, result.pairs().get(0).title());
    reject(tracks(path + "a", ALPHA));
    reject(tracks(PATH_A, title + "a"));
    pairs(tracks(PATH_A, "a".repeat(256)), "a".repeat(256) + "|" + "a".repeat(256) + "|a|-");
  }

  @Test
  void resultsDoNotAliasInputAndAllViewsAndDiagnosticsAreClosed() {
    var planner = new MusicMigrationPairing();
    var input = tracks(PATH_A, ALPHA, PATH_Z, ALPHA_INST);
    var result = planner.plan(input);
    input.clear();
    assertEquals(List.of(ALPHA_PAIR), canonical(result));
    assertThrows(UnsupportedOperationException.class, () -> result.pairs().clear());
    assertThrows(UnsupportedOperationException.class, () -> result.shadowedPaths().clear());
    assertEquals("MusicMigrationPairing[REDACTED]", planner.toString());
    assertEquals("MigrationMusicPairingResult[REDACTED]", result.toString());
    assertEquals("MigrationMusicPair[REDACTED]", result.pairs().get(0).toString());
    assertNotSame(result, planner.plan(tracks(PATH_A, ALPHA)));
  }

  @Test
  void rejectedDeclarationDoesNotPoisonAnIndependentNormalCall() {
    var planner = new MusicMigrationPairing();
    reject(tracks("../unsafe", ALPHA));
    assertEquals(
        List.of(ALPHA_PAIR), canonical(planner.plan(tracks(PATH_A, ALPHA, PATH_Z, ALPHA_INST))));
    pairs(tracks("nested/file.ogg", "  9-9 Song  "), "9-9 Song|99song|nested/file.ogg|-");
  }

  @Test
  void finiteWorkersShareNoMutablePairOrShadowState()
      throws InterruptedException, ExecutionException, TimeoutException {
    var planner = new MusicMigrationPairing();
    var input = tracks(PATH_A, ALPHA, PATH_Z, ALPHA_INST);
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var results = new ArrayList<Future<List<String>>>();
      for (int i = 0; i < TASKS; i++)
        results.add(executor.submit(() -> canonical(planner.plan(input))));
      for (var result : results)
        assertEquals(List.of(ALPHA_PAIR), result.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  private static LinkedHashMap<String, String> tracks(String... cells) {
    var result = new LinkedHashMap<String, String>();
    for (int i = 0; i < cells.length; i += 2) result.put(cells[i], cells[i + 1]);
    return result;
  }

  private static void pairs(Map<String, String> input, String... expected) {
    assertEquals(List.of(expected), canonical(new MusicMigrationPairing().plan(input)));
  }

  private static List<String> canonical(MusicMigrationPairing.Result result) {
    return result.pairs().stream()
        .map(
            pair ->
                pair.title()
                    + "|"
                    + pair.key()
                    + "|"
                    + pair.mainDisplayPath().orElse("-")
                    + "|"
                    + pair.instrumentalDisplayPath().orElse("-"))
        .toList();
  }

  private static void reject(
      @Nullable Map<? extends @Nullable String, ? extends @Nullable String> input) {
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> new MusicMigrationPairing().plan(input))
            .getMessage());
  }
}
