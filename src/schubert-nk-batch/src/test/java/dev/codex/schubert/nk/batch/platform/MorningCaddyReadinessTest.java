package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.bootstrap.ChildStartupContext;
import java.io.IOException;
import java.util.*;
import org.junit.jupiter.api.Test;

/** SS342/SSC178/CADDY455: literal manager/kernel/HTTP values, no native authority. */
final class MorningCaddyReadinessTest {
  static final String INV = "7".repeat(32);
  static final ChildStartupContext.Observed ACTOR =
      new ChildStartupContext.Observed(
          "11111111-1111-4111-8111-111111111111",
          43,
          12345,
          200,
          201,
          List.of(201L),
          "0::/system.slice/caddy.service\n",
          true,
          true);

  static Map<String, String> values() {
    var m = new HashMap<String, String>();
    String text =
        """
        Id=caddy.service
        LoadState=loaded
        ActiveState=active
        SubState=running
        MainPID=43
        InvocationID=77777777777777777777777777777777
        Job=
        Type=notify
        Restart=no
        KillMode=control-group
        SendSIGKILL=no
        NoNewPrivileges=yes
        CapabilityBoundingSet=
        AmbientCapabilities=
        User=caddy
        Group=caddy
        SupplementaryGroups=
        TimeoutStartUSec=30s
        TimeoutStopUSec=30s
        Result=success
        ExecMainCode=0
        ExecMainStatus=0
        ExecMainStartTimestampMonotonic=1000000
        ExecMainExitTimestampMonotonic=0
        ExecStartPre={ path=/usr/bin/caddy ; argv[]=/usr/bin/caddy validate --config /etc/caddy/Caddyfile ; ignore_errors=no ; start_time=[Sun 2026-10-04 19:00:00 JST] ; stop_time=[Sun 2026-10-04 19:00:01 JST] ; pid=42 ; code=exited ; status=0/0 }
        ExecStart={ path=/usr/bin/caddy ; argv[]=/usr/bin/caddy run --config /etc/caddy/Caddyfile ; ignore_errors=no ; start_time=[Sun 2026-10-04 19:00:02 JST] ; stop_time=[n/a] ; pid=43 ; code=(null) ; status=0/0 }
        """;
    text.lines()
        .forEach(
            line -> {
              int i = line.indexOf('=');
              m.put(line.substring(0, i), line.substring(i + 1));
            });
    return m;
  }

  static Map<String, String> normalHistory() {
    var m = values();
    m.put("ActiveState", "inactive");
    m.put("SubState", "dead");
    m.put("MainPID", "0");
    m.put("ExecMainCode", "1");
    m.put("ExecMainExitTimestampMonotonic", "2000000");
    m.put("ExecStartPre", m.get("ExecStartPre").replace("status=0/0", "status=0"));
    m.put(
        "ExecStart",
        m.get("ExecStart")
            .replace("stop_time=[n/a]", "stop_time=[Sun 2026-10-04 19:01:00 JST]")
            .replace("code=(null)", "code=exited")
            .replace("status=0/0", "status=0"));
    return m;
  }

  static Map<String, String> noHistory() {
    var m = normalHistory();
    m.put("InvocationID", "");
    m.put("ExecMainCode", "0");
    m.put("ExecMainStartTimestampMonotonic", "0");
    m.put("ExecMainExitTimestampMonotonic", "0");
    m.put(
        "ExecStartPre",
        "{ path=/usr/bin/caddy ; argv[]=/usr/bin/caddy validate --config /etc/caddy/Caddyfile ; ignore_errors=no ; start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; code=(null) ; status=0/0 }");
    m.put(
        "ExecStart",
        "{ path=/usr/bin/caddy ; argv[]=/usr/bin/caddy run --config /etc/caddy/Caddyfile ; ignore_errors=no ; start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; code=(null) ; status=0/0 }");
    return m;
  }

