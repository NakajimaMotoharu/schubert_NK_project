package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.function.BiFunction;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** BTERM001..008; independent fixed Unit/placement and FD/metadata oracle, not root emulation. */
final class BackupUnitTerminationTest {
  private static final String FIXTURE_SCHUBERT_NK_BACKUP_SERVICE_3F43F5CD =
      "schubert-nk-backup.service";
  private static final String FIXTURE_MODE_B6D5C2C3 = "mode";
  private static final String FIXTURE_DEV_8A17302D = "dev";
  private static final String FIXTURE_INO_4BE7C1E0 = "ino";
  static final String UNIT =
      "Id=schubert-nk-backup.service\nLoadState=loaded\nActiveState=inactive\nSubState=dead\nJob=\nMainPID=0\nControlPID=0\nInvocationID=\nExecMainCode=0\nExecMainStatus=0\nExecMainStartTimestampMonotonic=0\nExecMainExitTimestampMonotonic=0\nResult=success\nType=oneshot\nRestart=no\nRemainAfterExit=yes\nKillMode=control-group\nSendSIGKILL=no\n";
  static final String PLACEMENT =
      "Id=schubert-nk-backup.service\nSlice=system.slice\nDelegate=no\nControlGroup=\n";
  static final List<String> ROLES =
      List.of(
          "root",
          "sys",
          "fs",
          "cgroup",
          "system.slice",
          FIXTURE_SCHUBERT_NK_BACKUP_SERVICE_3F43F5CD);
  @TempDir Path temporary;

  static InspectorUnitSnapshot state(String bytes) {
    return InspectorUnitSnapshot.parse(
        bytes.getBytes(StandardCharsets.US_ASCII), InspectorUnitSnapshot.Target.BACKUP);
  }

