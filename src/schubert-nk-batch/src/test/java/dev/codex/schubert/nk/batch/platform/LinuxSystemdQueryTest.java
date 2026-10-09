package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.*;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;

/** Independent fixed bytes/stateful owner and clock oracle; MANAGER817001..006. */
final class LinuxSystemdQueryTest {
  static final String FIELDS =
      "Id,LoadState,ActiveState,SubState,MainPID,InvocationID,ControlGroup";
  static final String DEADLINE = "Id,InvocationID,MainPID,ExecMainStartTimestampMonotonic";

  static final class Session implements LinuxSystemdQuery.Session {
    final List<String> events = new ArrayList<>();
    final Map<String, String> values =
        new HashMap<>(
            Map.of(
                "Id",
                "schubert-nk-api.service",
                "LoadState",
                "loaded",
                "ActiveState",
                "active",
                "SubState",
                "running",
                "MainPID",
                "200",
                "InvocationID",
                "00112233445566778899aabbccddeeff",
                "ControlGroup",
                "/system.slice/schubert-nk-api.service",
                "ExecMainStartTimestampMonotonic",
                "3000000"));
    LinuxSystemdQuery.Owner first = new LinuxSystemdQuery.Owner(1, 0, ":1.7"), second = first;
    int ownerReads;
    boolean closed, failClose;
    String fault = "";
    boolean fatal, runtime;

    void at(String at) throws IOException {
      events.add(at);
      if (at.equals(fault)) {
        if (fatal) throw new AssertionError("literal fatal");
        if (runtime) throw new IllegalStateException("literal runtime");
        throw new IOException("literal io");
      }
    }

    public void start(long micros) throws IOException {
      assertTrue(micros > 0 && micros <= 5000000);
      at("start");
    }

    public LinuxSystemdQuery.Owner owner(long micros) throws IOException {
      at("owner" + (++ownerReads));
      return ownerReads == 1 ? first : second;
    }

    public String read(
        RootStartupContext.Service service, LinuxSystemdQuery.Property p, long micros)
        throws IOException {
      assertEquals(RootStartupContext.Service.API, service);
      at(p.member);
      return values.get(p.member);
    }

    public void close() throws IOException {
      events.add("close");
      if (failClose) throw new IOException("literal uncertain close");
      closed = true;
    }

    public boolean closed() {
      return closed;
    }
  }

  @Test
  void exactFreshFullAndDeadlineGoldenBytes() throws Exception {
    List<Session> created = new ArrayList<>();
    var query =
        new LinuxSystemdQuery(
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
        query.read(RootStartupContext.Service.API, FIELDS));
    assertArrayEquals(
        ("Id=schubert-nk-api.service\n"
                + "InvocationID=00112233445566778899aabbccddeeff\n"
                + "MainPID=200\n"
                + "ExecMainStartTimestampMonotonic=3000000\n")
            .getBytes(StandardCharsets.US_ASCII),
        query.read(RootStartupContext.Service.API, DEADLINE));
    assertEquals(2, created.size());
    assertNotSame(created.get(0), created.get(1));
    assertEquals(
        List.of(
            "start",
            "owner1",
            "Id",
            "LoadState",
            "ActiveState",
            "SubState",
            "MainPID",
            "InvocationID",
            "ControlGroup",
            "owner2",
            "close"),
        created.get(0).events);
    assertTrue(created.stream().allMatch(s -> s.closed));
  }

  @Test
  void noCachedOwnerOrMutableProperty() throws Exception {
    var session = new Session();
    var query = new LinuxSystemdQuery(() -> session, () -> 0);
    session.second = new LinuxSystemdQuery.Owner(1, 0, ":1.8");
    assertThrows(IOException.class, () -> query.read(RootStartupContext.Service.API, FIELDS));
    assertTrue(session.closed);
    for (var owner :
        List.of(
            new LinuxSystemdQuery.Owner(2, 0, ":1.7"),
            new LinuxSystemdQuery.Owner(1, 2, ":1.7"),
            new LinuxSystemdQuery.Owner(1, 0, "foreign"),
            new LinuxSystemdQuery.Owner(1, 0, ":" + "7".repeat(64) + ".1"))) {
      var s = new Session();
      s.first = owner;
      assertThrows(
          IOException.class,
          () ->
              new LinuxSystemdQuery(() -> s, () -> 0).read(RootStartupContext.Service.API, FIELDS));
      assertEquals(List.of("start", "owner1", "close"), s.events);
    }
    assertEquals("SystemManagerOwner[REDACTED]", session.first.toString());
    for (String bad :
        List.of("foreign\nfield=secret", "\t", "日本語", "x".repeat(4097), "x".repeat(4096))) {
      var s = new Session();
      s.values.put("Id", bad);
      assertThrows(
          IOException.class,
          () ->
              new LinuxSystemdQuery(() -> s, () -> 0).read(RootStartupContext.Service.API, FIELDS));
      assertTrue(s.closed);
    }
  }

