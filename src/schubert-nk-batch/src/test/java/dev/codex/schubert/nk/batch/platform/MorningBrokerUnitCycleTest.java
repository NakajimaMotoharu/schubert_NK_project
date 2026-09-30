package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.bootstrap.ChildStartupContext;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.*;
import org.junit.jupiter.api.Test;

/** SSC125 BROKERSTART001/002: independent daemon generation/intent/owner sequencing vectors. */
final class MorningBrokerUnitCycleTest {
  static final String INV = "7".repeat(32);
  static final String LIVE =
      "Id=artemis.service\nLoadState=loaded\nActiveState=active\nSubState=running\nJob=\nMainPID=43\nControlPID=0\nInvocationID="
          + INV
          + "\nExecMainCode=0\nExecMainStatus=0\nExecMainStartTimestampMonotonic=1234567\nExecMainExitTimestampMonotonic=0\nResult=success\nType=simple\nRestart=on-failure\nRemainAfterExit=no\nKillMode=control-group\nSendSIGKILL=no\n";

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
              return () -> events.add("retire");
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
    assertEquals(1, events.stream().filter("retire"::equals).count());
    assertTrue(events.indexOf("retire") > events.lastIndexOf("Ops+journal"));
    assertTrue(events.indexOf("baseline") < events.indexOf("intent"));
    assertTrue(events.indexOf("intent") < events.indexOf("start"));
    assertThrows(IOException.class, () -> cycle.execute(actual -> fail("single start lifetime")));
    live.recheck();
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
                events.add("retained");
                throw new Retained();
              });
      assertThrows(
          Retained.class,
          () ->
              cycle.execute(
                  actual -> {
                    if (fault.equals("readiness")) throw new IOException("Ops unavailable");
                  }));
      assertFalse(events.contains("retire"), fault);
      assertTrue(events.contains("retained"), fault);
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
