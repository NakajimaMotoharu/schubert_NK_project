package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.MaintenanceRetirement;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HexFormat;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** SS343 6.16; SSC055/PG161; BAT090..097. Literal expected values never use Production encoders. */
final class MaintenanceRetirementRecordsTest {
  static final String ID = "12345678-9abc-def0-8123-456789abcdef";
  static final String ACT = "fedcba98-7654-3210-8fed-cba987654321";
  static final String CUTOFF = "2025-01-01T00:00:00.000000Z";
  static final String END = "2025-01-02T00:00:00.000000Z";
  static final String NOW = "2026-02-06T00:00:00.000001Z";
  static final String HASH = "a5bf8bfabd8dbcc640bae2c4aa19c1e3387e43cb1a96cc3d9951be048a4a4065";
  static final String ANCHOR = "NKRUN1\n" + ID + "\n" + CUTOFF + "\n";
  static final String BEGIN = "NKACT1\n" + ID + "\n" + CUTOFF + "\n" + ACT + "\n";
  static final String DONE = "NKDONE1\n" + ID + "\n" + CUTOFF + "\n" + ACT + "\n" + END + "\n0\n";
  static final String MARKER =
      "NKRET1\n" + ID + "\n" + CUTOFF + "\n" + END + "\n" + NOW + "\n1\n" + HASH + "\n";
  static final BatchRun RUN = new BatchRun(UUID.fromString(ID), Instant.parse(CUTOFF));
  @TempDir Path temporary;

  static byte[] ascii(String value) {
    return value.getBytes(StandardCharsets.US_ASCII);
  }

  static MaintenanceRetirement value() {
    return new MaintenanceRetirement(RUN, Instant.parse(END), Instant.parse(NOW), 1, HASH);
  }

  @Test
  void literalMarkerAndPlanHash() throws Exception {
    assertEquals(
        HASH,
        HexFormat.of()
            .formatHex(MessageDigest.getInstance("SHA-256").digest(ascii("NKPLAN1\n" + DONE))));
    assertEquals(195, ascii(MARKER).length);
    assertArrayEquals(ascii(MARKER), MaintenanceRecords.retirement(value()));
    trace("PT-BAT-090-marker.txt", MaintenanceRecords.retirement(value()));
    var restored = MaintenanceRecords.readRetirement(ascii(MARKER));
    assertEquals(RUN, restored.run());
    assertEquals(Instant.parse(END), restored.latestEnded());
    assertEquals(Instant.parse(NOW), restored.preparedAt());
    assertEquals(1, restored.count());
    assertEquals(HASH, restored.digest());
    var max =
        new MaintenanceRetirement(
            RUN, Instant.parse(END), Instant.parse(NOW), Integer.MAX_VALUE, HASH);
    String maximum = MARKER.replace("\n1\n", "\n2147483647\n");
    assertEquals(204, ascii(maximum).length);
    assertArrayEquals(ascii(maximum), MaintenanceRecords.retirement(max));
    trace("PT-BAT-090-maximum.txt", MaintenanceRecords.retirement(max));
    assertEquals(max, MaintenanceRecords.readRetirement(ascii(maximum)));
  }

