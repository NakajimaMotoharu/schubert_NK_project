package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.batch.file.MaintenanceRecords;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.time.Instant;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** OPS009/UI251/SS343 6.16; PT-BAT-RETVAL-001..006. Values never authorize retirement. */
final class MaintenanceRetirementValueCodecTest {
  private static final String RUN_ID = "12345678-9abc-def0-8123-456789abcdef";
  private static final String CUTOFF = "2020-01-01T00:00:00.000000Z";
  private static final String LATEST = "2020-01-02T00:00:00.000000Z";
  private static final String PREPARED = "2022-01-01T00:00:00.000000Z";
  private static final String DIGEST =
      "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef";
  private static final String GOLDEN =
      "NKRET1\n"
          + RUN_ID
          + "\n"
          + CUTOFF
          + "\n"
          + LATEST
          + "\n"
          + PREPARED
          + "\n1\n"
          + DIGEST
          + "\n";
  private static final String DIAGNOSTIC = "invalid maintenance retirement";
  private static final BatchRun RUN = new BatchRun(UUID.fromString(RUN_ID), Instant.parse(CUTOFF));
  private static final Instant END = Instant.parse(LATEST);
  private static final Instant NOW = Instant.parse(PREPARED);

  @Test
  void literalMinimumAndMaximumCountRecords() throws Exception {
    for (int count : List.of(1, Integer.MAX_VALUE)) {
      String literal = GOLDEN.replace("\n1\n", "\n" + count + "\n");
      byte[] expected = ascii(literal);
      assertEquals(count == 1 ? 195 : 204, expected.length);
      var value = new MaintenanceRetirement(RUN, END, NOW, count, DIGEST);
      assertArrayEquals(expected, MaintenanceRecords.retirement(value));
      var actual = MaintenanceRecords.readRetirement(expected);
      assertEquals(RUN, actual.run());
      assertEquals(END, actual.latestEnded());
      assertEquals(NOW, actual.preparedAt());
      assertEquals(count, actual.count());
      assertEquals(DIGEST, actual.digest());
      assertEquals(value, actual);
    }
  }

  @Test
  void strictAgeTimeCountAndDigestBoundaries() {
    Instant boundary = END.plus(Duration.ofDays(400));
    for (Instant prepared : List.of(boundary.minusNanos(1000), boundary))
      invalidValue(() -> new MaintenanceRetirement(RUN, END, prepared, 1, DIGEST));
    assertEquals(
        boundary.plusNanos(1000),
        new MaintenanceRetirement(RUN, END, boundary.plusNanos(1000), 1, DIGEST).preparedAt());
    for (Instant latest :
        List.of(
            RUN.cutoff().minusNanos(1000),
            Instant.parse("+10000-01-01T00:00:00Z"),
            END.plusNanos(1)))
      invalidValue(() -> new MaintenanceRetirement(RUN, latest, NOW, 1, DIGEST));
    for (Instant prepared : List.of(Instant.parse("+10000-01-01T00:00:00Z"), NOW.plusNanos(1)))
      invalidValue(() -> new MaintenanceRetirement(RUN, END, prepared, 1, DIGEST));
    for (int count : List.of(Integer.MIN_VALUE, -1, 0))
      invalidValue(() -> new MaintenanceRetirement(RUN, END, NOW, count, DIGEST));
    for (String digest :
        List.of(
            "",
            DIGEST.substring(1),
            DIGEST + "0",
            DIGEST.toUpperCase(Locale.ROOT),
            "g" + DIGEST.substring(1)))
      invalidValue(() -> new MaintenanceRetirement(RUN, END, NOW, 1, digest));
  }

  @Test
  void nullContractsAndRedactedDiagnostics() {
    for (Executable operation :
        List.<Executable>of(
            () -> new MaintenanceRetirement(null, END, NOW, 1, DIGEST),
            () -> new MaintenanceRetirement(RUN, null, NOW, 1, DIGEST),
            () -> new MaintenanceRetirement(RUN, END, null, 1, DIGEST),
            () -> new MaintenanceRetirement(RUN, END, NOW, 1, null),
            () -> MaintenanceRecords.retirement(null),
            () -> MaintenanceRecords.readRetirement(null)))
      assertThrows(NullPointerException.class, operation);
    assertEquals(
        "MaintenanceRetirement[identity/time/plan=<redacted>]",
        new MaintenanceRetirement(RUN, END, NOW, 1, DIGEST).toString());
  }

