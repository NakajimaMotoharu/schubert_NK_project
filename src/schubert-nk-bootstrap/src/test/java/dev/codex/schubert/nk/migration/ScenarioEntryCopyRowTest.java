package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** SSC347; PT-MIG-ROW001..012; independent schema/byte oracles in NK-MIG-001 specification019. */
final class ScenarioEntryCopyRowTest {
  private static final String GOLDEN =
      "1\t1\t2\t3\t0\t1\tdialogue\t4\t話者\t本文\\n二行\traw\\nblock\t2026-11-14T00:00:00Z\n";
  private final PostgresCopyTextEncoder encoder = new PostgresCopyTextEncoder();

  private static List<@Nullable String> fixture() {
    return new ArrayList<>(
        Arrays.asList(
            "1",
            "1",
            "2",
            "3",
            "0",
            "1",
            "dialogue",
            "4",
            "話者",
            "本文\n二行",
            "raw\nblock",
            "2026-11-14T00:00:00Z"));
  }

  private static List<@Nullable String> with(int column, @Nullable String value) {
    var fields = fixture();
    fields.set(column, value);
    return fields;
  }

  @Test
  void row001IndependentTwelveColumnsAndFullCopyBytes() {
    var row = new ScenarioEntryCopyRow(fixture());
    assertEquals(
        List.of(
            "id",
            "game_id",
            "script_file_id",
            "display_order",
            "entry_index",
            "line_number",
            "entry_type",
            "speaker_id",
            "speaker_label",
            "body",
            "raw_block",
            "created_at"),
        row.columnNames());
    assertEquals(12, row.fields().size());
    assertEquals("dialogue", row.fields().get(6));
    assertArrayEquals(GOLDEN.getBytes(StandardCharsets.UTF_8), row.copyBytes(encoder));
  }

  @Test
  void row002NarrationNullableFieldsAndEmptyValues() {
    var fields = fixture();
    fields.set(5, null);
    fields.set(6, "narration");
    fields.set(7, null);
    fields.set(8, null);
    fields.set(9, "text");
    fields.set(10, "");
    var row = new ScenarioEntryCopyRow(fields);
    assertNull(row.fields().get(5));
    assertNull(row.fields().get(7));
    assertNull(row.fields().get(8));
    assertArrayEquals(
        "1\t1\t2\t3\t0\t\\N\tnarration\t\\N\t\\N\ttext\t\t2026-11-14T00:00:00Z\n"
            .getBytes(StandardCharsets.US_ASCII),
        row.copyBytes(encoder));
    fields.set(8, "");
    assertEquals("", new ScenarioEntryCopyRow(fields).fields().get(8));
  }

  @Test
  void row003N12AndGameBoundariesAtEachColumn() {
    for (int column : new int[] {0, 2, 3, 7}) {
      for (String valid : List.of("1", "999999999999"))
        assertEquals(valid, new ScenarioEntryCopyRow(with(column, valid)).fields().get(column));
      for (String invalid :
          List.of("", "0", "-1", "1000000000000", "01", "+1", " 1", "1 ", "1.0")) {
        assertThrows(
            IllegalArgumentException.class, () -> new ScenarioEntryCopyRow(with(column, invalid)));
      }
    }
    assertEquals("2", new ScenarioEntryCopyRow(with(1, "2")).fields().get(1));
    for (String invalid : List.of("0", "3", "-1", "01", "1.0", ""))
      assertThrows(
          IllegalArgumentException.class, () -> new ScenarioEntryCopyRow(with(1, invalid)));
  }

