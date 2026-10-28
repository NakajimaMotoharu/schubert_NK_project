package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.DIR;
import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.DUMP_HASH;
import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.GID;
import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.MANIFEST_HASH;
import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.UID;
import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.golden;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.backup.BackupManifest;
import dev.codex.schubert.nk.batch.platform.CleanupWorkerRequest;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.BatchStep;
import dev.codex.schubert.nk.batch.repository.BatchStepAttempt;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.nio.file.DirectoryIteratorException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.FileTime;
import java.nio.file.attribute.PosixFilePermissions;
import java.security.NoSuchAlgorithmException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** NK-BAT-001/BAK/BKO/UI251/SS341 6.7/343; SSC062/PG169; BAT226..241; independent017046. */
final class BackupManifestReaderTest {
  private static final String FIXTURE_READ_1_D82DE594 = "read#1";
  private static final String FIXTURE_CLOSECHANNEL_1_2CBD3D35 = "closeChannel#1";
  private static final String FIXTURE_ATTRIBUTES_1_3F7B5B66 = "attributes#1";
  private static final String FIXTURE_MANIFEST_JSON_0D4099EC = "MANIFEST.json";
  private static final String FIXTURE_SIZE_EB1E91E4 = "size";
  private static final String FIXTURE_READ_6F365882 = "read";
  private static final String FIXTURE_CLOSEDIRECTORY_11E791D5 = "closeDirectory";
  private static final String FIXTURE_CLOCK_49F3C56E = "clock";
  private static final String FIXTURE_PARENT_E31E1F44 = "parent";
  private static final String FIXTURE_CHILD_0AFBC7C3 = "child";
  private static final String FIXTURE_MODE_B6D5C2C3 = "mode";
  private static final String FIXTURE_UID_0C18F38C = "uid";
  private static final String FIXTURE_GID_0ACDD642 = "gid";
  private static final String FIXTURE_PUBLIC_PRIMARY_DBDAEFC3 = "public primary";
  private static final String FIXTURE_PUBLIC_UNKNOWN_5B451478 = "public unknown";
  @TempDir Path temporary;
  private static final UUID CLEANUP_ACTIVATION =
      UUID.fromString("11111111-2222-4333-8444-555555555555");

  private static CleanupWorkerRequest cleanupRequest(BackupManifest manifest, String digest) {
    return new CleanupWorkerRequest(
        manifest.run().id(), CLEANUP_ACTIVATION, manifest.run().cutoff(), digest);
  }

  /** PG331/SSC104/PT-OPS-BMR017: fixed literal digest and read-only 2-scan agreement. */
  @Test
  void cleanupClaimSelectsExactCanonicalManifest() throws Exception {
    try (var f = fixture()) {
      assertEquals(
          f.expected, reader(f).findCleanupClaims(cleanupRequest(f.expected, MANIFEST_HASH)));
      assertEquals(2, f.counts.get("openNames"));
      // The new shared claim reader must not weaken the existing bounded publisher contract.
      assertEquals(
          f.expected,
          reader(f)
              .readWithin(DIR, f.expected.databaseStep(), f.expected.configurationStep(), 100));
      var database = f.expected.databaseStep();
      var configuration = f.expected.configurationStep();
      denied(
          () ->
              reader(f)
                  .readWithin(
                      DIR,
                      new BatchStepAttempt(
                          database.id() + 1,
                          database.run(),
                          database.step(),
                          database.attempt(),
                          database.startedAt(),
                          false),
                      configuration,
                      100));
      denied(
          () ->
              reader(f)
                  .readWithin(
                      DIR,
                      database,
                      new BatchStepAttempt(
                          configuration.id() + 1,
                          configuration.run(),
                          configuration.step(),
                          configuration.attempt(),
                          configuration.startedAt(),
                          false),
                      100));
      f.released();
      f.unchanged();
    }
  }

  /** PG331/SSC104/PT-OPS-BMR018: old part/other run/unknown are not adopted or removed. */
  @Test
  void cleanupClaimIgnoresUnrelatedNames() throws Exception {
    try (var f = fixture()) {
      Files.createDirectory(f.parent.resolve(DIR + ".part"));
      Files.createDirectory(
          f.parent.resolve("20260913-000003-aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee"));
      Files.createDirectory(f.parent.resolve("legacy_unknown"));
      assertEquals(
          f.expected, reader(f).findCleanupClaims(cleanupRequest(f.expected, MANIFEST_HASH)));
      assertTrue(Files.isDirectory(f.parent.resolve(DIR + ".part")));
      assertEquals(0, f.counts.getOrDefault("create", 0));
      f.released();
      f.unchanged();
    }
  }

