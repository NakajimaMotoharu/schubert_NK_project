package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;

/** Independent fixed bytes/stateful owner and clock oracle; MANAGER817001..006. */
final class SystemManagerObservationTest {
  private static final String FIXTURE_CLOSE_97959247 = "close";
  private static final String FIXTURE_LOADSTATE_26A05807 = "LoadState";
  private static final String FIXTURE_ACTIVESTATE_8ACAC4AA = "ActiveState";
  private static final String FIXTURE_SUBSTATE_39662EFC = "SubState";
  private static final String FIXTURE_MAINPID_D7C01CF7 = "MainPID";
  private static final String FIXTURE_INVOCATIONID_0F13ED0E = "InvocationID";
  private static final String FIXTURE_CONTROLGROUP_45352F50 = "ControlGroup";
  private static final String FIXTURE_START_A92AE961 = "start";
  private static final String FIXTURE_OWNER1_E15700EC = "owner1";
  private static final String FIXTURE_OWNER2_7DFC143F = "owner2";

  /** PT-OPS-MANAGEROWN001: failed/null acquisition never registers a pending owner. */
  @Test
  void managerown001FactoryFailuresKeepIdentityAndAllowAFreshNextAcquisition() throws Exception {
    Throwable[] failures = {
      new IOException("synthetic"),
      new IllegalStateException("synthetic"),
      new AssertionError("synthetic"),
      null
    };
    for (Throwable failure : failures) {
      int[] creates = {0};
      var accepted = new Session();
      var query =
          new SystemManagerObservation(
              () -> {
                if (creates[0]++ != 0) return accepted;
                if (failure instanceof IOException io) throw io;
                if (failure instanceof RuntimeException runtime) throw runtime;
                if (failure instanceof Error fatal) throw fatal;
                return null;
              },
              () -> 0);
      Class<? extends Throwable> expected =
          failure == null ? NullPointerException.class : failure.getClass();
      Throwable actual =
          assertThrows(expected, () -> query.read(SystemManagerObservation.Service.API, FIELDS));
      if (failure != null) assertSame(failure, actual);
      assertEquals(1, creates[0]);
      assertTrue(accepted.events.isEmpty());
      assertTrue(
          new String(
                  query.read(SystemManagerObservation.Service.API, FIELDS),
                  StandardCharsets.US_ASCII)
              .startsWith("Id=schubert-nk-api.service\nLoadState=loaded\n"));
      assertEquals(2, creates[0]);
      assertEquals(FIXTURE_CLOSE_97959247, accepted.events.getLast());
      assertTrue(accepted.closed);
    }
  }

  /** PT-OPS-MANAGEROWN002: post-release close observation is not a new release operation. */
  @Test
  void managerown002UnconfirmedPostCloseObservationRetainsPendingAndNeverCreatesAgain() {
    var delegate = new Session();
    var failure = new IllegalStateException("synthetic close observation");
    int[] creates = {0};
    int[] checks = {0};
    var session =
        new SystemManagerObservation.Session() {
          public void start(SystemManagerObservation.Budget budget) throws IOException {
            delegate.start(budget);
          }

          public SystemManagerObservation.Owner owner(long micros) throws IOException {
            return delegate.owner(micros);
          }

          public String read(
              SystemManagerObservation.Service service,
              SystemManagerObservation.Property property,
              long micros)
              throws IOException {
            return delegate.read(service, property, micros);
          }

          public void close() throws IOException {
            delegate.close();
          }

          public boolean closed() {
            checks[0]++;
            throw failure;
          }
        };
    var query =
        new SystemManagerObservation(
            () -> {
              creates[0]++;
              return session;
            },
            () -> 0);
    assertSame(
        failure,
        assertThrows(
            IllegalStateException.class,
            () -> query.read(SystemManagerObservation.Service.API, FIELDS)));
    assertTrue(delegate.closed);
    assertEquals(1, checks[0]);
    assertThrows(IOException.class, () -> query.read(SystemManagerObservation.Service.API, FIELDS));
    assertEquals(1, creates[0]);
    assertEquals(1, checks[0]);
    assertEquals(1, delegate.events.stream().filter(FIXTURE_CLOSE_97959247::equals).count());
  }