  @Test
  void caddy192001ReloadClearedAuxiliaryHistoryRetainsOnlyPreviousGeneration() throws Exception {
    var retained = normalHistory();
    // Independent manager literals: daemon-reload clears both auxiliary entries, not F18.
    retained.put("ExecStartPre", noHistory().get("ExecStartPre"));
    retained.put("ExecStart", noHistory().get("ExecStart"));
    assertEquals("77777777777777777777777777777777", MorningCaddyReadiness.cold(retained));
    assertThrows(
        IOException.class,
        () ->
            new MorningCaddyReadiness(() -> {}, new Fixture(), "77777777777777777777777777777777"));
    var fresh =
        new MorningCaddyReadiness(() -> {}, new Fixture(), "88888888888888888888888888888888");
    assertTrue(fresh.ready());
  }

  @Test
  void caddy192002MixedOrMalformedReloadEntriesNeverBecomeColdAuthority() {
    for (String key : List.of("ExecStartPre", "ExecStart")) {
      var mixed = normalHistory();
      mixed.put(key, noHistory().get(key));
      assertThrows(IOException.class, () -> MorningCaddyReadiness.cold(mixed), key);
      for (String bad :
          List.of(
              "path=/tmp/caddy",
              "ignore_errors=yes",
              "pid=1",
              "code=exited",
              "status=1/FAILURE",
              "start_time=[Mon 2026-10-05 13:00:00 JST]")) {
        var altered = normalHistory();
        altered.put("ExecStartPre", noHistory().get("ExecStartPre"));
        altered.put("ExecStart", noHistory().get("ExecStart"));
        String entry = altered.get(key);
        String expectedPart =
            bad.startsWith("path=")
                ? "path=/usr/bin/caddy"
                : bad.startsWith("ignore_errors=")
                    ? "ignore_errors=no"
                    : bad.startsWith("pid=")
                        ? "pid=0"
                        : bad.startsWith("code=")
                            ? "code=(null)"
                            : bad.startsWith("status=") ? "status=0/0" : "start_time=[n/a]";
        altered.put(key, entry.replace(expectedPart, bad));
        assertThrows(IOException.class, () -> MorningCaddyReadiness.cold(altered), key + bad);
      }
    }
  }

  @Test
  void caddy192003ResetAuxiliaryEntriesCannotHideBadRetainedF18OrProfile() {
    for (var change :
        Map.ofEntries(
                Map.entry("ActiveState", "failed"),
                Map.entry("SubState", "running"),
                Map.entry("MainPID", "43"),
                Map.entry("Job", "123"),
                Map.entry("Result", "exit-code"),
                Map.entry("ExecMainCode", "0"),
                Map.entry("ExecMainStatus", "143"),
                Map.entry("ExecMainStartTimestampMonotonic", "0"),
                Map.entry("ExecMainExitTimestampMonotonic", "999999"),
                Map.entry("InvocationID", "0".repeat(32)),
                Map.entry("Id", "foreign.service"),
                Map.entry("User", "root"),
                Map.entry("NoNewPrivileges", "no"))
            .entrySet()) {
      var altered = normalHistory();
      altered.put("ExecStartPre", noHistory().get("ExecStartPre"));
      altered.put("ExecStart", noHistory().get("ExecStart"));
      altered.put(change.getKey(), change.getValue());
      assertThrows(IOException.class, () -> MorningCaddyReadiness.cold(altered), change.getKey());
    }
    var missing = normalHistory();
    missing.put("ExecStartPre", noHistory().get("ExecStartPre"));
    missing.put("ExecStart", noHistory().get("ExecStart"));
    missing.remove("ExecMainExitTimestampMonotonic");
    assertThrows(IOException.class, () -> MorningCaddyReadiness.cold(missing));
  }

  @Test
  void caddy180001ColdIsInitialOrNormalHistoryNotInvocationEmptyOnly() throws Exception {
    assertEquals("77777777777777777777777777777777", MorningCaddyReadiness.cold(normalHistory()));
    assertEquals("", MorningCaddyReadiness.cold(noHistory()));
    var legacy = normalHistory();
    legacy.replaceAll(
        (key, value) ->
            key.startsWith("ExecStart") ? value.replace("status=0 }", "status=0/0 }") : value);
    assertEquals("77777777777777777777777777777777", MorningCaddyReadiness.cold(legacy));
    var bound = normalHistory();
    bound.put("ExecMainStartTimestampMonotonic", "18446744073709551615");
    bound.put("ExecMainExitTimestampMonotonic", "18446744073709551615");
    assertEquals("77777777777777777777777777777777", MorningCaddyReadiness.cold(bound));
    var min = normalHistory();
    min.put("ExecStart", min.get("ExecStart").replace("pid=43", "pid=2"));
    assertEquals("77777777777777777777777777777777", MorningCaddyReadiness.cold(min));
    var max = normalHistory();
    max.put("ExecStart", max.get("ExecStart").replace("pid=43", "pid=2147483647"));
    assertEquals("77777777777777777777777777777777", MorningCaddyReadiness.cold(max));
  }

