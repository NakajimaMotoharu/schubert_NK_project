package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** PT-MIG-ENTRYMAP001..024; literal Current values, target rows and COPY bytes are independent. */
final class CurrentScenarioEntryMapperTest {
  private static final String TARGET_ENTRY_ONE = "800";
  private static final String TARGET_SPEAKER_ONE = "500";
  private static final String SIGNED_MAX = "9223372036854775807";
  private static final String SIGNED_MIN = "-9223372036854775808";
  private static final String STAMP = "2026-01-02T03:04:05Z";
  private static final String TYPE = "dialogue";
  private static final String NARRATION = "narration";
  private static final String LABEL = " Alice / label ";
  private static final String BODY = "Hello\nworld";
  private static final String RAW = "text\t\\raw";
  private static final String DIAGNOSTIC = "migration entry conversion is invalid";
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;

  @Test
  void entryMap001TwoGameRowsBindAllTwelveFieldsInCurrentOrder() {
    var rows = normal();
    Collections.reverse(rows);
    var actual = mapper().copyRows(rows, at());
    assertEquals(
        List.of(
            TARGET_ENTRY_ONE,
            "1",
            "900",
            "1",
            "0",
            "1",
            TYPE,
            TARGET_SPEAKER_ONE,
            LABEL,
            BODY,
            RAW,
            STAMP),
        actual.rows().get(0).fields());
    assertEquals(
        Arrays.asList(
            "600", "2", "700", "2", "2", "3", NARRATION, null, null, "other", "raw2", STAMP),
        actual.rows().get(1).fields());
  }

  @Test
  void entryMap002EmptyBijectionStillChecksTime() {
    var f = new ScenarioFileMigrationMap(List.of());
    var p = new ScenarioEntryPlacementMap(f, new ScenarioEntryMigrationMap(List.of()), List.of());
    var m = new CurrentScenarioEntryMapper(f, p, new SpeakerMigrationMap(List.of()));
    assertEquals(List.of(), m.copyRows(List.of(), at()).rows());
    assertThrows(IllegalArgumentException.class, () -> m.copyRows(List.of(), Instant.MIN));
  }

