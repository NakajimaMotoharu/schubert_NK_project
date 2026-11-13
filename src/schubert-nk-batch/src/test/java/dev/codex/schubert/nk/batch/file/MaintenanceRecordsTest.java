package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import dev.codex.schubert.nk.batch.repository.MaintenanceCompletion;
import dev.codex.schubert.nk.batch.repository.MaintenanceCompletion.Outcome;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** SS343 6.13; SSC-055/PG-D-156; PT-BAT-038..045. All expected bytes are hand-written. */
final class MaintenanceRecordsTest {
  private static final String SUCCESS_LINE = "0\n";
  private static final String WARNING_LINE = "10\n";
  private static final String RUN_ID = "12345678-9abc-def0-8123-456789abcdef";
  private static final String ACTIVATION_ID = "fedcba98-7654-3210-8fed-cba987654321";
  private static final String CUTOFF = "2026-09-12T04:05:06.123456Z";
  private static final String END = "2026-09-12T05:06:07.234567Z";
  private static final String ANCHOR = "NKRUN1\n" + RUN_ID + "\n" + CUTOFF + "\n";
  private static final String ACTIVATION =
      "NKACT1\n" + RUN_ID + "\n" + CUTOFF + "\n" + ACTIVATION_ID + "\n";
  private static final String DONE =
      "NKDONE1\n" + RUN_ID + "\n" + CUTOFF + "\n" + ACTIVATION_ID + "\n" + END + "\n";
  private static final BatchRun RUN = new BatchRun(UUID.fromString(RUN_ID), Instant.parse(CUTOFF));
  private static final MaintenanceActivation ACTIVE =
      new MaintenanceActivation(RUN, UUID.fromString(ACTIVATION_ID));

  @Test
  void literalRecords() throws Exception {
    assertEquals(72, ascii(ANCHOR).length);
    assertEquals(109, ascii(ACTIVATION).length);
    assertEquals(140, ascii(DONE + SUCCESS_LINE).length);
    assertEquals(141, ascii(DONE + WARNING_LINE).length);
    byte[] anchorBytes = MaintenanceRecords.anchor(RUN);
    byte[] activationBytes = MaintenanceRecords.activation(ACTIVE);
    trace("PT-BAT-038-anchor.txt", anchorBytes);
    trace("PT-BAT-038-activation.txt", activationBytes);
    assertArrayEquals(ascii(ANCHOR), anchorBytes);
    assertArrayEquals(ascii(ACTIVATION), activationBytes);
    var restored = MaintenanceRecords.readAnchor(ascii(ANCHOR));
    assertEquals(UUID.fromString(RUN_ID), restored.id());
    assertEquals(Instant.parse(CUTOFF), restored.cutoff());
    var activation = MaintenanceRecords.readActivation(ascii(ACTIVATION));
    assertEquals(RUN, activation.run());
    assertEquals(UUID.fromString(ACTIVATION_ID), activation.id());
    for (var outcome : List.of(Outcome.SUCCESS, Outcome.WARNING)) {
      int expectedCode = outcome == Outcome.SUCCESS ? 0 : 10;
      var value = new MaintenanceCompletion(ACTIVE, Instant.parse(END), outcome);
      byte[] golden = ascii(DONE + expectedCode + "\n");
      byte[] actual = MaintenanceRecords.completion(value);
      trace("PT-BAT-038-completion-" + expectedCode + ".txt", actual);
      assertArrayEquals(golden, actual);
      var completion = MaintenanceRecords.readCompletion(golden);
      assertEquals(ACTIVE, completion.activation());
      assertEquals(Instant.parse(END), completion.endedAt());
      assertEquals(outcome, completion.outcome());
      assertEquals(expectedCode, completion.outcome().exitCode());
    }
  }

