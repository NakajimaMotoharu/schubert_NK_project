package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.CONFIG_HASH;
import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.COUNTS;
import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.CREDS_HASH;
import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.DIR;
import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.DUMP_HASH;
import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.GID;
import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.MANIFEST_HASH;
import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.NAMES;
import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.UID;
import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.golden;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.backup.BackupFileDigest;
import dev.codex.schubert.nk.batch.backup.BackupManifestFixture;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.FileTime;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** BAK/BKO/UI251/SS341 6.5/343 5.3; SSC059/PG166; BAT194..209, see 017/038. */
final class BackupArtifactVerifierTest {
  private static final String FIXTURE_SCHUBERT_NK_DUMP_96644B79 = "schubert_nk.dump";
  private static final String FIXTURE_CONFIG_TAR_7AD1B394 = "config.tar";
  private static final String FIXTURE_MANIFEST_JSON_0D4099EC = "MANIFEST.json";
  private static final String FIXTURE_PART_92B0D5FC = ".part";
  private static final String FIXTURE_PARENT_E31E1F44 = "parent";
  private static final String FIXTURE_INO_4BE7C1E0 = "ino";
  private static final String FIXTURE_DEV_8A17302D = "dev";
  private static final String FIXTURE_SIZE_EB1E91E4 = "size";
  private static final String FIXTURE_EXTRA_ED1BF81A = "extra";
  private static final String FIXTURE_READ_6F365882 = "read";
  private static final String FIXTURE_UID_0C18F38C = "uid";
  private static final String FIXTURE_CHILD_0AFBC7C3 = "child";
  private static final String FIXTURE_MODE_B6D5C2C3 = "mode";
  private static final String FIXTURE_GID_0ACDD642 = "gid";
  private static final String FIXTURE_CLOCK_49F3C56E = "clock";
  @TempDir Path temporary;

  /** PT-BAK-2740-001: pending163/171/182/188/229, independent inode/UID races. */
  @Test
  void backup2740001PendingRejectsEveryAdmissionDriftAndKeepsAllPublicBytes() throws Exception {
    var request =
        new dev.codex.schubert.nk.batch.platform.BackupWorkerRequest(
            UUID.fromString("12345678-9abc-def0-8123-456789abcdef"),
            java.time.Instant.parse("2026-09-12T15:00:02Z"));
    for (String bad :
        List.of(
            "nonroot",
            "childDevice",
            "negativeSize",
            "captureDrift",
            "fileDevice",
            "parentDrift",
            "lateNonroot")) {
      for (String selected :
          List.of(
              FIXTURE_SCHUBERT_NK_DUMP_96644B79,
              FIXTURE_CONFIG_TAR_7AD1B394,
              "credentials.tar.age")) {
        try (var f = fixture()) {
          Files.delete(f.child.resolve(FIXTURE_MANIFEST_JSON_0D4099EC));
          Path pending = f.parent.resolve(DIR + FIXTURE_PART_92B0D5FC);
          Files.move(f.child, pending);
          Map<String, byte[]> before = new HashMap<>();
          for (String name :
              List.of(
                  FIXTURE_SCHUBERT_NK_DUMP_96644B79,
                  FIXTURE_CONFIG_TAR_7AD1B394,
                  "credentials.tar.age"))
            before.put(name, Files.readAllBytes(pending.resolve(name)));
          var parentReads = new AtomicInteger();
          var fileReads = new AtomicInteger();
          if (bad.equals("nonroot")) f.effective = 1;
          f.metadata =
              (role, values) -> {
                if (role.equals(FIXTURE_PARENT_E31E1F44) && parentReads.incrementAndGet() == 2) {
                  if (bad.equals("parentDrift"))
                    values.put(FIXTURE_INO_4BE7C1E0, (Long) values.get(FIXTURE_INO_4BE7C1E0) + 1);
                  if (bad.equals("lateNonroot")) f.effective = 1;
                }
                if (bad.equals("childDevice") && role.equals(DIR + FIXTURE_PART_92B0D5FC))
                  values.put(FIXTURE_DEV_8A17302D, (Long) values.get(FIXTURE_DEV_8A17302D) + 1);
                if (role.equals(selected)) {
                  int count = fileReads.incrementAndGet();
                  if (bad.equals("negativeSize")) values.put(FIXTURE_SIZE_EB1E91E4, -1L);
                  if (bad.equals("fileDevice"))
                    values.put(FIXTURE_DEV_8A17302D, (Long) values.get(FIXTURE_DEV_8A17302D) + 1);
                  if (bad.equals("captureDrift") && count == 2)
                    values.put(FIXTURE_INO_4BE7C1E0, (Long) values.get(FIXTURE_INO_4BE7C1E0) + 1);
                }
              };
          var error =
              assertThrows(StorageIoException.class, () -> f.verifier().observePending(request));
          assertEquals(StorageIoException.Reason.UNAVAILABLE, error.reason(), bad + selected);
          assertNull(error.getCause());
          for (var value : before.entrySet())
            assertArrayEquals(
                value.getValue(), Files.readAllBytes(pending.resolve(value.getKey())));
          assertFalse(Files.exists(pending.resolve(FIXTURE_MANIFEST_JSON_0D4099EC)));
          if (bad.equals("captureDrift")) assertEquals(2, fileReads.get());
          if (bad.equals("parentDrift") || bad.equals("lateNonroot"))
            assertEquals(2, parentReads.get());
          f.released();
        }
      }
    }
  }

