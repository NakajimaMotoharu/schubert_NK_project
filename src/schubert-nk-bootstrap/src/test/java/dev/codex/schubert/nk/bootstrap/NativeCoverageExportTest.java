package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.MappedByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.channels.FileLock;
import java.nio.channels.ReadableByteChannel;
import java.nio.channels.WritableByteChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** NEXPORT617: modeled Root metadata is data only; actual host tmpfs, FD and bytes stay real. */
final class NativeCoverageExportTest {
  private static final String INV = "1234567890abcdef1234567890abcdef";
  private static final byte[] GOLDEN = {1, (byte) 0xc0, (byte) 0xc0, 0x10, 7, 0x10, 1};
  @TempDir Path temporary;
  private int sequence;

  private record Role(
      String directory,
      String label,
      String cgroup,
      long uid,
      long gid,
      List<Long> groups,
      FixedNativeCoverageProfile.Phase phase,
      FixedNativeCoverageProfile.@Nullable TerminalRole terminal) {}

  private static final List<Role> ROLES =
      List.of(
          new Role(
              "root-api193",
              "API",
              "0::/system.slice/schubert-nk-api.service\n",
              0,
              0,
              List.of(),
              FixedNativeCoverageProfile.Phase.ROOT,
              null),
          new Role(
              "root-web193",
              "WEB",
              "0::/system.slice/schubert-nk-web.service\n",
              0,
              0,
              List.of(),
              FixedNativeCoverageProfile.Phase.ROOT,
              null),
          new Role(
              "ordinary-api193",
              "API",
              "0::/system.slice/schubert-nk-api.service\n",
              999,
              981,
              List.of(980L, 981L, 982L, 986L),
              FixedNativeCoverageProfile.Phase.ORDINARY,
              null),
          new Role(
              "ordinary-web193",
              "WEB",
              "0::/system.slice/schubert-nk-web.service\n",
              998,
              980,
              List.of(980L, 982L, 986L),
              FixedNativeCoverageProfile.Phase.ORDINARY,
              null),
          new Role(
              "ordinary-inspector196",
              "INSPECTOR",
              "0::/system.slice/schubert-nk-inbox-inspector.service\n",
              991,
              976,
              List.of(976L, 982L, 986L),
              FixedNativeCoverageProfile.Phase.ORDINARY,
              FixedNativeCoverageProfile.TerminalRole.INSPECTOR),
          new Role(
              "ordinary-bootstrap196",
              "BOOTSTRAP",
              "0::/system.slice/schubert-nk-bootstrap-admin.service\n",
              999,
              981,
              List.of(980L, 981L, 982L, 986L),
              FixedNativeCoverageProfile.Phase.ORDINARY,
              FixedNativeCoverageProfile.TerminalRole.BOOTSTRAP));

  private static FixedNativeCoverageProfile profile(Role role) {
    String option =
        "-javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar"
            + "=output=none,append=false,dumponexit=false,sessionid="
            + role.label()
            + "-"
            + INV
            + "-"
            + (role.phase() == FixedNativeCoverageProfile.Phase.ROOT ? "root" : "ordinary");
    return role.terminal() != null
        ? FixedNativeCoverageProfile.parseTerminal(role.terminal(), INV, List.of(option))
            .orElseThrow()
        : FixedNativeCoverageProfile.parse(
                role.label().equals("WEB")
                    ? ServiceConfigFiles.Service.WEB
                    : ServiceConfigFiles.Service.API,
                role.phase(),
                INV,
                List.of(option))
            .orElseThrow();
  }

  private Fixture fixture(Role role) throws IOException {
    return new Fixture(temporary.resolve("case-" + sequence++), role);
  }

  private static void refused(Fixture f) {
    assertThrows(IOException.class, () -> f.export("terminal"));
    assertTrue(f.calls.live.isEmpty(), "all owned descriptors must be released after refusal");
  }

  @Test
  void nexport617001SixLiteralRolesAndRootBeforeExecUseRealHeldOutput() throws Exception {
    for (Role role : ROLES) {
      var f = fixture(role);
      f.export("terminal");
      f.success("terminal");
      assertEquals(2, f.invocations);
      assertEquals(2, f.cgroups);
      assertEquals(2, f.resolvers);
      assertEquals(role.phase() == FixedNativeCoverageProfile.Phase.ROOT ? 0 : 2, f.snapshots);
      if (role.phase() == FixedNativeCoverageProfile.Phase.ROOT) {
        var before = fixture(role);
        before.export("before-exec");
        before.success("before-exec");
      }
    }
  }