  static final String FIELDS =
      "Id,LoadState,ActiveState,SubState,MainPID,InvocationID,ControlGroup";
  static final String DEADLINE = "Id,InvocationID,MainPID,ExecMainStartTimestampMonotonic";

  static final class Session implements SystemManagerObservation.Session {
    final List<String> events = new ArrayList<>();
    final Map<String, String> values =
        new HashMap<>(
            Map.of(
                "Id",
                "schubert-nk-api.service",
                FIXTURE_LOADSTATE_26A05807,
                "loaded",
                FIXTURE_ACTIVESTATE_8ACAC4AA,
                "active",
                FIXTURE_SUBSTATE_39662EFC,
                "running",
                FIXTURE_MAINPID_D7C01CF7,
                "200",
                FIXTURE_INVOCATIONID_0F13ED0E,
                "00112233445566778899aabbccddeeff",
                FIXTURE_CONTROLGROUP_45352F50,
                "/system.slice/schubert-nk-api.service",
                "ExecMainStartTimestampMonotonic",
                "3000000"));
    SystemManagerObservation.Owner first = new SystemManagerObservation.Owner(1, 0, ":1.7");
    SystemManagerObservation.Owner second = first;
    int ownerReads;
    SystemManagerObservation.Service expectedService = SystemManagerObservation.Service.API;
    boolean closed;
    boolean failClose;
    String fault = "";
    boolean fatal;
    boolean runtime;

    void at(String at) throws IOException {
      events.add(at);
      if (at.equals(fault)) {
        if (fatal) throw new AssertionError("literal fatal");
        if (runtime) throw new IllegalStateException("literal runtime");
        throw new IOException("literal io");
      }
    }

    public void start(SystemManagerObservation.Budget budget) throws IOException {
      long micros = budget.remainingMicros();
      assertTrue(micros > 0 && micros <= 5000000);
      at(FIXTURE_START_A92AE961);
    }

    public SystemManagerObservation.Owner owner(long micros) throws IOException {
      at("owner" + (++ownerReads));
      return ownerReads == 1 ? first : second;
    }

    public String read(
        SystemManagerObservation.Service service, SystemManagerObservation.Property p, long micros)
        throws IOException {
      assertEquals(expectedService, service);
      at(p.member);
      return values.get(p.member);
    }

    public void close() throws IOException {
      events.add(FIXTURE_CLOSE_97959247);
      if (failClose) throw new IOException("literal uncertain close");
      closed = true;
    }

    public boolean closed() {
      return closed;
    }
  }