  @Test
  void pendingContentUsesIndependentLiteralHashesWithoutGrantingSuccess() throws Exception {
    var request =
        new dev.codex.schubert.nk.batch.platform.BackupWorkerRequest(
            UUID.fromString("12345678-9abc-def0-8123-456789abcdef"),
            java.time.Instant.parse("2026-09-12T15:00:02Z"));
    try (var f = fixture()) {
      Files.delete(f.child.resolve(FIXTURE_MANIFEST_JSON_0D4099EC));
      Files.move(f.child, f.parent.resolve(DIR + FIXTURE_PART_92B0D5FC));
      var actual = f.verifier().observePending(request);
      assertEquals(new BackupFileDigest(26, DUMP_HASH), actual.dump());
      assertEquals(new BackupFileDigest(35, CONFIG_HASH), actual.configuration());
      assertEquals(new BackupFileDigest(32, CREDS_HASH), actual.credentials());
      assertFalse(Files.exists(f.parent.resolve(DIR + ".part/MANIFEST.json")));
      f.released();
    }
    for (String bad :
        List.of(
            "manifest",
            "missing",
            FIXTURE_EXTRA_ED1BF81A,
            "wrongRequest",
            "owner",
            "drift",
            FIXTURE_READ_6F365882)) {
      try (var f = fixture()) {
        Files.delete(f.child.resolve(FIXTURE_MANIFEST_JSON_0D4099EC));
        Path pending = f.parent.resolve(DIR + FIXTURE_PART_92B0D5FC);
        Files.move(f.child, pending);
        switch (bad) {
          case "manifest" ->
              Files.writeString(pending.resolve(FIXTURE_MANIFEST_JSON_0D4099EC), "{}\n");
          case "missing" -> Files.delete(pending.resolve(FIXTURE_CONFIG_TAR_7AD1B394));
          case FIXTURE_EXTRA_ED1BF81A ->
              Files.writeString(pending.resolve(FIXTURE_EXTRA_ED1BF81A), "public");
          case "owner" ->
              f.metadata =
                  (role, values) -> {
                    if (role.equals(FIXTURE_CONFIG_TAR_7AD1B394))
                      values.put(FIXTURE_UID_0C18F38C, 1);
                  };
          case "drift" ->
              f.metadata =
                  (role, values) -> {
                    if (role.equals(FIXTURE_CONFIG_TAR_7AD1B394)
                        && f.counts.getOrDefault(FIXTURE_READ_6F365882, 0) >= 4)
                      values.put(
                          FIXTURE_INO_4BE7C1E0, ((Long) values.get(FIXTURE_INO_4BE7C1E0)) + 1);
                  };
          case FIXTURE_READ_6F365882 -> f.nullChannel = true;
          default -> {}
        }
        var chosen =
            bad.equals("wrongRequest")
                ? new dev.codex.schubert.nk.batch.platform.BackupWorkerRequest(
                    request.run(), request.started().plusSeconds(1))
                : request;
        failure(() -> f.verifier().observePending(chosen));
        assertTrue(Files.isDirectory(pending), bad);
        f.released();
      }
    }
    assertThrows(
        NullPointerException.class,
        () -> {
          try (var f = fixture()) {
            f.verifier().observePending(null);
          }
        });
  }

  @Test
  void trustedBundleAndManifestDigest() throws Exception {
    try (var f = fixture()) {
      BackupFileDigest actual = f.verifier().verify(f.expected);
      assertEquals(964, actual.size());
      assertEquals(MANIFEST_HASH, actual.sha256());
      assertEquals(93, f.expected.totalBytes());
      assertEquals(67, f.expected.configurationBytes());
      assertEquals(COUNTS, f.counts);
      assertEquals(123, f.position);
      f.released();
      f.unchanged();
      Path traces = Path.of("target", "backup-artifact-traces");
      Files.createDirectories(traces);
      Files.writeString(
          traces.resolve("PT-BAT-194-digest.txt"), actual.size() + "|" + actual.sha256() + "\n");
    }
    try (var f = fixture()) {
      // Default SHA-256 factory with injected IO/clock, not a production-generated expected.
      var actual = new BackupArtifactVerifier(f.root, f, UID, GID, f, f::clock).verify(f.expected);
      assertEquals(MANIFEST_HASH, actual.sha256());
      f.released();
    }
  }