  static final class Fixture
      implements BackupUnitTermination.Observations, BackupUnitTermination.Io {
    final Map<Integer, String> owned = new LinkedHashMap<>();
    final List<String> events = new ArrayList<>();
    final List<byte[]> materials = new ArrayList<>();
    final Map<String, Throwable> namedFaults = new HashMap<>();
    int next = 10;
    int position;
    int faultPosition;
    int bus;
    int reads;
    int placements;
    int closes;
    long uid;
    boolean present;
    boolean busEmpty = true;
    boolean drift;
    boolean placementDrift;
    boolean inodeDrift;
    boolean invalidFd;
    boolean interrupt;
    boolean emptyManagerGroup;
    String unit = UNIT;
    String placement = PLACEMENT;
    String badFs = "";
    String badAclRole = "";
    String missingRole = "";
    Throwable fault = new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    BiFunction<String, Map<String, Object>, Map<String, Object>> change = (r, m) -> m;

    void event(String name) throws StorageIoException {
      events.add(name);
      position++;
      Throwable named = namedFaults.remove(name);
      if (named instanceof StorageIoException io) throw io;
      if (named instanceof RuntimeException runtime) throw runtime;
      if (named instanceof Error error) throw error;
      if (interrupt && position == faultPosition) Thread.currentThread().interrupt();
      if (!interrupt && position == faultPosition) {
        if (fault instanceof StorageIoException io) throw io;
        if (fault instanceof RuntimeException runtime) throw runtime;
        throw (Error) fault;
      }
    }

    DirectoryCalls calls() {
      return (DirectoryCalls)
          Proxy.newProxyInstance(
              DirectoryCalls.class.getClassLoader(),
              new Class<?>[] {DirectoryCalls.class},
              (p, method, args) -> {
                if (method.getName().equals("close")) {
                  int descriptor = (Integer) args[0];
                  String role = owned.remove(descriptor);
                  assertNotNull(role, "close once, only an acquired FD");
                  closes++;
                  event("close:" + role);
                  return null;
                }
                String role;
                if (method.getName().equals("openRoot")) role = "root";
                else if (method.getName().equals("openDirectory")) {
                  assertTrue(owned.containsKey((Integer) args[0]));
                  role = (String) args[1];
                } else throw new AssertionError("read-only namespace only");
                event("open:" + role);
                if (role.equals(missingRole)
                    || (role.equals(FIXTURE_SCHUBERT_NK_BACKUP_SERVICE_3F43F5CD) && !present))
                  throw new StorageIoException(StorageIoException.Reason.MISSING);
                if (invalidFd) return -1;
                int descriptor = next++;
                owned.put(descriptor, role);
                return descriptor;
              });
    }

    InodeSecurityCalls security() {
      return new InodeSecurityCalls() {
        public long effectiveUid() {
          return uid;
        }

        public boolean readOnlyFilesystem(Path p) {
          throw new AssertionError("no RW inference");
        }

        public byte[] accessAcl(Path p, int maximum) throws StorageIoException {
          assertEquals(44, maximum);
          String role = role(p);
          event("acl:" + role);
          return role.equals(badAclRole) ? new byte[] {1} : new byte[0];
        }
      };
    }

    String role(Path p) {
      String role = owned.get(Integer.parseInt(p.getFileName().toString()));
      return Objects.requireNonNull(role, "held FD only");
    }

    public Map<String, Object> attributes(Path p) throws IOException {
      String role = role(p);
      event("attributes:" + role);
      int i = ROLES.indexOf(role);
      Map<String, Object> m = new HashMap<>();
      m.put(FIXTURE_MODE_B6D5C2C3, (i == 1 || i == 3) ? 040555 : 040755);
      m.put("uid", 0);
      m.put("gid", 0);
      m.put("nlink", 3);
      m.put("size", 0L);
      m.put(FIXTURE_DEV_8A17302D, i == 0 ? 1L : i < 3 ? 2L : 3L);
      m.put(
          FIXTURE_INO_4BE7C1E0, (long) i + 10 + (inodeDrift && next > (present ? 16 : 15) ? 1 : 0));
      return change.apply(role, m);
    }

    public String filesystem(Path p) throws IOException {
      String role = role(p);
      event("filesystem:" + role);
      return badFs.isEmpty() ? ROLES.indexOf(role) < 3 ? "sysfs" : "cgroup2" : badFs;
    }

    public InspectorUnitSnapshot read() {
      reads++;
      return state(drift && reads > 1 ? unit.replace("Result=success", "Result=failed") : unit);
    }

    public byte[] placement() {
      placements++;
      // SSC100: present positive fixtures bind the manager query to the actual fixed leaf.
      String observed =
          present && !emptyManagerGroup && placement.equals(PLACEMENT)
              ? PLACEMENT.replace(
                  "ControlGroup=\n", "ControlGroup=/system.slice/schubert-nk-backup.service\n")
              : placement;
      byte[] b =
          (placementDrift && placements > 1 ? observed + "\n" : observed)
              .getBytes(StandardCharsets.US_ASCII);
      materials.add(b);
      return b;
    }

    public Optional<InspectorUnitSnapshot> quiescent() {
      bus++;
      return busEmpty ? Optional.of(state(unit)) : Optional.empty();
    }

    BackupUnitTermination adapter() {
      return new BackupUnitTermination(() -> event("context"), this, calls(), security(), this);
    }

    void released() {
      assertTrue(owned.isEmpty());
      for (byte[] material : materials) assertArrayEquals(new byte[material.length], material);
    }
  }

  static void rejected(Fixture f) {
    IOException e = assertThrows(IOException.class, () -> f.adapter().quiescent());
    assertEquals("backup termination unavailable", e.getMessage());
    assertNull(e.getCause());
    f.released();
  }

  @Test
  void bterm001ColdAndPresentStableNamespace() throws Exception {
    for (boolean present : List.of(false, true)) {
      var f = new Fixture();
      f.present = present;
      if (present)
        f.placement =
            PLACEMENT.replace(
                "ControlGroup=\n", "ControlGroup=/system.slice/schubert-nk-backup.service\n");
      assertTrue(f.adapter().quiescent().orElseThrow().matches(state(UNIT)));
      assertEquals(present ? 1 : 0, f.bus);
      assertEquals(present ? 12 : 10, f.closes);
      assertEquals(3, f.reads);
      assertEquals(3, f.placements);
      f.released();
      assertTrue(f.adapter().quiescent().isPresent());
      assertEquals(6, f.reads);
      f.released();
    }
  }

