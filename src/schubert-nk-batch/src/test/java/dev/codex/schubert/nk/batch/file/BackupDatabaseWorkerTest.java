package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.platform.InspectorUnitSnapshot;
import dev.codex.schubert.nk.bootstrap.ChildStartupContext;
import dev.codex.schubert.nk.bootstrap.FixedServiceIdentity;
import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.function.BiConsumer;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** BWORK001..008/NK-OPS-001/BAK/BKO/UI251/SS3416.1/343/SSC092/BUG274. Public bytes only. */
final class BackupDatabaseWorkerTest {
  @TempDir Path temporary;
  static final String REQUEST =
      "NKBACKUP1\nrun=11111111-2222-4333-8444-555555555555\nstarted=2026-09-27T15:00:00Z\n";
  static final String DIRECTORY = "20260928-000000-11111111-2222-4333-8444-555555555555.part";
  static final String INVOCATION = "123456789abcdef08123456789abcdef";
  static final String UNIT =
      "Id=schubert-nk-backup.service\nLoadState=loaded\nActiveState=activating\nSubState=start\nJob=\nMainPID=123\nControlPID=0\nInvocationID="
          + INVOCATION
          + "\nExecMainCode=1\nExecMainStatus=0\nExecMainStartTimestampMonotonic=1234567\nExecMainExitTimestampMonotonic=0\nResult=success\nType=oneshot\nRestart=no\nRemainAfterExit=yes\nKillMode=control-group\nSendSIGKILL=no\n";
  static final FixedServiceIdentity.Value FIXED =
      new FixedServiceIdentity.Value(992, 977, List.of(977L, 986L));

  static ChildStartupContext.Observed self(
      long uid, long gid, List<Long> groups, boolean caps, boolean nnp, String cgroup) {
    return new ChildStartupContext.Observed(
        "11111111-2222-4333-8444-555555555555", 123, 100, uid, gid, groups, cgroup, caps, nnp);
  }

  static ChildStartupContext.Observed SELF =
      self(
          992,
          977,
          List.of(977L, 986L),
          true,
          true,
          "0::/system.slice/schubert-nk-backup.service\n");

  static byte[] pgpass() {
    return "127.0.0.1:5432:schubert_nk:schubert_backup:PUBLIC_FIXTURE\n"
        .getBytes(StandardCharsets.US_ASCII);
  }

