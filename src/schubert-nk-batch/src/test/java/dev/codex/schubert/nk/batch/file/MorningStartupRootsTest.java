package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.StorageIoException;
import dev.codex.schubert.nk.storage.StorageRootLayout;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.FileTime;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.function.Consumer;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * ISSROOT001/002. Real Linux NOFOLLOW FDs, explicitly synthetic uid/gid/mount metadata. Independent
 * literal six-line wire vector. Not native root/issuer acceptance.
 */
final class MorningStartupRootsTest {
  private static final String FIXTURE_INO_4BE7C1E0 = "ino";
  private static final String FIXTURE_READ_ONLY_A9812E1E = "read-only";
  @TempDir Path temporary;
  private static final StartupPermitRecords.Epoch EPOCH =
      new StartupPermitRecords.Epoch(
          StartupPermitRecords.State.INVALID,
          UUID.fromString("11111111-1111-4111-8111-111111111111"),
          UUID.fromString("22222222-2222-4222-8222-222222222222"),
          new MaintenanceActivation(
              new BatchRun(
                  UUID.fromString("33333333-3333-4333-8333-333333333333"),
                  Instant.parse("2026-09-27T15:00:00Z")),
              UUID.fromString("44444444-4444-4444-8444-444444444444")),
          Optional.empty());
  private static final String GOLD =
      "NKROOTS1\n"
          + "boot_id=11111111-1111-4111-8111-111111111111\n"
          + "epoch_id=22222222-2222-4222-8222-222222222222\n"
          + "run_id=33333333-3333-4333-8333-333333333333\n"
          + "cutoff_utc=2026-09-27T15:00:00.000000Z\n"
          + "activation_id=44444444-4444-4444-8444-444444444444\n"
          + "ASSET|@0|42|1000|10|20|0750|ext4|0|empty\n"
          + "TRANSFER|@1|42|1001|11|21|0750|ext4|0|empty\n"
          + "BACKUP|@2|42|1002|12|22|0700|ext4|0|empty\n"
          + "LOG|@3|42|1003|0|23|0750|ext4|0|empty\n"
          + "ARTEMIS|@4|42|1004|14|24|0700|ext4|0|empty\n"
          + "STAGING|@5|42|1005|15|25|0700|ext4|0|empty\n";