  @Test
  void caddy180002ColdRejectsAbnormalContradictoryUnknownAndMalformedHistory() {
    for (var change :
        Map.ofEntries(
                Map.entry("ActiveState", "active"),
                Map.entry("SubState", "running"),
                Map.entry("MainPID", "43"),
                Map.entry("Job", "123"),
                Map.entry("Result", "timeout"),
                Map.entry("ExecMainCode", "0"),
                Map.entry("ExecMainStatus", "143"),
                Map.entry("ExecMainStartTimestampMonotonic", "0"),
                Map.entry("ExecMainExitTimestampMonotonic", "999999"),
                Map.entry("InvocationID", "0".repeat(32)))
            .entrySet()) {
      var m = normalHistory();
      m.put(change.getKey(), change.getValue());
      assertThrows(IOException.class, () -> MorningCaddyReadiness.cold(m), change.getKey());
    }
    for (String field :
        List.of("ExecMainStartTimestampMonotonic", "ExecMainExitTimestampMonotonic"))
      for (String bad :
          List.of("-1", "01", "", "18446744073709551616", "184467440737095516150", "x")) {
        var m = normalHistory();
        m.put(field, bad);
        assertThrows(IOException.class, () -> MorningCaddyReadiness.cold(m));
      }
    for (String key : List.of("ExecStartPre", "ExecStart"))
      for (String bad :
          List.of(
              "status=1",
              "code=killed",
              "pid=1",
              "pid=2147483648",
              "stop_time=[n/a]",
              "start_time=[n/a]")) {
        var m = normalHistory();
        String old = m.get(key);
        String replaced =
            bad.startsWith("pid=")
                ? old.replace(key.equals("ExecStartPre") ? "pid=42" : "pid=43", bad)
                : bad.startsWith("start_time")
                    ? old.replace(
                        key.equals("ExecStartPre")
                            ? "start_time=[Sun 2026-10-04 19:00:00 JST]"
                            : "start_time=[Sun 2026-10-04 19:00:02 JST]",
                        bad)
                    : bad.startsWith("stop_time")
                        ? old.replace(
                            key.equals("ExecStartPre")
                                ? "stop_time=[Sun 2026-10-04 19:00:01 JST]"
                                : "stop_time=[Sun 2026-10-04 19:01:00 JST]",
                            bad)
                        : old.replace(bad.startsWith("status") ? "status=0" : "code=exited", bad);
        m.put(key, replaced);
        assertThrows(IOException.class, () -> MorningCaddyReadiness.cold(m), key + bad);
      }
    for (String key :
        List.of(
            "ExecMainCode",
            "ExecMainStartTimestampMonotonic",
            "ExecMainExitTimestampMonotonic",
            "ExecStartPre",
            "ExecStart")) {
      var m = noHistory();
      m.put(key, normalHistory().get(key));
      assertThrows(IOException.class, () -> MorningCaddyReadiness.cold(m), key);
    }
    var missing = normalHistory();
    missing.remove("Result");
    assertThrows(IOException.class, () -> MorningCaddyReadiness.cold(missing));
    var nullable = normalHistory();
    nullable.put("ExecMainStartTimestampMonotonic", null);
    assertThrows(IOException.class, () -> MorningCaddyReadiness.cold(nullable));
  }

