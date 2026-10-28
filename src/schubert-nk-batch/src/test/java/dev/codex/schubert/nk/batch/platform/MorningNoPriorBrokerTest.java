package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.file.MorningGateEvidence;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;

/** SSC166/BUG532/YKT377 ISSCOLD001..006: independent boot absence and fresh journal vectors. */
final class MorningNoPriorBrokerTest {
  private static final String FIXTURE_RETIRE_A2A9D4FF = "retire";

  static final class Query implements MorningPreviousBroker.Query {
    final List<byte[]> delivered = new ArrayList<>();
    int calls;
    String later = "";
    Throwable failure;
    boolean nullBytes;
    boolean overflow;

    public byte[] read(List<String> command, int limit, long nanos) throws IOException {
      calls++;
      assertEquals(4 * 1024 * 1024, limit);
      assertTrue(nanos > 0);
      assertEquals(
          List.of(
              "/usr/bin/journalctl",
              "--no-pager",
              "--quiet",
              "--all",
              "--output=json",
              "--output-fields=MESSAGE,PRIORITY,_SYSTEMD_INVOCATION_ID,_BOOT_ID,_SYSTEMD_UNIT",
              "_SYSTEMD_UNIT=artemis.service",
              "_BOOT_ID=11111111111141118111111111111111"),
          command);
      if (failure instanceof IOException known) throw known;
      if (failure instanceof RuntimeException unknown) throw unknown;
      if (failure instanceof Error fatal) throw fatal;
      if (nullBytes) return null;
      byte[] result =
          overflow
              ? new byte[limit + 1]
              : (calls == 1 ? "" : later).getBytes(StandardCharsets.UTF_8);
      delivered.add(result);
      return result;
    }

    void erased() {
      for (var value : delivered) assertArrayEquals(new byte[value.length], value);
    }
  }

  static MorningPreviousBroker.Evidence absence(Query query) throws IOException {
    return MorningPreviousBroker.collectForStartup(
        BrokerJournalEvidenceTest.BOOT,
        MorningPreviousBrokerTest.cold(),
        query,
        () -> 1_000_000_000L);
  }

  static MorningBrokerUnitCycle cycle(InspectorUnitSnapshot previous, List<String> events) {
    return new MorningBrokerUnitCycle(
        () -> {},
        () -> previous,
        () -> Optional.of(MorningBrokerUnitCycleTest.observation()),
        () -> MorningBrokerUnitCycleTest.start(events, 0),
        () -> {
          events.add("retained");
          throw new MorningBrokerUnitCycleTest.Retained();
        });
  }

  @Test
  void isscold001TwoActualEmptyReadsAreAbsenceNotCleanOrReceipt() throws Exception {
    var q = new Query();
    var proof = absence(q);
    assertInstanceOf(MorningPreviousBroker.NoPrior.class, proof);
    assertEquals(BrokerJournalEvidenceTest.BOOT, proof.boot());
    assertEquals("PreviousBroker[no-prior-current-boot]", proof.toString());
    assertEquals(2, q.calls);
    q.erased();
    for (boolean nativeInterval : List.of(false, true)) {
      var old = new MorningPreviousBrokerTest.Fixture();
      assertInstanceOf(
          MorningPreviousBroker.Closed.class,
          MorningPreviousBroker.collectForStartup(
              BrokerJournalEvidenceTest.BOOT,
              nativeInterval
                  ? MorningPreviousBrokerTest.stopped()
                  : MorningPreviousBrokerTest.cold(),
              old,
              () -> 1_000_000_000L));
      assertEquals(nativeInterval ? 1 : 6, old.calls);
      old.erased();
    }
  }

  @Test
  void isscold002NonemptySecondReadPartialColdAndUnknownAreNeverAbsence() {
    for (String bytes : List.of(" ", "\n", "{}", BrokerJournalEvidenceTest.GOLDEN)) {
      var q = new Query();
      q.later = bytes;
      assertThrows(IOException.class, () -> absence(q));
      assertEquals(2, q.calls);
      q.erased();
    }
    for (String fault : List.of("ExecMainCode=1", "ExecMainStatus=143", "Result=exit-code")) {
      var q = new Query();
      var text =
          MorningBrokerUnitCycleTest.LIVE
              .replace("ActiveState=active", "ActiveState=inactive")
              .replace("SubState=running", "SubState=dead")
              .replace("MainPID=43", "MainPID=0")
              .replace("InvocationID=" + "7".repeat(32), "InvocationID=")
              .replace(
                  "ExecMainStartTimestampMonotonic=1234567", "ExecMainStartTimestampMonotonic=0")
              .replace(
                  fault.substring(0, fault.indexOf('='))
                      + "="
                      + (fault.startsWith("Result") ? "success" : "0"),
                  fault);
      assertThrows(
          IOException.class,
          () ->
              MorningPreviousBroker.collectForStartup(
                  BrokerJournalEvidenceTest.BOOT,
                  MorningBrokerUnitCycleTest.parse(text),
                  q,
                  () -> 1_000_000_000L));
      q.erased();
    }
    for (Throwable failure :
        List.of(
            new IOException("timeout"),
            new IllegalStateException("unknown"),
            new AssertionError("fatal"))) {
      var q = new Query();
      q.failure = failure;
      assertSame(failure, assertThrows(Throwable.class, () -> absence(q)));
    }
    var nil = new Query();
    nil.nullBytes = true;
    assertThrows(NullPointerException.class, () -> absence(nil));
    var huge = new Query();
    huge.overflow = true;
    assertThrows(IOException.class, () -> absence(huge));
    huge.erased();
    assertThrows(
        IOException.class,
        () ->
            MorningPreviousBroker.collectForStartup(
                BrokerJournalEvidenceTest.BOOT,
                MorningBrokerUnitCycleTest.parse(MorningBrokerUnitCycleTest.LIVE),
                new Query(),
                () -> 1_000_000_000L));
  }