  /** PT-OPS-MANAGER4404-001: literal targets, fresh sessions and unchanged complete fields. */
  @Test
  void everyFixedTargetKeepsFreshOwnerAndAllSevenFields() throws Exception {
    var targets = SystemManagerObservation.Service.values();
    String[] units = {
      "schubert-nk-api.service", "schubert-nk-web.service",
      "schubert-nk-morning-controller.service", "schubert-nk-cleanup.service",
      "schubert-nk-expiry-cleanup.service", "schubert-nk-inbox-inspector.service",
      "artemis.service", "caddy.service"
    };
    assertEquals(8, targets.length);
    for (int index = 0; index < units.length; index++) {
      var target = targets[index];
      String unit = units[index];
      assertEquals(unit, target.unit());
      var created = new ArrayList<Session>();
      var query =
          new SystemManagerObservation(
              () -> {
                var session = new Session();
                session.expectedService = target;
                session.values.put("Id", unit);
                session.values.put(FIXTURE_CONTROLGROUP_45352F50, "/system.slice/" + unit);
                created.add(session);
                return session;
              },
              () -> 0);
      byte[] golden =
          ("Id="
                  + unit
                  + "\nLoadState=loaded\nActiveState=active\nSubState=running\n"
                  + "MainPID=200\nInvocationID=00112233445566778899aabbccddeeff\nControlGroup=/system.slice/"
                  + unit
                  + "\n")
              .getBytes(StandardCharsets.US_ASCII);
      assertArrayEquals(golden, query.read(target, FIELDS));
      assertArrayEquals(golden, query.read(target, FIELDS));
      assertEquals(2, created.size());
      assertNotSame(created.getFirst(), created.getLast());
      for (var session : created) {
        assertEquals(
            List.of(
                FIXTURE_START_A92AE961,
                FIXTURE_OWNER1_E15700EC,
                "Id",
                FIXTURE_LOADSTATE_26A05807,
                FIXTURE_ACTIVESTATE_8ACAC4AA,
                FIXTURE_SUBSTATE_39662EFC,
                FIXTURE_MAINPID_D7C01CF7,
                FIXTURE_INVOCATIONID_0F13ED0E,
                FIXTURE_CONTROLGROUP_45352F50,
                FIXTURE_OWNER2_7DFC143F,
                FIXTURE_CLOSE_97959247),
            session.events);
        assertTrue(session.closed);
      }
    }
  }

  /** PT-OPS-MANAGER4404-002: all Child observers route through the same strict reader. */
  @Test
  void childFixedObserversKeepFreshReadsAndNeverSelectAnArbitraryUnit() throws Exception {
    var expected =
        new ArrayDeque<>(
            List.of(
                SystemManagerObservation.Service.MORNING,
                SystemManagerObservation.Service.CLEANUP,
                SystemManagerObservation.Service.INSPECTOR,
                SystemManagerObservation.Service.BROKER,
                SystemManagerObservation.Service.CADDY));
    var created = new ArrayList<Session>();
    var query =
        new SystemManagerObservation(
            () -> {
              var session = new Session();
              session.expectedService = expected.removeFirst();
              created.add(session);
              return session;
            },
            () -> 0);
    var io = new ChildStartupContext.NativeIo(query);
    assertThrows(NullPointerException.class, () -> new ChildStartupContext.NativeIo(null));
    assertThrows(NullPointerException.class, () -> io.maintenanceUnit(null));
    for (var parent : ChildStartupContext.MaintenanceParent.values())
      assertTrue(io.maintenanceUnit(parent).length > 0);
    assertTrue(io.inspectorUnit().length > 0);
    assertTrue(io.brokerUnit().length > 0);
    assertTrue(io.caddyUnit().length > 0);
    assertTrue(expected.isEmpty());
    assertEquals(5, created.size());
    assertTrue(created.stream().allMatch(s -> s.closed && s.ownerReads == 2));
  }

  @Test
  void exactFreshFullAndDeadlineGoldenBytes() throws Exception {
    List<Session> created = new ArrayList<>();
    var query =
        new SystemManagerObservation(
            () -> {
              var s = new Session();
              created.add(s);
              return s;
            },
            () -> 0);
    assertArrayEquals(
        ("Id=schubert-nk-api.service\n"
                + "LoadState=loaded\n"
                + "ActiveState=active\n"
                + "SubState=running\n"
                + "MainPID=200\n"
                + "InvocationID=00112233445566778899aabbccddeeff\n"
                + "ControlGroup=/system.slice/schubert-nk-api.service\n")
            .getBytes(StandardCharsets.US_ASCII),
        query.read(SystemManagerObservation.Service.API, FIELDS));
    assertArrayEquals(
        ("Id=schubert-nk-api.service\n"
                + "InvocationID=00112233445566778899aabbccddeeff\n"
                + "MainPID=200\n"
                + "ExecMainStartTimestampMonotonic=3000000\n")
            .getBytes(StandardCharsets.US_ASCII),
        query.read(SystemManagerObservation.Service.API, DEADLINE));
    assertEquals(2, created.size());
    assertNotSame(created.get(0), created.get(1));
    assertEquals(
        List.of(
            FIXTURE_START_A92AE961,
            FIXTURE_OWNER1_E15700EC,
            "Id",
            FIXTURE_LOADSTATE_26A05807,
            FIXTURE_ACTIVESTATE_8ACAC4AA,
            FIXTURE_SUBSTATE_39662EFC,
            FIXTURE_MAINPID_D7C01CF7,
            FIXTURE_INVOCATIONID_0F13ED0E,
            FIXTURE_CONTROLGROUP_45352F50,
            FIXTURE_OWNER2_7DFC143F,
            FIXTURE_CLOSE_97959247),
        created.get(0).events);
    assertTrue(created.stream().allMatch(s -> s.closed));
  }