  @Test
  void completeFileSetAndCanonicalName() throws Exception {
    for (int option = 0; option < 6; option++) {
      final int chosen = option;
      try (var f = fixture()) {
        f.listing =
            held -> {
              var paths = new ArrayList<>(NAMES.stream().map(held::resolve).toList());
              switch (chosen) {
                case 0 -> paths.remove(3);
                case 1 -> paths.add(held.resolve("unknown"));
                case 2 -> paths.set(3, paths.get(0));
                case 3 -> paths.set(3, null);
                case 4 -> paths.set(3, Path.of("relative"));
                case 5 -> paths.set(3, held.resolve("unknown"));
                default -> throw new AssertionError();
              }
              return paths;
            };
        failure(() -> f.verifier().verify(f.expected));
        f.released();
        f.unchanged();
      }
    }
    try (var f = fixture()) {
      Files.move(f.child, f.parent.resolve(DIR + FIXTURE_PART_92B0D5FC));
      failure(() -> f.verifier().verify(f.expected));
      assertTrue(Files.exists(f.parent.resolve(DIR + FIXTURE_PART_92B0D5FC)));
      f.released();
    }
    try (var f = fixture()) {
      Files.createDirectory(f.parent.resolve("public-other-generation"));
      assertEquals(MANIFEST_HASH, f.verifier().verify(f.expected).sha256());
      assertTrue(Files.isDirectory(f.parent.resolve("public-other-generation")));
      f.released();
      f.unchanged();
    }
  }

  @Test
  void directoryAndOwnerContracts() throws Exception {
    for (String role : List.of(FIXTURE_PARENT_E31E1F44, FIXTURE_CHILD_0AFBC7C3))
      for (var bad :
          List.<Map.Entry<String, Object>>of(
              Map.entry(FIXTURE_MODE_B6D5C2C3, 040750), Map.entry(FIXTURE_MODE_B6D5C2C3, 0100700),
              Map.entry(FIXTURE_UID_0C18F38C, 0), Map.entry(FIXTURE_GID_0ACDD642, 0),
              Map.entry("nlink", 1), Map.entry(FIXTURE_SIZE_EB1E91E4, -1L))) {
        try (var f = fixture()) {
          f.selectedRole = role;
          f.metadata = (name, values) -> values.put(bad.getKey(), bad.getValue());
          failure(() -> f.verifier().verify(f.expected));
          f.released();
          f.unchanged();
        }
      }
    for (String role : List.of(FIXTURE_PARENT_E31E1F44, FIXTURE_CHILD_0AFBC7C3)) {
      try (var f = fixture()) {
        f.selectedRole = role;
        f.readonly = true;
        failure(() -> f.verifier().verify(f.expected));
        f.released();
      }
    }
    try (var f = fixture()) {
      f.selectedRole = FIXTURE_CHILD_0AFBC7C3;
      f.metadata =
          (role, values) ->
              values.put(FIXTURE_DEV_8A17302D, ((Long) values.get(FIXTURE_DEV_8A17302D)) + 1);
      failure(() -> f.verifier().verify(f.expected));
      f.released();
    }
    for (long id : new long[] {Long.MIN_VALUE, 0, 0x100000000L, Long.MAX_VALUE})
      try (var f = fixture()) {
        assertThrows(
            IllegalArgumentException.class, () -> new BackupArtifactVerifier(f.root, f, id, GID));
        assertThrows(
            IllegalArgumentException.class, () -> new BackupArtifactVerifier(f.root, f, UID, id));
      }
    for (long id : new long[] {1, 0xffffffffL})
      try (var f = fixture()) {
        var verifier = new BackupArtifactVerifier(f.root, f, id, id, f, f::digest, f::clock);
        f.metadata =
            (role, values) -> {
              if (role.equals(FIXTURE_PARENT_E31E1F44)
                  || role.equals(FIXTURE_CHILD_0AFBC7C3)
                  || role.equals(FIXTURE_SCHUBERT_NK_DUMP_96644B79)) {
                values.put(FIXTURE_UID_0C18F38C, (int) id);
                values.put(FIXTURE_GID_0ACDD642, (int) id);
              }
            };
        assertEquals(MANIFEST_HASH, verifier.verify(f.expected).sha256());
        f.released();
      }
    try (var f = fixture()) {
      f.effective = 1000;
      failure(() -> f.verifier().verify(f.expected));
      assertEquals(0, f.channelCount);
      f.released();
    }
    try (var f = fixture()) {
      f.hook =
          (name, n) -> {
            if (name.equals("effectiveUid") && n == 2) f.effective = 1000;
          };
      failure(() -> f.verifier().verify(f.expected));
      f.released();
    }
  }