  @Test
  void temporalAndCountInvariants() {
    Instant ended = Instant.parse(END);
    Instant now = Instant.parse(NOW);
    for (Instant invalid :
        List.of(
            RUN.cutoff().minusNanos(1000),
            Instant.parse("+10000-01-01T00:00:00Z"),
            ended.plusNanos(1)))
      assertThrows(
          IllegalArgumentException.class,
          () -> new MaintenanceRetirement(RUN, invalid, now, 1, HASH));
    for (Instant invalid :
        List.of(
            Instant.MIN,
            ended,
            now.minusNanos(1000),
            now.plusNanos(1),
            Instant.parse("+10000-01-01T00:00:00Z")))
      assertThrows(
          IllegalArgumentException.class,
          () -> new MaintenanceRetirement(RUN, ended, invalid, 1, HASH));
    for (int count : List.of(0, -1, Integer.MIN_VALUE))
      assertThrows(
          IllegalArgumentException.class,
          () -> new MaintenanceRetirement(RUN, ended, now, count, HASH));
    for (String hash :
        List.of(
            "",
            "0".repeat(63),
            "0".repeat(65),
            HASH.toUpperCase(Locale.ROOT),
            "g" + HASH.substring(1),
            " ".repeat(64)))
      assertThrows(
          IllegalArgumentException.class,
          () -> new MaintenanceRetirement(RUN, ended, now, 1, hash));
    var earliest = new BatchRun(RUN.id(), Instant.parse("0001-01-01T00:00:00Z"));
    assertEquals(
        earliest.cutoff(),
        new MaintenanceRetirement(
                earliest, earliest.cutoff(), Instant.parse("0002-02-06T00:00:00Z"), 1, HASH)
            .latestEnded());
    assertEquals(
        Instant.parse("9999-12-31T23:59:59.999999Z"),
        new MaintenanceRetirement(RUN, ended, Instant.parse("9999-12-31T23:59:59.999999Z"), 1, HASH)
            .preparedAt());
  }

  @Test
  void nullAndOwnership() throws Exception {
    Instant end = Instant.parse(END);
    Instant now = Instant.parse(NOW);
    assertThrows(
        NullPointerException.class, () -> new MaintenanceRetirement(null, end, now, 1, HASH));
    assertThrows(
        NullPointerException.class, () -> new MaintenanceRetirement(RUN, null, now, 1, HASH));
    assertThrows(
        NullPointerException.class, () -> new MaintenanceRetirement(RUN, end, null, 1, HASH));
    assertThrows(
        NullPointerException.class, () -> new MaintenanceRetirement(RUN, end, now, 1, null));
    assertThrows(NullPointerException.class, () -> MaintenanceRecords.retirement(null));
    assertThrows(NullPointerException.class, () -> MaintenanceRecords.readRetirement(null));
    byte[] first = MaintenanceRecords.retirement(value());
    byte[] second = MaintenanceRecords.retirement(value());
    assertNotSame(first, second);
    first[0] = 0;
    assertArrayEquals(ascii(MARKER), second);
    var copy = MaintenanceRecords.readRetirement(second);
    second[0] = 0;
    assertEquals(value(), copy);
    assertEquals(value().hashCode(), copy.hashCode());
    assertEquals("MaintenanceRetirement[identity/time/plan=<redacted>]", copy.toString());
    assertNotEquals(value(), new MaintenanceRetirement(RUN, end, now, 2, HASH));
  }

  @Test
  void malformedMarkerBytes() {
    for (int length = 0; length <= 205; length++) {
      if (length == 195) continue;
      invalid(Arrays.copyOf(ascii(MARKER), length));
    }
    for (int position = 0; position < 195; position++)
      for (byte replacement : new byte[] {0, (byte) 0x80, (byte) '\r'}) {
        byte[] bytes = ascii(MARKER);
        bytes[position] = replacement;
        invalid(bytes);
      }
    for (String text :
        List.of(
            MARKER.replace("\n", "\r\n"),
            MARKER + "\n",
            MARKER.replace("NKRET1", "NKRET2"),
            MARKER.substring(0, 194) + "x",
            MARKER.replace("\n1\n", "xx1\n"),
            MARKER.replace("\n1\n", "\n\n1\n"))) invalid(ascii(text));
  }

  @Test
  void markerAliases() {
    for (String text :
        List.of(
            MARKER.replace(ID, ID.toUpperCase(Locale.ROOT)),
            MARKER.replace(ID, "1-2-3-4-5"),
            MARKER.replace(NOW, "2026-02-06T00:00:00.000001+00:00"),
            MARKER.replace(CUTOFF, "2025-01-01T00:00:00.000000z"),
            MARKER.replace(END, "2025-01-01T23:59:60.000000Z"),
            MARKER.replace(END, "2025-01-02T00:00:00.00000Z"),
            MARKER.replace("\n1\n", "\n+1\n"),
            MARKER.replace("\n1\n", "\n01\n"),
            MARKER.replace("\n1\n", "\n2147483648\n"),
            MARKER.replace("\n1\n", "\n-1\n"),
            MARKER.replace("\n1\n", "\nx\n"),
            MARKER.replace(NOW, CUTOFF),
            MARKER.replace(CUTOFF, "2025-13-01T00:00:00.000000Z"))) invalid(ascii(text));
  }

