package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.storage.LinuxStartupAdmission;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import org.junit.jupiter.api.Test;

/** PT-OPS-CHILDCTX-001..008: independent public proof and Linux text vectors. */
final class ChildStartupContextTest {
  private static final String FIXTURE_128_6F7E5D9F = "128";
  private static final String FIXTURE_INVOCATION_ID_AC3E1A2D = "INVOCATION_ID";
  private static final String FIXTURE_PROC_1E4EC60E = "proc";
  static final String BOOT = "11111111-1111-1111-1111-111111111111";
  static final String INV = "11111111111111111111111111111111";
  static final String A = "SCHUBERT_NK_STARTUP_ADMISSION_FD";
  static final String P = "SCHUBERT_NK_STARTUP_PROOF_FD";

  static byte[] bytes(String value) {
    return value.getBytes(StandardCharsets.US_ASCII);
  }

  static final String GOLDEN =
      """
      NKSTART1
      service=API
      boot_id=11111111-1111-1111-1111-111111111111
      invocation_id=11111111111111111111111111111111
      pid=42
      start_ticks=12345
      admission_fd=128
      admission_device=123
      admission_inode=456
      service_uid=200
      service_gid=201
      service_groups=200,201,202
      permit_epoch=33333333-3333-3333-3333-333333333333
      permit_sha256=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
      release_sha256=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
      config_sha256=cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
      roots_sha256=dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd
      broker_invocation_id=22222222222222222222222222222222
      """;
  static final String STATUS =
      """
      Name:\tpublic-child
      Uid:\t200\t200\t200\t200
      Gid:\t201\t201\t201\t201
      Groups:\t202 200 201
      CapInh:\t0000000000000000
      CapPrm:\t0000000000000000
      CapEff:\t0000000000000000
      CapBnd:\t0000000000000000
      CapAmb:\t0000000000000000
      NoNewPrivs:\t1
      """;

  static Map<String, String> environment() {
    return new HashMap<>(
        Map.of(A, FIXTURE_128_6F7E5D9F, P, "129", FIXTURE_INVOCATION_ID_AC3E1A2D, INV));
  }

  static final class Fixture implements ChildStartupContext.Io {
    long pid = 42;
    long uid = 200;
    String filesystem = FIXTURE_PROC_1E4EC60E;
    String boot = BOOT + "\n";
    String stat = "42 (comm (with) spaces) S " + "0 ".repeat(18) + "12345\n";
    String status = STATUS;
    String cgroup = "0::/system.slice/schubert-nk-api.service\n";

    public long pid() {
      return pid;
    }

    public long uid() {
      return uid;
    }

    public String filesystem() {
      return filesystem;
    }

    public byte[] boot() {
      return bytes(boot);
    }

    public byte[] stat(long p) {
      assertEquals(pid, p);
      return bytes(stat);
    }

    public byte[] status(long p) {
      assertEquals(pid, p);
      return bytes(status);
    }

    public byte[] cgroup(long p) {
      assertEquals(pid, p);
      return bytes(cgroup);
    }

    ChildStartupContext subject() {
      return new ChildStartupContext(this);
    }
  }

  static ChildStartupContext.Observed own() {
    return new ChildStartupContext.Observed(
        BOOT,
        42,
        12345,
        200,
        201,
        List.of(200L, 201L, 202L),
        "0::/system.slice/schubert-nk-api.service\n",
        true,
        true);
  }

  static void verify(String proof, ChildStartupContext.Observed observation) throws IOException {
    ChildStartupContext.verify(
        ServiceConfigFiles.Service.API,
        ChildStartupContext.inputs(environment()),
        StartupProofFrame.parse(bytes(proof)),
        new LinuxStartupAdmission.Identity(128, 123, 456),
        observation,
        new FixedServiceIdentity.Value(200, 201, List.of(200L, 201L, 202L)),
        "c".repeat(64),
        "b".repeat(64));
  }

  static void rejected(Fixture fixture) {
    var e = assertThrows(IOException.class, () -> fixture.subject().capture());
    assertEquals("child startup context unavailable", e.getMessage());
    assertNull(e.getCause());
  }