  /** SSC234/PT-OPS-NCLOSE743001: real held new-only file, modeled metadata is not OS proof. */
  @Test
  void nclose743001ClosingOnlyTwoTerminalRolesNeverReplacesTheirPreservedTerminal()
      throws Exception {
    for (Role role : ROLES) {
      var f = fixture(role);
      if (role.terminal() == null) {
        assertThrows(IOException.class, () -> f.export("closing"));
        assertEquals(0, f.calls.creates);
      } else {
        f.export("terminal");
        f.success("terminal");
        f.export("closing");
        assertArrayEquals(
            new byte[] {1, (byte) 0xc0, (byte) 0xc0, 0x10, 7, 0x10, 1},
            Files.readAllBytes(f.output("closing")));
        assertArrayEquals(
            new byte[] {1, (byte) 0xc0, (byte) 0xc0, 0x10, 7, 0x10, 1},
            Files.readAllBytes(f.output("terminal")));
        assertEquals(0100600, Files.getAttribute(f.output("closing"), "unix:mode"));
        assertEquals(1, Files.getAttribute(f.output("closing"), "unix:nlink"));
        assertEquals(2, f.calls.creates);
        assertEquals(2, f.calls.syncs);
        assertThrows(IOException.class, () -> f.export("closing"));
        assertArrayEquals(GOLDEN, Files.readAllBytes(f.output("closing")));
        assertTrue(f.calls.live.isEmpty());
      }
    }
  }

  @Test
  void nexport617002InitialObservationsAndNullsCannotCreateAnyOutput() throws Exception {
    for (String fault :
        List.of(
            "uid#1",
            "invocation#1",
            "invocation-null#1",
            "cgroup#1",
            "resolver#1",
            "ordinary#1",
            "ordinary#2",
            "ordinary#3",
            "ordinary#4",
            "ordinary#5",
            "ordinary#6")) {
      var f = fixture(ROLES.get(2));
      f.fault = fault;
      refused(f);
      assertEquals(0, f.calls.creates, fault);
      assertFalse(Files.exists(f.output("terminal")));
    }
    var f = fixture(ROLES.get(0));
    for (String name : List.of("foreign", INV + ".unknown.exec", "../terminal.exec"))
      assertThrows(
          IOException.class,
          () -> NativeCoveragePrivateFile.export(profile(f.role), name, GOLDEN, f));
    assertThrows(
        IllegalArgumentException.class,
        () -> NativeCoveragePrivateFile.export(null, INV, GOLDEN, f));
    assertThrows(
        IllegalArgumentException.class,
        () -> NativeCoveragePrivateFile.export(profile(f.role), null, GOLDEN, f));
    assertThrows(
        IllegalArgumentException.class,
        () -> NativeCoveragePrivateFile.export(profile(f.role), INV, null, f));
    assertThrows(
        IllegalArgumentException.class,
        () -> NativeCoveragePrivateFile.export(profile(f.role), INV, GOLDEN, null));
    var ordinary = fixture(ROLES.get(2));
    assertThrows(IOException.class, () -> ordinary.export("before-exec"));
    assertEquals(0, ordinary.calls.creates);
    assertTrue(f.calls.live.isEmpty());
  }

  @Test
  void nexport1276001ClosingCapableRolesStillRefuseUnknownAndRootOnlyNamesBeforeCreate()
      throws Exception {
    for (Role role : ROLES) {
      if (role.terminal() == null) continue;
      for (String suffix : List.of("unknown", "before-exec")) {
        var f = fixture(role);
        assertThrows(
            IOException.class,
            () ->
                NativeCoveragePrivateFile.export(
                    profile(role), INV + "." + suffix + ".exec", GOLDEN, f));
        assertEquals(0, f.calls.creates);
        assertTrue(f.calls.live.isEmpty());
        try (var entries = Files.list(f.target)) {
          assertEquals(0, entries.count(), "unknown phase cannot publish a file");
        }
      }
    }
  }

  @Test
  void nexport1276002SameInodeAndSameLengthTamperRejectsFirstAndReopenedDigest() throws Exception {
    for (int observation : new int[] {2, 3}) {
      var f = fixture(ROLES.get(0));
      f.fault = "same-inode-byte-tamper#" + observation;
      refused(f);
      assertEquals(1, f.calls.creates);
      assertEquals(observation, f.sizeReads);
      assertEquals(observation == 2 ? 0 : 1, f.calls.syncs);
      assertArrayEquals(
          new byte[] {9, (byte) 0xc0, (byte) 0xc0, 0x10, 7, 0x10, 1},
          Files.readAllBytes(f.output("terminal")));
      assertArrayEquals(new byte[] {1, (byte) 0xc0, (byte) 0xc0, 0x10, 7, 0x10, 1}, GOLDEN);
      assertEquals(0100600, Files.getAttribute(f.output("terminal"), "unix:mode"));
      assertEquals(1, Files.getAttribute(f.output("terminal"), "unix:nlink"));
    }
  }

