package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** PT-MIG-SPEAKERROW001..016; V002-derived seven literal columns, no current master or IO. */
final class SpeakerCopyRowTest {
  private static final String STAMP = "2026-01-02T03:04:05Z";
  private static final String NAME = "話者";
  private static final String NOTES = "備考\t一行\n二行";
  private static final String DIAGNOSTIC = "migration speaker COPY row is invalid";
  private static final String GOLDEN = "700\t1\t話者\t話者\ttrue\t備考\\t一行\\n二行\t2026-01-02T03:04:05Z\n";
  private static final int NOTES_INDEX = 5;
  private static final int STAMP_INDEX = 6;
  private static final int NAME_LIMIT = 128;
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;

  @Test
  void speakerRow001SevenLiteralColumnsAndIndependentGolden() {
    var row = new SpeakerCopyRow(raw());
    assertEquals(
        List.of(
            "id", "game_id", "name", "normalized_name", "is_protagonist", "notes", "created_at"),
        row.columnNames());
    assertArrayEquals(GOLDEN.getBytes(StandardCharsets.UTF_8), row.copyBytes(encoder()));
    assertEquals(raw(), row.fields());
  }

  @Test
  void speakerRow002NullEmptyAndLiteralCopyNullAreDistinct() {
    var nullNotes = row(NOTES_INDEX, null);
    assertNull(nullNotes.fields().get(NOTES_INDEX));
    assertArrayEquals(
        ("700\t1\t話者\t話者\ttrue\t\\N\t" + STAMP + "\n").getBytes(StandardCharsets.UTF_8),
        nullNotes.copyBytes(encoder()));
    assertArrayEquals(
        ("700\t1\t話者\t話者\ttrue\t\t" + STAMP + "\n").getBytes(StandardCharsets.UTF_8),
        row(NOTES_INDEX, "").copyBytes(encoder()));
    assertArrayEquals(
        ("700\t1\t話者\t話者\ttrue\t\\\\N\t" + STAMP + "\n").getBytes(StandardCharsets.UTF_8),
        row(NOTES_INDEX, "\\N").copyBytes(encoder()));
  }

  @Test
  void speakerRow003NameByteBoundariesAreUtf8NotCharacters() {
    for (int index : List.of(2, 3)) {
      assertEquals("a", row(index, "a").fields().get(index));
      assertEquals("a".repeat(NAME_LIMIT), row(index, "a".repeat(NAME_LIMIT)).fields().get(index));
      assertEquals("あ".repeat(42), row(index, "あ".repeat(42)).fields().get(index));
      reject(index, "あ".repeat(43));
      reject(index, "a".repeat(NAME_LIMIT + 1));
      reject(index, "");
    }
  }

  @Test
  void speakerRow004NormalizedNameIsRetainedWithoutInventingDerivation() {
    var fields = raw();
    fields.set(2, " Name ");
    fields.set(3, "別の宣言名");
    var row = new SpeakerCopyRow(fields);
    assertEquals(" Name ", row.fields().get(2));
    assertEquals("別の宣言名", row.fields().get(3));
    assertArrayEquals(
        ("700\t1\t Name \t別の宣言名\ttrue\t備考\\t一行\\n二行\t" + STAMP + "\n")
            .getBytes(StandardCharsets.UTF_8),
        row.copyBytes(encoder()));
  }

  @Test
  void speakerRow005CanonicalPositiveN12Boundaries() {
    for (String value : List.of("1", "999999999999"))
      assertEquals(value, row(0, value).fields().get(0));
    for (String value : List.of("0", "-1", "+1", "01", "1000000000000", " 1", "1 ", "1.0", "１", ""))
      reject(0, value);
  }

  @Test
  void speakerRow006OnlyTwoGameValues() {
    for (String value : List.of("1", "2")) assertEquals(value, row(1, value).fields().get(1));
    for (String value : List.of("0", "3", "01", "NUKITASHI1", "")) reject(1, value);
  }

  @Test
  void speakerRow007CanonicalBooleanTextWithoutImplicitDefault() {
    for (String value : List.of("true", "false"))
      assertEquals(value, row(4, value).fields().get(4));
    for (String value : List.of("TRUE", "False", "t", "f", "1", "0", "", " true")) reject(4, value);
  }

  @Test
  void speakerRow008UtcYearAndMicrosecondBoundaries() {
    for (String value :
        List.of(
            "0001-01-01T00:00:00Z", "9999-12-31T23:59:59.999999Z", "2026-01-02T03:04:05.000001Z"))
      assertEquals(value, row(STAMP_INDEX, value).fields().get(STAMP_INDEX));
  }

  @Test
  void speakerRow009InvalidNoncanonicalOrExcessPrecisionTimes() {
    for (String value :
        List.of(
            "",
            "not-time",
            "2026-01-02",
            "0000-12-31T23:59:59Z",
            "+10000-01-01T00:00:00Z",
            "2026-01-02T03:04:05+00:00",
            "2026-01-02T03:04:05.000000001Z",
            "2026-01-02T03:04:05.0000010Z")) reject(STAMP_INDEX, value);
  }