  @Test
  void perFileMetadataAndAcl() throws Exception {
    for (String name : NAMES) {
      for (var bad :
          List.<Map.Entry<String, Object>>of(
              Map.entry(FIXTURE_MODE_B6D5C2C3, 0100640),
              Map.entry(FIXTURE_MODE_B6D5C2C3, 0120600),
              Map.entry(FIXTURE_UID_0C18F38C, 99),
              Map.entry(FIXTURE_GID_0ACDD642, 99),
              Map.entry("nlink", 2),
              Map.entry(FIXTURE_SIZE_EB1E91E4, 0L),
              Map.entry(FIXTURE_DEV_8A17302D, Long.MIN_VALUE))) {
        try (var f = fixture()) {
          f.selectedRole = name;
          f.metadata = (role, values) -> values.put(bad.getKey(), bad.getValue());
          failure(() -> f.verifier().verify(f.expected));
          f.released();
          f.unchanged();
        }
      }
      for (byte[] acl : Arrays.asList(null, new byte[1], new byte[44])) {
        try (var f = fixture()) {
          f.selectedRole = name;
          f.acl = acl;
          failure(() -> f.verifier().verify(f.expected));
          f.released();
        }
      }
      try (var f = fixture()) {
        f.selectedRole = name;
        f.readonly = true;
        failure(() -> f.verifier().verify(f.expected));
        f.released();
      }
    }
    for (String field :
        List.of(
            FIXTURE_MODE_B6D5C2C3,
            FIXTURE_UID_0C18F38C,
            FIXTURE_GID_0ACDD642,
            "nlink",
            FIXTURE_SIZE_EB1E91E4,
            FIXTURE_DEV_8A17302D,
            FIXTURE_INO_4BE7C1E0,
            "lastModifiedTime",
            "ctime"))
      for (boolean absent : List.of(false, true))
        try (var f = fixture()) {
          f.metadata =
              (role, values) -> {
                if (absent) values.remove(field);
                else values.put(field, "not-a-typed-value");
              };
          failure(() -> f.verifier().verify(f.expected));
          f.released();
        }
    try (var f = fixture()) {
      f.nullAttributes = true;
      failure(() -> f.verifier().verify(f.expected));
      f.released();
    }
  }

  @Test
  void sizesShortLongAndZeroRead() throws Exception {
    for (String name : NAMES) {
      for (String mode :
          List.of("zero", "short", "count", "position", FIXTURE_EXTRA_ED1BF81A, "eof-position"))
        try (var f = fixture()) {
          f.selectedRole = name;
          f.readMode = mode;
          failure(() -> f.verifier().verify(f.expected));
          f.released();
          f.unchanged();
        }
      for (String mode : List.of("first", "last"))
        try (var f = fixture()) {
          f.selectedRole = name;
          f.sizeMode = mode;
          failure(() -> f.verifier().verify(f.expected));
          f.released();
          f.unchanged();
        }
    }
    try (var f = fixture()) {
      f.smallRead = 1;
      assertEquals(MANIFEST_HASH, f.verifier().verify(f.expected).sha256());
      assertEquals(
          1061,
          f.counts.get(FIXTURE_READ_6F365882)); // 964+26+35+32 data reads, plus four EOF reads.
      f.released();
      f.unchanged();
    }
  }

  @Test
  void independentHashAndGoldenMismatch() throws Exception {
    for (String name : NAMES)
      try (var f = fixture()) {
        f.selectedRole = name;
        f.readMode = "content";
        failure(() -> f.verifier().verify(f.expected));
        f.released();
        f.unchanged();
      }
    for (int position : new int[] {0, 500, 963})
      try (var f = fixture()) {
        byte[] wrong = golden();
        wrong[position] ^= 1;
        Files.write(f.child.resolve(FIXTURE_MANIFEST_JSON_0D4099EC), wrong);
        failure(() -> f.verifier().verify(f.expected));
        f.released();
        assertArrayEquals(
            wrong, Files.readAllBytes(f.child.resolve(FIXTURE_MANIFEST_JSON_0D4099EC)));
      }
    try (var f = fixture()) {
      var wrong =
          BackupManifestFixture.manifest(
              6,
              new BackupFileDigest(26, "0".repeat(64)),
              7,
              new BackupFileDigest(35, CONFIG_HASH),
              8,
              new BackupFileDigest(32, CREDS_HASH));
      failure(() -> f.verifier().verify(wrong));
      f.released();
      f.unchanged();
    }
  }