  final class Fixture
      implements BackupDatabaseWorker.Ports,
          InspectorEnvironmentPublisher.Io,
          InodeSecurityCalls,
          AutoCloseable {
    final Path ram;
    final Path backup;
    final Path credentials;
    final Set<Integer> fds = new HashSet<>();
    final Map<String, Integer> counts = new HashMap<>();
    final Map<String, Throwable> failures = new HashMap<>();
    final InspectorEnvironmentPublisher.NioIo nio = new InspectorEnvironmentPublisher.NioIo();
    String requestText = REQUEST;
    final DirectoryCalls calls;
    FixedServiceIdentity.Value identity = FIXED;
    ChildStartupContext.Observed own = SELF;
    String state = UNIT;
    String invocation = INVOCATION;
    String filesystem = "tmpfs";
    String nullPort = "";
    byte[] raw;
    byte[] request;
    byte[] acl = new byte[0];
    boolean readonly;
    boolean emptyDump;
    boolean replaceDump;
    BiConsumer<Path, Map<String, Object>> metadata = (p, m) -> {};
    BiConsumer<String, Integer> hook = (n, k) -> {};

    Fixture() throws Exception {
      ram = privateDirectory("runtime-");
      backup = privateDirectory("backup-");
      credentials = privateDirectory("credentials-");
      var nativeCalls = LinuxDirectoryCalls.create();
      calls =
          (DirectoryCalls)
              Proxy.newProxyInstance(
                  getClass().getClassLoader(),
                  new Class<?>[] {DirectoryCalls.class},
                  (proxy, method, args) -> {
                    String name = method.getName();
                    Object result;
                    if (!name.equals("close")) point(name);
                    try {
                      result = method.invoke(nativeCalls, args);
                    } catch (InvocationTargetException e) {
                      throw e.getCause();
                    }
                    if (name.equals("close")) {
                      fds.remove((Integer) args[0]);
                      point(name);
                    } else if (Set.of("openRoot", "openDirectory", "openEntry", "createPrivateFile")
                        .contains(name)) fds.add((Integer) result);
                    return result;
                  });
    }

    Path privateDirectory(String prefix) throws IOException {
      Path p = Files.createTempDirectory(temporary, prefix);
      Files.setPosixFilePermissions(p, PosixFilePermissions.fromString("rwx------"));
      return p;
    }

    void point(String name) throws IOException {
      int n = counts.merge(name, 1, Integer::sum);
      hook.accept(name, n);
      Throwable t = failures.getOrDefault(name + "#" + n, failures.get(name));
      if (t instanceof IOException e) throw e;
      if (t instanceof RuntimeException e) throw e;
      if (t instanceof Error e) throw e;
    }

    public FixedServiceIdentity.Value identity() throws IOException {
      point("identity");
      return nullPort.equals("identity") ? null : identity;
    }

    public ChildStartupContext.Observed self() throws IOException {
      point("self");
      return nullPort.equals("self") ? null : own;
    }

    public InspectorUnitSnapshot unit() {
      return nullPort.equals("unit")
          ? null
          : InspectorUnitSnapshot.parse(
              state.getBytes(StandardCharsets.US_ASCII), InspectorUnitSnapshot.Target.BACKUP);
    }

    public String invocation() {
      return nullPort.equals("invocation") ? null : invocation;
    }

    public OwnedTransferDirectory credentials() throws IOException {
      point("credentials");
      return nullPort.equals("credentials")
          ? null
          : OwnedTransferDirectory.open(calls, credentials);
    }

    public OwnedTransferDirectory runtime() throws IOException {
      point("runtime");
      return nullPort.equals("runtime") ? null : OwnedTransferDirectory.open(calls, ram);
    }

    public OwnedTransferDirectory backup() throws IOException {
      point("backup");
      return nullPort.equals("backup") ? null : OwnedTransferDirectory.open(calls, backup);
    }

    public byte[] request(OwnedTransferDirectory root) throws IOException {
      point("request");
      if (nullPort.equals("request")) return null;
      request = requestText.getBytes(StandardCharsets.US_ASCII);
      return request;
    }

    public byte[] pgpass(OwnedTransferDirectory root) throws IOException {
      point("pgpass");
      if (nullPort.equals("pgpass")) return null;
      raw = BackupDatabaseWorkerTest.pgpass();
      return raw;
    }

    public void dump(Path output, Path pass, long uid) throws IOException {
      point("dump");
      assertEquals(992, uid);
      assertArrayEquals(BackupDatabaseWorkerTest.pgpass(), Files.readAllBytes(pass));
      assertArrayEquals(new byte[raw.length], raw);
      assertEquals(
          PosixFilePermissions.fromString("rw-------"), Files.getPosixFilePermissions(output));
      if (!emptyDump) Files.writeString(output, "PUBLIC DATABASE DUMP FIXTURE\n");
      if (replaceDump) {
        Path name = backup.resolve(DIRECTORY).resolve("schubert_nk.dump");
        Files.move(name, name.resolveSibling("kept-original"));
        Files.writeString(name, "PUBLIC replacement\n");
        Files.setPosixFilePermissions(name, PosixFilePermissions.fromString("rw-------"));
      }
    }

    public void verifyDump(Path output, long uid) throws IOException {
      point("verifyDump");
      assertEquals(992, uid);
      assertEquals("abc", Files.readString(output));
      if (replaceDump) {
        Path name =
            backup
                .resolve(DIRECTORY.substring(0, DIRECTORY.length() - 5))
                .resolve("schubert_nk.dump");
        Files.move(name, name.resolveSibling("kept-original"));
        Files.writeString(name, "abc");
        Files.setPosixFilePermissions(name, PosixFilePermissions.fromString("rw-------"));
      }
    }

    public InspectorEnvironmentPublisher.Io io() {
      return nullPort.equals("io") ? null : this;
    }

    public InodeSecurityCalls security() {
      return nullPort.equals("security") ? null : this;
    }

    public Map<String, Object> attributes(Path p) throws IOException {
      point("attributes");
      var m = new HashMap<>(nio.attributes(p));
      m.put("uid", 992);
      m.put("gid", 977);
      metadata.accept(p, m);
      return m;
    }

    public String filesystem(Path p) throws IOException {
      point("filesystem");
      return filesystem;
    }

    public InspectorEnvironmentPublisher.Writer openWriter(Path p) throws IOException {
      point("openWriter");
      return nio.openWriter(p);
    }

    public java.nio.channels.SeekableByteChannel open(Path p) throws IOException {
      point("openReader");
      return nio.open(p);
    }

    public byte[] accessAcl(Path p, int max) throws StorageIoException {
      assertEquals(44, max);
      return acl;
    }

    public boolean readOnlyFilesystem(Path p) {
      return readonly;
    }

    public long effectiveUid() {
      return 992;
    }

    void execute() throws IOException {
      new BackupDatabaseWorker(this).execute();
    }

    void released() {
      assertTrue(fds.isEmpty(), "all acquired FDs terminal/closed");
      if (request != null) assertArrayEquals(new byte[request.length], request);
      if (raw != null) assertArrayEquals(new byte[raw.length], raw);
    }

    public void close() {
      released();
    }
  }