  @Test
  void speakerRow010MissingBoundaryAndEveryRequiredElement() {
    var failure = assertThrows(IllegalArgumentException.class, () -> new SpeakerCopyRow(null));
    assertEquals(DIAGNOSTIC, failure.getMessage());
    for (int index : List.of(0, 1, 2, 3, 4, STAMP_INDEX)) reject(index, null);
    assertNull(row(NOTES_INDEX, null).fields().get(NOTES_INDEX));
  }

  @Test
  void speakerRow011WrongColumnCountsDoNotInventDefaults() {
    var shortRow = raw();
    shortRow.removeLast();
    assertThrows(IllegalArgumentException.class, () -> new SpeakerCopyRow(shortRow));
    var extraRow = raw();
    extraRow.add("extra");
    assertThrows(IllegalArgumentException.class, () -> new SpeakerCopyRow(extraRow));
  }

  @Test
  void speakerRow012MalformedNamesAreRejectedWithoutNormalization() {
    for (int index : List.of(2, 3))
      for (String value : List.of("e\u0301", "x\0y", "\ud800", "\udc00")) reject(index, value);
  }

  @Test
  void speakerRow013NotesKeepPostgresTextAndRejectNulOrMalformedUnicode() {
    String value = "\t\n\r\b\f\u000b\u0001\\";
    var notes = row(NOTES_INDEX, value);
    assertEquals(value, notes.fields().get(NOTES_INDEX));
    assertArrayEquals(
        ("700\t1\t話者\t話者\ttrue\t\\t\\n\\r\\b\\f\\v\u0001\\\\\t" + STAMP + "\n")
            .getBytes(StandardCharsets.UTF_8),
        notes.copyBytes(encoder()));
    assertEquals("x".repeat(4097), row(NOTES_INDEX, "x".repeat(4097)).fields().get(NOTES_INDEX));
    for (String invalid : List.of("e\u0301", "x\0", "\ud800")) reject(NOTES_INDEX, invalid);
    assertEquals("name\nline", row(2, "name\nline").fields().get(2));
  }

  @Test
  void speakerRow014InputCollectionAndOutputBytesAreIndependent() {
    var fields = raw();
    var row = new SpeakerCopyRow(fields);
    fields.clear();
    assertEquals(7, row.fields().size());
    assertThrows(UnsupportedOperationException.class, () -> row.fields().clear());
    assertThrows(UnsupportedOperationException.class, () -> row.columnNames().clear());
    byte[] first = row.copyBytes(encoder());
    byte[] second = row.copyBytes(encoder());
    assertNotSame(first, second);
    first[0] = 0;
    assertArrayEquals(GOLDEN.getBytes(StandardCharsets.UTF_8), second);
    assertArrayEquals(GOLDEN.getBytes(StandardCharsets.UTF_8), row.copyBytes(encoder()));
  }

  @Test
  void speakerRow015NullEncoderFixedDiagnosticAndSuccessAfterRejection() {
    var row = new SpeakerCopyRow(raw());
    var failure = assertThrows(IllegalArgumentException.class, () -> row.copyBytes(null));
    assertEquals(DIAGNOSTIC, failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    assertEquals("SpeakerCopyRow[REDACTED]", row.toString());
    assertFalse(row.toString().contains(NAME));
    reject(0, "private-invalid");
    assertArrayEquals(
        GOLDEN.getBytes(StandardCharsets.UTF_8), new SpeakerCopyRow(raw()).copyBytes(encoder()));
  }

  @Test
  void speakerRow016FiniteParallelCopiesHaveIndependentBuffers() throws Exception {
    var row = new SpeakerCopyRow(raw());
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var futures = new ArrayList<Future<byte[]>>();
      for (int index = 0; index < TASKS; index++)
        futures.add(executor.submit(() -> row.copyBytes(encoder())));
      for (var future : futures)
        assertArrayEquals(
            GOLDEN.getBytes(StandardCharsets.UTF_8), future.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  private static ArrayList<@Nullable String> raw() {
    return new ArrayList<>(
        Arrays.<@Nullable String>asList("700", "1", NAME, NAME, "true", NOTES, STAMP));
  }

  private static SpeakerCopyRow row(int index, @Nullable String value) {
    var fields = raw();
    fields.set(index, value);
    return new SpeakerCopyRow(fields);
  }

  private static void reject(int index, @Nullable String value) {
    var fields = raw();
    fields.set(index, value);
    var failure = assertThrows(IllegalArgumentException.class, () -> new SpeakerCopyRow(fields));
    assertEquals(DIAGNOSTIC, failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static PostgresCopyTextEncoder encoder() {
    return new PostgresCopyTextEncoder();
  }
}