  @Test
  void identityTemporalBoundaries() throws Exception {
    for (String id :
        List.of("00000000-0000-0000-0000-000000000000", "ffffffff-ffff-ffff-ffff-ffffffffffff"))
      for (String time : List.of("0001-01-01T00:00:00.000000Z", "9999-12-31T23:59:59.999999Z")) {
        var run = new BatchRun(UUID.fromString(id), Instant.parse(time));
        var active = new MaintenanceActivation(run, UUID.fromString(id));
        var completed = new MaintenanceCompletion(active, Instant.parse(time), Outcome.WARNING);
        String anchor = "NKRUN1\n" + id + "\n" + time + "\n";
        String begin = "NKACT1\n" + id + "\n" + time + "\n" + id + "\n";
        String done = "NKDONE1\n" + id + "\n" + time + "\n" + id + "\n" + time + "\n10\n";
        assertArrayEquals(ascii(anchor), MaintenanceRecords.anchor(run));
        assertArrayEquals(ascii(begin), MaintenanceRecords.activation(active));
        assertArrayEquals(ascii(done), MaintenanceRecords.completion(completed));
        assertEquals(run, MaintenanceRecords.readAnchor(ascii(anchor)));
        assertEquals(active, MaintenanceRecords.readActivation(ascii(begin)));
        assertEquals(completed, MaintenanceRecords.readCompletion(ascii(done)));
        assertEquals(
            time.startsWith("0001") ? LocalDate.of(1, 1, 1) : LocalDate.of(10000, 1, 1),
            active.businessDate());
      }
    var before =
        new MaintenanceActivation(
            new BatchRun(RUN.id(), Instant.parse("2026-09-12T14:59:59.999999Z")), ACTIVE.id());
    var after =
        new MaintenanceActivation(
            new BatchRun(RUN.id(), Instant.parse("2026-09-12T15:00:00Z")), ACTIVE.id());
    assertEquals(LocalDate.of(2026, 9, 12), before.businessDate());
    assertEquals(LocalDate.of(2026, 9, 13), after.businessDate());
  }

  @Test
  void malformedSources() {
    for (String golden : List.of(ANCHOR, ACTIVATION, DONE + SUCCESS_LINE, DONE + WARNING_LINE)) {
      for (byte[] wrong :
          List.of(
              new byte[0],
              ascii(golden.substring(1)),
              ascii(golden + "x"),
              ascii(golden.replace("\n", "\r\n")),
              ascii(golden + "\n"),
              ("\ufeff" + golden).getBytes(StandardCharsets.UTF_8))) rejectAs(golden, wrong);
      byte[] original = ascii(golden);
      // Only fixed magic/delimiters are mutation-rejection oracles; a new canonical ID is valid.
      int magicEnd = golden.indexOf('\n');
      for (int position = 0; position < original.length; position++) {
        if (position > magicEnd && original[position] != '\n') continue;
        for (int value = 0; value < 256; value++) {
          if (value == Byte.toUnsignedInt(original[position])) continue;
          byte[] wrong = original.clone();
          wrong[position] = (byte) value;
          rejectAs(golden, wrong);
        }
      }
      for (int value : new int[] {0, 1, 9, 13, 31, 127, 128, 255}) {
        byte[] wrong = original.clone();
        wrong[magicEnd + 2] = (byte) value;
        rejectAs(golden, wrong);
      }
      // Preserve the field count independently of the terminal-empty-field guard.
      byte[] wrong = original.clone();
      wrong[magicEnd + 2] = '\n';
      wrong[wrong.length - 1] = 'x';
      rejectAs(golden, wrong);
    }
    failure(() -> MaintenanceRecords.readAnchor(ascii(ACTIVATION)));
    failure(() -> MaintenanceRecords.readActivation(ascii(ANCHOR)));
    failure(() -> MaintenanceRecords.readCompletion(ascii(ACTIVATION)));
    failure(() -> MaintenanceRecords.readCompletion(new byte[141]));
  }