  @Test
  void childctx009MissingUnitObserversNeverReturnOwnershipData() throws Exception {
    // SS343: absent fixed observers must not mint Morning/Cleanup/Inspector/Broker evidence.
    var io = new Fixture();
    for (var parent : ChildStartupContext.MaintenanceParent.values()) {
      var error = assertThrows(IOException.class, () -> io.maintenanceUnit(parent));
      assertEquals("child startup context unavailable", error.getMessage());
      assertNull(error.getCause());
    }
    var inspector = assertThrows(IOException.class, io::inspectorUnit);
    var broker = assertThrows(IOException.class, io::brokerUnit);
    var caddy = assertThrows(IOException.class, io::caddyUnit);
    for (var error : List.of(inspector, broker, caddy)) {
      assertEquals("child startup context unavailable", error.getMessage());
      assertNull(error.getCause());
    }
    // Refused unit observers neither alter the self-capture fixture nor produce parent-unit data.
    assertEquals(own(), io.subject().capture());
  }

  @Test
  void childctx001IndependentGoldenBindingsAndBothUnits() throws Exception {
    assertEquals(own(), new Fixture().subject().capture());
    verify(GOLDEN, own());
    assertEquals(
        "ChildStartupContext.Inputs[REDACTED]",
        ChildStartupContext.inputs(environment()).toString());
    assertEquals("ChildStartupContext.Observed[REDACTED]", own().toString());
    var web =
        new ChildStartupContext.Observed(
            BOOT,
            42,
            12345,
            200,
            201,
            List.of(200L, 201L, 202L),
            "0::/system.slice/schubert-nk-web.service\n",
            true,
            true);
    ChildStartupContext.verify(
        ServiceConfigFiles.Service.WEB,
        ChildStartupContext.inputs(environment()),
        StartupProofFrame.parse(bytes(GOLDEN.replace("service=API", "service=WEB"))),
        new LinuxStartupAdmission.Identity(128, 123, 456),
        web,
        new FixedServiceIdentity.Value(200, 201, List.of(200L, 201L, 202L)),
        "c".repeat(64),
        "b".repeat(64));
    var unsigned =
        GOLDEN
            .replace("admission_device=123", "admission_device=18446744073709551615")
            .replace("admission_inode=456", "admission_inode=18446744073709551615");
    ChildStartupContext.verify(
        ServiceConfigFiles.Service.API,
        ChildStartupContext.inputs(environment()),
        StartupProofFrame.parse(bytes(unsigned)),
        new LinuxStartupAdmission.Identity(128, -1, -1),
        own(),
        new FixedServiceIdentity.Value(200, 201, List.of(200L, 201L, 202L)),
        "c".repeat(64),
        "b".repeat(64));
  }

  @Test
  void childctx002EnvironmentMissingAliasNullAndDescriptorBounds() throws Exception {
    for (String key : List.of(A, P, FIXTURE_INVOCATION_ID_AC3E1A2D)) {
      var env = environment();
      env.remove(key);
      assertThrows(IOException.class, () -> ChildStartupContext.inputs(env));
    }
    for (String key : List.of(A, P))
      for (String bad :
          List.of("", "127", "65536", "0128", "-128", "128\n", "999999", "0", "abc")) {
        var env = environment();
        env.put(key, bad);
        assertThrows(IOException.class, () -> ChildStartupContext.inputs(env));
      }
    for (String key : List.of("schubert_nk_startup_admission_fd", "SCHUBERT_NK_STARTUP_OTHER")) {
      var env = environment();
      env.put(key, FIXTURE_128_6F7E5D9F);
      assertThrows(IOException.class, () -> ChildStartupContext.inputs(env));
    }
    for (String bad : List.of("0".repeat(32), "A".repeat(32), "1".repeat(31), INV + "\n")) {
      var env = environment();
      env.put(FIXTURE_INVOCATION_ID_AC3E1A2D, bad);
      assertThrows(IOException.class, () -> ChildStartupContext.inputs(env));
    }
    var same = environment();
    same.put(P, FIXTURE_128_6F7E5D9F);
    assertThrows(IOException.class, () -> ChildStartupContext.inputs(same));
    var edge = environment();
    edge.put(P, "65535");
    assertEquals(65535, ChildStartupContext.inputs(edge).proofFd());
    assertThrows(NullPointerException.class, () -> ChildStartupContext.inputs(null));
    for (String key : List.of(A, P, FIXTURE_INVOCATION_ID_AC3E1A2D)) {
      var env = environment();
      env.put(key, null);
      assertThrows(NullPointerException.class, () -> ChildStartupContext.inputs(env));
    }
    var nullKey = environment();
    nullKey.put(null, FIXTURE_128_6F7E5D9F);
    assertThrows(NullPointerException.class, () -> ChildStartupContext.inputs(nullKey));
    assertThrows(NullPointerException.class, () -> new ChildStartupContext.Inputs(128, 129, null));
  }