  @Test
  void bterm002EveryPlacementByteAndField() {
    List<String> invalid =
        new ArrayList<>(
            List.of(
                "",
                PLACEMENT + "\n",
                PLACEMENT + "x",
                PLACEMENT.replace("Delegate=no", "Delegate=n\u007f"),
                PLACEMENT.replace("\n", "\r\n"),
                PLACEMENT.replace("Id=", "=Id"),
                PLACEMENT.replace("Delegate=no", "Delegate=yes"),
                PLACEMENT.replace("system.slice", "other.slice"),
                PLACEMENT.replace(
                    "ControlGroup=\n", "ControlGroup=/other.slice/schubert-nk-backup.service\n"),
                PLACEMENT.replace("Id=schubert-nk-backup.service", "Id=other.service"),
                PLACEMENT.replace("Slice=system.slice", "Unknown=system.slice"),
                PLACEMENT.replace("Slice=system.slice", "Id=schubert-nk-backup.service"),
                PLACEMENT.replace("Delegate=no\n", ""),
                PLACEMENT + "x".repeat(1025),
                PLACEMENT.replace("Delegate=no", "Delegate=n\0")));
    for (String input : invalid) {
      var f = new Fixture();
      f.placement = input;
      rejected(f);
      assertEquals(0, f.closes);
    }
    var f = new Fixture();
    var nullPlacement =
        new BackupUnitTermination.Observations() {
          public InspectorUnitSnapshot read() {
            return state(UNIT);
          }

          public byte[] placement() {
            return null;
          }

          public Optional<InspectorUnitSnapshot> quiescent() {
            return Optional.empty();
          }
        };
    assertThrows(
        NullPointerException.class,
        () ->
            new BackupUnitTermination(() -> {}, nullPlacement, f.calls(), f.security(), f)
                .quiescent());
    f.released();
    for (int kind : List.of(0, 1)) {
      final int variant = kind;
      var bad = new Fixture();
      bad.present = true;
      var nullObservation =
          new BackupUnitTermination.Observations() {
            public InspectorUnitSnapshot read() {
              return variant == 0 ? null : state(UNIT);
            }

            public byte[] placement() {
              return bad.placement();
            }

            public Optional<InspectorUnitSnapshot> quiescent() {
              return null;
            }
          };
      assertThrows(
          NullPointerException.class,
          () ->
              new BackupUnitTermination(() -> {}, nullObservation, bad.calls(), bad.security(), bad)
                  .quiescent());
      bad.released();
    }
  }