  /** PG331/SSC104/PT-OPS-BMR019: digest, run and cutoff each bind the same claim. */
  @Test
  void cleanupClaimRefusesOtherCorrelation() throws Exception {
    try (var f = fixture()) {
      denied(() -> reader(f).findCleanupClaims(cleanupRequest(f.expected, "0".repeat(64))));
      denied(
          () ->
              reader(f)
                  .findCleanupClaims(
                      new CleanupWorkerRequest(
                          f.expected.run().id(),
                          CLEANUP_ACTIVATION,
                          f.expected.run().cutoff().plusSeconds(1),
                          MANIFEST_HASH)));
      denied(
          () ->
              reader(f)
                  .findCleanupClaims(
                      new CleanupWorkerRequest(
                          UUID.fromString("aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee"),
                          CLEANUP_ACTIVATION,
                          f.expected.run().cutoff(),
                          MANIFEST_HASH)));
      f.released();
      f.unchanged();
    }
  }

  /** PG331/SSC104/PT-OPS-BMR020: a self-run suffix with noncanonical name is unsafe. */
  @Test
  void cleanupClaimRefusesMalformedSelfName() throws Exception {
    try (var f = fixture()) {
      Files.createDirectory(f.parent.resolve("bad-" + f.expected.run().id()));
      denied(() -> reader(f).findCleanupClaims(cleanupRequest(f.expected, MANIFEST_HASH)));
      f.released();
      f.unchanged();
    }
    try (var f = fixture()) {
      Files.createDirectory(f.parent.resolve("20260913_000002-" + f.expected.run().id()));
      denied(() -> reader(f).findCleanupClaims(cleanupRequest(f.expected, MANIFEST_HASH)));
      f.released();
      f.unchanged();
    }
  }

  /** PG331/SSC104/PT-OPS-BMR021: two directory inventories cannot drift. */
  @Test
  void cleanupClaimRefusesInventoryDrift() throws Exception {
    try (var f = fixture()) {
      AtomicInteger scans = new AtomicInteger();
      f.listing =
          held -> {
            int number = scans.incrementAndGet();
            return number == 1
                ? List.of(held.resolve(DIR))
                : List.of(held.resolve(DIR), held.resolve("legacy_unknown"));
          };
      denied(() -> reader(f).findCleanupClaims(cleanupRequest(f.expected, MANIFEST_HASH)));
      assertEquals(2, scans.get());
      f.released();
      f.unchanged();
    }
    try (var f = fixture()) {
      f.hook =
          (event, number) -> {
            if (event.equals("openNames") && number == 2)
              try {
                Files.setLastModifiedTime(f.parent, FileTime.fromMillis(1_000_000));
              } catch (IOException failure) {
                throw new AssertionError(failure);
              }
          };
      denied(() -> reader(f).findCleanupClaims(cleanupRequest(f.expected, MANIFEST_HASH)));
      f.released();
      f.unchanged();
    }
    for (boolean cutoff : List.of(false, true))
      try (var f = fixture()) {
        f.hook =
            (event, number) -> {
              if (event.equals("openDirectory") && number == 3)
                try {
                  Path manifest = f.child.resolve(FIXTURE_MANIFEST_JSON_0D4099EC);
                  String original = Files.readString(manifest, StandardCharsets.US_ASCII);
                  String changed =
                      cutoff
                          ? original.replace(
                              "\"cutoff\":\"2026-09-12T15:00:00.000000Z\"",
                              "\"cutoff\":\"2026-09-12T14:59:59.000000Z\"")
                          : original.replace(
                              "\"recipientSha256\":\"" + "0".repeat(64),
                              "\"recipientSha256\":\"" + "1".repeat(64));
                  assertNotEquals(original, changed);
                  Files.writeString(manifest, changed, StandardCharsets.US_ASCII);
                } catch (IOException failure) {
                  throw new AssertionError(failure);
                }
            };
        denied(() -> reader(f).findCleanupClaims(cleanupRequest(f.expected, MANIFEST_HASH)));
        f.released();
      }
  }

  /** PG331/SSC104/PT-OPS-BMR022: duplicate/oversize listing is not a selection. */
  @Test
  void cleanupClaimRefusesDuplicateOrUnboundedInventory() throws Exception {
    try (var f = fixture()) {
      f.listing = held -> List.of(held.resolve(DIR), held.resolve(DIR));
      denied(() -> reader(f).findCleanupClaims(cleanupRequest(f.expected, MANIFEST_HASH)));
      f.released();
    }
    try (var f = fixture()) {
      f.listing =
          held -> {
            List<Path> entries = new ArrayList<>();
            for (int index = 0; index <= 4096; index++) entries.add(held.resolve("entry-" + index));
            return entries;
          };
      denied(() -> reader(f).findCleanupClaims(cleanupRequest(f.expected, MANIFEST_HASH)));
      f.released();
    }
    for (List<Path> malformed : List.of(Arrays.asList((Path) null), List.of(Path.of("/tmp/else"))))
      try (var f = fixture()) {
        f.listing = held -> malformed;
        denied(() -> reader(f).findCleanupClaims(cleanupRequest(f.expected, MANIFEST_HASH)));
        f.released();
      }
  }