  @Test
  void bverify003ActualHeldDumpReadAndValidationOnlyNoNewPartOrSecret() throws Exception {
    try (var f = new Fixture()) {
      prepareVerification(f);
      new BackupDatabaseWorker(f).execute();
      assertEquals(1, f.counts.get("verifyDump"));
      assertFalse(f.counts.containsKey("dump"));
      assertFalse(f.counts.containsKey("pgpass"));
      assertFalse(f.counts.containsKey("runtime"));
      assertFalse(f.counts.containsKey("createPrivateFile"));
      assertEquals(
          "abc",
          Files.readString(
              f.backup
                  .resolve(DIRECTORY.substring(0, DIRECTORY.length() - 5))
                  .resolve("schubert_nk.dump")));
      assertArrayEquals(new byte[f.request.length], f.request);
      assertTrue(f.fds.isEmpty());
    }
  }

  @Test
  void bverify004CorruptionReplacementProcessFailureAndUnknownNeverRegenerate() throws Exception {
    for (String failure : List.of("hash", "size", "replace", "process", "unknown", "missing")) {
      try (var f = new Fixture()) {
        prepareVerification(f);
        if (failure.equals("hash")) f.requestText = f.requestText.replace("ba7816bf", "ca7816bf");
        if (failure.equals("size"))
          f.requestText = f.requestText.replace("dump_size=3", "dump_size=4");
        if (failure.equals("replace")) f.replaceDump = true;
        if (failure.equals("process")) f.failures.put("verifyDump", new IOException("fixture"));
        if (failure.equals("missing"))
          f.requestText = f.requestText.replace("2026-09-27T15:00:00Z", "2026-09-27T15:00:01Z");
        var unknown = new IllegalStateException("fixture unknown");
        if (failure.equals("unknown")) f.failures.put("verifyDump", unknown);
        if (failure.equals("unknown"))
          assertSame(
              unknown,
              assertThrows(
                  IllegalStateException.class, () -> new BackupDatabaseWorker(f).execute()));
        else assertThrows(IOException.class, () -> new BackupDatabaseWorker(f).execute());
        assertFalse(f.counts.containsKey("dump"));
        assertFalse(f.counts.containsKey("pgpass"));
        assertTrue(f.fds.isEmpty());
      }
    }
  }

