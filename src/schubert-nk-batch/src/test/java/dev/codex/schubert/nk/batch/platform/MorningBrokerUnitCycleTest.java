package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.bootstrap.ChildStartupContext;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.Test;

/** SSC125 BROKERSTART001/002: independent daemon generation/intent/owner sequencing vectors. */
final class MorningBrokerUnitCycleTest {
  private static final String FIXTURE_RETIRE_A2A9D4FF = "retire";
  private static final String FIXTURE_RETAINED_743E2854 = "retained";

  @Test
  void issbrokerstop001Known143IsNotAReceiptAndNeedsIndependentStoppedJournal() {
    String stopped =
        LIVE.replace("ActiveState=active", "ActiveState=failed")
            .replace("SubState=running", "SubState=failed")
            .replace("MainPID=43", "MainPID=0")
            .replace("ExecMainCode=0", "ExecMainCode=1")
            .replace("ExecMainStatus=0", "ExecMainStatus=143")
            .replace("ExecMainExitTimestampMonotonic=0", "ExecMainExitTimestampMonotonic=2234567")
            .replace("Result=success", "Result=exit-code");
    assertTrue(parse(stopped).brokerStoppedNormally());
    assertTrue(
        parse(
                stopped
                    .replace("ActiveState=failed", "ActiveState=inactive")
                    .replace("SubState=failed", "SubState=dead")
                    .replace("Result=exit-code", "Result=success"))
            .brokerStoppedNormally());
    assertFalse(parse(stopped).inactiveBaseline());
    assertTrue(parse(stopped).receiptAfter(Optional.empty()).isEmpty());
    for (var bad :
        List.of(
            stopped.replace("ExecMainCode=1", "ExecMainCode=2"),
            stopped.replace("ExecMainStatus=143", "ExecMainStatus=137"),
            stopped.replace("MainPID=0", "MainPID=43"),
            stopped.replace("Job=\n", "Job=12\n"),
            stopped.replace("2234567", "1234566"),
            stopped.replace("1234567", "0"),
            stopped.replace("Result=exit-code", "Result=timeout")))
      assertFalse(parse(bad).brokerStoppedNormally());
    var starts = new java.util.concurrent.atomic.AtomicInteger();
    var cycle =
        new MorningBrokerUnitCycle(
            () -> {},
            () -> parse(stopped),
            Optional::<MorningBrokerUnitCycle.Observation>empty,
            () -> {
              starts.incrementAndGet();
              throw new AssertionError("must not start");
            },
            () -> {
              throw new AssertionError("not delivered");
            });
    assertThrows(IOException.class, () -> cycle.execute(actual -> fail("live not granted")));
    assertEquals(0, starts.get());
  }

  static final String INV = "7".repeat(32);
  static final String LIVE =
      "Id=artemis.service\n"
          + "LoadState=loaded\n"
          + "ActiveState=active\n"
          + "SubState=running\n"
          + "Job=\n"
          + "MainPID=43\n"
          + "ControlPID=0\n"
          + "InvocationID="
          + INV
          + "\n"
          + "ExecMainCode=0\n"
          + "ExecMainStatus=0\n"
          + "ExecMainStartTimestampMonotonic=1234567\n"
          + "ExecMainExitTimestampMonotonic=0\n"
          + "Result=success\n"
          + "Type=simple\n"
          + "Restart=on-failure\n"
          + "RemainAfterExit=no\n"
          + "KillMode=control-group\n"
          + "SendSIGKILL=no\n";

  static InspectorUnitSnapshot parse(String text) {
    return InspectorUnitSnapshot.parse(
        text.getBytes(StandardCharsets.US_ASCII), InspectorUnitSnapshot.Target.ARTEMIS);
  }

  static InspectorUnitSnapshot baseline() {
    return parse(
        LIVE.replace("ActiveState=active", "ActiveState=inactive")
            .replace("SubState=running", "SubState=dead")
            .replace("MainPID=43", "MainPID=0")
            .replace(INV, "6".repeat(32)));
  }

  static final ChildStartupContext.Observed KERNEL =
      new ChildStartupContext.Observed(
          "11111111-1111-4111-8111-111111111111",
          43,
          12345,
          200,
          201,
          List.of(201L),
          "0::/system.slice/artemis.service\n",
          true,
          true);

  static MorningBrokerUnitCycle.Observation observation() {
    return new MorningBrokerUnitCycle.Observation(parse(LIVE), KERNEL);
  }