  @Test
  void caddy180003NewReadyCannotReusePriorColdGeneration() throws Exception {
    var f = new Fixture();
    var fresh = new MorningCaddyReadiness(() -> {}, f, "88888888888888888888888888888888");
    assertTrue(fresh.ready());
    assertThrows(
        IOException.class,
        () ->
            new MorningCaddyReadiness(() -> {}, new Fixture(), "77777777777777777777777777777777"));
    for (String malformed : List.of("0".repeat(32), "x", "8".repeat(31), "8".repeat(33)))
      assertThrows(
          IOException.class, () -> new MorningCaddyReadiness(() -> {}, new Fixture(), malformed));
    assertThrows(
        NullPointerException.class, () -> new MorningCaddyReadiness(() -> {}, new Fixture(), null));
    for (var change :
        Map.of(
                "Result",
                "exit-code",
                "ExecMainCode",
                "1",
                "ExecMainStatus",
                "10",
                "ExecMainStartTimestampMonotonic",
                "0",
                "ExecMainExitTimestampMonotonic",
                "1")
            .entrySet()) {
      var mutated = new Fixture();
      mutated.manager.put(change.getKey(), change.getValue());
      assertThrows(IOException.class, () -> mutated.create(), change.getKey());
    }
  }

  static final class Fixture implements MorningCaddyReadiness.Io {
    Map<String, String> manager = values();
    ChildStartupContext.Observed actor = ACTOR;
    Set<String> before = Set.of("12345"), after = Set.of("12345");
    int status = 200, sockets, guards, failGuard, calls, failIo;
    final List<String> events = new ArrayList<>();

    void guard() throws IOException {
      events.add("guard");
      if (++guards == failGuard) throw new IOException("fixed fault");
    }

    void io() throws IOException {
      if (++calls == failIo) throw new IOException("fixed fault");
    }

    public Map<String, String> manager() throws IOException {
      io();
      events.add("manager");
      return manager;
    }

    public ChildStartupContext.Observed actor(String invocation) throws IOException {
      io();
      assertEquals(INV, invocation);
      events.add("actor");
      return actor;
    }

    public Set<String> sockets(long pid) throws IOException {
      io();
      assertEquals(43, pid);
      events.add("socket");
      return ++sockets == 1 ? before : after;
    }

    public int login() throws IOException {
      io();
      events.add("TLS-login");
      return status;
    }

    MorningCaddyReadiness create() throws IOException {
      return new MorningCaddyReadiness(this::guard, this);
    }
  }

  @Test
  void caddy457003ActualSystemdValidateZeroAndOnlyNormalZeroVariantsAccepted() throws Exception {
    for (String status : List.of("0", "0/0")) {
      var m = values();
      m.put("ExecStartPre", m.get("ExecStartPre").replace("status=0/0", "status=" + status));
      MorningCaddyReadiness.profile(m);
      var f = new Fixture();
      f.manager = m;
      assertTrue(f.create().ready());
    }
    for (String status :
        List.of("00", "1", "30", "0/1", "1/0", "0/00", "0/0/0", "0x0", "", "unexpected")) {
      var m = values();
      m.put("ExecStartPre", m.get("ExecStartPre").replace("status=0/0", "status=" + status));
      assertThrows(IOException.class, () -> MorningCaddyReadiness.profile(m), status);
    }
  }

  @Test
  void caddy455001TrueHttpsAndSameActorSocketOrder() throws Exception {
    var f = new Fixture();
    var observer = f.create();
    f.events.clear();
    assertTrue(observer.ready());
    assertEquals(
        List.of(
            "guard",
            "manager",
            "actor",
            "socket",
            "TLS-login",
            "guard",
            "actor",
            "manager",
            "socket",
            "guard"),
        f.events);
  }