  @Test
  void everyIoFailure() throws Exception {
    List<String> observed;
    try (var f = fixture()) {
      f.verifier().verify(f.expected);
      assertEquals(COUNTS, f.counts);
      assertEquals(123, f.events.size());
      observed = List.copyOf(f.events);
    }
    int injected = 0;
    for (int position = 1; position <= 123; position++) {
      try (var f = fixture()) {
        f.faultAt = position;
        failure(() -> f.verifier().verify(f.expected));
        assertTrue(f.events.size() >= position);
        assertEquals(observed.get(position - 1), f.events.get(position - 1));
        f.released();
        f.unchanged();
        injected++;
      }
    }
    assertEquals(123, injected);
  }

  @Test
  void borrowedRootOwnershipAndClosed() throws Exception {
    try (var f = fixture()) {
      f.verifier().verify(f.expected);
      f.released();
      assertEquals(Boolean.TRUE, f.root.atDirectory(held -> Files.isDirectory(held)));
      assertEquals(MANIFEST_HASH, f.verifier().verify(f.expected).sha256());
      f.released();
      f.unchanged();
    }
    try (var f = fixture()) {
      f.tracking = false;
      f.root.close();
      f.tracking = true;
      failure(() -> f.verifier().verify(f.expected));
      assertTrue(f.directories.isEmpty());
    }
    try (var f = fixture()) {
      // The real metadata adapter does not trust synthetic policy ownership.
      var verifier = new BackupArtifactVerifier(f.root, f, 1, 1);
      failure(() -> verifier.verify(f.expected));
      f.released();
      f.unchanged();
    }
  }

  @Test
  void rootAndChildRebinding() throws Exception {
    for (int point : new int[] {15, 16, 17})
      try (var f = fixture()) {
        f.hook =
            (name, count) -> {
              if (name.equals("attributes") && count == point)
                f.metadata =
                    (role, values) ->
                        values.put(
                            FIXTURE_INO_4BE7C1E0, ((Long) values.get(FIXTURE_INO_4BE7C1E0)) + 1);
            };
        failure(() -> f.verifier().verify(f.expected));
        f.released();
      }
    try (var f = fixture()) {
      f.hook =
          (name, n) -> {
            if (name.equals("openDirectory") && n == 2) {
              try {
                Files.move(f.child, f.parent.resolve("saved-generation"));
                Files.createDirectory(f.child);
                Files.setPosixFilePermissions(
                    f.child, java.nio.file.attribute.PosixFilePermissions.fromString("rwx------"));
              } catch (IOException e) {
                throw new UncheckedIOException(e);
              }
            }
          };
      failure(() -> f.verifier().verify(f.expected));
      f.released();
      assertTrue(Files.exists(f.parent.resolve("saved-generation/MANIFEST.json")));
    }
    try (var f = fixture()) {
      f.hook =
          (name, n) -> {
            if (name.equals("closeDirectory") && n == 2)
              try {
                Files.writeString(f.parent.resolve("public-interference"), "public");
              } catch (IOException e) {
                throw new UncheckedIOException(e);
              }
          };
      failure(() -> f.verifier().verify(f.expected));
      f.released();
      f.unchanged();
    }
  }

  @Test
  void eachFileReplacementAndMutation() throws Exception {
    for (int index = 0; index < NAMES.size(); index++)
      for (String mode : List.of("replacement", "same-bytes", "mtime", "permission")) {
        final int selected = index;
        try (var f = fixture()) {
          String target = NAMES.get(index);
          f.hook =
              (name, n) -> {
                if (name.equals("openEntry") && n == 5) {
                  Path file = f.child.resolve(target);
                  try {
                    switch (mode) {
                      case "replacement" -> {
                        byte[] bytes = Files.readAllBytes(file);
                        Files.move(file, f.child.resolve("saved-" + target));
                        Files.write(file, bytes);
                        Files.setPosixFilePermissions(
                            file,
                            java.nio.file.attribute.PosixFilePermissions.fromString("rw-------"));
                      }
                      case "same-bytes" -> Files.write(file, Files.readAllBytes(file));
                      case "mtime" -> Files.setLastModifiedTime(file, FileTime.fromMillis(1));
                      case "permission" ->
                          Files.setPosixFilePermissions(
                              file,
                              java.nio.file.attribute.PosixFilePermissions.fromString("rw-r-----"));
                      default -> throw new AssertionError();
                    }
                  } catch (IOException e) {
                    throw new UncheckedIOException(e);
                  }
                }
              };
          failure(() -> f.verifier().verify(f.expected));
          assertEquals(5 + selected, f.counts.get("openEntry"));
          f.released();
        }
      }
    // A real in-place mutation during read is rejected, not just a synthetic metadata difference.
    try (var f = fixture()) {
      f.hook =
          (name, n) -> {
            if (name.equals(FIXTURE_READ_6F365882) && n == 3)
              try {
                Files.writeString(
                    f.child.resolve(FIXTURE_SCHUBERT_NK_DUMP_96644B79), "X".repeat(26));
              } catch (IOException e) {
                throw new UncheckedIOException(e);
              }
          };
      failure(() -> f.verifier().verify(f.expected));
      f.released();
    }
  }