  @Test
  void scalarAliases() throws Exception {
    for (String golden : List.of(ANCHOR, ACTIVATION, DONE + SUCCESS_LINE, DONE + WARNING_LINE)) {
      for (String wrongId :
          List.of(RUN_ID.toUpperCase(Locale.ROOT), "1-1-1-1-1", "g" + RUN_ID.substring(1)))
        rejectAs(golden, ascii(golden.replace(RUN_ID, wrongId)));
      for (String wrongTime :
          List.of(
              "2026-09-12T04:05:06.123456z",
              "2026-09-12T04:05:06.1234560Z",
              "2026-09-12T04:05:06.12345Z",
              "2026-09-12T13:05:06.123456+09:00",
              "2016-12-31T23:59:60.123456Z",
              "2026-02-30T04:05:06.123456Z",
              "0000-01-01T00:00:00.000000Z"))
        rejectAs(golden, ascii(golden.replace(CUTOFF, wrongTime)));
    }
    for (String golden : List.of(ACTIVATION, DONE + SUCCESS_LINE))
      for (String bad :
          List.of(ACTIVATION_ID.toUpperCase(Locale.ROOT), "z" + ACTIVATION_ID.substring(1)))
        rejectAs(golden, ascii(golden.replace(ACTIVATION_ID, bad)));
    for (String status : List.of("00", "01", "11", "50", "70", "+0", " 0", "0 ", "x"))
      failure(() -> MaintenanceRecords.readCompletion(ascii(DONE + status + "\n")));
    for (String badEnd :
        List.of(
            "2026-09-12T04:05:06.123455Z",
            "2026-02-30T05:06:07.234567Z",
            "2026-09-12T05:06:07.234567z"))
      failure(
          () ->
              MaintenanceRecords.readCompletion(ascii((DONE + SUCCESS_LINE).replace(END, badEnd))));
    // Valid different identities/times are data, not authentication failures of this parser.
    String different = ANCHOR.replace(RUN_ID, "02345678-9abc-def0-8123-456789abcdef");
    assertEquals(
        UUID.fromString("02345678-9abc-def0-8123-456789abcdef"),
        MaintenanceRecords.readAnchor(ascii(different)).id());
    var changed =
        MaintenanceRecords.readActivation(
            ascii(ACTIVATION.replace(CUTOFF, "2026-09-12T04:05:06.123457Z")));
    assertEquals(Instant.parse("2026-09-12T04:05:06.123457Z"), changed.run().cutoff());
    assertNotEquals(ACTIVE, changed);
  }

  @Test
  void completionInvariants() {
    for (Instant wrong :
        List.of(
            RUN.cutoff().minusNanos(1000),
            Instant.parse("+10000-01-01T00:00:00Z"),
            RUN.cutoff().plusNanos(1))) {
      var failure =
          assertThrows(
              IllegalArgumentException.class,
              () -> new MaintenanceCompletion(ACTIVE, wrong, Outcome.SUCCESS));
      assertEquals("invalid maintenance completion time", failure.getMessage());
      assertNull(failure.getCause());
    }
    assertEquals(
        RUN.cutoff(), new MaintenanceCompletion(ACTIVE, RUN.cutoff(), Outcome.SUCCESS).endedAt());
    assertEquals(0, Outcome.SUCCESS.exitCode());
    assertEquals(10, Outcome.WARNING.exitCode());
  }

  @Test
  void nullContracts() {
    for (Executable operation :
        List.<Executable>of(
            () -> MaintenanceRecords.anchor(null),
            () -> MaintenanceRecords.activation(null),
            () -> MaintenanceRecords.completion(null),
            () -> MaintenanceRecords.readAnchor(null),
            () -> MaintenanceRecords.readActivation(null),
            () -> MaintenanceRecords.readCompletion(null),
            () -> new MaintenanceActivation(null, ACTIVE.id()),
            () -> new MaintenanceActivation(RUN, null),
            () -> new MaintenanceCompletion(null, Instant.parse(END), Outcome.SUCCESS),
            () -> new MaintenanceCompletion(ACTIVE, null, Outcome.SUCCESS),
            () -> new MaintenanceCompletion(ACTIVE, Instant.parse(END), null)))
      assertThrows(NullPointerException.class, operation);
  }