  @Test
  void caddy455002AllFixedProfileFieldsMissingOrChangedReject() throws Exception {
    MorningCaddyReadiness.profile(values());
    for (String key : values().keySet()) {
      var missing = values();
      missing.remove(key);
      assertThrows(IOException.class, () -> MorningCaddyReadiness.profile(missing), key);
      var changed = values();
      changed.put(key, "unexpected");
      assertThrows(IOException.class, () -> MorningCaddyReadiness.profile(changed), key);
    }
    for (String pid : List.of("0", "1", "01", "2147483648", "9999999999", "-1")) {
      var m = values();
      m.put("MainPID", pid);
      assertThrows(IOException.class, () -> MorningCaddyReadiness.profile(m));
    }
    for (String inv : List.of("0".repeat(32), "A".repeat(32), "7".repeat(31))) {
      var m = values();
      m.put("InvocationID", inv);
      assertThrows(IOException.class, () -> MorningCaddyReadiness.profile(m));
    }
    for (String mutation :
        List.of("status=30/0", "ignore_errors=yes", "code=killed", "start_time=[n/a]")) {
      var m = values();
      String source = m.get("ExecStartPre");
      m.put(
          "ExecStartPre",
          mutation.startsWith("start_time")
              ? source.replace("start_time=[Sun 2026-10-04 19:00:00 JST]", mutation)
              : source.replace(
                  mutation.startsWith("status")
                      ? "status=0/0"
                      : mutation.startsWith("ignore") ? "ignore_errors=no" : "code=exited",
                  mutation));
      assertThrows(IOException.class, () -> MorningCaddyReadiness.profile(m));
    }
    assertThrows(NullPointerException.class, () -> MorningCaddyReadiness.profile(null));
  }

  @Test
  void caddy455003SocketOrHttpsFailureNeverReady() throws Exception {
    for (int status : List.of(301, 302, 403, 500, 503)) {
      var f = new Fixture();
      f.status = status;
      assertFalse(f.create().ready());
    }
    var f = new Fixture();
    f.before = Set.of();
    assertFalse(f.create().ready());
    assertFalse(f.events.contains("TLS-login"));
    f = new Fixture();
    f.after = Set.of("99999");
    assertFalse(f.create().ready());
    f = new Fixture();
    f.before = Set.of("12345", "88888");
    assertTrue(f.create().ready());
  }

  @Test
  void caddy455004EveryObservationGuardAndGenerationFailureRejects() throws Exception {
    for (int i = 1; i <= 5; i++) {
      var f = new Fixture();
      f.failGuard = i;
      assertThrows(IOException.class, () -> f.create().ready());
    }
    for (int i = 1; i <= 10; i++) {
      var f = new Fixture();
      f.failIo = i;
      assertThrows(IOException.class, () -> f.create().ready());
    }
    var f = new Fixture();
    var observer = f.create();
    f.manager = values();
    f.manager.put("InvocationID", "8".repeat(32));
    assertThrows(IOException.class, observer::ready);
    f = new Fixture();
    observer = f.create();
    f.actor =
        new ChildStartupContext.Observed(
            ACTOR.boot(), 43, 12346, 200, 201, List.of(201L), ACTOR.cgroup(), true, true);
    assertThrows(IOException.class, observer::ready);
    var wrong = new Fixture();
    wrong.actor =
        new ChildStartupContext.Observed(
            ACTOR.boot(), 44, 12345, 200, 201, List.of(201L), ACTOR.cgroup(), true, true);
    assertThrows(IOException.class, wrong::create);
    assertThrows(NullPointerException.class, () -> new MorningCaddyReadiness(null, new Fixture()));
    assertThrows(NullPointerException.class, () -> new MorningCaddyReadiness(() -> {}, null));
  }

  @Test
  void caddy455005IndependentProcAddressAndListenerVectors() {
    assertEquals("0100007F", MorningCaddyReadiness.kernelAddress(new byte[] {127, 0, 0, 1}));
    assertEquals(
        "0000000000000000FFFF00000100007F",
        MorningCaddyReadiness.kernelAddress(
            new byte[] {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, (byte) 255, (byte) 255, 127, 0, 0, 1}));
    assertThrows(
        IllegalArgumentException.class, () -> MorningCaddyReadiness.kernelAddress(new byte[5]));
    String row = "0: 0100007F:D778 00000000:0000 0A 0 0 0 0 0 12345\n";
    assertEquals(
        Set.of("12345"), MorningCaddyReadiness.listeners(row, Set.of("12345"), "0100007F", false));
    for (String bad :
        List.of(
            row.replace("0A", "01"),
            row.replace("12345", "0"),
            row.replace("D778", "D777"),
            row.replace("0100007F", "00000000"),
            ""))
      assertEquals(
          Set.of(), MorningCaddyReadiness.listeners(bad, Set.of("12345"), "0100007F", false));
    assertEquals(
        Set.of(), MorningCaddyReadiness.listeners(row, Set.of("99999"), "0100007F", false));
  }
}