  @Test
  void childctx003EveryAttestedFieldAndNativeIdentityMismatch() {
    for (var pair :
        List.of(
            new String[] {"service=API", "service=WEB"},
            new String[] {"admission_fd=128", "admission_fd=130"},
            new String[] {"admission_device=123", "admission_device=124"},
            new String[] {"admission_inode=456", "admission_inode=457"},
            new String[] {"boot_id=" + BOOT, "boot_id=22222222-2222-2222-2222-222222222222"},
            new String[] {"invocation_id=" + INV, "invocation_id=" + "2".repeat(32)},
            new String[] {"pid=42", "pid=43"},
            new String[] {"start_ticks=12345", "start_ticks=12346"},
            new String[] {"service_uid=200", "service_uid=203"},
            new String[] {"service_gid=201", "service_gid=203"},
            new String[] {"service_groups=200,201,202", "service_groups=200,201,203"},
            new String[] {"config_sha256=" + "c".repeat(64), "config_sha256=" + "e".repeat(64)},
            new String[] {"release_sha256=" + "b".repeat(64), "release_sha256=" + "e".repeat(64)}))
      assertThrows(IOException.class, () -> verify(GOLDEN.replace(pair[0], pair[1]), own()));
    for (var o :
        List.of(
            new ChildStartupContext.Observed(
                BOOT, 42, 12345, 203, 201, own().groups(), own().cgroup(), true, true),
            new ChildStartupContext.Observed(
                BOOT, 42, 12345, 200, 203, own().groups(), own().cgroup(), true, true),
            new ChildStartupContext.Observed(
                BOOT, 42, 12345, 200, 201, List.of(200L, 201L), own().cgroup(), true, true),
            new ChildStartupContext.Observed(
                BOOT, 42, 12345, 200, 201, own().groups(), "other", true, true),
            new ChildStartupContext.Observed(
                BOOT, 42, 12345, 200, 201, own().groups(), own().cgroup(), false, true),
            new ChildStartupContext.Observed(
                BOOT, 42, 12345, 200, 201, own().groups(), own().cgroup(), true, false)))
      assertThrows(IOException.class, () -> verify(GOLDEN, o));
    assertThrows(
        IOException.class,
        () ->
            ChildStartupContext.verify(
                ServiceConfigFiles.Service.API,
                ChildStartupContext.inputs(environment()),
                StartupProofFrame.parse(bytes(GOLDEN)),
                new LinuxStartupAdmission.Identity(130, 123, 456),
                own(),
                new FixedServiceIdentity.Value(200, 201, own().groups()),
                "c".repeat(64),
                "b".repeat(64)));
  }

  @Test
  void childctx004KernelBoundariesCapabilitiesAndImmutableSnapshots() throws Exception {
    var f = new Fixture();
    f.stat = f.stat.replace("12345", "9223372036854775807");
    assertEquals(Long.MAX_VALUE, f.subject().capture().startTicks());
    f.stat = f.stat.replace("9223372036854775807", "1");
    assertEquals(1, f.subject().capture().startTicks());
    for (String cap : List.of("CapInh", "CapPrm", "CapEff", "CapBnd", "CapAmb")) {
      var nonzero = new Fixture();
      nonzero.status = STATUS.replace(cap + ":\t0000000000000000", cap + ":\t0000000000000001");
      assertFalse(nonzero.subject().capture().zeroCapabilities());
    }
    var nnp = new Fixture();
    nnp.status = STATUS.replace("NoNewPrivs:\t1", "NoNewPrivs:\t0");
    assertFalse(nnp.subject().capture().noNewPrivileges());
    var groups = new ArrayList<>(List.of(200L, 201L, 202L));
    var o =
        new ChildStartupContext.Observed(
            BOOT, 42, 12345, 200, 201, groups, own().cgroup(), true, true);
    groups.clear();
    assertEquals(List.of(200L, 201L, 202L), o.groups());
    assertThrows(UnsupportedOperationException.class, () -> o.groups().clear());
  }