  @Test
  void row004IndexAndOptionalLineIntDomains() {
    for (String valid : List.of("0", "1", "2147483647"))
      assertEquals(valid, new ScenarioEntryCopyRow(with(4, valid)).fields().get(4));
    for (String valid : List.of("1", "2147483647"))
      assertEquals(valid, new ScenarioEntryCopyRow(with(5, valid)).fields().get(5));
    for (String invalid :
        List.of("-1", "2147483648", "9999999999", "10000000000", "01", "+1", "1.0", "")) {
      assertThrows(
          IllegalArgumentException.class, () -> new ScenarioEntryCopyRow(with(4, invalid)));
      assertThrows(
          IllegalArgumentException.class, () -> new ScenarioEntryCopyRow(with(5, invalid)));
    }
    assertThrows(IllegalArgumentException.class, () -> new ScenarioEntryCopyRow(with(5, "0")));
  }

  @Test
  void row005ClosedTypeAndSpeakerPair() {
    assertThrows(NullPointerException.class, () -> new ScenarioEntryCopyRow(with(6, null)));
    for (String invalid : List.of("Dialogue", "other", "", "dialogue "))
      assertThrows(
          IllegalArgumentException.class, () -> new ScenarioEntryCopyRow(with(6, invalid)));
    assertThrows(IllegalArgumentException.class, () -> new ScenarioEntryCopyRow(with(7, null)));
    assertThrows(
        IllegalArgumentException.class, () -> new ScenarioEntryCopyRow(with(6, "narration")));
  }

  @Test
  void row006IndependentUtf8ByteLimitsAndUnboundedRawBlock() {
    assertEquals(
        "a".repeat(4096), new ScenarioEntryCopyRow(with(9, "a".repeat(4096))).fields().get(9));
    assertThrows(
        IllegalArgumentException.class, () -> new ScenarioEntryCopyRow(with(9, "a".repeat(4097))));
    assertEquals(
        "あ".repeat(1365) + "a",
        new ScenarioEntryCopyRow(with(9, "あ".repeat(1365) + "a")).fields().get(9));
    assertThrows(
        IllegalArgumentException.class, () -> new ScenarioEntryCopyRow(with(9, "あ".repeat(1366))));
    assertThrows(IllegalArgumentException.class, () -> new ScenarioEntryCopyRow(with(9, "")));
    assertEquals(
        "a".repeat(128), new ScenarioEntryCopyRow(with(8, "a".repeat(128))).fields().get(8));
    assertThrows(
        IllegalArgumentException.class, () -> new ScenarioEntryCopyRow(with(8, "a".repeat(129))));
    assertEquals(
        "あ".repeat(42) + "ab",
        new ScenarioEntryCopyRow(with(8, "あ".repeat(42) + "ab")).fields().get(8));
    assertThrows(
        IllegalArgumentException.class, () -> new ScenarioEntryCopyRow(with(8, "あ".repeat(43))));
    assertEquals(
        "r".repeat(8193), new ScenarioEntryCopyRow(with(10, "r".repeat(8193))).fields().get(10));
  }

  @Test
  void row007NfcScalarAndEveryControlDomain() {
    String nonNfc = new String(new char[] {(char) 0x0065, (char) 0x0301});
    String loneHigh = new String(new char[] {(char) 0xd800});
    String loneLow = new String(new char[] {(char) 0xdc00});
    for (int column : new int[] {8, 9, 10}) {
      for (String invalid : List.of(nonNfc, loneHigh, loneLow))
        assertThrows(
            IllegalArgumentException.class, () -> new ScenarioEntryCopyRow(with(column, invalid)));
      for (int value = 0; value < 160; value++) {
        if (value > 31 && value < 127) continue;
        char control = (char) value;
        if (column != 8 && (control == 9 || control == 10 || control == 13)) continue;
        String invalid = "a" + control + "b";
        assertThrows(
            IllegalArgumentException.class, () -> new ScenarioEntryCopyRow(with(column, invalid)));
      }
    }
    for (int column : new int[] {9, 10})
      assertEquals(
          "a\tb\nc\rd", new ScenarioEntryCopyRow(with(column, "a\tb\nc\rd")).fields().get(column));
  }