  /** PG331/SSC104/PT-OPS-BMR023: list/read/close uncertainty never returns claims. */
  @Test
  void cleanupClaimRefusesOwnedIoFailure() throws Exception {
    for (String event : List.of("openNames#1", "closeNames#1", "openChannel#1"))
      try (var f = fixture()) {
        f.extraFaults.add(event);
        denied(() -> reader(f).findCleanupClaims(cleanupRequest(f.expected, MANIFEST_HASH)));
        f.released();
        f.unchanged();
      }
    try (var f = fixture()) {
      f.nullNames = true;
      denied(() -> reader(f).findCleanupClaims(cleanupRequest(f.expected, MANIFEST_HASH)));
      f.released();
    }
    try (var f = fixture()) {
      f.effective = 1;
      denied(() -> reader(f).findCleanupClaims(cleanupRequest(f.expected, MANIFEST_HASH)));
      f.released();
    }
    try (var f = fixture()) {
      var noDigest =
          new BackupManifestReader(
              f.root,
              f,
              UID,
              GID,
              f,
              f::clock,
              () -> {
                throw new NoSuchAlgorithmException("synthetic provider unavailable");
              });
      denied(() -> noDigest.findCleanupClaims(cleanupRequest(f.expected, MANIFEST_HASH)));
      f.released();
    }
  }

  /** PG331/SSC104/PT-OPS-BMR024: null and same-reader parallel replay. */
  @Test
  void cleanupClaimNullAndConcurrentReplay() throws Exception {
    try (var f = fixture()) {
      BackupManifestReader source = reader(f);
      assertThrows(NullPointerException.class, () -> source.findCleanupClaims(null));
      try (var pool = Executors.newFixedThreadPool(2)) {
        var first =
            pool.submit(() -> source.findCleanupClaims(cleanupRequest(f.expected, MANIFEST_HASH)));
        var second =
            pool.submit(() -> source.findCleanupClaims(cleanupRequest(f.expected, MANIFEST_HASH)));
        assertEquals(f.expected, first.get());
        assertEquals(f.expected, second.get());
      }
      f.released();
      f.unchanged();
    }
    try (var f = fixture()) {
      Thread.currentThread().interrupt();
      try {
        denied(() -> reader(f).findCleanupClaims(cleanupRequest(f.expected, MANIFEST_HASH)));
        assertTrue(Thread.currentThread().isInterrupted());
      } finally {
        Thread.interrupted();
      }
      f.released();
    }
    try (var f = fixture();
        var names = new BackupManifestReader.NioIo().openNames(f.parent)) {
      assertTrue(
          java.util.stream.StreamSupport.stream(names.spliterator(), false)
              .anyMatch(path -> path.getFileName().toString().equals(DIR)));
      f.released();
    }
  }

  static final Map<String, Integer> INVENTORY =
      Map.ofEntries(
          Map.entry("attributes", 8),
          Map.entry("acl", 8),
          Map.entry("readonly", 8),
          Map.entry("openChannel", 1),
          Map.entry(FIXTURE_SIZE_EB1E91E4, 2),
          Map.entry(FIXTURE_READ_6F365882, 2),
          Map.entry("closeChannel", 1),
          Map.entry("openDirectory", 2),
          Map.entry(FIXTURE_CLOSEDIRECTORY_11E791D5, 2),
          Map.entry("openEntry", 2),
          Map.entry("closeEntry", 2),
          Map.entry("effectiveUid", 2),
          Map.entry(FIXTURE_CLOCK_49F3C56E, 63));

  @Test
  void canonicalRootManifest() throws Exception {
    try (var f = fixture()) {
      var actual = read(f);
      assertEquals(f.expected, actual);
      assertEquals(UUID.fromString("12345678-9abc-def0-8123-456789abcdef"), actual.run().id());
      assertEquals(Instant.parse("2026-09-12T15:00:02.123456Z"), actual.startedAt());
      assertEquals(90000, actual.databaseStep().id());
      assertEquals(90001, actual.configurationStep().id());
      assertEquals(26, actual.dump().size());
      assertEquals(DUMP_HASH, actual.dump().sha256());
      assertEquals(67, actual.configurationBytes());
      assertEquals(INVENTORY, f.counts);
      assertEquals(38, f.position);
      f.released();
      f.unchanged();
    }
  }