  static final class Retained extends Error {
    private static final long serialVersionUID = 1;
  }

  static BackupUnitStartClient.Attempt start(List<String> events, int exit) throws IOException {
    var child = new InspectorUnitProbeFixture.Child(new byte[0]);
    child.waitSeconds = 120;
    child.code = exit;
    return new BackupUnitStartClient(
            () -> events.add("root"),
            () -> {},
            command -> {
              assertEquals("artemis.service", command.getLast());
              events.add("start");
              return child;
            },
            () -> {
              events.add("intent");
              return () -> events.add(FIXTURE_RETIRE_A2A9D4FF);
            },
            BackupUnitStartClient.Target.BROKER)
        .start();
  }

  @Test
  void actualReadinessAndTwoLiveProofsPrecedeIntentRetirement() throws Exception {
    var events = new ArrayList<String>();
    var cycle =
        new MorningBrokerUnitCycle(
            () -> events.add("parent"),
            () -> {
              events.add("baseline");
              return baseline();
            },
            () -> Optional.of(observation()),
            () -> start(events, 0),
            () -> {
              throw new Retained();
            });
    var live =
        cycle.execute(
            actual -> {
              assertEquals(INV, actual.invocation());
              actual.recheck();
              events.add("Ops+journal");
            });
    assertEquals(INV, live.invocation());
    assertEquals("BrokerLive[observations=<redacted>]", live.toString());
    assertEquals(2, events.stream().filter("Ops+journal"::equals).count());
    assertEquals(1, events.stream().filter(FIXTURE_RETIRE_A2A9D4FF::equals).count());
    assertTrue(events.indexOf(FIXTURE_RETIRE_A2A9D4FF) > events.lastIndexOf("Ops+journal"));
    assertTrue(events.indexOf("baseline") < events.indexOf("intent"));
    assertTrue(events.indexOf("intent") < events.indexOf("start"));
    assertThrows(IOException.class, () -> cycle.execute(actual -> fail("single start lifetime")));
    live.recheck();
    assertTrue(live.stoppedJournal().isEmpty());
    assertTrue(live.previousObservation().inactiveBaseline());
  }

  @Test
  void issbrokerstop001IndependentProofIsRetainedButOnlyFreshLiveIsReadiness() throws Exception {
    String prior =
        LIVE.replace(INV, "6".repeat(32))
            .replace("ActiveState=active", "ActiveState=failed")
            .replace("SubState=running", "SubState=failed")
            .replace("MainPID=43", "MainPID=0")
            .replace("ExecMainCode=0", "ExecMainCode=1")
            .replace("ExecMainStatus=0", "ExecMainStatus=143")
            .replace("ExecMainExitTimestampMonotonic=0", "ExecMainExitTimestampMonotonic=2234567")
            .replace("Result=success", "Result=exit-code");
    var previous = parse(prior);
    byte[] stopped =
        BrokerJournalEvidenceTest.row(
                "AMQ221002: Apache Artemis Message Broker version 2.56.0 [public-fixture] stopped,"
                    + " uptime 2 hours",
                4)
            .replace(INV, "6".repeat(32))
            .getBytes(StandardCharsets.UTF_8);
    var actualSummary =
        BrokerJournalEvidence.consumeStopped(
            stopped,
            BrokerJournalEvidenceTest.BOOT,
            "6".repeat(32),
            java.math.BigInteger.valueOf(1234567),
            java.math.BigInteger.valueOf(2234567));
    var events = new ArrayList<String>();
    var cycle =
        new MorningBrokerUnitCycle(
            () -> {},
            new MorningBrokerUnitCycle.Baseline() {
              public InspectorUnitSnapshot read() {
                return previous;
              }

              public Optional<BrokerJournalEvidence.Summary> stoppedProof(
                  InspectorUnitSnapshot value) {
                assertSame(previous, value);
                events.add("prior-proof");
                return Optional.of(actualSummary);
              }
            },
            () -> Optional.of(observation()),
            () -> start(events, 0),
            () -> {
              throw new Retained();
            });
    var live =
        cycle.execute(
            actual -> {
              assertEquals(INV, actual.invocation());
              assertSame(previous, actual.previousObservation());
              assertSame(actualSummary, actual.stoppedJournal().orElseThrow());
            });
    assertSame(actualSummary, live.stoppedJournal().orElseThrow());
    assertTrue(events.indexOf("prior-proof") < events.indexOf("start"));
    assertEquals(1, events.stream().filter(FIXTURE_RETIRE_A2A9D4FF::equals).count());
  }