  @Test
  void entryMap003NullConstructorDependenciesHaveFixedDiagnostic() {
    var f = files();
    var p = placement(f);
    var s = speakers();
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class, () -> new CurrentScenarioEntryMapper(null, p, s))
            .getMessage());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class, () -> new CurrentScenarioEntryMapper(f, null, s))
            .getMessage());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class, () -> new CurrentScenarioEntryMapper(f, p, null))
            .getMessage());
  }

  @Test
  void entryMap004NullRowsTimeAndNonmicrosecondFail() {
    var m = mapper();
    assertThrows(IllegalArgumentException.class, () -> m.copyRows(null, at()));
    assertThrows(IllegalArgumentException.class, () -> m.copyRows(normal(), null));
    for (var stamp :
        List.of(Instant.MIN, Instant.MAX, Instant.parse("2026-01-02T03:04:05.000000001Z")))
      assertThrows(IllegalArgumentException.class, () -> m.copyRows(normal(), stamp));
  }

  @Test
  void entryMap005MissingAndExtraRowsAreRejected() {
    var few = normal();
    few.remove(1);
    reject(few);
    var extra = normal();
    extra.add(new ArrayList<>(extra.get(0)));
    reject(extra);
  }

  @Test
  void entryMap006NullRowsAndNineOrElevenFieldsAreRejected() {
    var nul = normal();
    nul.set(0, null);
    reject(nul);
    var shortRow = normal();
    shortRow.get(0).remove(9);
    reject(shortRow);
    var longRow = normal();
    longRow.get(0).add("extra");
    reject(longRow);
  }

  @Test
  void entryMap007CurrentEntryIdMustBeCanonicalSignedLongAndKnown() {
    for (String id : invalidIds()) reject(changed(0, id));
    reject(changed(0, "99"));
  }

  @Test
  void entryMap008CurrentFileIdMustBeCanonicalSignedLongAndKnown() {
    for (String id : invalidIds()) reject(changed(2, id));
    reject(changed(2, "99"));
  }

  @Test
  void entryMap009GameAndIndexAreExactCanonicalPlacementValues() {
    for (String game : Arrays.asList(null, "2", "3", "01", "+1", " 1")) reject(changed(1, game));
    for (String index : Arrays.asList(null, "2", "00", "+0", "-0", " 0")) reject(changed(3, index));
  }

  @Test
  void entryMap010IndependentFileMappingCannotSubstituteTargetFile() {
    var wrong =
        new ScenarioFileMigrationMap(
            List.of(
                new ScenarioFileMigrationMap.FilePair(1, -5, 901),
                new ScenarioFileMigrationMap.FilePair(2, 5, 700)));
    var m = new CurrentScenarioEntryMapper(wrong, placement(files()), speakers());
    assertThrows(IllegalArgumentException.class, () -> m.copyRows(normal(), at()));
  }

  @Test
  void entryMap011SpeakerMustBeCanonicalKnownAndSameGame() {
    for (String speaker : invalidIds()) {
      if (speaker != null) reject(changed(6, speaker));
    }
    reject(changed(6, "99"));
    reject(changed(6, "30"));
  }

  @Test
  void entryMap012DuplicateSourceIdsCannotReplaceMissingMember() {
    var rows = normal();
    rows.set(1, new ArrayList<>(rows.get(0)));
    reject(rows);
  }

  @Test
  void entryMap013NullableSpeakerAndDialogueNarrationRemainConsistent() {
    var rows = mapper().copyRows(normal(), at()).rows();
    assertEquals(TARGET_SPEAKER_ONE, rows.get(0).fields().get(7));
    assertNull(rows.get(1).fields().get(7));
    reject(changed(6, null));
    reject(changed(5, NARRATION));
  }

  @Test
  void entryMap014RequiredTextSqlNullsAreRejectedWithoutNpeOrRepair() {
    for (int column : List.of(4, 5, 8, 9)) {
      var row = changed(column, null);
      var failure =
          assertThrows(IllegalArgumentException.class, () -> mapper().copyRows(row, at()));
      assertEquals(DIAGNOSTIC, failure.getMessage());
      assertNull(row.get(0).get(column));
    }
  }

  @Test
  void entryMap015StoredTextIsPreservedAndTargetUnicodeByteLimitsApply() {
    String preserved = "  A/日本語  ";
    for (int column : List.of(7, 8, 9)) {
      var actual = mapper().copyRows(changed(column, preserved), at()).rows().get(0).fields();
      int targetColumn = column == 7 ? 8 : column == 8 ? 9 : 10;
      assertEquals(preserved, actual.get(targetColumn));
      reject(changed(column, "e\u0301"));
      reject(changed(column, "bad\0text"));
    }
    reject(changed(7, "a".repeat(129)));
    reject(changed(8, "a".repeat(4097)));
    assertEquals("", mapper().copyRows(changed(9, ""), at()).rows().get(0).fields().get(10));
  }

  @Test
  void entryMap016LineTypeAndBodyDomainsAreNotRepaired() {
    for (String line : List.of("0", "-1", "01", "2147483648")) reject(changed(4, line));
    for (String type : List.of("unknown", "Dialogue", " dialogue ", "")) reject(changed(5, type));
    reject(changed(8, ""));
    assertEquals(
        "2147483647",
        mapper().copyRows(changed(4, "2147483647"), at()).rows().get(0).fields().get(5));
  }

  @Test
  void entryMap017InputAndResultAreDeepSnapshots() {
    var input = normal();
    var output = mapper().copyRows(input, at());
    input.get(0).set(8, "mutated");
    input.clear();
    assertEquals(BODY, output.rows().get(0).fields().get(9));
    assertThrows(UnsupportedOperationException.class, output.rows()::clear);
    assertThrows(
        UnsupportedOperationException.class, () -> output.rows().get(0).fields().set(0, "mutated"));
  }

  @Test
  void entryMap018IndependentFixedCopyBytesContainMappedIdsAndEscapes() {
    String expected =
        "800\t1\t900\t1\t0\t1\tdialogue\t500\t Alice / label \tHello\\nworld\ttext\\t\\\\raw\t2026-01-02T03:04:05Z\n600\t2\t700\t2\t2\t3\tnarration\t\\N\t\\N\tother\traw2\t2026-01-02T03:04:05Z\n";
    assertEquals(
        expected,
        new String(
            mapper().copyRows(normal(), at()).copyBytes(new PostgresCopyTextEncoder()),
            StandardCharsets.UTF_8));
  }

  @Test
  void entryMap019TimestampBoundariesAndMicrosShareOneStamp() {
    for (String stamp :
        List.of(
            "0001-01-01T00:00:00Z", "9999-12-31T23:59:59.999999Z", "2026-01-02T03:04:05.123456Z")) {
      var rows = mapper().copyRows(normal(), Instant.parse(stamp)).rows();
      assertEquals(stamp, rows.get(0).fields().get(11));
      assertEquals(stamp, rows.get(1).fields().get(11));
    }
  }

  @Test
  void entryMap020SignedCurrentIdsFilesAndSpeakersUseBothLongExtremes() {
    var f =
        new ScenarioFileMigrationMap(
            List.of(
                new ScenarioFileMigrationMap.FilePair(1, Long.MIN_VALUE, 900),
                new ScenarioFileMigrationMap.FilePair(2, Long.MAX_VALUE, 700)));
    var e =
        new ScenarioEntryMigrationMap(
            List.of(
                new ScenarioEntryMigrationMap.IdPair(Long.MIN_VALUE, 800),
                new ScenarioEntryMigrationMap.IdPair(Long.MAX_VALUE, 600)));
    var p =
        new ScenarioEntryPlacementMap(
            f,
            e,
            List.of(
                new ScenarioEntryPlacementMap.Placement(1, Long.MIN_VALUE, Long.MIN_VALUE, 0),
                new ScenarioEntryPlacementMap.Placement(2, Long.MAX_VALUE, Long.MAX_VALUE, 2)));
    var s =
        new SpeakerMigrationMap(
            List.of(
                new SpeakerMigrationMap.SpeakerMapping(1, Long.MIN_VALUE, 500),
                new SpeakerMigrationMap.SpeakerMapping(2, Long.MAX_VALUE, 400)));
    var rows = normal();
    rows.get(0).set(0, SIGNED_MIN);
    rows.get(0).set(2, SIGNED_MIN);
    rows.get(0).set(6, SIGNED_MIN);
    rows.get(1).set(0, SIGNED_MAX);
    rows.get(1).set(2, SIGNED_MAX);
    var actual = new CurrentScenarioEntryMapper(f, p, s).copyRows(rows, at());
    assertEquals(TARGET_ENTRY_ONE, actual.rows().get(0).fields().get(0));
    assertEquals(TARGET_SPEAKER_ONE, actual.rows().get(0).fields().get(7));
    rows.get(1).set(5, TYPE);
    rows.get(1).set(6, SIGNED_MAX);
    assertEquals(
        "400",
        new CurrentScenarioEntryMapper(f, p, s).copyRows(rows, at()).rows().get(1).fields().get(7));
  }

  @Test
  void entryMap021CurrentOrderIsSeparateFromTargetNumericOrder() {
    var rows = mapper().copyRows(normal(), at()).rows();
    assertEquals(
        List.of(TARGET_ENTRY_ONE, "600"), rows.stream().map(x -> x.fields().get(0)).toList());
    assertEquals(List.of("1", "2"), rows.stream().map(x -> x.fields().get(3)).toList());
  }

  @Test
  void entryMap022FailureDoesNotPoisonLaterConversionAndDiagnosticIsFixed() {
    var m = mapper();
    var bad = changed(0, "+1");
    Throwable failure = assertThrows(IllegalArgumentException.class, () -> m.copyRows(bad, at()));
    assertEquals(DIAGNOSTIC, failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    assertEquals("CurrentScenarioEntryMapper[REDACTED]", m.toString());
    assertEquals(2, m.copyRows(normal(), at()).rows().size());
  }

  @Test
  void entryMap023MissingSpeakerAndFileMappingsFailAndArbitraryInputOrderWorks() {
    var f = files();
    var p = placement(f);
    var noSpeakers = new CurrentScenarioEntryMapper(f, p, new SpeakerMigrationMap(List.of()));
    assertThrows(IllegalArgumentException.class, () -> noSpeakers.copyRows(normal(), at()));
    var noFiles =
        new CurrentScenarioEntryMapper(new ScenarioFileMigrationMap(List.of()), p, speakers());
    assertThrows(IllegalArgumentException.class, () -> noFiles.copyRows(normal(), at()));
    var rows = normal();
    Collections.reverse(rows);
    assertEquals(TARGET_ENTRY_ONE, mapper().copyRows(rows, at()).rows().get(0).fields().get(0));
  }

  @Test
  void entryMap024ConcurrentCallsShareOnlyImmutableMappings() throws Exception {
    var m = mapper();
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var futures = new ArrayList<Future<String>>();
      for (int index = 0; index < TASKS; index++)
        futures.add(
            executor.submit(() -> m.copyRows(normal(), at()).rows().get(0).fields().get(0)));
      for (var future : futures)
        assertEquals(TARGET_ENTRY_ONE, future.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  private static CurrentScenarioEntryMapper mapper() {
    var f = files();
    return new CurrentScenarioEntryMapper(f, placement(f), speakers());
  }

  private static ScenarioFileMigrationMap files() {
    return new ScenarioFileMigrationMap(
        List.of(
            new ScenarioFileMigrationMap.FilePair(1, -5, 900),
            new ScenarioFileMigrationMap.FilePair(2, 5, 700)));
  }

  private static ScenarioEntryPlacementMap placement(ScenarioFileMigrationMap f) {
    return new ScenarioEntryPlacementMap(
        f,
        new ScenarioEntryMigrationMap(
            List.of(
                new ScenarioEntryMigrationMap.IdPair(-20, 800),
                new ScenarioEntryMigrationMap.IdPair(10, 600))),
        List.of(
            new ScenarioEntryPlacementMap.Placement(2, 5, 10, 2),
            new ScenarioEntryPlacementMap.Placement(1, -5, -20, 0)));
  }

  private static SpeakerMigrationMap speakers() {
    return new SpeakerMigrationMap(
        List.of(
            new SpeakerMigrationMap.SpeakerMapping(1, -30, 500),
            new SpeakerMigrationMap.SpeakerMapping(2, 30, 400)));
  }

  private static Instant at() {
    return Instant.parse(STAMP);
  }

  private static List<String> invalidIds() {
    return Arrays.asList(
        null, "", "+1", "01", "-0", " 1", "1 ", "9223372036854775808", "-9223372036854775809");
  }

  private static List<List<@Nullable String>> normal() {
    var rows = new ArrayList<List<@Nullable String>>();
    rows.add(new ArrayList<>(List.of("-20", "1", "-5", "0", "1", TYPE, "-30", LABEL, BODY, RAW)));
    rows.add(
        new ArrayList<>(
            Arrays.asList("10", "2", "5", "2", "3", NARRATION, null, null, "other", "raw2")));
    return rows;
  }

  private static List<List<@Nullable String>> changed(int column, @Nullable String value) {
    var rows = normal();
    rows.get(0).set(column, value);
    return rows;
  }

  private static void reject(List<? extends @Nullable List<@Nullable String>> rows) {
    assertThrows(IllegalArgumentException.class, () -> mapper().copyRows(rows, at()));
  }
}