  @Test
  void nameAndFullHandleBinding() throws Exception {
    for (String name :
        List.of(
            "",
            ".",
            "..",
            DIR + ".part",
            "/" + DIR,
            DIR + "/x",
            DIR.toUpperCase(Locale.ROOT),
            "x".repeat(52),
            DIR.replace("20260913", "20260914"))) {
      try (var f = fixture()) {
        denied(
            () -> reader(f).read(name, f.expected.databaseStep(), f.expected.configurationStep()));
        f.released();
        f.unchanged();
      }
    }
    try (var f = fixture()) {
      Files.move(f.child, f.parent.resolve(DIR.replace("20260913", "20260914")));
      denied(
          () ->
              reader(f)
                  .read(
                      DIR.replace("20260913", "20260914"),
                      f.expected.databaseStep(),
                      f.expected.configurationStep()));
      f.released();
    }
    for (boolean database : List.of(false, true)) {
      try (var f = fixture()) {
        var original = database ? f.expected.databaseStep() : f.expected.configurationStep();
        List<BatchStepAttempt> changes =
            List.of(
                new BatchStepAttempt(
                    original.id() + 10,
                    original.run(),
                    original.step(),
                    original.attempt(),
                    original.startedAt(),
                    false),
                new BatchStepAttempt(
                    original.id(),
                    new BatchRun(new UUID(0, 1), original.run().cutoff()),
                    original.step(),
                    original.attempt(),
                    original.startedAt(),
                    false),
                new BatchStepAttempt(
                    original.id(),
                    new BatchRun(original.run().id(), original.run().cutoff().minusSeconds(1)),
                    original.step(),
                    original.attempt(),
                    original.startedAt(),
                    false),
                new BatchStepAttempt(
                    original.id(),
                    original.run(),
                    BatchStep.CLEAN_SESSION,
                    original.attempt(),
                    original.startedAt(),
                    false),
                new BatchStepAttempt(
                    original.id(),
                    original.run(),
                    original.step(),
                    original.attempt() + 1,
                    original.startedAt(),
                    false),
                new BatchStepAttempt(
                    original.id(),
                    original.run(),
                    original.step(),
                    original.attempt(),
                    original.startedAt().plusNanos(1000),
                    false));
        for (var changed : changes) {
          denied(
              () ->
                  reader(f)
                      .read(
                          DIR,
                          database ? changed : f.expected.databaseStep(),
                          database ? f.expected.configurationStep() : changed));
          f.released();
        }
      }
    }
  }

  @Test
  void directoryAndOwnerContracts() throws Exception {
    for (String role : List.of(FIXTURE_PARENT_E31E1F44, FIXTURE_CHILD_0AFBC7C3))
      for (var bad :
          List.<Map.Entry<String, Object>>of(
              Map.entry(FIXTURE_MODE_B6D5C2C3, 040750),
              Map.entry(FIXTURE_MODE_B6D5C2C3, 0100700),
              Map.entry(FIXTURE_UID_0C18F38C, 0),
              Map.entry(FIXTURE_GID_0ACDD642, 0),
              Map.entry("nlink", 1),
              Map.entry(FIXTURE_SIZE_EB1E91E4, -1L))) {
        try (var f = fixture()) {
          f.selectedRole = role;
          f.metadata = (r, m) -> m.put(bad.getKey(), bad.getValue());
          denied(() -> read(f));
          f.released();
          f.unchanged();
        }
      }
    try (var f = fixture()) {
      f.selectedRole = FIXTURE_CHILD_0AFBC7C3;
      f.metadata = (r, m) -> m.put("dev", Long.MIN_VALUE);
      denied(() -> read(f));
      f.released();
    }
    for (String role : List.of(FIXTURE_PARENT_E31E1F44, FIXTURE_CHILD_0AFBC7C3)) {
      try (var f = fixture()) {
        f.selectedRole = role;
        f.readonly = true;
        denied(() -> read(f));
        f.released();
      }
    }
    for (long invalid : new long[] {Long.MIN_VALUE, 0, 0x100000000L, Long.MAX_VALUE}) {
      try (var f = fixture()) {
        assertThrows(
            IllegalArgumentException.class,
            () -> new BackupManifestReader(f.root, f, invalid, GID));
        assertThrows(
            IllegalArgumentException.class,
            () -> new BackupManifestReader(f.root, f, UID, invalid));
      }
    }
    for (long boundary : new long[] {1, 0xffffffffL}) {
      try (var f = fixture()) {
        f.metadata =
            (r, m) -> {
              if (r.equals(FIXTURE_PARENT_E31E1F44) || r.equals(FIXTURE_CHILD_0AFBC7C3)) {
                m.put(FIXTURE_UID_0C18F38C, (int) boundary);
                m.put(FIXTURE_GID_0ACDD642, (int) boundary);
              }
            };
        var actual =
            new BackupManifestReader(f.root, f, boundary, boundary, f, f::clock)
                .read(DIR, f.expected.databaseStep(), f.expected.configurationStep());
        assertEquals(f.expected, actual);
        f.released();
      }
    }
    for (int point : new int[] {1, 2}) {
      try (var f = fixture()) {
        f.hook =
            (name, n) -> {
              if (name.equals("effectiveUid") && n == point) f.effective = 1000;
            };
        denied(() -> read(f));
        f.released();
      }
    }
  }