  @Test
  void streamingBoundaryAndLargeFile() throws Exception {
    Map<Integer, String> fileHashes =
        Map.of(
            65535, "00cb85dd20678f79167f809e3f17f03c63007640367ec24ff7bde50250f65431",
            65536, "dcb3cceeb89595b15abac3233c5871a9dc8d5e4af56443c0c5085386c9b50439",
            65537, "c2c8deb12c89c8025c92a362b28cafc28437fc5b54bce28df26763b810b22652",
            196613, "77c51a7e252a8d972e7d4ac7897a7a80eb95f37c7ba798d9f8a5b76056738f91");
    Map<Integer, String> manifestHashes =
        Map.of(
            65535, "e16edf98d60d11aed52517ca8a367c0026ad416c5b955bf84cc25383fe6ec82e",
            65536, "20c4fbf06b348ae91fb9908186a44997951bd00e558d760467bb7076a3638a08",
            65537, "ce4e4ddcddce82822438b31c700d82ef73542b1acdbd0751f54a487fd358b6a2",
            196613, "1568db96d49dba9f5f5c24eced6ab35c3b5c7cb43748acc056d11baceedb2ab1");
    for (int size : List.of(65535, 65536, 65537, 196613))
      try (var f = fixture()) {
        byte[] bytes = new byte[size];
        Arrays.fill(bytes, (byte) 'D');
        Files.write(f.child.resolve(FIXTURE_SCHUBERT_NK_DUMP_96644B79), bytes);
        String literal =
            new String(golden(), java.nio.charset.StandardCharsets.US_ASCII)
                .replace("\"size\":26,", "\"size\":" + size + ",")
                .replace(DUMP_HASH, fileHashes.get(size));
        Files.writeString(
            f.child.resolve(FIXTURE_MANIFEST_JSON_0D4099EC),
            literal,
            java.nio.charset.StandardCharsets.US_ASCII);
        f.expected =
            BackupManifestFixture.manifest(
                6,
                new BackupFileDigest(size, fileHashes.get(size)),
                7,
                new BackupFileDigest(35, CONFIG_HASH),
                8,
                new BackupFileDigest(32, CREDS_HASH));
        var actual = f.verifier().verify(f.expected);
        assertEquals(size == 196613 ? 968 : 967, actual.size());
        assertEquals(manifestHashes.get(size), actual.sha256());
        assertEquals(7 + (size + 65535) / 65536, f.counts.get(FIXTURE_READ_6F365882));
        assertTrue(f.buffers.stream().allMatch(b -> b.length == 65536));
        f.released();
      }
  }