  private void prepareVerification(Fixture f) throws Exception {
    String name = DIRECTORY.substring(0, DIRECTORY.length() - 5);
    Path directory = f.privateDirectory("existing-");
    Files.move(directory, f.backup.resolve(name));
    Path dump = f.backup.resolve(name).resolve("schubert_nk.dump");
    Files.writeString(dump, "abc");
    Files.setPosixFilePermissions(dump, PosixFilePermissions.fromString("rw-------"));
    f.requestText =
        "NKBACKUPVERIFY1\nrun=11111111-2222-4333-8444-555555555555\nstarted=2026-09-27T15:00:00Z\n"
            + "manifest_sha256=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\ndump_size=3\n"
            + "dump_sha256=ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad\n";
  }

  @Test
  void literalRequestDumpAndFullClose() throws Exception {
    try (var f = new Fixture()) {
      f.execute();
      f.released();
      assertEquals(
          "PUBLIC DATABASE DUMP FIXTURE\n",
          Files.readString(f.backup.resolve(DIRECTORY).resolve("schubert_nk.dump")));
      try (var files = Files.list(f.ram)) {
        assertEquals(0, files.count());
      }
      assertEquals(1, f.counts.get("pgpass"));
      assertEquals(1, f.counts.get("dump"));
      assertEquals(2, f.counts.get("identity"));
      assertEquals(
          PosixFilePermissions.fromString("rwx------"),
          Files.getPosixFilePermissions(f.backup.resolve(DIRECTORY)));
    }
  }

  @Test
  void selfAndUnitAdmissionBeforePrivateIo() throws Exception {
    for (var own :
        List.of(
            self(993, 977, SELF.groups(), true, true, SELF.cgroup()),
            self(992, 978, SELF.groups(), true, true, SELF.cgroup()),
            self(992, 977, List.of(977L), true, true, SELF.cgroup()),
            self(992, 977, SELF.groups(), false, true, SELF.cgroup()),
            self(992, 977, SELF.groups(), true, false, SELF.cgroup()),
            self(992, 977, SELF.groups(), true, true, "0::/wrong\n")))
      try (var f = new Fixture()) {
        f.own = own;
        assertThrows(StorageIoException.class, f::execute);
        assertFalse(f.counts.containsKey("credentials"));
      }
    try (var f = new Fixture()) {
      f.invocation = "public-wrong";
      assertThrows(StorageIoException.class, f::execute);
      assertFalse(f.counts.containsKey("credentials"));
    }
    try (var f = new Fixture()) {
      f.state = UNIT.replace("MainPID=123", "MainPID=124");
      assertThrows(StorageIoException.class, f::execute);
    }
    try (var f = new Fixture()) {
      Thread.currentThread().interrupt();
      try {
        assertThrows(StorageIoException.class, f::execute);
        assertFalse(f.counts.containsKey("credentials"));
      } finally {
        assertTrue(Thread.interrupted());
      }
    }
  }

  @Test
  void nullBoundariesAndSecretOwnerBeforeAcquisition() throws Exception {
    assertThrows(NullPointerException.class, () -> new BackupDatabaseWorker(null));
    for (String name :
        List.of(
            "identity",
            "self",
            "unit",
            "invocation",
            "credentials",
            "runtime",
            "backup",
            "request",
            "pgpass"))
      try (var f = new Fixture()) {
        f.nullPort = name;
        assertThrows(NullPointerException.class, f::execute);
      }
    for (String name : List.of("io", "security"))
      try (var f = new Fixture()) {
        // Material is not acquired if copy invariant cannot be established (BUG274).
        f.nullPort = name;
        assertThrows(NullPointerException.class, f::execute);
        assertFalse(f.counts.containsKey("pgpass"));
      }
  }