  @Test
  void manifestMetadataAndAcl() throws Exception {
    for (var bad :
        List.<Map.Entry<String, Object>>of(
            Map.entry(FIXTURE_MODE_B6D5C2C3, 0100640),
            Map.entry(FIXTURE_MODE_B6D5C2C3, 0120600),
            Map.entry(FIXTURE_UID_0C18F38C, (int) UID),
            Map.entry(FIXTURE_GID_0ACDD642, (int) GID),
            Map.entry("nlink", 2),
            Map.entry(FIXTURE_SIZE_EB1E91E4, 0L),
            Map.entry(FIXTURE_SIZE_EB1E91E4, 4097L),
            Map.entry("dev", Long.MIN_VALUE))) {
      try (var f = fixture()) {
        f.selectedRole = FIXTURE_MANIFEST_JSON_0D4099EC;
        f.metadata = (r, m) -> m.put(bad.getKey(), bad.getValue());
        denied(() -> read(f));
        f.released();
        f.unchanged();
      }
    }
    for (String field :
        List.of(
            FIXTURE_MODE_B6D5C2C3,
            FIXTURE_UID_0C18F38C,
            FIXTURE_GID_0ACDD642,
            "nlink",
            FIXTURE_SIZE_EB1E91E4,
            "dev",
            "ino",
            "lastModifiedTime",
            "ctime"))
      for (boolean missing : List.of(false, true)) {
        try (var f = fixture()) {
          f.metadata =
              (r, m) -> {
                if (missing) m.remove(field);
                else m.put(field, "invalid");
              };
          denied(() -> read(f));
          f.released();
        }
      }
    for (String role :
        List.of(FIXTURE_PARENT_E31E1F44, FIXTURE_CHILD_0AFBC7C3, FIXTURE_MANIFEST_JSON_0D4099EC))
      for (byte[] acl : Arrays.asList(null, new byte[1], new byte[44])) {
        try (var f = fixture()) {
          f.selectedRole = role;
          f.acl = acl;
          denied(() -> read(f));
          f.released();
        }
      }
    try (var f = fixture()) {
      f.selectedRole = FIXTURE_MANIFEST_JSON_0D4099EC;
      f.readonly = true;
      denied(() -> read(f));
      f.released();
    }
  }

  @Test
  void rootAndChildRebinding() throws Exception {
    // Independent order: parent1, child2, file3/4/5, child6/7, parent8.
    for (int point : new int[] {6, 7, 8}) {
      try (var f = fixture()) {
        f.hook =
            (name, n) -> {
              if (name.equals("attributes") && n == point)
                f.metadata = (r, m) -> m.put("ino", ((Long) m.get("ino")) + 1);
            };
        denied(() -> read(f));
        f.released();
      }
    }
    try (var f = fixture()) {
      f.hook =
          (name, n) -> {
            if (name.equals("openDirectory") && n == 2)
              io(
                  () -> {
                    Files.move(f.child, f.parent.resolve("saved-generation"));
                    Files.createDirectory(f.child);
                    Files.setPosixFilePermissions(
                        f.child, PosixFilePermissions.fromString("rwx------"));
                  });
          };
      denied(() -> read(f));
      f.released();
      assertArrayEquals(
          golden(), Files.readAllBytes(f.parent.resolve("saved-generation/MANIFEST.json")));
    }
    try (var f = fixture()) {
      f.hook =
          (name, n) -> {
            if (name.equals(FIXTURE_CLOSEDIRECTORY_11E791D5) && n == 2)
              io(() -> Files.writeString(f.parent.resolve("interference"), "public"));
          };
      denied(() -> read(f));
      f.released();
      f.unchanged();
    }
  }

  @Test
  void manifestReplacementAndMutation() throws Exception {
    for (String mode : List.of("replacement", "same-bytes", "mtime", "permission"))
      try (var f = fixture()) {
        f.hook =
            (name, n) -> {
              if (name.equals("openEntry") && n == 2)
                io(
                    () -> {
                      Path p = f.child.resolve(FIXTURE_MANIFEST_JSON_0D4099EC);
                      switch (mode) {
                        case "replacement" -> {
                          Files.move(p, f.child.resolve("saved"));
                          Files.write(p, golden());
                          Files.setPosixFilePermissions(
                              p, PosixFilePermissions.fromString("rw-------"));
                        }
                        case "same-bytes" -> {
                          Files.write(p, golden());
                          Files.setLastModifiedTime(p, FileTime.fromMillis(1));
                        }
                        case "mtime" -> Files.setLastModifiedTime(p, FileTime.fromMillis(1));
                        case "permission" ->
                            Files.setPosixFilePermissions(
                                p, PosixFilePermissions.fromString("rw-r-----"));
                        default -> throw new AssertionError();
                      }
                    });
            };
        denied(() -> read(f));
        assertEquals(2, f.counts.get("openEntry"));
        f.released();
      }
    for (boolean hard : List.of(false, true))
      try (var f = fixture()) {
        Path p = f.child.resolve(FIXTURE_MANIFEST_JSON_0D4099EC);
        Path saved = f.child.resolve("saved");
        Files.move(p, saved);
        if (hard) Files.createLink(p, saved);
        else Files.createSymbolicLink(p, Path.of("saved"));
        denied(() -> read(f));
        f.released();
        assertArrayEquals(golden(), Files.readAllBytes(saved));
      }
    try (var f = fixture()) {
      f.hook =
          (name, n) -> {
            if (name.equals(FIXTURE_READ_6F365882) && n == 2)
              io(
                  () -> {
                    Files.write(f.child.resolve(FIXTURE_MANIFEST_JSON_0D4099EC), golden());
                    Files.setLastModifiedTime(
                        f.child.resolve(FIXTURE_MANIFEST_JSON_0D4099EC), FileTime.fromMillis(1));
                  });
          };
      denied(() -> read(f));
      f.released();
    }
  }