  @Test
  void nexport617003EachHeldDirectoryAndFileObservationRejectsBeforeAcceptance() throws Exception {
    for (String part : List.of("run", "service", "parent", "target"))
      for (String field : List.of("uid", "gid", "mode", "nlink", "dev", "ino", "acl", "null"))
        for (int visit : part.equals("target") ? new int[] {1, 2, 3, 4, 5} : new int[] {1, 2}) {
          var f = fixture(ROLES.get(0));
          f.fault = part + "#" + visit + ":" + field;
          refused(f);
        }
    for (String fault :
        List.of(
            "filesystem",
            "readonly",
            "file#1:uid",
            "file#1:mode",
            "file#1:nlink",
            "file#1:dev",
            "size#1:null",
            "size#1:negative",
            "size#1:unknown",
            "size#1:nonzero",
            "size#2:wrong",
            "size#3:wrong",
            "file#2:ino",
            "file#3:ino")) {
      var f = fixture(ROLES.get(0));
      f.fault = fault;
      refused(f);
    }
    var existing = fixture(ROLES.get(0));
    Files.write(existing.output("terminal"), new byte[] {9}, StandardOpenOption.CREATE_NEW);
    refused(existing);
    assertArrayEquals(new byte[] {9}, Files.readAllBytes(existing.output("terminal")));
    var symlink = fixture(ROLES.get(0));
    Path target = symlink.parent.resolve("original");
    Files.write(target, new byte[] {8}, StandardOpenOption.CREATE_NEW);
    Files.createSymbolicLink(symlink.output("terminal"), target);
    refused(symlink);
    assertTrue(Files.isSymbolicLink(symlink.output("terminal")));
    assertArrayEquals(new byte[] {8}, Files.readAllBytes(target));
    var missing = fixture(ROLES.get(0));
    Files.move(missing.target, missing.target.resolveSibling("preserved"));
    refused(missing);
    assertEquals(0, missing.calls.creates);
  }

  @Test
  void nexport617004RechecksAndCloseFailuresNeverReportSuccessfulPublication() throws Exception {
    for (String fault :
        List.of(
            "target#3:ino",
            "target#4:ino",
            "target#5:ino",
            "parent#2:ino",
            "service#2:ino",
            "run#2:ino",
            "close:target#1",
            "close:target#2",
            "close:parent#1",
            "close:service#1",
            "close:run#1",
            "close:file#1",
            "close:file#2",
            "sync",
            "replace-target")) {
      var f = fixture(ROLES.get(0));
      f.fault = fault;
      refused(f);
      assertArrayEquals(
          GOLDEN,
          Files.readAllBytes(
              fault.equals("replace-target")
                  ? f.parent.resolve("saved-target").resolve(INV + ".terminal.exec")
                  : f.output("terminal")));
      assertEquals(1, f.calls.creates);
      assertFalse(f.calls.closes.isEmpty());
    }
  }

  @Test
  void nexport617005ObserverExceptionsAlwaysReleaseAcquiredScopes() throws Exception {
    for (String fault :
        List.of(
            "throw:open",
            "throw:filesystem",
            "throw:attributes",
            "throw:size",
            "throw:cgroup",
            "throw:ordinary",
            "throw:resolver")) {
      var f = fixture(ROLES.get(2));
      f.fault = fault;
      refused(f);
    }
    for (int length : new int[] {0, 4, 16 * 1024 * 1024 + 1}) {
      var f = fixture(ROLES.get(0));
      assertThrows(
          IOException.class,
          () ->
              NativeCoveragePrivateFile.export(
                  profile(f.role), INV + ".terminal.exec", new byte[length], f));
      assertEquals(0, f.calls.creates);
      assertTrue(f.calls.live.isEmpty());
    }
  }

  @Test
  void nexport617006FinalIdentityAndEveryOrdinaryFieldDriftRejectsWithRetainedBytes()
      throws Exception {
    for (String fault :
        List.of("invocation#2", "invocation-null#2", "cgroup#2", "uid#2", "resolver#2")) {
      var f = fixture(ROLES.get(2));
      f.fault = fault;
      refused(f);
      assertArrayEquals(GOLDEN, Files.readAllBytes(f.output("terminal")));
    }
    for (int field = 1; field <= 9; field++) {
      var f = fixture(ROLES.get(2));
      f.fault = "ordinary-final#" + field;
      refused(f);
      assertArrayEquals(GOLDEN, Files.readAllBytes(f.output("terminal")));
      assertEquals(2, f.snapshots);
    }
  }