  @Test
  void isscold003FreshFullBootJournalIsCheckedTwiceBeforeRetirementAndLater() throws Exception {
    var q = new Query();
    var proof = absence(q);
    q.later = BrokerJournalEvidenceTest.GOLDEN;
    var events = new ArrayList<String>();
    var live = cycle(MorningPreviousBrokerTest.cold(), events).execute(proof::recheck);
    assertEquals(4, q.calls);
    assertEquals(1, events.stream().filter(FIXTURE_RETIRE_A2A9D4FF::equals).count());
    proof.recheck(live);
    assertEquals(5, q.calls);
    q.erased();
    assertThrows(NullPointerException.class, () -> proof.recheck(null));
    var failure = new AtomicReference<Throwable>();
    Thread other =
        new Thread(
            () -> {
              try {
                proof.recheck(live);
              } catch (Throwable actual) {
                failure.set(actual);
              }
            });
    other.start();
    other.join();
    assertInstanceOf(IOException.class, failure.get());
    assertEquals(5, q.calls);
  }

  @Test
  void isscold004DelayedPriorForeignPrestartMalformedAndSecondFailureRetainIntent()
      throws Exception {
    for (String raw :
        List.of(
            "",
            "{}",
            BrokerJournalEvidenceTest.GOLDEN
                + MorningPreviousBrokerTest.STOP.replace("7".repeat(32), "6".repeat(32)),
            BrokerJournalEvidenceTest.GOLDEN.replace("7".repeat(32), "6".repeat(32)),
            BrokerJournalEvidenceTest.GOLDEN.replace("1234567", "1234566"),
            BrokerJournalEvidenceTest.GOLDEN.replace("Using NIO Journal", "ERROR NIO Journal"),
            BrokerJournalEvidenceTest.GOLDEN + BrokerJournalEvidenceTest.GOLDEN,
            BrokerJournalEvidenceTest.GOLDEN.replace(
                "Using NIO Journal", "Using NIO Journal\\ud800"))) {
      var q = new Query();
      var proof = absence(q);
      q.later = raw;
      var events = new ArrayList<String>();
      assertThrows(
          MorningBrokerUnitCycleTest.Retained.class,
          () -> cycle(MorningPreviousBrokerTest.cold(), events).execute(proof::recheck));
      assertFalse(events.contains(FIXTURE_RETIRE_A2A9D4FF));
      assertTrue(events.contains("retained"));
      q.erased();
    }
    var q = new Query();
    var proof = absence(q);
    q.later = BrokerJournalEvidenceTest.GOLDEN;
    var events = new ArrayList<String>();
    int[] checks = {0};
    assertThrows(
        MorningBrokerUnitCycleTest.Retained.class,
        () ->
            cycle(MorningPreviousBrokerTest.cold(), events)
                .execute(
                    actual -> {
                      if (++checks[0] == 2)
                        q.later +=
                            MorningPreviousBrokerTest.STOP.replace("7".repeat(32), "6".repeat(32));
                      proof.recheck(actual);
                    }));
    assertEquals(2, checks[0]);
    assertFalse(events.contains(FIXTURE_RETIRE_A2A9D4FF));
    q.erased();
  }

  @Test
  void isscold005BaselineMismatchRefusesBeforeJournalAndLawfulAppendRechecks() throws Exception {
    var q = new Query();
    var proof = absence(q);
    q.later = BrokerJournalEvidenceTest.GOLDEN;
    var events = new ArrayList<String>();
    assertThrows(
        MorningBrokerUnitCycleTest.Retained.class,
        () -> cycle(MorningBrokerUnitCycleTest.baseline(), events).execute(proof::recheck));
    assertEquals(2, q.calls);
    assertFalse(events.contains(FIXTURE_RETIRE_A2A9D4FF));
    var live = cycle(MorningPreviousBrokerTest.cold(), new ArrayList<>()).execute(proof::recheck);
    q.later += BrokerJournalEvidenceTest.row("AMQ221031: Ready", 4).replace("1234567", "1234568");
    proof.recheck(live);
    q.erased();
  }