  @Test
  void sizeAndReadBoundaries() throws Exception {
    for (int size : new int[] {0, 1, 4096, 4097})
      try (var f = fixture()) {
        Files.write(f.child.resolve(FIXTURE_MANIFEST_JSON_0D4099EC), new byte[size]);
        denied(() -> read(f));
        f.released();
      }
    for (String mode : List.of("zero", "short", "count", "position", "extra", "eof-position"))
      try (var f = fixture()) {
        f.selectedRole = FIXTURE_MANIFEST_JSON_0D4099EC;
        f.readMode = mode;
        denied(() -> read(f));
        f.released();
      }
    for (String mode : List.of("first", "last"))
      try (var f = fixture()) {
        f.selectedRole = FIXTURE_MANIFEST_JSON_0D4099EC;
        f.sizeMode = mode;
        denied(() -> read(f));
        f.released();
      }
    for (int chunk : new int[] {1, 7, 963, 964})
      try (var f = fixture()) {
        f.smallRead = chunk;
        assertEquals(f.expected, read(f));
        assertEquals((964 + chunk - 1) / chunk + 1, f.counts.get(FIXTURE_READ_6F365882));
        f.released();
        f.unchanged();
      }
  }

  @Test
  void canonicalByteRejection() throws Exception {
    for (byte[] invalid :
        List.of(
            new byte[] {(byte) 0xff},
            new byte[] {0},
            "{}\n".getBytes(java.nio.charset.StandardCharsets.US_ASCII),
            (new String(golden(), java.nio.charset.StandardCharsets.US_ASCII) + "\n")
                .getBytes(java.nio.charset.StandardCharsets.US_ASCII))) {
      try (var f = fixture()) {
        Files.write(f.child.resolve(FIXTURE_MANIFEST_JSON_0D4099EC), invalid);
        var failed = denied(() -> read(f));
        assertNull(failed.getCause());
        f.released();
      }
    }
    // Still canonical, but a different genuine full handle must not bind to caller's pair.
    try (var f = fixture()) {
      String changed =
          new String(golden(), java.nio.charset.StandardCharsets.US_ASCII)
              .replace("\"id\":90000,", "\"id\":90002,");
      Files.writeString(f.child.resolve(FIXTURE_MANIFEST_JSON_0D4099EC), changed);
      denied(() -> read(f));
      f.released();
    }
  }

  @Test
  void everyIoFailure() throws Exception {
    for (int position = 1; position <= 38; position++)
      try (var f = fixture()) {
        f.faultAt = position;
        denied(() -> read(f));
        assertTrue(f.position >= position);
        f.released();
        f.unchanged();
      }
  }

  @Test
  void closeFailurePrecedence() throws Exception {
    // BUG195: same unknown instance must never become TWR self-suppression failure.
    for (String close : List.of("closeChannel", "closeEntry", FIXTURE_CLOSEDIRECTORY_11E791D5))
      for (Throwable primary :
          List.of(
              new IllegalStateException("public repeated"),
              new NullPointerException("public repeated"),
              new AssertionError("public repeated"))) {
        try (var f = fixture()) {
          f.extraFaults.add(FIXTURE_READ_1_D82DE594);
          f.faultTypes.put(FIXTURE_READ_1_D82DE594, primary);
          f.extraFaults.add(close + "#1");
          f.faultTypes.put(close + "#1", primary);
          assertSame(primary, assertThrows(primary.getClass(), () -> read(f)));
          assertEquals(1, primary.getSuppressed().length);
          assertInstanceOf(StorageIoException.class, primary.getSuppressed()[0]);
          f.released();
        }
      }
    try (var f = fixture()) {
      var fatal = new AssertionError("public close fatal");
      f.extraFaults.add(FIXTURE_READ_1_D82DE594);
      f.extraFaults.add(FIXTURE_CLOSECHANNEL_1_2CBD3D35);
      f.faultTypes.put(FIXTURE_CLOSECHANNEL_1_2CBD3D35, fatal);
      assertSame(fatal, assertThrows(AssertionError.class, () -> read(f)));
      f.released();
    }
    for (String close : List.of("closeChannel", "closeEntry", FIXTURE_CLOSEDIRECTORY_11E791D5))
      for (int kind = 0; kind < 4; kind++)
        try (var f = fixture()) {
          Throwable primary =
              switch (kind) {
                case 0 -> new IOException(FIXTURE_PUBLIC_PRIMARY_DBDAEFC3);
                case 1 -> new IllegalStateException(FIXTURE_PUBLIC_PRIMARY_DBDAEFC3);
                case 2 -> new NullPointerException(FIXTURE_PUBLIC_PRIMARY_DBDAEFC3);
                default -> new AssertionError(FIXTURE_PUBLIC_PRIMARY_DBDAEFC3);
              };
          f.extraFaults.add(FIXTURE_READ_1_D82DE594);
          f.faultTypes.put(FIXTURE_READ_1_D82DE594, primary);
          f.extraFaults.add(close + "#1");
          if (kind == 0) denied(() -> read(f));
          else {
            Throwable actual = assertThrows(primary.getClass(), () -> read(f));
            assertSame(primary, actual);
            assertEquals(1, actual.getSuppressed().length);
            Throwable secondary = actual.getSuppressed()[0];
            assertInstanceOf(StorageIoException.class, secondary);
            assertNull(secondary.getCause());
            assertEquals("transfer storage operation failed", secondary.getMessage());
          }
          assertEquals(1, f.counts.get(FIXTURE_READ_6F365882));
          assertTrue(f.counts.get(close) >= 1);
          f.released();
          f.unchanged();
        }
    for (Throwable cleanup :
        List.of(
            new IllegalStateException("public cleanup"),
            new NullPointerException("public cleanup"),
            new AssertionError("public cleanup"))) {
      try (var f = fixture()) {
        f.extraFaults.add(FIXTURE_CLOSECHANNEL_1_2CBD3D35);
        f.faultTypes.put(FIXTURE_CLOSECHANNEL_1_2CBD3D35, cleanup);
        assertSame(cleanup, assertThrows(cleanup.getClass(), () -> read(f)));
        f.released();
      }
    }
  }