  @Test
  void childctx005MalformedKernelStatBootPidAndByteInputs() {
    for (long p : List.of(0L, 1L, 2147483648L)) {
      var f = new Fixture();
      f.pid = p;
      rejected(f);
    }
    var fs = new Fixture();
    fs.filesystem = "tmpfs";
    rejected(fs);
    for (String bad :
        List.of(
            "",
            BOOT,
            BOOT + "\n\n",
            "00000000-0000-0000-0000-000000000000\n",
            BOOT.toUpperCase(Locale.ROOT).replace('1', 'A') + "\n",
            "x".repeat(38))) {
      var f = new Fixture();
      f.boot = bad;
      rejected(f);
    }
    for (String bad :
        List.of(
            "",
            "43 (comm) S " + "0 ".repeat(18) + "12345\n",
            "42 (missing delimiter\n",
            "42 (comm) Z " + "0 ".repeat(18) + "12345\n",
            "42 (comm) S 1\n",
            "42 (comm) S " + "0 ".repeat(18) + "0\n",
            "42 (comm) S " + "0 ".repeat(18) + "9223372036854775808\n",
            "42 (comm) S " + "0 ".repeat(18) + "01\n",
            "x".repeat(4097))) {
      var f = new Fixture();
      f.stat = bad;
      rejected(f);
    }
    var noLf = new Fixture();
    noLf.stat = noLf.stat.trim();
    rejected(noLf);
    for (String bad : List.of("", "\u0000", "\r", "\u007f", "x".repeat(4097))) {
      var f = new Fixture();
      f.cgroup = bad;
      rejected(f);
    }
    var uid = new Fixture();
    uid.uid = 203;
    rejected(uid);
  }

  @Test
  void childctx006EveryStatusMissingDuplicateBoundsAndMalformedValue() {
    for (String row : STATUS.stripTrailing().split("\n")) {
      var f = new Fixture();
      f.status = STATUS.replace(row + "\n", "");
      if (!row.startsWith("Name:")) rejected(f);
      var duplicate = new Fixture();
      duplicate.status = STATUS + row + "\n";
      rejected(duplicate);
    }
    for (String bad :
        List.of("", STATUS.trim(), "bad\n", ":empty-key\n", STATUS + "\n", "x".repeat(65537))) {
      var f = new Fixture();
      f.status = bad;
      rejected(f);
    }
    for (String key : List.of("Uid", "Gid"))
      for (String value :
          List.of(
              "200 200 200",
              "0 0 0 0",
              "200 200 200 201",
              "01 01 01 01",
              "4294967295 4294967295 4294967295 4294967295")) {
        var f = new Fixture();
        String row = key.equals("Uid") ? "200\t200\t200\t200" : "201\t201\t201\t201";
        f.status = STATUS.replace(key + ":\t" + row, key + ":\t" + value);
        rejected(f);
      }
    for (String bad :
        List.of(
            "",
            "200 200",
            "0",
            "4294967295",
            "01",
            String.join(
                " ",
                java.util.stream.IntStream.rangeClosed(1, 17)
                    .mapToObj(Integer::toString)
                    .toList()))) {
      var f = new Fixture();
      f.status = STATUS.replace("202 200 201", bad);
      rejected(f);
    }
    for (String bad : List.of("0", "G".repeat(16), "0".repeat(17))) {
      var f = new Fixture();
      f.status = STATUS.replace("CapInh:\t0000000000000000", "CapInh:\t" + bad);
      rejected(f);
    }
    var nnp = new Fixture();
    nnp.status = STATUS.replace("NoNewPrivs:\t1", "NoNewPrivs:\t2");
    rejected(nnp);
  }

