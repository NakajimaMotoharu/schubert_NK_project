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
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/**
 * SSC346; PT-MIG-COPY001..012; independent ASCII/UTF8 hex goldens in NK-MIG-001 specification017.
 */
final class PostgresCopyTextEncoderTest {
  private final PostgresCopyTextEncoder encoder = new PostgresCopyTextEncoder();

  @Test
  void copy001LiteralRowsAndBothEntryPoints() {
    assertArrayEquals(
        new byte[] {0x31, 9, 0x41, 10, 0x32, 9, 0x42, 10},
        encoder.encodeRows(List.of(List.of("1", "A"), List.of("2", "B"))));
    assertArrayEquals(new byte[] {0x31, 9, 0x41, 10}, encoder.encodeRow(List.of("1", "A")));
  }

  @Test
  void copy002NullEmptyAndLiteralNullMarkerAreDistinct() {
    assertArrayEquals(
        new byte[] {0x5c, 0x4e, 9, 9, 0x5c, 0x5c, 0x4e, 10},
        encoder.encodeRow(Arrays.asList(null, "", "\\N")));
    assertArrayEquals(new byte[] {10}, encoder.encodeRow(List.of("")));
    assertArrayEquals(new byte[] {0x5c, 0x4e, 10}, encoder.encodeRow(Arrays.asList((String) null)));
  }

  @Test
  void copy003MandatoryDelimiterAndLineEscapes() {
    assertArrayEquals(
        new byte[] {0x5c, 0x5c, 0x5c, 0x74, 0x5c, 0x6e, 0x5c, 0x72, 10},
        encoder.encodeRow(List.of("\\\t\n\r")));
  }

  @Test
  void copy004OtherControlEscapesAndOrdinaryQuotes() {
    assertArrayEquals(
        new byte[] {0x5c, 0x62, 0x5c, 0x66, 0x5c, 0x76, 10},
        encoder.encodeRow(List.of("\b\f" + (char) 11)));
    assertArrayEquals(
        new byte[] {0x27, 0x22, 0x2c, 0x20, 0x41, 0x7f, 10},
        encoder.encodeRow(List.of("'\", A" + (char) 127)));
  }

  @Test
  void copy005FixedUnicodeHexAndNoImplicitNormalization() {
    assertArrayEquals(
        new byte[] {
          (byte) 0xe3,
          (byte) 0x81,
          (byte) 0x82,
          (byte) 0xc3,
          (byte) 0xa9,
          (byte) 0xf0,
          (byte) 0x9f,
          (byte) 0x8e,
          (byte) 0xb5,
          10
        },
        encoder.encodeRow(List.of("あé🎵")));
    assertArrayEquals(
        new byte[] {0x65, (byte) 0xcc, (byte) 0x81, 10},
        encoder.encodeRow(List.of(new String(new char[] {(char) 0x0065, (char) 0x0301}))));
  }

  @Test
  void copy006LiteralTerminatorAndSqlLikeDataStayFields() {
    assertArrayEquals(new byte[] {0x5c, 0x5c, 0x2e, 10}, encoder.encodeRow(List.of("\\.")));
    assertArrayEquals(
        "';SELECT 1;--\\n\\\\.\n".getBytes(StandardCharsets.US_ASCII),
        encoder.encodeRow(List.of("';SELECT 1;--\n\\.")));
    assertArrayEquals(new byte[] {0x2e, 10}, encoder.encodeRow(List.of(".")));
  }

  @Test
  void copy007NullOuterAndRowsRefusedButNullableFieldsAllowed() {
    assertThrows(NullPointerException.class, () -> encoder.encodeRows(null));
    assertThrows(NullPointerException.class, () -> encoder.encodeRow(null));
    assertThrows(
        NullPointerException.class, () -> encoder.encodeRows(Arrays.asList(List.of("a"), null)));
    assertArrayEquals(new byte[] {0x5c, 0x4e, 10}, encoder.encodeRow(Arrays.asList((String) null)));
  }