  @Test
  void resourceClosureAndSuppression() throws Exception {
    // BUG195: same unknown instance must never become TWR self-suppression failure.
    for (String close : List.of("closeChannel", "closeEntry", "closeDirectory"))
      for (Throwable primary :
          List.of(
              new IllegalStateException("public repeated"),
              new NullPointerException("public repeated"),
              new AssertionError("public repeated"))) {
        try (var f = fixture()) {
          f.extraFaults.add("read#1");
          f.faultTypes.put("read#1", primary);
          f.extraFaults.add(close + "#1");
          f.faultTypes.put(close + "#1", primary);
          assertSame(
              primary, assertThrows(primary.getClass(), () -> f.verifier().verify(f.expected)));
          assertEquals(1, primary.getSuppressed().length);
          assertInstanceOf(StorageIoException.class, primary.getSuppressed()[0]);
          f.released();
        }
      }
    try (var f = fixture()) {
      var fatal = new AssertionError("public close fatal");
      f.extraFaults.add("read#1");
      f.extraFaults.add("closeChannel#1");
      f.faultTypes.put("closeChannel#1", fatal);
      assertSame(fatal, assertThrows(AssertionError.class, () -> f.verifier().verify(f.expected)));
      f.released();
    }
    for (String location : List.of(FIXTURE_READ_6F365882, "next", "openEntry"))
      for (int kind = 0; kind < 4; kind++)
        try (var f = fixture()) {
          Throwable primary =
              switch (kind) {
                case 0 -> new IOException("public original IO");
                case 1 -> new IllegalStateException("public unknown runtime");
                case 2 -> new NullPointerException("public contract failure");
                default -> new AssertionError("public unknown error");
              };
          f.extraFaults.add(location + "#1");
          f.faultTypes.put(location + "#1", primary);
          f.extraFaults.add("closeDirectory#1");
          if (location.equals(FIXTURE_READ_6F365882)) f.extraFaults.add("closeChannel#1");
          if (location.equals("next")) f.extraFaults.add("closeNames#1");
          if (kind == 0) failure(() -> f.verifier().verify(f.expected));
          else {
            Throwable actual =
                assertThrows(primary.getClass(), () -> f.verifier().verify(f.expected));
            assertSame(primary, actual);
            assertNull(actual.getCause());
            assertTrue(actual.getSuppressed().length >= 1);
            for (Throwable secondary : actual.getSuppressed()) {
              assertInstanceOf(StorageIoException.class, secondary);
              assertNull(secondary.getCause());
              assertEquals("transfer storage operation failed", secondary.getMessage());
            }
          }
          f.released();
          f.unchanged();
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
        failure(() -> f.verifier().verify(f.expected));
        f.released();
      }
    try (var f = fixture()) {
      f.hook =
          (name, n) -> {
            if (name.equals(FIXTURE_CLOCK_49F3C56E) && n == 2) f.clockValue = 100 + 1799999999999L;
          };
      assertEquals(MANIFEST_HASH, f.verifier().verify(f.expected).sha256());
      f.released();
    }
    try (var f = fixture()) {
      f.clockValue = Long.MAX_VALUE - 50;
      f.hook =
          (name, n) -> {
            if (name.equals(FIXTURE_CLOCK_49F3C56E) && n == 2) f.clockValue = Long.MIN_VALUE + 49;
          };
      assertEquals(MANIFEST_HASH, f.verifier().verify(f.expected).sha256());
      f.released();
    }
    for (int position = 2; position <= 207; position++) {
      final int selected = position;
      try (var f = fixture()) {
        f.hook =
            (name, n) -> {
              if (name.equals(FIXTURE_CLOCK_49F3C56E) && n == selected)
                f.clockValue = 100 + 1800000000000L;
            };
        failure(() -> f.verifier().verify(f.expected));
        f.released();
        f.unchanged();
      }
    }
    for (int position = 1; position <= 207; position++) {
      final int selected = position;
      try (var f = fixture()) {
        f.hook =
            (name, n) -> {
              if (name.equals(FIXTURE_CLOCK_49F3C56E) && n == selected)
                Thread.currentThread().interrupt();
            };
        try {
          failure(() -> f.verifier().verify(f.expected));
          assertTrue(Thread.currentThread().isInterrupted());
        } finally {
          Thread.interrupted();
        }
        f.released();
        f.unchanged();
      }
    }
  }

  @Test
  void providerNullRuntimeAndRedaction() throws Exception {
    try (var f = fixture()) {
      assertThrows(NullPointerException.class, () -> new BackupArtifactVerifier(null, f, UID, GID));
      assertThrows(
          NullPointerException.class, () -> new BackupArtifactVerifier(f.root, null, UID, GID));
      assertThrows(
          NullPointerException.class,
          () -> new BackupArtifactVerifier(f.root, f, UID, GID, null, f::digest, f::clock));
      assertThrows(
          NullPointerException.class,
          () -> new BackupArtifactVerifier(f.root, f, UID, GID, f, null, f::clock));
      assertThrows(
          NullPointerException.class,
          () -> new BackupArtifactVerifier(f.root, f, UID, GID, f, f::digest, null));
      assertThrows(NullPointerException.class, () -> f.verifier().verify(null));
      assertEquals(Map.of(), f.counts);
      f.released();
    }
    for (int mode = 0; mode < 3; mode++)
      try (var f = fixture()) {
        f.nullNames = mode == 0;
        f.nullChannel = mode == 1;
        f.nullDigest = mode == 2;
        if (mode == 2)
          assertThrows(NullPointerException.class, () -> f.verifier().verify(f.expected));
        else failure(() -> f.verifier().verify(f.expected));
        f.released();
      }
    for (byte[] digest : Arrays.asList(null, new byte[31], new byte[32]))
      try (var f = fixture()) {
        var verifier =
            new BackupArtifactVerifier(
                f.root,
                f,
                UID,
                GID,
                f,
                () ->
                    new MessageDigest("public test provider") {
                      @Override
                      protected void engineUpdate(byte b) {}

                      @Override
                      protected void engineUpdate(byte[] b, int off, int len) {}

                      @Override
                      protected byte[] engineDigest() {
                        return digest;
                      }

                      @Override
                      protected void engineReset() {}
                    },
                f::clock);
        failure(() -> verifier.verify(f.expected));
        f.released();
      }
    try (var f = fixture()) {
      var verifier =
          new BackupArtifactVerifier(
              f.root,
              f,
              UID,
              GID,
              f,
              () -> {
                throw new NoSuchAlgorithmException("public provider detail");
              },
              f::clock);
      failure(() -> verifier.verify(f.expected));
      f.released();
    }
    for (Throwable primary :
        List.of(
            new IllegalStateException("public runtime"),
            new NullPointerException("public NPE"),
            new AssertionError("public Error")))
      try (var f = fixture()) {
        f.extraFaults.add("attributes#4");
        f.faultTypes.put("attributes#4", primary);
        assertSame(
            primary, assertThrows(primary.getClass(), () -> f.verifier().verify(f.expected)));
        f.released();
        f.unchanged();
      }
    try (var f = fixture()) {
      f.hook =
          (name, n) -> {
            if (name.equals("attributes") && n == 1)
              throw new UnsupportedOperationException("public unsupported IO");
          };
      failure(() -> f.verifier().verify(f.expected));
      f.released();
    }
  }