  @Test
  void nexport617007NativeAdapterReadsOnlyFixedRunAndCurrentHostObservations() throws Exception {
    var io = new NativeCoveragePrivateFile.NativeIo();
    assertEquals(System.getenv("INVOCATION_ID"), io.invocation());
    assertEquals(Files.readString(Path.of("/proc/self/cgroup")), io.cgroup());
    var status = new HashMap<String, String>();
    for (String line : Files.readAllLines(Path.of("/proc/self/status"))) {
      int separator = line.indexOf(':');
      if (separator > 0)
        status.put(line.substring(0, separator), line.substring(separator + 1).strip());
    }
    long uid = Long.parseLong(status.get("Uid").split("\\s+")[1]);
    long gid = Long.parseLong(status.get("Gid").split("\\s+")[1]);
    assertEquals(uid, io.security().effectiveUid());
    var observed = io.ordinary();
    assertEquals(ProcessHandle.current().pid(), observed.pid());
    assertEquals(
        Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).strip(), observed.boot());
    assertEquals(uid, observed.uid());
    assertEquals(gid, observed.gid());
    assertEquals(
        Arrays.stream(status.get("Groups").split("\\s+")).map(Long::parseLong).sorted().toList(),
        observed.groups());
    assertEquals(Files.readString(Path.of("/proc/self/cgroup")), observed.cgroup());
    assertEquals(status.get("NoNewPrivs").equals("1"), observed.noNewPrivileges());
    assertEquals(
        List.of("CapInh", "CapPrm", "CapEff", "CapBnd", "CapAmb").stream()
            .allMatch(key -> status.get(key).equals("0000000000000000")),
        observed.zeroCapabilities());
    var directory = io.openRun();
    try (directory) {
      directory.atDirectory(
          held -> {
            assertTrue(Files.isSameFile(Path.of("/run"), held));
            assertEquals(Files.getFileStore(Path.of("/run")).type(), io.filesystem(held));
            assertEquals(
                Files.readAttributes(Path.of("/run"), "unix:uid,gid,mode,nlink,dev,ino"),
                io.attributes(held));
            assertEquals(Files.getAttribute(Path.of("/run"), "unix:size"), io.size(held));
            assertEquals(
                Files.getFileStore(Path.of("/run")).isReadOnly(),
                io.security().readOnlyFilesystem(held));
            return true;
          });
    }
    assertThrows(StorageIoException.class, () -> directory.atDirectory(held -> true));
  }

  @Test
  void nexport617008DefaultExportRejectsActualMissingFixedNssBeforeNamespaceWrite()
      throws Exception {
    var query = new ProcessBuilder("/usr/bin/getent", "passwd", "schubert-api").start();
    assertEquals(2, query.waitFor(), "host fixture requires no production service NSS account");
    assertEquals(0, query.getInputStream().readAllBytes().length);
    var io = new NativeCoveragePrivateFile.NativeIo();
    assertEquals(
        "service identity unavailable",
        assertThrows(IOException.class, () -> io.resolver().resolve(ServiceConfigFiles.Service.API))
            .getMessage());
    var error =
        assertThrows(
            IOException.class,
            () ->
                NativeCoveragePrivateFile.export(
                    profile(ROLES.get(0)), INV + ".terminal.exec", GOLDEN));
    assertEquals("service identity unavailable", error.getMessage());
    assertNull(error.getCause());
    // Independent getent exit2 proves the rejecting prerequisite; no fake role/UID grant or write.
  }

  @Test
  void nexport619001TypedOracleMutationsHaveTheSpecifiedValuesRatherThanTypeErrors()
      throws Exception {
    for (String field : List.of("uid", "gid", "mode", "nlink", "dev", "ino")) {
      var f = fixture(ROLES.get(0));
      f.fault = "target#1:" + field;
      long originalInode = (Long) Files.getAttribute(f.target, "unix:ino");
      try (var held = OwnedTransferDirectory.open(f.calls, f.target)) {
        var metadata = held.atDirectory(f::attributes);
        assertNotNull(metadata);
        Object value = metadata.get(field);
        if (field.equals("dev") || field.equals("ino")) {
          assertInstanceOf(Long.class, value);
          assertEquals(field.equals("dev") ? 0L : originalInode + 1, value);
        } else {
          assertInstanceOf(Integer.class, value);
          assertEquals(Integer.valueOf(1), value);
        }
      }
      assertTrue(f.calls.live.isEmpty());
    }
    var f = fixture(ROLES.get(0));
    f.fault = "file#1:nlink";
    Files.write(f.output("terminal"), new byte[] {9}, StandardOpenOption.CREATE_NEW);
    try (var held = OwnedTransferDirectory.open(f.calls, f.target)) {
      var metadata = held.atExistingEntryHandle(INV + ".terminal.exec", f::attributes);
      assertNotNull(metadata);
      assertInstanceOf(Integer.class, metadata.get("nlink"));
      assertEquals(Integer.valueOf(2), metadata.get("nlink"));
    }
    assertTrue(f.calls.live.isEmpty());
  }

  @Test
  void nchannel193001ReadOnlyAgentMetadataRequiresExactlyOneLink() throws Exception {
    Map<String, Object> metadata =
        new HashMap<>(
            Map.of("uid", 0, "gid", 0, "mode", 0100644, "nlink", 1, "dev", 2L, "ino", 3L));
    var identity = NativeCoveragePrivateFile.checked(metadata, new byte[0], 0, 0, 0100644);
    assertEquals(0L, identity.uid());
    assertEquals(0L, identity.gid());
    assertEquals(0100644, identity.mode());
    assertEquals(1, identity.links());
    assertEquals(2L, identity.device());
    assertEquals(3L, identity.inode());
    for (int links : new int[] {0, 2}) {
      metadata.put("nlink", links);
      assertThrows(
          IOException.class,
          () -> NativeCoveragePrivateFile.checked(metadata, new byte[0], 0, 0, 0100644));
    }
  }

  @Test
  void nchannel1278001PinShapeDataPreservesShortCircuitNotPhysicalAuthority() throws Exception {
    for (long size : new long[] {-1, 0, 307842, 307844}) {
      int[] reads = {0};
      assertThrows(
          IOException.class,
          () ->
              NativeCoveragePrivateFile.verifyAgentShape(
                  size,
                  () -> {
                    reads[0]++;
                    return true;
                  }));
      assertEquals(0, reads[0]);
    }
    NativeCoveragePrivateFile.verifyAgentShape(307843, () -> true);
    assertThrows(
        IOException.class, () -> NativeCoveragePrivateFile.verifyAgentShape(307843, () -> false));
    assertThrows(
        IllegalArgumentException.class,
        () -> NativeCoveragePrivateFile.verifyAgentShape(307843, null));
    assertThrows(
        IOException.class,
        () ->
            NativeCoveragePrivateFile.verifyAgentShape(
                307843,
                () -> {
                  throw new IOException("literal observation failure");
                }));
  }

  @Test
  void nchannel1278002NullResourcesRefuseAndReturnAllOwnedFileDescriptors() throws Exception {
    var untouched = fixture(ROLES.get(0));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            NativeCoveragePrivateFile.export(
                profile(untouched.role), INV + ".terminal.exec", GOLDEN, untouched, null));
    assertEquals(0, untouched.calls.creates);
    for (String fault : List.of("write-null", "read-null")) {
      var f = fixture(ROLES.get(0));
      var channels = new FaultChannels(f, fault);
      assertThrows(
          IllegalArgumentException.class,
          () ->
              NativeCoveragePrivateFile.export(
                  profile(f.role), INV + ".terminal.exec", GOLDEN, f, channels));
      assertTrue(f.calls.live.isEmpty());
      assertTrue(channels.opened.stream().allMatch(c -> !c.isOpen() && !c.delegate.isOpen()));
      assertEquals(1, f.calls.creates);
      assertEquals(fault.equals("write-null") ? 0 : 7, Files.size(f.output("terminal")));
    }
  }

  @Test
  void nchannel1278003ActualHeldChannelZeroSizeShortLongForceCloseFailuresAreNonSuccess()
      throws Exception {
    for (String fault :
        List.of(
            "write-zero",
            "write-size",
            "write-error",
            "force-error",
            "write-close",
            "read-size-begin",
            "read-zero",
            "read-long",
            "read-short",
            "read-size-end",
            "read-close")) {
      var f = fixture(ROLES.get(0));
      var channels = new FaultChannels(f, fault);
      assertThrows(
          IOException.class,
          () ->
              NativeCoveragePrivateFile.export(
                  profile(f.role), INV + ".terminal.exec", GOLDEN, f, channels),
          fault);
      assertTrue(f.calls.live.isEmpty(), fault);
      assertTrue(
          channels.opened.stream().allMatch(c -> !c.isOpen() && !c.delegate.isOpen()), fault);
      assertEquals(1, f.calls.creates);
      assertEquals(0, f.calls.syncs);
      assertArrayEquals(
          fault.equals("write-zero") || fault.equals("write-error")
              ? new byte[0]
              : new byte[] {1, (byte) 0xc0, (byte) 0xc0, 0x10, 7, 0x10, 1},
          Files.readAllBytes(f.output("terminal")),
          fault);
      assertEquals(fault.startsWith("read-") ? 1 : 0, channels.readerCount);
      assertEquals(fault.startsWith("read-") ? 2 : 1, channels.opened.size());
      assertArrayEquals(new byte[] {1, (byte) 0xc0, (byte) 0xc0, 0x10, 7, 0x10, 1}, GOLDEN);
    }
  }

  private static final class FaultChannels implements NativeCoveragePrivateFile.FileCalls {
    final Fixture fixture;
    final String fault;
    final List<FaultChannel> opened = new ArrayList<>();
    int readerCount;

    FaultChannels(Fixture fixture, String fault) {
      this.fixture = fixture;
      this.fault = fault;
    }

    public @Nullable FileChannel read(Path held) throws IOException {
      readerCount++;
      return fault.equals("read-null") ? null : open(held, true);
    }

    public @Nullable FileChannel write(Path held) throws IOException {
      return fault.equals("write-null") ? null : open(held, false);
    }

    private FileChannel open(Path held, boolean reading) throws IOException {
      assertTrue(Files.isSameFile(held, fixture.output("terminal")));
      var delegate =
          Objects.requireNonNull(
              reading
                  ? NativeCoveragePrivateFile.NATIVE_CHANNELS.read(held)
                  : NativeCoveragePrivateFile.NATIVE_CHANNELS.write(held));
      var value =
          new FaultChannel(delegate, reading ? fault : fault.startsWith("read-") ? "" : fault);
      opened.add(value);
      return value;
    }
  }

  /** Resource fault provider around a real held Linux FileChannel, never namespace authority. */
  private static final class FaultChannel extends FileChannel {
    final FileChannel delegate;
    final String fault;
    int reads;
    int sizes;

    FaultChannel(FileChannel delegate, String fault) {
      this.delegate = delegate;
      this.fault = fault;
    }

    @Override
    public int read(ByteBuffer target) throws IOException {
      reads++;
      if (fault.equals("read-zero")) return 0;
      if (fault.equals("read-long")) {
        target.put(new byte[8]);
        return 8;
      }
      if (fault.equals("read-short")) {
        if (reads > 1) return -1;
        target.limit(3);
      }
      return delegate.read(target);
    }

    @Override
    public int write(ByteBuffer input) throws IOException {
      if (fault.equals("write-zero")) return 0;
      if (fault.equals("write-error")) throw new IOException("literal provider refusal");
      return delegate.write(input);
    }

    @Override
    public long size() throws IOException {
      sizes++;
      return delegate.size()
          + (fault.equals("write-size")
                  || fault.equals("read-size-begin")
                  || (fault.equals("read-size-end") && sizes > 1)
              ? 1
              : 0);
    }

    @Override
    public void force(boolean metadata) throws IOException {
      assertTrue(metadata);
      if (fault.equals("force-error")) throw new IOException("literal force refusal");
      delegate.force(metadata);
    }

    @Override
    protected void implCloseChannel() throws IOException {
      delegate.close();
      if (fault.equals("write-close") || fault.equals("read-close"))
        throw new IOException("literal close refusal");
    }

    @Override
    public long read(ByteBuffer[] b, int o, int n) throws IOException {
      return delegate.read(b, o, n);
    }

    @Override
    public long write(ByteBuffer[] b, int o, int n) throws IOException {
      return delegate.write(b, o, n);
    }

    @Override
    public long position() throws IOException {
      return delegate.position();
    }

    @Override
    public FileChannel position(long p) throws IOException {
      delegate.position(p);
      return this;
    }

    @Override
    public FileChannel truncate(long s) throws IOException {
      delegate.truncate(s);
      return this;
    }

    @Override
    public long transferTo(long p, long n, WritableByteChannel c) throws IOException {
      return delegate.transferTo(p, n, c);
    }

    @Override
    public long transferFrom(ReadableByteChannel c, long p, long n) throws IOException {
      return delegate.transferFrom(c, p, n);
    }

    @Override
    public int read(ByteBuffer b, long p) throws IOException {
      return delegate.read(b, p);
    }

    @Override
    public int write(ByteBuffer b, long p) throws IOException {
      return delegate.write(b, p);
    }

    @Override
    public MappedByteBuffer map(MapMode m, long p, long s) throws IOException {
      return delegate.map(m, p, s);
    }

    @Override
    public FileLock lock(long p, long s, boolean shared) throws IOException {
      return delegate.lock(p, s, shared);
    }

    @Override
    public FileLock tryLock(long p, long s, boolean shared) throws IOException {
      return delegate.tryLock(p, s, shared);
    }
  }

  private static final class Fixture implements NativeCoveragePrivateFile.Io {
    final Path run;
    final Path service;
    final Path parent;
    final Path target;
    final Role role;
    final Calls calls;
    final Map<String, Integer> visits = new HashMap<>();
    String fault = "";
    int invocations;
    int cgroups;
    int resolvers;
    int snapshots;
    int uidReads;
    int sizeReads;

    Fixture(Path run, Role role) throws IOException {
      this.run = run;
      this.role = role;
      service = run.resolve("schubert-nk");
      parent = service.resolve("pt-coverage");
      target = parent.resolve(role.directory());
      Files.createDirectories(target);
      for (Path path : List.of(run, service, parent))
        Files.setPosixFilePermissions(path, PosixFilePermissions.fromString("rwxr-xr-x"));
      Files.setPosixFilePermissions(target, PosixFilePermissions.fromString("rwx------"));
      calls = new Calls(this);
      assertEquals("tmpfs", Files.getFileStore(target).type(), "fixture requires a real tmpfs");
    }

    Path output(String phase) {
      return target.resolve(INV + "." + phase + ".exec");
    }

    void export(String phase) throws IOException {
      NativeCoveragePrivateFile.export(profile(role), INV + "." + phase + ".exec", GOLDEN, this);
    }

    void success(String phase) throws IOException {
      assertArrayEquals(GOLDEN, Files.readAllBytes(output(phase)));
      assertEquals(0100600, Files.getAttribute(output(phase), "unix:mode"));
      assertEquals(1, Files.getAttribute(output(phase), "unix:nlink"));
      assertEquals(
          Files.getAttribute(run, "unix:uid"),
          Files.getAttribute(output(phase), "unix:uid"),
          "physical owner stays the actual host UID, not modeled Root");
      assertEquals(1, calls.creates);
      assertEquals(1, calls.syncs);
      assertTrue(calls.live.isEmpty());
      assertEquals(Map.of("run", 2, "service", 2, "parent", 2, "target", 5, "file", 3), visits);
    }

    private void fail(String operation) throws IOException {
      if (fault.equals("throw:" + operation)) throw new IOException("public fixture unavailable");
    }

    public InodeSecurityCalls security() {
      return new InodeSecurityCalls() {
        final InodeSecurityCalls physical = LinuxInodeSecurity.create();

        public byte[] accessAcl(Path held, int max) throws StorageIoException {
          try {
            String key = part(held) + "#" + visits.getOrDefault(part(held), 0) + ":acl";
            return fault.equals(key) ? new byte[] {1} : physical.accessAcl(held, max);
          } catch (IOException e) {
            throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
          }
        }

        public boolean readOnlyFilesystem(Path held) throws StorageIoException {
          return fault.equals("readonly") || physical.readOnlyFilesystem(held);
        }

        public long effectiveUid() {
          return fault.equals("uid#" + ++uidReads) ? role.uid() + 1 : role.uid();
        }
      };
    }

    public FixedServiceIdentity resolver() {
      resolvers++;
      return new FixedServiceIdentity(
          command -> {
            fail("resolver");
            var values = new HashMap<>(FixedServiceIdentityTest.GOLDEN);
            values.put(
                "passwd/schubert-inbox-inspector",
                "schubert-inbox-inspector:x:991:976::/nonexistent:/usr/sbin/nologin\n");
            values.put("group/schubert-inbox-inspector", "schubert-inbox-inspector:x:976:\n");
            if (fault.equals("resolver#" + resolvers))
              values.put(
                  "passwd/schubert-api",
                  "schubert-api:x:997:981::/nonexistent:/usr/sbin/nologin\n");
            return values
                .getOrDefault(command.get(1) + "/" + command.get(2), "")
                .getBytes(StandardCharsets.US_ASCII);
          });
    }

    public OwnedTransferDirectory openRun() throws IOException {
      fail("open");
      return OwnedTransferDirectory.open(calls, run);
    }

    public @Nullable String invocation() {
      int call = ++invocations;
      if (fault.equals("invocation-null#" + call)) return null;
      return fault.equals("invocation#" + call) ? "foreign" : INV;
    }

    public String cgroup() throws IOException {
      fail("cgroup");
      return fault.equals("cgroup#" + ++cgroups) ? "0::/foreign\n" : role.cgroup();
    }

    public ChildStartupContext.Observed ordinary() throws IOException {
      fail("ordinary");
      snapshots++;
      int initial = 0;
      int finalField = 0;
      for (int i = 1; i <= 9; i++) {
        if (snapshots == 1 && fault.equals("ordinary#" + i)) initial = i;
        if (snapshots == 2 && fault.equals("ordinary-final#" + i)) finalField = i;
      }
      int field = finalField;
      return new ChildStartupContext.Observed(
          field == 1 ? "PUBLIC_BOOT_B" : "PUBLIC_BOOT_A",
          field == 2 ? 43 : 42,
          field == 3 ? 101 : 100,
          initial == 1 || field == 4 ? 997 : role.uid(),
          initial == 2 || field == 5 ? 979 : role.gid(),
          initial == 3 || field == 6 ? List.of(979L) : role.groups(),
          initial == 6 || field == 7 ? "0::/foreign\n" : role.cgroup(),
          initial != 4 && field != 8,
          initial != 5 && field != 9);
    }

    public String filesystem(Path held) throws IOException {
      fail("filesystem");
      return fault.equals("filesystem") ? "ext4" : Files.getFileStore(held).type();
    }

    private String part(Path held) throws IOException {
      Path path = Files.readSymbolicLink(held);
      if (path.equals(run)) return "run";
      if (path.equals(service)) return "service";
      if (path.equals(parent)) return "parent";
      if (path.equals(target)) return "target";
      return Files.isRegularFile(held) ? "file" : "ancestor";
    }

    public @Nullable Map<String, ? extends @Nullable Object> attributes(Path held)
        throws IOException {
      fail("attributes");
      String part = part(held);
      int visit = visits.merge(part, 1, Integer::sum);
      var values =
          new HashMap<String, Object>(
              Files.readAttributes(held, "unix:uid,gid,mode,nlink,dev,ino"));
      boolean actor = part.equals("target") || part.equals("file");
      values.put("uid", (int) (actor ? role.uid() : 0));
      values.put("gid", (int) (actor ? role.gid() : 0));
      String prefix = part + "#" + visit + ":";
      if (fault.equals(prefix + "null")) return null;
      for (String field : List.of("uid", "gid", "mode", "nlink", "dev", "ino"))
        if (fault.equals(prefix + field)) {
          if (field.equals("dev") || field.equals("ino")) {
            long changed = field.equals("ino") ? ((Long) values.get("ino")) + 1 : 0;
            values.put(field, Long.valueOf(changed));
          } else {
            int changed = field.equals("nlink") && part.equals("file") ? 2 : 1;
            values.put(field, Integer.valueOf(changed));
          }
        }
      return values;
    }

    public @Nullable Object size(Path held) throws IOException {
      fail("size");
      String prefix = "size#" + ++sizeReads + ":";
      if (fault.equals("same-inode-byte-tamper#" + sizeReads)) {
        // An adversarial writer changes the owned temporary inode at the exact
        // observation boundary, not its returned metadata or expected digest.
        var before = Files.readAttributes(held, "unix:dev,ino,size");
        Files.write(
            held,
            new byte[] {9, (byte) 0xc0, (byte) 0xc0, 0x10, 7, 0x10, 1},
            StandardOpenOption.WRITE,
            StandardOpenOption.TRUNCATE_EXISTING);
        assertEquals(before, Files.readAttributes(held, "unix:dev,ino,size"));
      }
      if (fault.equals(prefix + "null")) return null;
      if (fault.equals(prefix + "unknown")) return "unknown";
      if (fault.equals(prefix + "negative")) return -1L;
      if (fault.equals(prefix + "nonzero") || fault.equals(prefix + "wrong")) return 1L;
      return Files.getAttribute(held, "unix:size");
    }
  }

  private static final class Calls implements DirectoryCalls {
    final DirectoryCalls actual = LinuxDirectoryCalls.create();
    final Fixture fixture;
    final Set<Integer> live = new HashSet<>();
    final Map<String, Integer> closes = new HashMap<>();
    int creates;
    int syncs;

    Calls(Fixture fixture) {
      this.fixture = fixture;
    }

    int own(int fd) {
      assertTrue(live.add(fd));
      return fd;
    }

    public int openRoot() throws StorageIoException {
      return own(actual.openRoot());
    }

    public int openDirectory(int parent, String name) throws StorageIoException {
      return own(actual.openDirectory(parent, name));
    }

    public int openEntry(int parent, String name) throws StorageIoException {
      return own(actual.openEntry(parent, name));
    }

    public int createFile(int parent, String name) throws StorageIoException {
      return own(actual.createFile(parent, name));
    }

    public int createPrivateFile(int parent, String name) throws StorageIoException {
      creates++;
      return own(actual.createPrivateFile(parent, name));
    }

    public void createDirectory(int parent, String name) throws StorageIoException {
      actual.createDirectory(parent, name);
    }

    public void publish(int parent, String from, String to) throws StorageIoException {
      actual.publish(parent, from, to);
    }

    public void unlink(int parent, String name) throws StorageIoException {
      actual.unlink(parent, name);
    }

    public void sync(int fd) throws StorageIoException {
      syncs++;
      actual.sync(fd);
      if (fixture.fault.equals("sync"))
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }

    public void close(int fd) throws StorageIoException {
      String part;
      try {
        part = fixture.part(Path.of("/proc/self/fd/" + fd));
      } catch (IOException failure) {
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      }
      assertTrue(live.remove(fd));
      actual.close(fd);
      int count = closes.merge(part, 1, Integer::sum);
      if (fixture.fault.equals("replace-target") && part.equals("target") && count == 1) {
        try {
          Files.move(fixture.target, fixture.parent.resolve("saved-target"));
          Files.createDirectory(fixture.target);
          Files.setPosixFilePermissions(
              fixture.target, PosixFilePermissions.fromString("rwx------"));
        } catch (IOException failure) {
          throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
        }
      }
      if (fixture.fault.equals("close:" + part + "#" + count))
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }
  }
}