  @Test
  void noCachedOwnerOrMutableProperty() throws Exception {
    var session = new Session();
    var query = new SystemManagerObservation(() -> session, () -> 0);
    session.second = new SystemManagerObservation.Owner(1, 0, ":1.8");
    assertThrows(IOException.class, () -> query.read(SystemManagerObservation.Service.API, FIELDS));
    assertTrue(session.closed);
    for (var owner :
        List.of(
            new SystemManagerObservation.Owner(2, 0, ":1.7"),
            new SystemManagerObservation.Owner(1, 2, ":1.7"),
            new SystemManagerObservation.Owner(1, 0, "foreign"),
            new SystemManagerObservation.Owner(1, 0, ":" + "7".repeat(64) + ".1"))) {
      var s = new Session();
      s.first = owner;
      assertThrows(
          IOException.class,
          () ->
              new SystemManagerObservation(() -> s, () -> 0)
                  .read(SystemManagerObservation.Service.API, FIELDS));
      assertEquals(
          List.of(FIXTURE_START_A92AE961, FIXTURE_OWNER1_E15700EC, FIXTURE_CLOSE_97959247),
          s.events);
    }
    assertEquals("SystemManagerOwner[REDACTED]", session.first.toString());
    for (String bad :
        List.of("foreign\nfield=secret", "\t", "日本語", "x".repeat(4097), "x".repeat(4096))) {
      var s = new Session();
      s.values.put("Id", bad);
      assertThrows(
          IOException.class,
          () ->
              new SystemManagerObservation(() -> s, () -> 0)
                  .read(SystemManagerObservation.Service.API, FIELDS));
      assertTrue(s.closed);
    }
  }

  @Test
  void everyBoundaryIoRuntimeFatalAndUnknownCloseRemainFailure() {
    for (String fault :
        List.of(
            FIXTURE_START_A92AE961,
            FIXTURE_OWNER1_E15700EC,
            "Id",
            FIXTURE_LOADSTATE_26A05807,
            FIXTURE_ACTIVESTATE_8ACAC4AA,
            FIXTURE_SUBSTATE_39662EFC,
            FIXTURE_MAINPID_D7C01CF7,
            FIXTURE_INVOCATIONID_0F13ED0E,
            FIXTURE_CONTROLGROUP_45352F50,
            FIXTURE_OWNER2_7DFC143F))
      for (int kind = 0; kind < 3; kind++) {
        var s = new Session();
        s.fault = fault;
        s.runtime = kind == 1;
        s.fatal = kind == 2;
        var query = new SystemManagerObservation(() -> s, () -> 0);
        Class<? extends Throwable> expected =
            switch (kind) {
              case 0 -> IOException.class;
              case 1 -> IllegalStateException.class;
              default -> AssertionError.class;
            };
        assertThrows(expected, () -> query.read(SystemManagerObservation.Service.API, FIELDS));
        assertTrue(s.closed);
        assertEquals(FIXTURE_CLOSE_97959247, s.events.getLast());
      }
    var s = new Session();
    s.failClose = true;
    int[] creates = {0};
    var query =
        new SystemManagerObservation(
            () -> {
              creates[0]++;
              return s;
            },
            () -> 0);
    assertThrows(IOException.class, () -> query.read(SystemManagerObservation.Service.API, FIELDS));
    assertFalse(s.closed);
    assertThrows(IOException.class, () -> query.read(SystemManagerObservation.Service.API, FIELDS));
    assertEquals(1, creates[0]);
    var combined = new Session();
    combined.fault = "Id";
    combined.failClose = true;
    assertThrows(
        IOException.class,
        () ->
            new SystemManagerObservation(() -> combined, () -> 0)
                .read(SystemManagerObservation.Service.API, FIELDS));
    assertFalse(combined.closed);
  }