  @Test
  void copy008EmptyInputAndWidthContracts() {
    assertArrayEquals(new byte[0], encoder.encodeRows(List.of()));
    assertThrows(IllegalArgumentException.class, () -> encoder.encodeRow(List.of()));
    assertThrows(
        IllegalArgumentException.class, () -> encoder.encodeRows(List.of(List.of("A"), List.of())));
    assertThrows(
        IllegalArgumentException.class,
        () -> encoder.encodeRows(List.of(List.of("A"), List.of("B", "C"))));
    assertArrayEquals(
        new byte[] {0x41, 10, 0x42, 10}, encoder.encodeRows(List.of(List.of("A"), List.of("B"))));
  }

  @Test
  void copy009NulAndUnpairedSurrogateRefusedAtEveryPosition() {
    for (String invalid :
        List.of(
            "\0",
            "a\0b",
            new String(new char[] {(char) 0xd800}),
            new String(new char[] {(char) 0x0061, (char) 0xd800}),
            new String(new char[] {(char) 0xd800, (char) 0x0041}),
            new String(new char[] {(char) 0xd800, (char) 0xd800}),
            new String(new char[] {(char) 0xdc00}),
            new String(new char[] {(char) 0x0061, (char) 0xdc00}))) {
      assertThrows(IllegalArgumentException.class, () -> encoder.encodeRow(List.of(invalid)));
    }
    assertArrayEquals(
        new byte[] {0x41, (byte) 0xf0, (byte) 0x90, (byte) 0x80, (byte) 0x80, 0x42, 10},
        encoder.encodeRow(
            List.of(
                new String(
                    new char[] {(char) 0x0041, (char) 0xd800, (char) 0xdc00, (char) 0x0042}))));
    assertArrayEquals(
        new byte[] {(byte) 0xf4, (byte) 0x8f, (byte) 0xbf, (byte) 0xbf, 10},
        encoder.encodeRow(List.of(new String(new char[] {(char) 0xdbff, (char) 0xdfff}))));
  }

  @Test
  void copy010InputAndReturnOwnershipAreIndependent() {
    var row = new ArrayList<@Nullable String>(List.of("A", "B"));
    var rows = new ArrayList<List<@Nullable String>>();
    rows.add(row);
    byte[] first = encoder.encodeRows(rows);
    row.clear();
    rows.clear();
    assertArrayEquals(new byte[] {0x41, 9, 0x42, 10}, first);
    Arrays.fill(first, (byte) 0);
    assertArrayEquals(new byte[] {0x41, 9, 0x42, 10}, encoder.encodeRow(List.of("A", "B")));
  }

  @Test
  void copy011SafeDiagnosticAndUninterpretedNumericText() {
    var failure =
        assertThrows(IllegalArgumentException.class, () -> encoder.encodeRow(List.of("PRIVATE\0")));
    assertEquals("migration COPY text data is invalid", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    assertEquals("PostgresCopyTextEncoder[REDACTED]", encoder.toString());
    assertArrayEquals(
        new byte[] {0x30, 0x30, 0x31, 9, 0x2b, 0x30, 9, 0x20, 0x31, 0x20, 10},
        encoder.encodeRow(List.of("001", "+0", " 1 ")));
  }

  @Test
  void copy012ConcurrentCallsHaveSeparateOutputOwnership() throws Exception {
    var workers = Executors.newFixedThreadPool(8);
    var futures = new ArrayList<Future<?>>();
    try {
      for (int index = 0; index < 64; index++) {
        futures.add(
            workers.submit(
                () -> {
                  byte[] actual = encoder.encodeRow(Arrays.asList("A\tB", null));
                  assertArrayEquals(new byte[] {0x41, 0x5c, 0x74, 0x42, 9, 0x5c, 0x4e, 10}, actual);
                  Arrays.fill(actual, (byte) 0);
                }));
      }
      for (Future<?> future : futures) future.get(5, TimeUnit.SECONDS);
    } finally {
      workers.shutdownNow();
      assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS), "owned COPY workers terminate");
    }
    assertArrayEquals(
        new byte[] {0x41, 0x5c, 0x74, 0x42, 9, 0x5c, 0x4e, 10},
        encoder.encodeRow(Arrays.asList("A\tB", null)));
  }
}