  @Test
  void isscold006AbsentAndPresentCanonicalVectorsContainNoInventedOldFields() throws Exception {
    for (boolean present : List.of(false, true)) {
      var initial = MorningStopEvidenceTest.snapshot(present);
      var boot = UUID.fromString(initial.parent().boot());
      var q = new MorningPreviousBrokerTest.Fixture();
      q.full = "";
      q.bootHex = boot.toString().replace("-", "");
      var proof =
          MorningPreviousBroker.collectForStartup(
              boot, MorningPreviousBrokerTest.cold(), q, () -> 1_000_000_000L);
      assertArrayEquals(
          MorningStopEvidenceTest.fixture(
              "issuer-stop-" + (present ? "present" : "absent") + "-no-prior-golden.txt"),
          MorningGateEvidence.stop(
              MorningStopEvidenceTest.epoch(boot), "1".repeat(32), "2".repeat(32), initial, proof));
      assertEquals(2, q.calls);
      q.erased();
    }
  }

  @Test
  void isscold007ClosedEvidenceStillRechecksActualSavedOldGenerationAgainstFreshLive()
      throws Exception {
    var old = new MorningPreviousBrokerTest.Fixture();
    old.full = old.full.replace("7".repeat(32), "6".repeat(32));
    old.start = old.start.replace("7".repeat(32), "6".repeat(32));
    old.last = old.last.replace("7".repeat(32), "6".repeat(32));
    var proof =
        MorningPreviousBroker.collectForStartup(
            BrokerJournalEvidenceTest.BOOT,
            MorningPreviousBrokerTest.cold(),
            old,
            () -> 1_000_000_000L);
    var live = cycle(MorningPreviousBrokerTest.cold(), new ArrayList<>()).execute(proof::recheck);
    proof.recheck(live);
    assertThrows(NullPointerException.class, () -> proof.recheck(null));
    old.erased();
    old.full = old.full.replace("uptime 2 hours", "uptime 3 hours");
    assertThrows(IOException.class, () -> proof.recheck(live));
    old.erased();
  }

  @Test
  void isscold008PartialBaselineAndClosedThreadOrExtraRetainedEntryRefuse() throws Exception {
    String cold =
        MorningBrokerUnitCycleTest.LIVE
            .replace("ActiveState=active", "ActiveState=inactive")
            .replace("SubState=running", "SubState=dead")
            .replace("MainPID=43", "MainPID=0")
            .replace("InvocationID=" + "7".repeat(32), "InvocationID=")
            .replace(
                "ExecMainStartTimestampMonotonic=1234567", "ExecMainStartTimestampMonotonic=0");
    for (String bad :
        List.of(
            cold.replace("InvocationID=\n", "InvocationID=" + "6".repeat(32) + "\n"),
            cold.replace(
                "ExecMainStartTimestampMonotonic=0", "ExecMainStartTimestampMonotonic=1234567"),
            cold.replace(
                "ExecMainExitTimestampMonotonic=0", "ExecMainExitTimestampMonotonic=1234568"))) {
      var q = new Query();
      var previous = MorningBrokerUnitCycleTest.parse(bad);
      assertThrows(
          IOException.class,
          () ->
              MorningPreviousBroker.collectForStartup(
                  BrokerJournalEvidenceTest.BOOT, previous, q, () -> 1_000_000_000L));
      assertThrows(
          IOException.class,
          () ->
              MorningPreviousBroker.collect(
                  BrokerJournalEvidenceTest.BOOT, previous, q, () -> 1_000_000_000L));
      assertEquals(0, q.calls);
    }
    var old = new MorningPreviousBrokerTest.Fixture();
    var proof =
        MorningPreviousBroker.collect(
            BrokerJournalEvidenceTest.BOOT,
            MorningPreviousBrokerTest.cold(),
            old,
            () -> 1_000_000_000L);
    var failure = new AtomicReference<Throwable>();
    Thread other =
        new Thread(
            () -> {
              try {
                proof.recheck();
              } catch (Throwable actual) {
                failure.set(actual);
              }
            });
    other.start();
    other.join();
    assertInstanceOf(IOException.class, failure.get());
    assertEquals(5, old.calls);
    old.full += BrokerJournalEvidenceTest.row("AMQ221031: Ready", 5).replace("1234567", "1234568");
    assertThrows(IOException.class, proof::recheck);
    old.erased();
  }
}