  @Test
  void timeAndInterrupt() throws Exception {
    for (long elapsed : new long[] {-1, 1800000000000L, 1800000000001L})
      try (var f = fixture()) {
        f.hook =
            (name, n) -> {
              if (name.equals(FIXTURE_CLOCK_49F3C56E) && n == 2) f.clockValue = 100 + elapsed;
            };
        denied(() -> read(f));
        f.released();
      }
    try (var f = fixture()) {
      f.hook =
          (name, n) -> {
            if (name.equals(FIXTURE_CLOCK_49F3C56E) && n == 2) f.clockValue = 100 + 1799999999999L;
          };
      assertEquals(f.expected, read(f));
      f.released();
    }
    try (var f = fixture()) {
      f.clockValue = Long.MAX_VALUE - 50;
      f.hook =
          (name, n) -> {
            if (name.equals(FIXTURE_CLOCK_49F3C56E) && n == 2) f.clockValue = Long.MIN_VALUE + 49;
          };
      assertEquals(f.expected, read(f));
      f.released();
    }
    for (int point = 1; point <= 63; point++) {
      int selected = point;
      try (var f = fixture()) {
        f.hook =
            (name, n) -> {
              if (name.equals(FIXTURE_CLOCK_49F3C56E) && n == selected)
                Thread.currentThread().interrupt();
            };
        try {
          denied(() -> read(f));
          assertTrue(Thread.currentThread().isInterrupted());
        } finally {
          Thread.interrupted();
        }
        assertEquals(selected, f.counts.get(FIXTURE_CLOCK_49F3C56E));
        f.released();
        f.unchanged();
      }
    }
    try (var f = fixture()) {
      Thread.currentThread().interrupt();
      try {
        denied(() -> read(f));
        assertTrue(Thread.currentThread().isInterrupted());
      } finally {
        Thread.interrupted();
      }
      f.released();
    }
  }

  @Test
  void nullAndUnknownProviders() throws Exception {
    try (var f = fixture()) {
      assertThrows(NullPointerException.class, () -> new BackupManifestReader(null, f, UID, GID));
      assertThrows(
          NullPointerException.class, () -> new BackupManifestReader(f.root, null, UID, GID));
      assertThrows(
          NullPointerException.class,
          () -> new BackupManifestReader(f.root, f, UID, GID, null, f::clock));
      assertThrows(
          NullPointerException.class, () -> new BackupManifestReader(f.root, f, UID, GID, f, null));
      assertThrows(
          NullPointerException.class,
          () -> reader(f).read(null, f.expected.databaseStep(), f.expected.configurationStep()));
      assertThrows(
          NullPointerException.class,
          () -> reader(f).read(DIR, null, f.expected.configurationStep()));
      assertThrows(
          NullPointerException.class, () -> reader(f).read(DIR, f.expected.databaseStep(), null));
      f.released();
    }
    for (boolean attrs : List.of(false, true))
      try (var f = fixture()) {
        f.nullAttributes = attrs;
        f.nullChannel = !attrs;
        denied(() -> read(f));
        f.released();
      }
    for (String point : List.of("attributes", "openChannel", FIXTURE_READ_6F365882))
      for (Throwable problem :
          List.of(
              new IllegalArgumentException(FIXTURE_PUBLIC_UNKNOWN_5B451478),
              new IllegalStateException(FIXTURE_PUBLIC_UNKNOWN_5B451478),
              new NullPointerException(FIXTURE_PUBLIC_UNKNOWN_5B451478),
              new AssertionError(FIXTURE_PUBLIC_UNKNOWN_5B451478))) {
        try (var f = fixture()) {
          f.extraFaults.add(point + "#1");
          f.faultTypes.put(point + "#1", problem);
          assertSame(problem, assertThrows(problem.getClass(), () -> read(f)));
          f.released();
          f.unchanged();
        }
      }
    try (var f = fixture()) {
      f.extraFaults.add(FIXTURE_ATTRIBUTES_1_3F7B5B66);
      f.faultTypes.put(
          FIXTURE_ATTRIBUTES_1_3F7B5B66, new UnsupportedOperationException("public unavailable"));
      denied(() -> read(f));
      f.released();
    }
    try (var f = fixture()) {
      f.extraFaults.add(FIXTURE_ATTRIBUTES_1_3F7B5B66);
      f.faultTypes.put(
          FIXTURE_ATTRIBUTES_1_3F7B5B66,
          new DirectoryIteratorException(new IOException("public unavailable")));
      denied(() -> read(f));
      f.released();
    }
  }