  @Test
  void concurrentSerializedAccess() throws Exception {
    try (var f = fixture();
        var pool = Executors.newFixedThreadPool(8)) {
      var verifier = f.verifier();
      AtomicInteger active = new AtomicInteger();
      AtomicInteger maximum = new AtomicInteger();
      f.hook =
          (name, n) -> {
            if (name.equals(FIXTURE_CLOCK_49F3C56E)) {
              if ((n - 1) % 207 == 0) maximum.accumulateAndGet(active.incrementAndGet(), Math::max);
              if (n % 207 == 0) active.decrementAndGet();
            }
          };
      var tasks = new ArrayList<Future<BackupFileDigest>>();
      for (int i = 0; i < 64; i++) tasks.add(pool.submit(() -> verifier.verify(f.expected)));
      for (var task : tasks) {
        var actual = task.get(20, TimeUnit.SECONDS);
        assertEquals(964, actual.size());
        assertEquals(MANIFEST_HASH, actual.sha256());
      }
      assertEquals(1, maximum.get());
      assertEquals(0, active.get());
      f.released();
      f.unchanged();
    }
    try (var f = fixture();
        var pool = Executors.newFixedThreadPool(8)) {
      var verifier = f.verifier();
      f.extraFaults.add("read#1");
      var tasks = new ArrayList<Future<Boolean>>();
      for (int i = 0; i < 64; i++)
        tasks.add(
            pool.submit(
                () -> {
                  try {
                    assertEquals(MANIFEST_HASH, verifier.verify(f.expected).sha256());
                    return true;
                  } catch (StorageIoException error) {
                    assertNull(error.getCause());
                    assertEquals(0, error.getSuppressed().length);
                    return false;
                  }
                }));
      int accepted = 0;
      int rejected = 0;
      for (var task : tasks) {
        if (task.get(20, TimeUnit.SECONDS)) accepted++;
        else rejected++;
      }
      assertEquals(63, accepted);
      assertEquals(1, rejected);
      f.released();
      f.unchanged();
    }
  }

  @Test
  void readOnlyNoMutationInventory() throws Exception {
    try (var f = fixture()) {
      var before = new LinkedHashMap<Path, Map<String, Object>>();
      var paths = new ArrayList<Path>();
      paths.add(f.parent);
      paths.add(f.child);
      for (String name : NAMES) paths.add(f.child.resolve(name));
      for (Path path : paths)
        before.put(
            path,
            Files.readAttributes(
                path, "unix:mode,uid,gid,nlink,size,dev,ino,lastModifiedTime,ctime"));
      var result = f.verifier().verify(f.expected);
      assertEquals(MANIFEST_HASH, result.sha256());
      for (Path path : paths)
        assertEquals(
            before.get(path),
            Files.readAttributes(
                path, "unix:mode,uid,gid,nlink,size,dev,ino,lastModifiedTime,ctime"));
      assertEquals(COUNTS, f.counts);
      f.unchanged();
      f.released();
    }
  }

  private BackupArtifactFixture fixture() throws Exception {
    return new BackupArtifactFixture(temporary);
  }

  static StorageIoException failure(org.junit.jupiter.api.function.Executable action) {
    var error = assertThrows(StorageIoException.class, action);
    assertEquals(StorageIoException.Reason.UNAVAILABLE, error.reason());
    assertEquals("transfer storage operation failed", error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
    return error;
  }
}