  @Test
  void row008AllMandatoryNullAndRowWidthBoundaries() {
    assertThrows(NullPointerException.class, () -> new ScenarioEntryCopyRow(null));
    for (int column : new int[] {0, 1, 2, 3, 4, 6, 9, 10, 11})
      assertThrows(NullPointerException.class, () -> new ScenarioEntryCopyRow(with(column, null)));
    var shortRow = fixture();
    shortRow.remove(11);
    assertThrows(IllegalArgumentException.class, () -> new ScenarioEntryCopyRow(shortRow));
    var longRow = fixture();
    longRow.add("extra");
    assertThrows(IllegalArgumentException.class, () -> new ScenarioEntryCopyRow(longRow));
  }

  @Test
  void row009CanonicalUtcFiniteYearAndMicroseconds() {
    for (String valid :
        List.of(
            "0001-01-01T00:00:00Z",
            "9999-12-31T23:59:59.999999Z",
            "2026-11-14T00:00:00.000001Z",
            "2026-11-14T00:00:00.123Z",
            "2026-11-14T00:00:00.123456Z"))
      assertEquals(valid, new ScenarioEntryCopyRow(with(11, valid)).fields().get(11));
    for (String invalid :
        List.of(
            "0000-12-31T23:59:59Z",
            "+10000-01-01T00:00:00Z",
            "2026-11-14T00:00:00.000000001Z",
            "2026-11-14T00:00:00.000Z",
            "2026-11-14T00:00:00.123000Z",
            "2026-11-14T00:00:00+00:00",
            "infinity",
            "",
            "PRIVATE"))
      assertThrows(
          IllegalArgumentException.class, () -> new ScenarioEntryCopyRow(with(11, invalid)));
  }

  @Test
  void row010SnapshotListColumnAndByteOwnership() {
    var fields = fixture();
    var row = new ScenarioEntryCopyRow(fields);
    fields.clear();
    assertEquals(12, row.fields().size());
    assertThrows(UnsupportedOperationException.class, () -> row.fields().clear());
    assertThrows(UnsupportedOperationException.class, () -> row.fields().set(0, "9"));
    assertThrows(UnsupportedOperationException.class, () -> row.columnNames().clear());
    byte[] first = row.copyBytes(encoder);
    Arrays.fill(first, (byte) 0);
    assertArrayEquals(GOLDEN.getBytes(StandardCharsets.UTF_8), row.copyBytes(encoder));
  }

  @Test
  void row011NoTrimSafeDiagnosticAndEncoderContract() {
    var row = new ScenarioEntryCopyRow(with(9, " a "));
    assertEquals(" a ", row.fields().get(9));
    assertEquals("ScenarioEntryCopyRow[REDACTED]", row.toString());
    assertThrows(NullPointerException.class, () -> row.copyBytes(null));
    var failure =
        assertThrows(
            IllegalArgumentException.class, () -> new ScenarioEntryCopyRow(with(0, "PRIVATE")));
    assertEquals("migration scenario COPY row is invalid", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    assertArrayEquals(
        GOLDEN.getBytes(StandardCharsets.UTF_8),
        new ScenarioEntryCopyRow(fixture()).copyBytes(encoder));
  }

  @Test
  void row012ConcurrentCopyAndValueOwnership()
      throws InterruptedException, ExecutionException, TimeoutException {
    var row = new ScenarioEntryCopyRow(fixture());
    var workers = Executors.newFixedThreadPool(8);
    var futures = new ArrayList<Future<?>>();
    try {
      for (int index = 0; index < 64; index++) {
        futures.add(
            workers.submit(
                () -> {
                  byte[] actual = row.copyBytes(encoder);
                  assertArrayEquals(GOLDEN.getBytes(StandardCharsets.UTF_8), actual);
                  Arrays.fill(actual, (byte) 0);
                  assertEquals("dialogue", row.fields().get(6));
                }));
      }
      for (Future<?> future : futures) future.get(5, TimeUnit.SECONDS);
    } finally {
      workers.shutdownNow();
      assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS), "owned row workers terminate");
    }
    assertArrayEquals(GOLDEN.getBytes(StandardCharsets.UTF_8), row.copyBytes(encoder));
  }
}