  @Test
  void everyBoundaryIoRuntimeFatalAndUnknownCloseRemainFailure() {
    for (String fault :
        List.of(
            "start",
            "owner1",
            "Id",
            "LoadState",
            "ActiveState",
            "SubState",
            "MainPID",
            "InvocationID",
            "ControlGroup",
            "owner2"))
      for (int kind = 0; kind < 3; kind++) {
        var s = new Session();
        s.fault = fault;
        s.runtime = kind == 1;
        s.fatal = kind == 2;
        var query = new LinuxSystemdQuery(() -> s, () -> 0);
        assertThrows(
            kind == 0
                ? IOException.class
                : kind == 1 ? IllegalStateException.class : AssertionError.class,
            () -> query.read(RootStartupContext.Service.API, FIELDS));
        assertTrue(s.closed);
        assertEquals("close", s.events.getLast());
      }
    var s = new Session();
    s.failClose = true;
    int[] creates = {0};
    var query =
        new LinuxSystemdQuery(
            () -> {
              creates[0]++;
              return s;
            },
            () -> 0);
    assertThrows(IOException.class, () -> query.read(RootStartupContext.Service.API, FIELDS));
    assertFalse(s.closed);
    assertThrows(IOException.class, () -> query.read(RootStartupContext.Service.API, FIELDS));
    assertEquals(1, creates[0]);
    var combined = new Session();
    combined.fault = "Id";
    combined.failClose = true;
    assertThrows(
        IOException.class,
        () ->
            new LinuxSystemdQuery(() -> combined, () -> 0)
                .read(RootStartupContext.Service.API, FIELDS));
    assertFalse(combined.closed);
  }

  @Test
  void originalFiveSecondsWholeQueryNotPerRpcAndSubMicrosecondBoundary() {
    for (long elapsed : new long[] {-1, 4_999_999_001L, 5_000_000_000L, Long.MAX_VALUE}) {
      var s = new Session();
      int[] reads = {0};
      var query = new LinuxSystemdQuery(() -> s, () -> reads[0]++ == 0 ? 0 : elapsed);
      assertThrows(IOException.class, () -> query.read(RootStartupContext.Service.API, FIELDS));
      assertTrue(s.closed);
      assertEquals(List.of("close"), s.events);
    }
    var s = new Session();
    int[] reads = {0};
    var query = new LinuxSystemdQuery(() -> s, () -> reads[0]++ < 5 ? 0 : 5_000_000_000L);
    assertThrows(IOException.class, () -> query.read(RootStartupContext.Service.API, FIELDS));
    assertFalse(s.events.contains("owner2"));
    assertTrue(s.closed);
  }

  @Test
  void rejectedInputsForeignThreadAndInterruptDoNotCreateCapability() throws Exception {
    int[] creates = {0};
    var query =
        new LinuxSystemdQuery(
            () -> {
              creates[0]++;
              return new Session();
            },
            () -> 0);
    assertThrows(IOException.class, () -> query.read(RootStartupContext.Service.API, "MainPID"));
    assertThrows(NullPointerException.class, () -> query.read(null, FIELDS));
    assertThrows(
        NullPointerException.class, () -> query.read(RootStartupContext.Service.API, null));
    assertThrows(NullPointerException.class, () -> new LinuxSystemdQuery(null, () -> 0));
    assertThrows(NullPointerException.class, () -> new LinuxSystemdQuery(Session::new, null));
    var error = new AtomicReference<Throwable>();
    var thread =
        new Thread(
            () -> {
              try {
                query.read(RootStartupContext.Service.API, FIELDS);
              } catch (Throwable failure) {
                error.set(failure);
              }
            });
    thread.start();
    thread.join();
    assertInstanceOf(IOException.class, error.get());
    Thread.currentThread().interrupt();
    try {
      assertThrows(IOException.class, () -> query.read(RootStartupContext.Service.API, FIELDS));
      assertTrue(Thread.currentThread().isInterrupted());
    } finally {
      Thread.interrupted();
    }
    assertEquals(0, creates[0]);
    assertThrows(
        NullPointerException.class,
        () ->
            new LinuxSystemdQuery(() -> null, () -> 0)
                .read(RootStartupContext.Service.API, FIELDS));
    assertThrows(NullPointerException.class, () -> new LinuxSystemdQuery.Owner(1, 0, null));
  }
}