  @Test
  void borrowedRootAndClosed() throws Exception {
    try (var f = fixture()) {
      var reader = reader(f);
      assertEquals(
          f.expected, reader.read(DIR, f.expected.databaseStep(), f.expected.configurationStep()));
      f.released();
      assertEquals(
          f.expected, reader.read(DIR, f.expected.databaseStep(), f.expected.configurationStep()));
      f.released();
      f.unchanged();
      f.tracking = false;
      f.root.close();
      f.tracking = true;
      denied(() -> reader.read(DIR, f.expected.databaseStep(), f.expected.configurationStep()));
      assertTrue(f.directories.isEmpty());
      assertEquals(0, f.channelCount);
    }
  }

  @Test
  void concurrentSerializedReaders() throws Exception {
    try (var f = fixture();
        var pool = Executors.newVirtualThreadPerTaskExecutor()) {
      var reader = reader(f);
      var calls = new ArrayList<Future<BackupManifest>>();
      for (int i = 0; i < 64; i++)
        calls.add(
            pool.submit(
                () -> reader.read(DIR, f.expected.databaseStep(), f.expected.configurationStep())));
      for (var future : calls) assertEquals(f.expected, future.get());
      assertEquals(64, f.counts.get("openChannel"));
      f.released();
      f.unchanged();
      f.faultAt = f.position + 1;
      denied(() -> reader.read(DIR, f.expected.databaseStep(), f.expected.configurationStep()));
      assertEquals(
          f.expected, reader.read(DIR, f.expected.databaseStep(), f.expected.configurationStep()));
      f.released();
    }
  }

  @Test
  void readOnlyNativeAdapters() throws Exception {
    try (var f = fixture()) {
      var nio = new BackupManifestReader.NioIo();
      var attributes = nio.attributes(f.child.resolve(FIXTURE_MANIFEST_JSON_0D4099EC));
      assertEquals(964L, attributes.get(FIXTURE_SIZE_EB1E91E4));
      assertEquals(0100600, attributes.get(FIXTURE_MODE_B6D5C2C3));
      try (var channel = nio.open(f.child.resolve(FIXTURE_MANIFEST_JSON_0D4099EC))) {
        var buffer = ByteBuffer.allocate(965);
        assertEquals(964, channel.read(buffer));
        assertEquals(-1, channel.read(buffer));
        assertArrayEquals(golden(), Arrays.copyOf(buffer.array(), 964));
      }
      // Public factory uses native attributes; synthetic root security does not change actual UID.
      var nativeReader = new BackupManifestReader(f.root, f, UID, GID);
      denied(
          () -> nativeReader.read(DIR, f.expected.databaseStep(), f.expected.configurationStep()));
      f.released();
      f.unchanged();
    }
  }

  @Test
  void independentTraceAndDownstream() throws Exception {
    try (var f = fixture()) {
      var value = read(f);
      f.released();
      var digest = f.verifier().verify(value);
      assertEquals(MANIFEST_HASH, digest.sha256());
      f.released();
      f.unchanged();
      Path target = Path.of("target", "backup-reader-traces");
      Files.createDirectories(target);
      Files.writeString(
          target.resolve("PT-BAT-241-reader.txt"),
          value.directoryName()
              + "\n"
              + value.databaseStep().id()
              + "|"
              + value.configurationStep().id()
              + "\n"
              + value.dump().size()
              + "|"
              + value.configurationBytes()
              + "\n"
              + digest.size()
              + "|"
              + digest.sha256()
              + "\n");
    }
  }

  BackupArtifactFixture fixture() throws Exception {
    return new BackupArtifactFixture(temporary);
  }

  static BackupManifestReader reader(BackupArtifactFixture f) {
    return new BackupManifestReader(f.root, f, UID, GID, f, f::clock);
  }

  static BackupManifest read(BackupArtifactFixture f) throws Exception {
    return reader(f).read(DIR, f.expected.databaseStep(), f.expected.configurationStep());
  }

  static StorageIoException denied(org.junit.jupiter.api.function.Executable action) {
    var failure = assertThrows(StorageIoException.class, action);
    assertEquals(StorageIoException.Reason.UNAVAILABLE, failure.reason());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    return failure;
  }

  @FunctionalInterface
  interface IoAction {
    void run() throws IOException;
  }

  static void io(IoAction action) {
    try {
      action.run();
    } catch (IOException e) {
      throw new UncheckedIOException(e);
    }
  }
}
