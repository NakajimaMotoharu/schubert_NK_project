package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.MaintenanceRetirement;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Arrays;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** SS343 6.16 pure value serialization; never a GC operation, publication or permission. */
final class PureRetirementCodecContractTest {
  private static final String ID = "00000000-0000-0000-0000-000000000123";
  private static final String CUTOFF = "2020-01-01T00:00:00.000000Z";
  private static final String PREPARED = "2021-02-04T00:00:00.000001Z";
  private static final String DIGEST = "0123456789abcdef".repeat(4);
  private static final BatchRun RUN = new BatchRun(UUID.fromString(ID), Instant.parse(CUTOFF));
  private static final String PREFIX =
      "NKRET1\n" + ID + "\n" + CUTOFF + "\n" + CUTOFF + "\n" + PREPARED + "\n";

  @Test
  void retirementCodec001CanonicalMarkersUseIndependentExactBytesAndPositiveCounts()
      throws Exception {
    for (int count : new int[] {1, Integer.MAX_VALUE}) {
      String golden = PREFIX + (count == 1 ? "1" : "2147483647") + "\n" + DIGEST + "\n";
      byte[] bytes = ascii(golden);
      assertEquals(count == 1 ? 195 : 204, bytes.length);
      var value = value(Instant.parse(CUTOFF), Instant.parse(PREPARED), count, DIGEST);
      assertArrayEquals(bytes, MaintenanceRecords.retirement(value));
      var restored = MaintenanceRecords.readRetirement(bytes);
      assertEquals(UUID.fromString(ID), restored.run().id());
      assertEquals(Instant.parse(CUTOFF), restored.run().cutoff());
      assertEquals(Instant.parse(CUTOFF), restored.latestEnded());
      assertEquals(Instant.parse(PREPARED), restored.preparedAt());
      assertEquals(count, restored.count());
      assertEquals(DIGEST, restored.digest());
    }
    var maximum =
        value(
            Instant.parse("9998-01-01T00:00:00Z"),
            Instant.parse("9999-12-31T23:59:59.999999Z"),
            1,
            DIGEST);
    assertEquals(
        Instant.parse("9999-12-31T23:59:59.999999Z"),
        MaintenanceRecords.readRetirement(MaintenanceRecords.retirement(maximum)).preparedAt());
  }

  @Test
  void retirementCodec002EveryValueInvariantHasAnIndependentBoundary() {
    Instant ended = Instant.parse(CUTOFF);
    Instant prepared = Instant.parse(PREPARED);
    for (Instant wrong :
        List.of(
            Instant.parse("2019-12-31T23:59:59.999999Z"),
            Instant.parse("+10000-01-01T00:00:00Z"),
            Instant.parse("2020-01-01T00:00:00.000000001Z")))
      invalidValue(() -> value(wrong, prepared, 1, DIGEST));
    for (Instant wrong :
        List.of(
            Instant.parse("+10000-01-01T00:00:00Z"),
            Instant.parse("2021-02-04T00:00:00.000001001Z"),
            Instant.parse("2021-02-04T00:00:00Z"),
            Instant.parse("2021-02-03T23:59:59.999999Z"),
            ended))
      invalidValue(() -> value(ended, wrong, 1, DIGEST));
    for (int wrong : new int[] {0, -1, Integer.MIN_VALUE})
      invalidValue(() -> value(ended, prepared, wrong, DIGEST));
    for (String wrong :
        List.of("", "a".repeat(63), "a".repeat(65), "A".repeat(64), "g".repeat(64)))
      invalidValue(() -> value(ended, prepared, 1, wrong));
  }

  @Test
  void retirementCodec003NonCanonicalOrMalformedMarkersHaveOneFixedDiagnostic() {
    String golden = PREFIX + "1\n" + DIGEST + "\n";
    byte[] original = ascii(golden);
    for (byte[] wrong :
        List.of(
            new byte[0],
            Arrays.copyOf(original, 194),
            Arrays.copyOf(original, 205),
            ascii(golden.replace("NKRET1", "NKACT1")),
            ascii(golden.replace("\n", "\r\n")),
            ascii(golden + "\n"),
            ascii(golden.substring(0, golden.length() - 1) + "x"),
            ascii(golden.replace("\n1\n", "\n+1\n")),
            ascii(golden.replace("\n1\n", "\n0000000001\n")),
            ascii(golden.replace("\n1\n", "\nx\n")),
            ascii(golden.replace("\n1\n", "\n0\n")),
            ascii(golden.replace(CUTOFF, "2020-02-30T00:00:00.000000Z")),
            ascii(golden.replace(PREPARED, "2021-02-04T00:00:00.000001z")),
            ascii(golden.replace(DIGEST, "A".repeat(64))))) invalidWire(wrong);
    byte[] high = original.clone();
    high[20] = (byte) 128;
    invalidWire(high);
    byte[] extraField = original.clone();
    extraField[20] = '\n';
    invalidWire(extraField);
    for (int index = 0; index < original.length; index++) {
      if (index >= 7 && original[index] != '\n') continue;
      byte[] wrong = original.clone();
      wrong[index] = original[index] == '\n' ? (byte) 'x' : (byte) '?';
      invalidWire(wrong);
    }
  }

  @Test
  void retirementCodec004NullsOwnershipAndRedactionNeverIssuePermission() throws Exception {
    Instant ended = Instant.parse(CUTOFF);
    Instant prepared = Instant.parse(PREPARED);
    for (Executable operation :
        List.<Executable>of(
            () -> new MaintenanceRetirement(null, ended, prepared, 1, DIGEST),
            () -> new MaintenanceRetirement(RUN, null, prepared, 1, DIGEST),
            () -> new MaintenanceRetirement(RUN, ended, null, 1, DIGEST),
            () -> new MaintenanceRetirement(RUN, ended, prepared, 1, null),
            () -> MaintenanceRecords.retirement(null),
            () -> MaintenanceRecords.readRetirement(null)))
      assertThrows(NullPointerException.class, operation);
    var value = value(ended, prepared, 1, DIGEST);
    byte[] first = MaintenanceRecords.retirement(value);
    byte[] second = MaintenanceRecords.retirement(value);
    assertNotSame(first, second);
    first[0] = '?';
    byte[] golden = ascii(PREFIX + "1\n" + DIGEST + "\n");
    assertArrayEquals(golden, second);
    var restored = MaintenanceRecords.readRetirement(second);
    assertArrayEquals(golden, second);
    Arrays.fill(second, (byte) 0);
    assertEquals(DIGEST, restored.digest());
    assertEquals(1, restored.count());
    assertEquals(Instant.parse(PREPARED), restored.preparedAt());
    assertEquals(
        "MaintenanceRetirement[identity/time/plan=<redacted>]", restored.toString());
  }

  private static MaintenanceRetirement value(
      Instant ended, Instant prepared, int count, String digest) {
    return new MaintenanceRetirement(RUN, ended, prepared, count, digest);
  }

  private static byte[] ascii(String value) {
    return value.getBytes(StandardCharsets.US_ASCII);
  }

  private static void invalidValue(Executable operation) {
    var failure = assertThrows(IllegalArgumentException.class, operation);
    assertEquals("invalid maintenance retirement", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static void invalidWire(byte[] bytes) {
    var failure = assertThrows(IOException.class, () -> MaintenanceRecords.readRetirement(bytes));
    assertEquals("maintenance record is invalid", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }
}