  @Test
  void originalFiveSecondsWholeQueryNotPerRpcAndSubMicrosecondBoundary() {
    int[] interruptedReads = {0};
    var interruptedSession = new Session();
    var interruptedQuery =
        new SystemManagerObservation(
            () -> interruptedSession,
            () -> {
              if (interruptedReads[0]++ > 0) Thread.currentThread().interrupt();
              return 0;
            });
    try {
      assertThrows(
          IOException.class,
          () -> interruptedQuery.read(SystemManagerObservation.Service.API, FIELDS));
      assertTrue(interruptedSession.closed);
      assertEquals(List.of(FIXTURE_CLOSE_97959247), interruptedSession.events);
    } finally {
      Thread.interrupted();
    }
    for (long elapsed : new long[] {-1, 4_999_999_001L, 5_000_000_000L, Long.MAX_VALUE}) {
      var s = new Session();
      int[] reads = {0};
      var query = new SystemManagerObservation(() -> s, () -> reads[0]++ == 0 ? 0 : elapsed);
      assertThrows(
          IOException.class, () -> query.read(SystemManagerObservation.Service.API, FIELDS));
      assertTrue(s.closed);
      assertEquals(List.of(FIXTURE_CLOSE_97959247), s.events);
    }
    var s = new Session();
    int[] reads = {0};
    var query = new SystemManagerObservation(() -> s, () -> reads[0]++ < 5 ? 0 : 5_000_000_000L);
    assertThrows(IOException.class, () -> query.read(SystemManagerObservation.Service.API, FIELDS));
    assertFalse(s.events.contains(FIXTURE_OWNER2_7DFC143F));
    assertTrue(s.closed);
  }

  @Test
  void rejectedInputsForeignThreadAndInterruptDoNotCreateCapability() throws Exception {
    int[] creates = {0};
    var query =
        new SystemManagerObservation(
            () -> {
              creates[0]++;
              return new Session();
            },
            () -> 0);
    assertThrows(
        IOException.class,
        () -> query.read(SystemManagerObservation.Service.API, FIXTURE_MAINPID_D7C01CF7));
    assertThrows(NullPointerException.class, () -> query.read(null, FIELDS));
    assertThrows(
        NullPointerException.class, () -> query.read(SystemManagerObservation.Service.API, null));
    assertThrows(NullPointerException.class, () -> new SystemManagerObservation(null, () -> 0));
    assertThrows(
        NullPointerException.class, () -> new SystemManagerObservation(Session::new, null));
    var error = new AtomicReference<Throwable>();
    var thread =
        new Thread(
            () -> {
              try {
                query.read(SystemManagerObservation.Service.API, FIELDS);
              } catch (Throwable failure) {
                error.set(failure);
              }
            });
    thread.start();
    thread.join();
    assertInstanceOf(IOException.class, error.get());
    Thread.currentThread().interrupt();
    try {
      assertThrows(
          IOException.class, () -> query.read(SystemManagerObservation.Service.API, FIELDS));
      assertTrue(Thread.currentThread().isInterrupted());
    } finally {
      Thread.interrupted();
    }
    assertEquals(0, creates[0]);
    assertThrows(
        NullPointerException.class,
        () ->
            new SystemManagerObservation(() -> null, () -> 0)
                .read(SystemManagerObservation.Service.API, FIELDS));
    assertThrows(NullPointerException.class, () -> new SystemManagerObservation.Owner(1, 0, null));
  }
}