  @Test
  void oldGenerationUnknownProviderAndReadinessFailureNeverRetire() throws Exception {
    for (String fault : List.of("old", "client", "unknown", "readiness", "drift")) {
      var events = new ArrayList<String>();
      int[] reads = {0};
      var cycle =
          new MorningBrokerUnitCycle(
              () -> {},
              () ->
                  fault.equals("old")
                      ? parse(
                          LIVE.replace("ActiveState=active", "ActiveState=inactive")
                              .replace("SubState=running", "SubState=dead")
                              .replace("MainPID=43", "MainPID=0"))
                      : baseline(),
              () -> {
                if (fault.equals("drift") && reads[0]++ > 0) return Optional.empty();
                return Optional.of(observation());
              },
              () -> {
                if (fault.equals("unknown")) throw new IOException("test-only uncertain delivery");
                return start(events, fault.equals("client") ? 1 : 0);
              },
              () -> {
                events.add(FIXTURE_RETAINED_743E2854);
                throw new Retained();
              });
      assertThrows(
          Retained.class,
          () ->
              cycle.execute(
                  actual -> {
                    if (fault.equals("readiness")) throw new IOException("Ops unavailable");
                  }));
      assertFalse(events.contains(FIXTURE_RETIRE_A2A9D4FF), fault);
      assertTrue(events.contains(FIXTURE_RETAINED_743E2854), fault);
    }
  }

  @Test
  void issbroker005FinalReadinessIsFreshAndSecondFailureCannotReuseFirst() throws Exception {
    for (boolean secondFails : List.of(false, true)) {
      var events = new ArrayList<String>();
      var observations = new ArrayList<String>();
      var cycle =
          new MorningBrokerUnitCycle(
              () -> {},
              MorningBrokerUnitCycleTest::baseline,
              () -> Optional.of(observation()),
              () -> start(events, 0),
              () -> {
                events.add(FIXTURE_RETAINED_743E2854);
                throw new Retained();
              });
      MorningBrokerUnitCycle.Readiness capture =
          actual -> {
            actual.recheck();
            if (secondFails && !observations.isEmpty())
              throw new IOException("independent second observation unavailable");
            observations.add(observations.isEmpty() ? "first-actual" : "final-actual");
          };
      if (secondFails) {
        assertThrows(Retained.class, () -> cycle.execute(capture));
        assertEquals(List.of("first-actual"), observations);
        assertFalse(events.contains(FIXTURE_RETIRE_A2A9D4FF));
        assertTrue(events.contains(FIXTURE_RETAINED_743E2854));
      } else {
        var live = cycle.execute(capture);
        live.recheck();
        assertEquals(List.of("first-actual", "final-actual"), observations);
        assertEquals("final-actual", observations.getLast());
        assertEquals(1, events.stream().filter(FIXTURE_RETIRE_A2A9D4FF::equals).count());
        assertFalse(events.contains(FIXTURE_RETAINED_743E2854));
      }
    }
  }

  @Test
  void beforeStartRefusalDoesNotIssueStartAndDetachedThreadCannotUseLive() throws Exception {
    var events = new ArrayList<String>();
    var cycle =
        new MorningBrokerUnitCycle(
            () -> {},
            MorningBrokerUnitCycleTest::baseline,
            () -> Optional.of(observation()),
            () -> start(events, 0),
            () -> {
              throw new Retained();
            });
    var live = cycle.execute(actual -> actual.recheck());
    var failure = new java.util.concurrent.atomic.AtomicReference<Throwable>();
    Thread thread =
        new Thread(
            () -> {
              try {
                live.recheck();
              } catch (Throwable known) {
                failure.set(known);
              }
            });
    thread.start();
    thread.join();
    assertInstanceOf(IOException.class, failure.get());
    var invalid =
        new MorningBrokerUnitCycle(
            () -> {},
            () -> parse(LIVE),
            () -> Optional.of(observation()),
            () -> {
              throw new AssertionError("no start before baseline");
            },
            () -> {
              throw new Retained();
            });
    assertThrows(
        IOException.class, () -> invalid.execute(actual -> fail("no readiness before baseline")));
    assertThrows(NullPointerException.class, () -> invalid.execute(null));
  }
}