  @Test
  void issroot001ActualHeldRootsMatchIndependentGoldenAndAllowPrivateReadonly() throws Exception {
    var f = fixture();
    var actual = f.reader().capture();
    String golden = GOLD;
    for (int index = 0; index < 6; index++)
      golden = golden.replace("@" + index, f.paths.get(index).toString());
    byte[] expected = golden.getBytes(StandardCharsets.US_ASCII);
    assertArrayEquals(expected, actual.canonical(EPOCH));
    var permit =
        new StartupPermitRecords.Permit(
            EPOCH.boot(),
            EPOCH.epoch(),
            EPOCH.activation(),
            "1".repeat(32),
            "a".repeat(64),
            "b".repeat(64),
            "c".repeat(64),
            "d".repeat(64),
            "e".repeat(64));
    assertArrayEquals(expected, actual.canonicalIssued(permit));
    assertEquals(
        HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(expected)),
        actual.sha256Issued(permit));
    assertThrows(NullPointerException.class, () -> actual.canonicalIssued(null));
    assertThrows(NullPointerException.class, () -> actual.sha256Issued(null));
    assertEquals(
        HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(expected)),
        actual.sha256(EPOCH));
    f.reader().recheck(actual);
    assertEquals(0, f.host.open.size() + f.local.open.size());
    assertEquals("MorningRootObservation[redacted]", actual.toString());
    // A different completed maintenance observation may change size/times/nlink, not digest
    // identity.
    f.size = 4096;
    f.time = FileTime.fromMillis(1000);
    f.links = 3;
    f.reader().recheck(actual);
    assertThrows(IOException.class, () -> actual.canonical(EPOCH.issued("1".repeat(64))));
    assertThrows(NullPointerException.class, () -> actual.canonical(null));
    assertThrows(NullPointerException.class, () -> f.reader().recheck(null));
  }

  @Test
  void issroot002PolicyUnknownNullAndWithinIoDriftRefuseWithoutFdLeak() throws Exception {
    for (Consumer<Map<String, Object>> invalid :
        List.<Consumer<Map<String, Object>>>of(
            map -> map.put("uid", 999),
            map -> map.put("gid", 999),
            map -> map.put("mode", 040777),
            map -> map.put("nlink", 1),
            map -> map.put("dev", -1L),
            map -> map.put(FIXTURE_INO_4BE7C1E0, 0L),
            map -> map.put("size", -1L),
            map -> map.put("ctime", "wrong"),
            map -> map.put(FIXTURE_INO_4BE7C1E0, 1000L))) {
      var f = fixture();
      f.invalid = invalid;
      assertThrows(IOException.class, () -> f.reader().capture());
      assertEquals(0, f.host.open.size() + f.local.open.size());
    }
    for (int fault = 0; fault < 6; fault++) {
      var f = fixture();
      if (fault == 0) f.acl = new byte[] {1};
      if (fault == 1) f.hostReadonly = true;
      if (fault == 2) f.filesystem = "nfs";
      if (fault == 3) f.filesystem = null;
      if (fault == 4) f.nullAttributes = true;
      if (fault == 5) f.drift = true;
      assertThrows(IOException.class, () -> f.reader().capture());
      assertEquals(0, f.host.open.size() + f.local.open.size());
    }
    var f = fixture();
    var actual = f.reader().capture();
    f.invalid = map -> map.put(FIXTURE_INO_4BE7C1E0, (long) map.get(FIXTURE_INO_4BE7C1E0) + 100);
    assertThrows(IOException.class, () -> f.reader().recheck(actual));
    var nullAcl = fixture();
    nullAcl.nullAcl = true;
    assertThrows(IOException.class, () -> nullAcl.reader().capture());
  }

  @Test
  void issroot002FixedProfilesNullWrongActorAndUnknownFailureAreNotSuccess() throws Exception {
    var f = fixture();
    var original = List.copyOf(f.profiles);
    f.profiles = new ArrayList<>(original.subList(0, 5));
    assertThrows(IOException.class, () -> f.reader().capture());
    f.profiles = new ArrayList<>(original);
    f.profiles.set(2, null);
    assertThrows(NullPointerException.class, () -> f.reader().capture());
    f.profiles = new ArrayList<>(original);
    f.profileDrift = true;
    assertThrows(IOException.class, () -> f.reader().capture());
    f.profileDrift = false;
    f.gateFailure = true;
    assertThrows(IOException.class, () -> f.reader().capture());
    f.gateFailure = false;
    var unknown = new IllegalStateException("programming failure");
    f.unknown = unknown;
    assertSame(unknown, assertThrows(IllegalStateException.class, () -> f.reader().capture()));
    assertEquals(0, f.host.open.size() + f.local.open.size());
    for (var values :
        new long[][] {
          {-1, 20, 0750},
          {4294967295L, 20, 0750},
          {1, 0, 0750},
          {1, 4294967295L, 0750},
          {1, 20, 0777}
        })
      assertThrows(
          IllegalArgumentException.class,
          () -> new MorningStartupRoots.Profile(values[0], values[1], (int) values[2]));
    assertThrows(
        NullPointerException.class,
        () ->
            new MorningStartupRoots(
                null, f.layout, () -> original, f.host, f.local, f.security, f.source));
  }

  @Test
  void issroot002ReadonlyHoldingCloseFailureAndUnsafePathsNeverReturnObservation()
      throws Exception {
    var f = fixture();
    f.host.failClose = true;
    assertThrows(IOException.class, () -> f.reader().capture());
    assertEquals(0, f.host.open.size() + f.local.open.size());
    var unsafeFixture = fixture();
    Path unsafe = Files.createDirectory(temporary.resolve("unsafe|path"));
    unsafeFixture.layout =
        new StorageRootLayout(
            unsafe,
            unsafeFixture.paths.get(1),
            unsafeFixture.paths.get(2),
            unsafeFixture.paths.get(3),
            unsafeFixture.paths.get(4),
            unsafeFixture.paths.get(5));
    assertThrows(IOException.class, () -> unsafeFixture.reader().capture());
  }

  private Fixture fixture() throws IOException {
    return new Fixture(Files.createTempDirectory(temporary, "roots-"));
  }

  private static final class Fixture {
    final List<Path> paths = new ArrayList<>();
    StorageRootLayout layout;
    List<MorningStartupRoots.Profile> profiles = new ArrayList<>();
    final Calls host = new Calls();
    final Calls local = new Calls();
    Consumer<Map<String, Object>> invalid = map -> {};
    long size = 0;
    int links = 2;
    int reads = 0;
    int profileReads = 0;
    FileTime time = FileTime.fromMillis(0);
    byte[] acl = new byte[0];
    String filesystem = "ext4";
    boolean hostReadonly;
    boolean nullAttributes;
    boolean nullAcl;
    boolean drift;
    boolean profileDrift;
    boolean gateFailure;
    IllegalStateException unknown;

    Fixture(Path root) throws IOException {
      for (int index = 0; index < 6; index++) {
        paths.add(Files.createDirectory(root.resolve("n" + index)));
        profiles.add(
            new MorningStartupRoots.Profile(
                index == 3 ? 0 : 10 + index,
                20 + index,
                index == 0 || index == 1 || index == 3 ? 0750 : 0700));
      }
      layout =
          new StorageRootLayout(
              paths.get(0), paths.get(1), paths.get(2), paths.get(3), paths.get(4), paths.get(5));
    }

    final InodeSecurityCalls security =
        new InodeSecurityCalls() {
          public byte[] accessAcl(Path p, int max) {
            return nullAcl ? null : acl.clone();
          }

          public boolean readOnlyFilesystem(Path p) {
            return host.open.contains(Integer.valueOf(p.getFileName().toString()))
                ? hostReadonly
                : true;
          }

          public long effectiveUid() {
            return 0;
          }
        };
    final EnvironmentInodePolicy.Source source =
        new EnvironmentInodePolicy.Source() {
          public Map<String, Object> attributes(Path p) throws IOException {
            if (unknown != null) throw unknown;
            if (nullAttributes) return null;
            int index =
                Integer.parseInt(Files.readSymbolicLink(p).getFileName().toString().substring(1));
            var profile = profiles.get(index);
            var map =
                new HashMap<String, Object>(
                    Map.of(
                        "mode",
                        040000 | profile.mode(),
                        "uid",
                        (int) profile.uid(),
                        "gid",
                        (int) profile.gid(),
                        "nlink",
                        links,
                        "size",
                        drift ? (long) ++reads : size,
                        "dev",
                        42L,
                        FIXTURE_INO_4BE7C1E0,
                        1000L + index,
                        "lastModifiedTime",
                        time,
                        "ctime",
                        time));
            invalid.accept(map);
            return map;
          }

          public String filesystem(Path p) {
            return filesystem;
          }
        };

    MorningStartupRoots reader() {
      return new MorningStartupRoots(
          () -> {
            if (gateFailure) throw new IOException("actor unavailable");
          },
          layout,
          () -> {
            if (profileDrift && ++profileReads > 1) return List.of();
            return profiles;
          },
          host,
          local,
          security,
          source);
    }
  }

  private static final class Calls implements DirectoryCalls {
    private final DirectoryCalls nativeCalls = LinuxDirectoryCalls.create();
    final Set<Integer> open = new HashSet<>();
    boolean failClose;

    public int openRoot() throws StorageIoException {
      int fd = nativeCalls.openRoot();
      open.add(fd);
      return fd;
    }

    public int openDirectory(int parent, String name) throws StorageIoException {
      int fd = nativeCalls.openDirectory(parent, name);
      open.add(fd);
      return fd;
    }

    public int openEntry(int parent, String name) throws StorageIoException {
      return nativeCalls.openEntry(parent, name);
    }

    public void close(int fd) throws StorageIoException {
      nativeCalls.close(fd);
      open.remove(fd);
      if (failClose) throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }

    public int createFile(int parent, String name) {
      throw new AssertionError(FIXTURE_READ_ONLY_A9812E1E);
    }

    public void createDirectory(int parent, String name) {
      throw new AssertionError(FIXTURE_READ_ONLY_A9812E1E);
    }

    public void publish(int directory, String part, String ready) {
      throw new AssertionError(FIXTURE_READ_ONLY_A9812E1E);
    }

    public void unlink(int directory, String name) {
      throw new AssertionError(FIXTURE_READ_ONLY_A9812E1E);
    }

    public void sync(int directory) {
      throw new AssertionError(FIXTURE_READ_ONLY_A9812E1E);
    }
  }
}