  @Test
  void bterm003EveryMetadataAndFilesystemCondition() {
    for (String role : ROLES) {
      for (String key :
          List.of(
              FIXTURE_MODE_B6D5C2C3,
              "uid",
              "gid",
              "nlink",
              "size",
              FIXTURE_DEV_8A17302D,
              FIXTURE_INO_4BE7C1E0)) {
        for (int kind = 0; kind < 3; kind++) {
          var f = new Fixture();
          f.present = true;
          final int variant = kind;
          f.change =
              (r, m) -> {
                if (r.equals(role)) {
                  if (variant == 0) m.remove(key);
                  else if (variant == 1) m.put(key, null);
                  else m.put(key, "unknown");
                }
                return m;
              };
          rejected(f);
        }
      }
      for (var entry :
          Map.<String, Object>of(
                  FIXTURE_MODE_B6D5C2C3,
                  040777,
                  "uid",
                  1,
                  "gid",
                  1,
                  "nlink",
                  1,
                  "size",
                  -1L,
                  FIXTURE_DEV_8A17302D,
                  -1L,
                  FIXTURE_INO_4BE7C1E0,
                  0L)
              .entrySet()) {
        var f = new Fixture();
        f.present = true;
        f.change =
            (r, m) -> {
              if (r.equals(role)) m.put(entry.getKey(), entry.getValue());
              return m;
            };
        rejected(f);
      }
      var absent = new Fixture();
      absent.present = true;
      absent.change = (r, m) -> r.equals(role) ? null : m;
      rejected(absent);
      var acl = new Fixture();
      acl.present = true;
      acl.badAclRole = role;
      rejected(acl);
    }
    for (String role : List.of("fs", "system.slice", FIXTURE_SCHUBERT_NK_BACKUP_SERVICE_3F43F5CD)) {
      var f = new Fixture();
      f.present = true;
      f.change =
          (r, m) -> {
            if (r.equals(role)) m.put(FIXTURE_DEV_8A17302D, 20L);
            return m;
          };
      rejected(f);
    }
    for (String fs : List.of("ext4", "proc", "sysfs", "cgroup2")) {
      var f = new Fixture();
      f.badFs = fs;
      rejected(f);
    }
    var notRoot = new Fixture();
    notRoot.uid = 1;
    rejected(notRoot);
    assertEquals(0, notRoot.next - 10);
    var negative = new Fixture();
    negative.invalidFd = true;
    rejected(negative);
  }

  @Test
  void bterm004MissingOnlyAtExactLeafAndDriftRefused() throws Exception {
    for (String ancestor : ROLES.subList(0, 5)) {
      var f = new Fixture();
      f.missingRole = ancestor;
      rejected(f);
    }
    var baseline = new Fixture();
    baseline.present = true;
    baseline.adapter().quiescent();
    for (int i = 0; i < baseline.events.size(); i++) {
      if (!baseline.events.get(i).contains(FIXTURE_SCHUBERT_NK_BACKUP_SERVICE_3F43F5CD)) continue;
      for (var reason : StorageIoException.Reason.values()) {
        if (baseline.events.get(i).equals("open:schubert-nk-backup.service")
            && reason == StorageIoException.Reason.MISSING) continue;
        var f = new Fixture();
        f.present = true;
        f.faultPosition = i + 1;
        f.fault = new StorageIoException(reason);
        rejected(f);
      }
    }
    for (int kind = 0; kind < 3; kind++) {
      var f = new Fixture();
      f.drift = kind == 0;
      f.placementDrift = kind == 1;
      f.inodeDrift = kind == 2;
      rejected(f);
    }
    var busy = new Fixture();
    busy.unit = UNIT.replace("MainPID=0", "MainPID=3");
    assertTrue(busy.adapter().quiescent().isEmpty());
    assertEquals(0, busy.next - 10);
    var populated = new Fixture();
    populated.present = true;
    populated.busEmpty = false;
    assertTrue(populated.adapter().quiescent().isEmpty());
    populated.released();
    var mismatch = new Fixture();
    mismatch.present = true;
    var obs =
        new BackupUnitTermination.Observations() {
          public InspectorUnitSnapshot read() {
            return state(UNIT);
          }

          public byte[] placement() {
            return PLACEMENT
                .replace(
                    "ControlGroup=\n", "ControlGroup=/system.slice/schubert-nk-backup.service\n")
                .getBytes(StandardCharsets.US_ASCII);
          }

          public Optional<InspectorUnitSnapshot> quiescent() {
            return Optional.of(state(UNIT.replace("Result=success", "Result=failed")));
          }
        };
    assertTrue(
        new BackupUnitTermination(() -> {}, obs, mismatch.calls(), mismatch.security(), mismatch)
            .quiescent()
            .isEmpty());
    mismatch.released();
    // BUG308/YKT241: manager's empty query has no binding to a still-present kernel tree.
    var unbound = new Fixture();
    unbound.present = true;
    unbound.emptyManagerGroup = true;
    rejected(unbound);
    assertEquals(0, unbound.bus, "reject before querying a manager with no cgroup binding");
  }