  @Test
  void structureAndByteRejection() throws Exception {
    for (byte[] wrong :
        List.of(
            new byte[0],
            ascii(GOLDEN.substring(1)),
            ascii(GOLDEN + "x"),
            ascii(GOLDEN + "\n"),
            ascii(GOLDEN.replace("\n", "\r\n")),
            ("\ufeff" + GOLDEN).getBytes(StandardCharsets.UTF_8))) invalidBytes(wrong);
    byte[] original = ascii(GOLDEN);
    for (int offset = 0; offset < original.length; offset++) {
      if (offset > 5 && original[offset] != '\n') continue;
      byte[] wrong = original.clone();
      wrong[offset] = 'x';
      invalidBytes(wrong);
    }
    byte[] wrong = original.clone();
    wrong[10] = (byte) 0x80;
    invalidBytes(wrong);
    wrong = original.clone();
    wrong[10] = '\n';
    wrong[wrong.length - 1] = 'x';
    invalidBytes(wrong);
    String different = GOLDEN.replace(RUN_ID, "02345678-9abc-def0-8123-456789abcdef");
    assertEquals(
        UUID.fromString("02345678-9abc-def0-8123-456789abcdef"),
        MaintenanceRecords.readRetirement(ascii(different)).run().id());
  }

  @Test
  void canonicalScalarAliasesAreRejected() throws Exception {
    for (String id :
        List.of(RUN_ID.toUpperCase(Locale.ROOT), "1-1-1-1-1", "z" + RUN_ID.substring(1)))
      invalidBytes(ascii(GOLDEN.replace(RUN_ID, id)));
    for (String cutoff :
        List.of(
            "0000-01-01T00:00:00.000000Z",
            "2020-01-01T00:00:00.000000z",
            "2020-01-01T00:00:00.0000010Z",
            "2020-02-30T00:00:00.000000Z",
            "2020-01-01T09:00:00.000000+09:00"))
      invalidBytes(ascii(GOLDEN.replace(CUTOFF, cutoff)));
    for (String count : List.of("01", "+1", " 1", "0", "-1", "2147483648", "x"))
      invalidBytes(ascii(GOLDEN.replace("\n1\n", "\n" + count + "\n")));
    invalidBytes(ascii(GOLDEN.replace(DIGEST, DIGEST.toUpperCase(Locale.ROOT))));
    invalidBytes(ascii(GOLDEN.replace(LATEST, "2019-12-31T23:59:59.999999Z")));
    assertEquals(
        Instant.parse("2020-01-01T00:00:00.000001Z"),
        MaintenanceRecords.readRetirement(
                ascii(GOLDEN.replace(LATEST, "2020-01-01T00:00:00.000001Z")))
            .latestEnded());
    invalidBytes(ascii(GOLDEN.replace(PREPARED, "2020-01-03T00:00:00.000000Z")));
  }

  @Test
  void independentArrayOwnershipEqualityAndYearMaximum() throws Exception {
    byte[] input = ascii(GOLDEN);
    var first = MaintenanceRecords.readRetirement(input);
    assertArrayEquals(ascii(GOLDEN), input);
    Arrays.fill(input, (byte) 0);
    assertEquals(1, first.count());
    assertEquals(DIGEST, first.digest());
    byte[] encoded = MaintenanceRecords.retirement(first);
    byte[] separate = MaintenanceRecords.retirement(first);
    assertNotSame(encoded, separate);
    encoded[0] = 'x';
    assertArrayEquals(ascii(GOLDEN), separate);
    var same = new MaintenanceRetirement(new BatchRun(RUN.id(), RUN.cutoff()), END, NOW, 1, DIGEST);
    assertEquals(first, same);
    assertEquals(first.hashCode(), same.hashCode());
    assertNotEquals(first, new MaintenanceRetirement(RUN, END, NOW, 2, DIGEST));
    Instant maximum = Instant.parse("9999-12-31T23:59:59.999999Z");
    assertEquals(maximum, new MaintenanceRetirement(RUN, END, maximum, 1, DIGEST).preparedAt());
    assertArrayEquals(
        ascii(GOLDEN.replace(PREPARED, "9999-12-31T23:59:59.999999Z")),
        MaintenanceRecords.retirement(new MaintenanceRetirement(RUN, END, maximum, 1, DIGEST)));
  }

  private static byte[] ascii(String value) {
    return value.getBytes(StandardCharsets.US_ASCII);
  }

  private static void invalidValue(Executable operation) {
    var failure = assertThrows(IllegalArgumentException.class, operation);
    assertEquals(DIAGNOSTIC, failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static void invalidBytes(byte[] input) {
    var failure = assertThrows(IOException.class, () -> MaintenanceRecords.readRetirement(input));
    assertEquals("maintenance record is invalid", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }
}