  @Test
  void childctx007NullUnknownFailureAndConcurrency() throws Exception {
    assertThrows(NullPointerException.class, () -> new ChildStartupContext(null));
    assertThrows(
        NullPointerException.class,
        () -> new ChildStartupContext.Observed(null, 42, 1, 200, 201, List.of(), "x", true, true));
    assertThrows(
        NullPointerException.class,
        () -> new ChildStartupContext.Observed(BOOT, 42, 1, 200, 201, null, "x", true, true));
    assertThrows(
        NullPointerException.class,
        () -> new ChildStartupContext.Observed(BOOT, 42, 1, 200, 201, List.of(), null, true, true));
    var unknown = new AssertionError("identity preserved");
    var io =
        new ChildStartupContext.Io() {
          public long pid() {
            throw unknown;
          }

          public long uid() {
            return 200;
          }

          public String filesystem() {
            return FIXTURE_PROC_1E4EC60E;
          }

          public byte[] boot() {
            return null;
          }

          public byte[] stat(long p) {
            return null;
          }

          public byte[] status(long p) {
            return null;
          }

          public byte[] cgroup(long p) {
            return null;
          }
        };
    assertSame(
        unknown, assertThrows(AssertionError.class, () -> new ChildStartupContext(io).capture()));
    var nullBytes =
        new ChildStartupContext.Io() {
          public long pid() {
            return 42;
          }

          public long uid() {
            return 200;
          }

          public String filesystem() {
            return FIXTURE_PROC_1E4EC60E;
          }

          public byte[] boot() {
            return null;
          }

          public byte[] stat(long p) {
            return null;
          }

          public byte[] status(long p) {
            return null;
          }

          public byte[] cgroup(long p) {
            return null;
          }
        };
    assertThrows(NullPointerException.class, () -> new ChildStartupContext(nullBytes).capture());
    try (var pool = Executors.newFixedThreadPool(4)) {
      var futures = new ArrayList<Future<ChildStartupContext.Observed>>();
      for (int i = 0; i < 32; i++)
        futures.add(pool.submit(() -> new Fixture().subject().capture()));
      for (var future : futures) assertEquals(own(), future.get());
    }
    var args =
        new Object[] {
          ServiceConfigFiles.Service.API,
          ChildStartupContext.inputs(environment()),
          StartupProofFrame.parse(bytes(GOLDEN)),
          new LinuxStartupAdmission.Identity(128, 123, 456),
          own(),
          new FixedServiceIdentity.Value(200, 201, own().groups()),
          "c".repeat(64),
          "b".repeat(64)
        };
    for (int i = 0; i < 8; i++) {
      var copy = args.clone();
      copy[i] = null;
      assertThrows(
          NullPointerException.class,
          () ->
              ChildStartupContext.verify(
                  (ServiceConfigFiles.Service) copy[0],
                  (ChildStartupContext.Inputs) copy[1],
                  (StartupProofFrame) copy[2],
                  (LinuxStartupAdmission.Identity) copy[3],
                  (ChildStartupContext.Observed) copy[4],
                  (FixedServiceIdentity.Value) copy[5],
                  (String) copy[6],
                  (String) copy[7]));
    }
  }

  @Test
  void childctx008NativeProcOnlyDoesNotGrantAuthority() throws Exception {
    var nativeIo = new ChildStartupContext.NativeIo();
    assertEquals(ProcessHandle.current().pid(), nativeIo.pid());
    assertEquals(FIXTURE_PROC_1E4EC60E, nativeIo.filesystem());
    assertEquals(37, nativeIo.boot().length);
    assertTrue(nativeIo.stat(nativeIo.pid()).length > 0);
    assertTrue(nativeIo.status(nativeIo.pid()).length > 0);
    assertTrue(nativeIo.cgroup(nativeIo.pid()).length > 0);
    var observed = new ChildStartupContext().capture();
    assertEquals(ProcessHandle.current().pid(), observed.pid());
    assertEquals(nativeIo.uid(), observed.uid());
    assertThrows(IOException.class, () -> verify(GOLDEN, observed));
    assertThrows(IOException.class, () -> nativeIo.stat(Long.MAX_VALUE));
  }
}