  @Test
  void bterm005AllAcquisitionIoUnknownAndCloseCompounds() throws Exception {
    var baseline = new Fixture();
    baseline.present = true;
    baseline.adapter().quiescent();
    for (int i = 1; i <= baseline.position; i++) {
      for (Throwable fault :
          List.of(
              new StorageIoException(StorageIoException.Reason.UNAVAILABLE),
              new IllegalStateException("public unknown"),
              new AssertionError("public fatal"))) {
        var f = new Fixture();
        f.present = true;
        f.faultPosition = i;
        f.fault = fault;
        Throwable actual = assertThrows(Throwable.class, () -> f.adapter().quiescent());
        if (fault instanceof RuntimeException || fault instanceof Error) assertSame(fault, actual);
        else assertInstanceOf(IOException.class, actual);
        f.released();
      }
    }
    for (int kind = 0; kind < 4; kind++) {
      Throwable body =
          kind == 0
              ? new StorageIoException(StorageIoException.Reason.UNAVAILABLE)
              : kind == 1
                  ? new IllegalStateException("public primary")
                  : new AssertionError("public primary");
      Throwable cleanup = kind == 3 ? body : new IllegalArgumentException("public cleanup");
      var compound = new Fixture();
      compound.present = true;
      compound.namedFaults.put("attributes:system.slice", body);
      compound.namedFaults.put("close:root", cleanup);
      Throwable actual = assertThrows(Throwable.class, () -> compound.adapter().quiescent());
      assertSame(kind == 0 ? cleanup : body, actual);
      compound.released();
    }
    var f = new Fixture();
    assertThrows(
        NullPointerException.class,
        () -> new BackupUnitTermination(null, f, f.calls(), f.security(), f));
    assertThrows(
        NullPointerException.class,
        () -> new BackupUnitTermination(() -> {}, null, f.calls(), f.security(), f));
    assertThrows(
        NullPointerException.class,
        () -> new BackupUnitTermination(() -> {}, f, null, f.security(), f));
    assertThrows(
        NullPointerException.class,
        () -> new BackupUnitTermination(() -> {}, f, f.calls(), null, f));
    assertThrows(
        NullPointerException.class,
        () -> new BackupUnitTermination(() -> {}, f, f.calls(), f.security(), null));
  }

  @Test
  void bterm006InterruptAndIndependentParallelInstances() throws Exception {
    var baseline = new Fixture();
    baseline.adapter().quiescent();
    for (int i = 1; i <= baseline.position; i++) {
      var f = new Fixture();
      f.faultPosition = i;
      f.interrupt = true;
      try {
        rejected(f);
        assertTrue(Thread.currentThread().isInterrupted());
      } finally {
        Thread.interrupted();
      }
    }
    Thread.currentThread().interrupt();
    try {
      rejected(new Fixture());
    } finally {
      Thread.interrupted();
    }
    try (var pool = Executors.newFixedThreadPool(2)) {
      var tasks =
          List.<Callable<Boolean>>of(
              () -> {
                var f = new Fixture();
                var result = f.adapter().quiescent().isPresent();
                f.released();
                return result;
              },
              () -> {
                var f = new Fixture();
                f.present = true;
                var result = f.adapter().quiescent().isPresent();
                f.released();
                return result;
              });
      for (var future : pool.invokeAll(tasks)) assertTrue(future.get());
      var shared = new Fixture();
      var oneAdapter = shared.adapter();
      for (var future :
          pool.invokeAll(
              List.<Callable<Boolean>>of(
                  () -> oneAdapter.quiescent().isPresent(),
                  () -> oneAdapter.quiescent().isPresent()))) assertTrue(future.get());
      assertEquals(6, shared.reads);
      assertEquals(20, shared.closes);
      shared.released();
    }
  }