  @Test
  void ownershipAndRedaction() throws Exception {
    byte[] anchor = ascii(ANCHOR);
    byte[] activation = ascii(ACTIVATION);
    byte[] done = ascii(DONE + SUCCESS_LINE);
    var readRun = MaintenanceRecords.readAnchor(anchor);
    var readActive = MaintenanceRecords.readActivation(activation);
    var readDone = MaintenanceRecords.readCompletion(done);
    assertArrayEquals(ascii(ANCHOR), anchor);
    assertArrayEquals(ascii(ACTIVATION), activation);
    assertArrayEquals(ascii(DONE + SUCCESS_LINE), done);
    Arrays.fill(anchor, (byte) 0);
    Arrays.fill(activation, (byte) 0);
    Arrays.fill(done, (byte) 0);
    assertEquals(RUN, readRun);
    assertEquals(ACTIVE, readActive);
    assertEquals(Instant.parse(END), readDone.endedAt());
    byte[] first = MaintenanceRecords.anchor(RUN);
    byte[] second = MaintenanceRecords.anchor(RUN);
    assertNotSame(first, second);
    first[0] = 'X';
    assertArrayEquals(ascii(ANCHOR), second);
    first = MaintenanceRecords.activation(ACTIVE);
    second = MaintenanceRecords.activation(ACTIVE);
    assertNotSame(first, second);
    first[0] = 'X';
    assertArrayEquals(ascii(ACTIVATION), second);
    first = MaintenanceRecords.completion(readDone);
    second = MaintenanceRecords.completion(readDone);
    assertNotSame(first, second);
    first[0] = 'X';
    assertArrayEquals(ascii(DONE + SUCCESS_LINE), second);
    assertEquals("MaintenanceActivation[identity/cutoff=<redacted>]", readActive.toString());
    assertEquals("MaintenanceCompletion[identity/time=<redacted>]", readDone.toString());
    var same = new MaintenanceActivation(new BatchRun(RUN.id(), RUN.cutoff()), ACTIVE.id());
    assertEquals(1, new HashSet<>(List.of(ACTIVE, same)).size());
    assertEquals(
        2, new HashSet<>(List.of(ACTIVE, new MaintenanceActivation(RUN, RUN.id()))).size());
    var completed = new MaintenanceCompletion(same, Instant.parse(END), Outcome.SUCCESS);
    assertEquals(1, new HashSet<>(List.of(readDone, completed)).size());
    assertNotEquals(readDone, new MaintenanceCompletion(same, Instant.parse(END), Outcome.WARNING));
    assertNotEquals(
        readDone,
        new MaintenanceCompletion(same, Instant.parse(END).plusNanos(1000), Outcome.SUCCESS));
    assertNotEquals(
        readDone,
        new MaintenanceCompletion(
            new MaintenanceActivation(RUN, RUN.id()), Instant.parse(END), Outcome.SUCCESS));
  }

  @Test
  void concurrentUse() throws Exception {
    var executor = Executors.newFixedThreadPool(8);
    try {
      var futures = new ArrayList<Future<MaintenanceCompletion>>();
      for (int index = 1; index <= 64; index++) {
        final int value = index;
        futures.add(
            executor.submit(
                () -> {
                  String id = String.format(Locale.ROOT, "00000000-0000-0000-0000-%012x", value);
                  Outcome outcome = value % 2 == 0 ? Outcome.SUCCESS : Outcome.WARNING;
                  var active = new MaintenanceActivation(RUN, UUID.fromString(id));
                  var complete = new MaintenanceCompletion(active, Instant.parse(END), outcome);
                  String expected =
                      "NKDONE1\n"
                          + RUN_ID
                          + "\n"
                          + CUTOFF
                          + "\n"
                          + id
                          + "\n"
                          + END
                          + "\n"
                          + (value % 2 == 0 ? SUCCESS_LINE : WARNING_LINE);
                  assertArrayEquals(ascii(expected), MaintenanceRecords.completion(complete));
                  assertEquals(complete, MaintenanceRecords.readCompletion(ascii(expected)));
                  return complete;
                }));
      }
      var actual = new HashSet<UUID>();
      int warnings = 0;
      for (var future : futures) {
        var value = future.get(5, TimeUnit.SECONDS);
        actual.add(value.activation().id());
        if (value.outcome() == Outcome.WARNING) warnings++;
      }
      assertEquals(64, actual.size());
      assertEquals(32, warnings);
    } finally {
      executor.shutdownNow();
      if (!executor.awaitTermination(10, TimeUnit.SECONDS))
        throw new AssertionError("owned maintenance record workers did not terminate");
    }
  }

  private static byte[] ascii(String value) {
    return value.getBytes(StandardCharsets.US_ASCII);
  }

  private static void trace(String name, byte[] actual) throws IOException {
    Path directory = Path.of("target/maintenance-record-traces");
    Files.createDirectories(directory);
    Files.write(directory.resolve(name), actual);
  }

  private static void rejectAs(String golden, byte[] actual) {
    if (golden.startsWith("NKRUN1\n")) failure(() -> MaintenanceRecords.readAnchor(actual));
    else if (golden.startsWith("NKACT1\n"))
      failure(() -> MaintenanceRecords.readActivation(actual));
    else failure(() -> MaintenanceRecords.readCompletion(actual));
  }

  private static void failure(Executable operation) {
    var failure = assertThrows(IOException.class, operation);
    assertEquals("maintenance record is invalid", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }
}