  @Test
  void rootMetadataAndOutputBinding() throws Exception {
    for (var key : List.of("mode", "uid", "gid", "nlink", "size"))
      try (var f = new Fixture()) {
        Object value =
            switch (key) {
              case "mode" -> Integer.valueOf(040750);
              case "uid" -> Integer.valueOf(991);
              case "gid" -> Integer.valueOf(978);
              case "nlink" -> Integer.valueOf(1);
              default -> Long.valueOf(-1);
            };
        f.metadata = (p, m) -> m.put(key, value);
        assertThrows(StorageIoException.class, f::execute);
        assertFalse(f.counts.containsKey("dump"));
      }
    for (String bad :
        List.of(
            "acl",
            "nullacl",
            "readonly",
            "filesystem",
            "alias",
            "childdev",
            "filelinks",
            "filesize",
            "filemode"))
      try (var f = new Fixture()) {
        switch (bad) {
          case "acl" -> f.acl = new byte[] {1};
          case "nullacl" -> f.acl = null;
          case "readonly" -> f.readonly = true;
          case "filesystem" -> f.filesystem = "ext4";
          case "alias" ->
              f.metadata =
                  (p, m) -> {
                    m.put("dev", 1L);
                    m.put("ino", 1L);
                  };
          case "childdev" ->
              f.metadata =
                  (p, m) -> {
                    if (Files.isDirectory(p) && p.toString().startsWith("/proc"))
                      try {
                        if (Files.isSameFile(p, f.backup.resolve(DIRECTORY))) m.put("dev", -1L);
                      } catch (IOException ignored) {
                        /* new child not yet present */
                      }
                  };
          default ->
              f.metadata =
                  (p, m) -> {
                    if (((Number) m.get("mode")).intValue() == 0100600) {
                      Object value =
                          switch (bad) {
                            case "filelinks" -> Integer.valueOf(2);
                            case "filemode" -> Integer.valueOf(0100640);
                            default -> Long.valueOf(1);
                          };
                      m.put(
                          bad.equals("filelinks")
                              ? "nlink"
                              : bad.equals("filesize") ? "size" : "mode",
                          value);
                    }
                  };
        }
        assertThrows(StorageIoException.class, f::execute);
      }
    for (boolean empty : List.of(true, false))
      try (var f = new Fixture()) {
        f.emptyDump = empty;
        f.replaceDump = !empty;
        assertThrows(StorageIoException.class, f::execute);
        assertTrue(Files.isDirectory(f.backup.resolve(DIRECTORY)));
      }
    // Independently corrupt the held output at its first/second observation, not an earlier part.
    for (String corruption : List.of("1:dev", "1:size", "2:dev", "2:ino"))
      try (var f = new Fixture()) {
        var observations = new java.util.concurrent.atomic.AtomicInteger();
        f.metadata =
            (p, m) -> {
              try {
                if (Files.readSymbolicLink(p).getFileName().toString().equals("schubert_nk.dump")) {
                  int n = observations.incrementAndGet();
                  if (corruption.startsWith(n + ":"))
                    m.put(corruption.substring(2), corruption.endsWith("size") ? 1L : -1L);
                }
              } catch (IOException e) {
                throw new AssertionError(e);
              }
            };
        assertThrows(StorageIoException.class, f::execute);
        assertTrue(observations.get() >= Integer.parseInt(corruption.substring(0, 1)));
      }
    try (var f = new Fixture()) {
      f.metadata =
          (p, m) -> {
            try {
              if (Files.isSameFile(p, f.ram)) m.put("dev", -1L);
            } catch (IOException e) {
              throw new AssertionError(e);
            }
          };
      assertThrows(
          StorageIoException.class,
          f::execute); // Different physical devices pass alias guard, fail copy binding.
    }
  }

  @Test
  void everyAcquisitionIoAndUnknownFailureCloses() throws Exception {
    var points = new LinkedHashMap<String, Integer>();
    try (var f = new Fixture()) {
      f.execute();
      points.putAll(f.counts);
    }
    for (var point : points.entrySet())
      for (int n = 1; n <= point.getValue(); n++)
        for (int kind = 0; kind < 3; kind++)
          try (var f = new Fixture()) {
            Throwable expected =
                kind == 0
                    ? new IOException("PUBLIC IO")
                    : kind == 1
                        ? new IllegalStateException("PUBLIC runtime")
                        : new AssertionError("PUBLIC fatal");
            f.failures.put(point.getKey() + "#" + n, expected);
            Throwable actual = assertThrows(Throwable.class, f::execute, point.getKey() + "#" + n);
            if (kind > 0) assertSame(expected, actual);
          }
  }