  @Test
  void bterm007FixedQueryProjectionAndNioPort() throws Exception {
    var stdout = new ByteArrayInputStream(PLACEMENT.getBytes(StandardCharsets.US_ASCII));
    var process =
        new Process() {
          public OutputStream getOutputStream() {
            return new ByteArrayOutputStream();
          }

          public InputStream getInputStream() {
            return stdout;
          }

          public InputStream getErrorStream() {
            return new ByteArrayInputStream(new byte[0]);
          }

          public int waitFor() {
            return 0;
          }

          public int exitValue() {
            return 0;
          }

          public void destroy() {
            fail("already terminal");
          }

          public boolean isAlive() {
            return false;
          }

          public boolean waitFor(long time, TimeUnit unit) {
            assertEquals(5, time);
            assertEquals(TimeUnit.SECONDS, unit);
            return true;
          }
        };
    var reader =
        new InspectorUnitProbe.NativeReader(
            command -> {
              assertEquals(
                  List.of(
                      "/usr/bin/systemctl",
                      "--system",
                      "--no-pager",
                      "--no-ask-password",
                      "show",
                      "--property=Id,Slice,Delegate,ControlGroup",
                      FIXTURE_SCHUBERT_NK_BACKUP_SERVICE_3F43F5CD),
                  command);
              return process;
            });
    var probe =
        new InspectorUnitProbe(
            new InspectorUnitProbe.Reader() {
              public byte[] readState() {
                return UNIT.getBytes(StandardCharsets.US_ASCII);
              }

              public byte[] readProcesses() {
                return "a(sus) 0\n".getBytes(StandardCharsets.US_ASCII);
              }
            },
            InspectorUnitSnapshot.Target.BACKUP);
    var nativeObservations = new BackupUnitTermination.NativeObservations(reader, probe);
    assertArrayEquals(
        PLACEMENT.getBytes(StandardCharsets.US_ASCII), nativeObservations.placement());
    assertTrue(nativeObservations.read().matches(state(UNIT)));
    assertTrue(nativeObservations.quiescent().orElseThrow().matches(state(UNIT)));
    assertThrows(
        NullPointerException.class,
        () -> new BackupUnitTermination.NativeObservations(reader, null));
    assertThrows(
        NullPointerException.class, () -> new BackupUnitTermination.NativeObservations(null));
    var io = new BackupUnitTermination.NioIo();
    var metadata = io.attributes(temporary);
    assertEquals(0, ((Integer) metadata.get(FIXTURE_MODE_B6D5C2C3)) & 0170000 ^ 040000);
    assertTrue(((Long) metadata.get(FIXTURE_INO_4BE7C1E0)) > 0);
    assertFalse(io.filesystem(temporary).isEmpty());
  }

  @Test
  void bterm008MorningContextAndNativeFactoryFailClosed() throws Exception {
    assertEquals(
        "schubert-nk-morning-controller.service", RootStartupContext.Service.MORNING.unit());
    var f = new RootStartupContextTest.Fixture();
    f.group = "0::/system.slice/schubert-nk-morning-controller.service\n";
    f.unit = RootStartupContextTest.unit(RootStartupContext.Service.MORNING);
    var context = f.context();
    var expected = context.capture(RootStartupContext.Service.MORNING);
    assertEquals(RootStartupContext.Service.MORNING, expected.service());
    context.recheck(expected);
    assertThrows(NullPointerException.class, () -> BackupUnitTermination.create(null, expected));
    assertThrows(NullPointerException.class, () -> BackupUnitTermination.create(context, null));
    var wrong =
        new RootStartupContext.Snapshot(
            RootStartupContext.Service.API,
            expected.boot(),
            expected.invocation(),
            expected.pid(),
            expected.startTicks(),
            expected.initStartTicks(),
            expected.controlGroup());
    assertThrows(IOException.class, () -> BackupUnitTermination.create(context, wrong));
    // Context validated by injected literal only; actual host UID gate remains fail closed.
    var nativeAdapter = BackupUnitTermination.create(context, expected);
    if (LinuxInodeSecurity.create().effectiveUid() != 0)
      assertThrows(IOException.class, nativeAdapter::quiescent);
  }
}