  @Test
  void boundedStorageRecords() throws Exception {
    try (var f = new MaintenanceRunFilesTest.Fixture(temporary);
        var root = OwnedTransferDirectory.open(f.calls, f.maintenance)) {
      var records = new DurableRecordFiles(root, f, f);
      String name = ID + ".retire";
      String literal = MARKER.replace("\n1\n", "\n2147483647\n");
      byte[] expected = ascii(literal);
      records.publish(name, expected, new UUID(1, 1));
      assertArrayEquals(expected, Files.readAllBytes(f.maintenance.resolve(name)));
      assertArrayEquals(expected, records.read(name).orElseThrow());
      f.overfillReader = true;
      assertThrows(StorageIoException.class, () -> records.read(name));
      f.overfillReader = false;
      records.publish(name, expected, new UUID(1, 2));
      records.remove(name, expected);
      assertTrue(records.read(name).isEmpty());
      records.remove(name, expected);
      Files.write(f.maintenance.resolve(name), Arrays.copyOf(expected, 205));
      assertThrows(StorageIoException.class, () -> records.read(name));
      assertEquals(205, Files.size(f.maintenance.resolve(name)));
    }
  }

  @Test
  void planNameBinding() throws Exception {
    try (var f = new MaintenanceRunFilesTest.Fixture(temporary);
        var root = OwnedTransferDirectory.open(f.calls, f.attempts)) {
      var records = new DurableRecordFiles(root, f, f);
      records.publish(ACT + ".plan", ascii(DONE), new UUID(1, 1));
      assertArrayEquals(ascii(DONE), records.read(ACT + ".plan").orElseThrow());
      records.remove(ACT + ".plan", ascii(DONE));
      for (String name : List.of(ID + ".plan", ACT + ".retire"))
        assertThrows(
            StorageIoException.class,
            () ->
                records.publish(
                    name, ascii(name.endsWith(".plan") ? DONE : MARKER), new UUID(1, 2)));
      assertThrows(
          StorageIoException.class,
          () -> records.publish(ACT + ".plan", ascii(MARKER), new UUID(1, 3)));
      assertThrows(
          StorageIoException.class,
          () -> records.publish(ID + ".retire", ascii(DONE), new UUID(1, 4)));
      assertThrows(IllegalArgumentException.class, () -> records.read(ID + ".unknown"));
    }
  }

  @Test
  void concurrentCanonicalRecords() throws Exception {
    try (var executor = Executors.newFixedThreadPool(4)) {
      List<Future<byte[]>> results = new ArrayList<>();
      for (int i = 0; i < 40; i++)
        results.add(
            executor.submit(
                () -> {
                  assertEquals(value(), MaintenanceRecords.readRetirement(ascii(MARKER)));
                  return MaintenanceRecords.retirement(value());
                }));
      Set<byte[]> distinct = Collections.newSetFromMap(new IdentityHashMap<>());
      for (var result : results) {
        byte[] bytes = result.get(10, TimeUnit.SECONDS);
        assertArrayEquals(ascii(MARKER), bytes);
        assertTrue(distinct.add(bytes));
      }
    }
  }

  static void trace(String name, byte[] actual) throws IOException {
    Path root = Path.of("target", "run-retirement-traces");
    Files.createDirectories(root);
    Files.write(root.resolve(name), actual);
  }

  private static void invalid(byte[] bytes) {
    var error = assertThrows(IOException.class, () -> MaintenanceRecords.readRetirement(bytes));
    assertEquals("maintenance record is invalid", error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }
}