  @Test
  void postconditionsAndCompoundCloseFailure() throws Exception {
    for (String change : List.of("identity", "self", "ram", "parent", "child", "child-device"))
      try (var f = new Fixture()) {
        f.hook =
            (name, n) -> {
              if (name.equals("dump")) {
                if (change.equals("identity"))
                  f.identity = new FixedServiceIdentity.Value(993, 977, List.of(977L, 986L));
                else if (change.equals("self"))
                  f.own = self(992, 977, SELF.groups(), true, true, "0::/changed\n");
                else
                  f.metadata =
                      (p, m) -> {
                        try {
                          Path target =
                              change.equals("ram")
                                  ? f.ram
                                  : change.equals("parent")
                                      ? f.backup
                                      : f.backup.resolve(DIRECTORY);
                          if (Files.isSameFile(p, target))
                            m.put(change.equals("child-device") ? "dev" : "ino", -1L);
                        } catch (IOException e) {
                          throw new AssertionError(e);
                        }
                      };
              }
            };
        assertThrows(StorageIoException.class, f::execute);
      }
    try (var f = new Fixture()) {
      var primary = new IllegalStateException("PUBLIC primary");
      f.failures.put("dump", primary);
      f.hook =
          (name, n) -> {
            if (name.equals("dump"))
              f.failures.put(
                  "close#" + (f.counts.get("close") + 1),
                  new StorageIoException(StorageIoException.Reason.UNAVAILABLE));
          };
      assertSame(primary, assertThrows(IllegalStateException.class, f::execute));
    }
  }

  @Test
  void newOnlyReplayAndIndependentParallelJobs() throws Exception {
    try (var f = new Fixture()) {
      Files.createDirectory(f.backup.resolve(DIRECTORY));
      Files.writeString(f.backup.resolve(DIRECTORY).resolve("original"), "KEEP");
      assertThrows(StorageIoException.class, f::execute);
      assertEquals("KEEP", Files.readString(f.backup.resolve(DIRECTORY).resolve("original")));
      assertFalse(f.counts.containsKey("pgpass"));
    }
    try (var pool = Executors.newFixedThreadPool(2)) {
      var tasks = new ArrayList<Future<Boolean>>();
      for (int i = 0; i < 2; i++)
        tasks.add(
            pool.submit(
                () -> {
                  try (var f = new Fixture()) {
                    f.execute();
                    return Files.exists(f.backup.resolve(DIRECTORY).resolve("schubert_nk.dump"));
                  }
                }));
      for (var task : tasks) assertTrue(task.get(10, TimeUnit.SECONDS));
    }
  }

  @Test
  void fixedNativeEntryRefusalAndRedactedDiagnostic() throws Exception {
    assertThrows(NullPointerException.class, () -> BackupDatabaseWorker.main(null));
    assertThrows(IOException.class, () -> BackupDatabaseWorker.main(new String[] {"unapproved"}));
    var previous = Thread.currentThread().getUncaughtExceptionHandler();
    try {
      assertThrows(
          IOException.class,
          () -> BackupDatabaseWorker.main(new String[0]),
          "unprovisioned host has no fixed worker authority");
      var output = new java.io.ByteArrayOutputStream();
      var original = System.err;
      try (var sink = new java.io.PrintStream(output, true, StandardCharsets.UTF_8)) {
        System.setErr(sink);
        BackupDatabaseWorker.fatal(Thread.currentThread(), new IOException("DO_NOT_PRINT"));
      } finally {
        System.setErr(original);
      }
      assertEquals("backup worker failed\n", output.toString(StandardCharsets.UTF_8));
    } finally {
      Thread.currentThread().setUncaughtExceptionHandler(previous);
    }
  }
}
