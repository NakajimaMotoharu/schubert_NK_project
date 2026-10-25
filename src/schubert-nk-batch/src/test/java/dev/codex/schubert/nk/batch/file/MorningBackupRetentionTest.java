package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.CONFIG_HASH;
import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.CREDS_HASH;
import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.DIR;
import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.DUMP_HASH;
import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.GID;
import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.NAMES;
import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.UID;
import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.golden;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.backup.BackupFileDigest;
import dev.codex.schubert.nk.batch.backup.BackupManifest;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import dev.codex.schubert.nk.batch.repository.MorningDatabaseSession;
import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.time.Instant;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.TreeMap;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** SS341§6.3/SSC133/ISSRET001..008: hand JSON + real FD/postconditions, no production expected. */
final class MorningBackupRetentionTest {
  @TempDir Path temporary;

  @Test
  void issret001SevenEightNineUseExactOldestSet() throws Exception {
    for (int generations : List.of(7, 8, 9)) {
      try (var f = new BackupArtifactFixture(temporary);
          var root =
              OwnedTransferDirectory.open(MorningBackupRetention.directoryCalls(), f.parent)) {
        var names = generations(f, generations - 1);
        var subject = subject(f, root, acceptsAll());
        var result =
            subject.collect(MorningBackupRetention.Mode.NEW_SUCCESS, Optional.of(f.expected));
        int removed = generations - 7;
        assertEquals(names.subList(0, removed), result.deleted);
        assertEquals(names.subList(removed, names.size()), new ArrayList<>(result.kept.keySet()));
        assertEquals(generations, result.before.size());
        assertEquals(7, result.after.size());
        for (String name : names.subList(0, removed))
          assertFalse(Files.exists(f.parent.resolve(name), LinkOption.NOFOLLOW_LINKS));
        assertTrue(Files.isDirectory(f.child));
        f.unchanged();
        subject.recheck();
        assertThrows(
            IOException.class,
            () ->
                subject.collect(MorningBackupRetention.Mode.NEW_SUCCESS, Optional.of(f.expected)));
        assertThrows(UnsupportedOperationException.class, () -> result.kept.clear());
        assertFalse(result.toString().contains(DIR));
        f.released();
      }
    }
  }

  @Test
  void issret009ProductionFactoryNotReadOnlyAndRefusalChangesNothing() throws Exception {
    var calls = MorningBackupRetention.directoryCalls();
    assertInstanceOf(LinuxDirectoryCalls.class, calls);
    try (var f = new BackupArtifactFixture(temporary)) {
      var names = generations(f, 7);
      var preserved = new TreeMap<Path, byte[]>();
      try (var paths = Files.walk(f.parent)) {
        for (var path : paths.filter(Files::isRegularFile).toList())
          preserved.put(path, Files.readAllBytes(path));
      }
      var mutations = new AtomicInteger();
      var readOnly =
          (DirectoryCalls)
              java.lang.reflect.Proxy.newProxyInstance(
                  getClass().getClassLoader(),
                  new Class<?>[] {DirectoryCalls.class},
                  (proxy, method, args) -> {
                    if (Set.of("unlink", "sync", "removeEmptyDirectory")
                        .contains(method.getName())) {
                      mutations.incrementAndGet();
                      throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
                    }
                    try {
                      return method.invoke(calls, args);
                    } catch (java.lang.reflect.InvocationTargetException failure) {
                      throw failure.getCause();
                    }
                  });
      try (var root = OwnedTransferDirectory.open(readOnly, f.parent)) {
        var subject = subject(f, root, acceptsAll());
        assertThrows(
            StorageIoException.class,
            () ->
                subject.collect(MorningBackupRetention.Mode.NEW_SUCCESS, Optional.of(f.expected)));
        assertEquals(1, mutations.get());
        assertThrows(IOException.class, subject::result);
        try (var children = Files.list(f.parent)) {
          assertEquals(names, children.map(p -> p.getFileName().toString()).sorted().toList());
        }
        for (String name : names)
          try (var files = Files.list(f.parent.resolve(name))) {
            assertEquals(
                Set.copyOf(NAMES),
                files
                    .map(p -> p.getFileName().toString())
                    .collect(java.util.stream.Collectors.toSet()));
          }
        f.unchanged();
        for (var entry : preserved.entrySet())
          assertArrayEquals(entry.getValue(), Files.readAllBytes(entry.getKey()));
      }
      // Corrected production-selected adapter, same files and claims, real unlink/rmdir/fsync.
      try (var root = OwnedTransferDirectory.open(calls, f.parent)) {
        var subject = subject(f, root, acceptsAll());
        var result =
            subject.collect(MorningBackupRetention.Mode.NEW_SUCCESS, Optional.of(f.expected));
        assertEquals(List.of(names.getFirst()), result.deleted);
        assertEquals(7, result.after.size());
        assertFalse(Files.exists(f.parent.resolve(names.getFirst()), LinkOption.NOFOLLOW_LINKS));
        for (var entry : preserved.entrySet())
          if (!entry.getKey().startsWith(f.parent.resolve(names.getFirst())))
            assertArrayEquals(entry.getValue(), Files.readAllBytes(entry.getKey()));
        subject.recheck();
        f.unchanged();
      }
      f.released();
    }
  }

  @Test
  void issret002FailedAndReuseNeverDelete() throws Exception {
    for (var mode :
        List.of(MorningBackupRetention.Mode.FAILED, MorningBackupRetention.Mode.REUSED_SUCCESS)) {
      try (var f = new BackupArtifactFixture(temporary)) {
        List<String> names = generations(f, 8);
        // Existing fixture rejects any mutation syscall: both modes must work with that port.
        var subject = subject(f, f.root, acceptsAll());
        var result =
            subject.collect(
                mode,
                mode == MorningBackupRetention.Mode.FAILED
                    ? Optional.empty()
                    : Optional.of(f.expected));
        assertEquals(names, result.before);
        assertEquals(names, result.after);
        assertEquals(List.of(), result.deleted);
        assertEquals(mode == MorningBackupRetention.Mode.FAILED ? 0 : 1, result.kept.size());
        subject.recheck();
        f.unchanged();
        f.released();
      }
    }
  }

  @Test
  void issret003UnknownPartSymlinkMalformedAndNonSuccessRemain() throws Exception {
    try (var f = new BackupArtifactFixture(temporary);
        var root = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), f.parent)) {
      var names = generations(f, 7);
      String notSuccessful = names.getFirst();
      String malformed = oldName(9);
      String symbolic = oldName(10);
      String corrupt = oldName(11);
      String empty = oldName(12);
      cloneGeneration(f, 9);
      Files.writeString(f.parent.resolve(malformed).resolve("MANIFEST.json"), "{}\n");
      Files.createSymbolicLink(f.parent.resolve(symbolic), f.child);
      cloneGeneration(f, 11);
      Files.writeString(
          f.parent.resolve(corrupt).resolve("schubert_nk.dump"), "PG166 public dump fixturE\n");
      cloneGeneration(f, 12);
      Files.writeString(f.parent.resolve(empty).resolve("config.tar"), "");
      Files.writeString(f.parent.resolve("public-note"), "public\n");
      Files.createDirectory(f.parent.resolve("uncommitted.part"));
      var subject =
          subject(
              f,
              root,
              new ReadOnlyAccess() {
                @Override
                public boolean retainedBackupSuccessful(BackupManifest m, Instant now) {
                  return !m.directoryName().equals(notSuccessful);
                }

                @Override
                public <T> T handoffCleanup(MorningDatabaseSession.CleanupHandoff<T> work) {
                  throw new AssertionError("no cleanup authority");
                }
              });
      var result =
          subject.collect(MorningBackupRetention.Mode.NEW_SUCCESS, Optional.of(f.expected));
      assertEquals(List.of(), result.deleted);
      assertEquals(
          Map.of(
              notSuccessful,
              "NON_SUCCESS_PAIR",
              malformed,
              "MALFORMED_MANIFEST",
              symbolic,
              "NOT_DIRECTORY",
              corrupt,
              "CONTENT_MISMATCH",
              empty,
              "CONTENT_MISMATCH",
              "public-note",
              "UNKNOWN_NAME",
              "uncommitted.part",
              "PART"),
          result.protectedNames);
      assertEquals(result.before, result.after);
      assertTrue(Files.isSymbolicLink(f.parent.resolve(symbolic)));
      assertEquals("{}\n", Files.readString(f.parent.resolve(malformed).resolve("MANIFEST.json")));
      subject.recheck();
      f.unchanged();
      f.released();
    }
  }

  @Test
  void issret1420001UnexpectedGenerationFileSetRemainsProtected() throws Exception {
    for (boolean extraDirectory : List.of(false, true)) {
      try (var f = new BackupArtifactFixture(temporary);
          var root = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), f.parent)) {
        var names = generations(f, 7);
        String foreign = names.getFirst();
        Path foreignDirectory = f.parent.resolve(foreign);
        Path extra = foreignDirectory.resolve("extra-public-entry");
        if (extraDirectory) Files.createDirectory(extra);
        else Files.writeString(extra, "public uncommitted member\n", StandardCharsets.US_ASCII);
        var bytesBefore = new TreeMap<Path, byte[]>();
        var metadataBefore = new TreeMap<Path, Map<String, Object>>();
        try (var paths = Files.walk(foreignDirectory)) {
          for (Path path : paths.toList()) {
            metadataBefore.put(
                path,
                Files.readAttributes(
                    path,
                    "unix:dev,ino,uid,gid,mode,size,nlink,lastModifiedTime,ctime",
                    LinkOption.NOFOLLOW_LINKS));
            if (Files.isRegularFile(path, LinkOption.NOFOLLOW_LINKS))
              bytesBefore.put(path, Files.readAllBytes(path));
          }
        }
        var subject = subject(f, root, acceptsAll());
        var result =
            subject.collect(MorningBackupRetention.Mode.NEW_SUCCESS, Optional.of(f.expected));
        assertEquals(Map.of(foreign, "UNEXPECTED_FILE_SET"), result.protectedNames);
        assertEquals(List.of(), result.deleted);
        assertEquals(result.before, result.after);
        assertEquals(7, result.kept.size());
        assertFalse(result.kept.containsKey(foreign));
        assertEquals(8, result.after.size());
        subject.recheck();
        for (var entry : metadataBefore.entrySet())
          assertEquals(
              entry.getValue(),
              Files.readAttributes(
                  entry.getKey(),
                  "unix:dev,ino,uid,gid,mode,size,nlink,lastModifiedTime,ctime",
                  LinkOption.NOFOLLOW_LINKS));
        for (var entry : bytesBefore.entrySet())
          assertArrayEquals(entry.getValue(), Files.readAllBytes(entry.getKey()));
        assertEquals(extraDirectory, Files.isDirectory(extra, LinkOption.NOFOLLOW_LINKS));
        f.unchanged();
        f.released();
      }
    }
  }

  @Test
  void issret004CurrentNotNewestOrMissingNeverDeletes() throws Exception {
    try (var f = new BackupArtifactFixture(temporary);
        var root = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), f.parent)) {
      for (int offset = -8; offset < 0; offset++) cloneGeneration(f, offset);
      var subject = subject(f, root, acceptsAll());
      assertThrows(
          IOException.class,
          () -> subject.collect(MorningBackupRetention.Mode.NEW_SUCCESS, Optional.of(f.expected)));
      try (var names = Files.list(f.parent)) {
        assertEquals(9, names.count());
      }
      f.unchanged();
      f.released();
    }
  }

  @Test
  void issret005UnknownSqlCloseOwnerAndPostReadDriftFailClosed() throws Exception {
    try (var f = new BackupArtifactFixture(temporary)) {
      var unknown = new AssertionError("synthetic unknown");
      var db =
          new ReadOnlyAccess() {
            @Override
            public boolean retainedBackupSuccessful(BackupManifest m, Instant now) {
              throw unknown;
            }

            @Override
            public <T> T handoffCleanup(MorningDatabaseSession.CleanupHandoff<T> work) {
              throw unknown;
            }
          };
      assertSame(
          unknown,
          assertThrows(
              AssertionError.class,
              () ->
                  subject(f, f.root, db)
                      .collect(
                          MorningBackupRetention.Mode.REUSED_SUCCESS, Optional.of(f.expected))));
      f.unchanged();
      f.released();
    }
    try (var f = new BackupArtifactFixture(temporary)) {
      f.extraFaults.add("closeNames#1");
      assertThrows(
          IOException.class,
          () ->
              subject(f, f.root, acceptsAll())
                  .collect(MorningBackupRetention.Mode.FAILED, Optional.empty()));
      f.unchanged();
      f.released();
    }
    try (var f = new BackupArtifactFixture(temporary)) {
      var subject = subject(f, f.root, acceptsAll());
      subject.collect(MorningBackupRetention.Mode.REUSED_SUCCESS, Optional.of(f.expected));
      Files.writeString(f.parent.resolve("foreign-change"), "public\n");
      assertThrows(IOException.class, subject::recheck);
      f.released();
    }
  }

  @Test
  void issret006NullMissingResultAndThreadCannotGrantAuthority() throws Exception {
    try (var f = new BackupArtifactFixture(temporary)) {
      var subject = subject(f, f.root, acceptsAll());
      assertThrows(IOException.class, subject::result);
      assertThrows(IOException.class, subject::recheck);
      assertThrows(NullPointerException.class, () -> subject.collect(null, Optional.empty()));
      assertThrows(
          NullPointerException.class,
          () -> subject.collect(MorningBackupRetention.Mode.FAILED, null));
      assertThrows(
          IOException.class,
          () -> subject.collect(MorningBackupRetention.Mode.FAILED, Optional.of(f.expected)));
      assertThrows(
          IOException.class,
          () -> subject.collect(MorningBackupRetention.Mode.NEW_SUCCESS, Optional.empty()));
      subject.collect(MorningBackupRetention.Mode.FAILED, Optional.empty());
      try (var pool = Executors.newSingleThreadExecutor()) {
        pool.submit(() -> assertThrows(IOException.class, subject::recheck))
            .get(5, TimeUnit.SECONDS);
      }
      f.unchanged();
      f.released();
    }
  }

  static MorningBackupRetention subject(
      BackupArtifactFixture f, OwnedTransferDirectory root, MorningDatabaseSession.Access db) {
    return new MorningBackupRetention(
        new BackupManifestReader(root, f, UID, GID, f, f::clock),
        new BackupArtifactVerifier(root, f, UID, GID, f, f::clock),
        db,
        () -> 1_000_000,
        100);
  }

  static MorningDatabaseSession.Access acceptsAll() {
    return new ReadOnlyAccess() {
      @Override
      public boolean retainedBackupSuccessful(BackupManifest m, Instant now) {
        assertEquals(new BackupFileDigest(26, DUMP_HASH), m.dump());
        assertEquals(new BackupFileDigest(35, CONFIG_HASH), m.configuration());
        assertEquals(new BackupFileDigest(32, CREDS_HASH), m.credentials());
        return true;
      }

      @Override
      public <T> T handoffCleanup(MorningDatabaseSession.CleanupHandoff<T> work) {
        throw new AssertionError("no cleanup authority");
      }
    };
  }

  @Test
  void issret007ThreePersistedWholeByteFramesAndBindings() throws Exception {
    for (var mode : MorningBackupRetention.Mode.values()) {
      try (var f = new BackupArtifactFixture(temporary)) {
        f.metadata =
            (role, fields) -> {
              fields.put("dev", 11L);
              if (role.equals("parent")) fields.put("ino", 12L);
            };
        var result =
            subject(f, f.root, acceptsAll())
                .collect(
                    mode,
                    mode == MorningBackupRetention.Mode.FAILED
                        ? Optional.empty()
                        : Optional.of(f.expected));
        var epoch =
            new StartupPermitRecords.Epoch(
                StartupPermitRecords.State.INVALID,
                UUID.fromString("11111111-1111-4111-8111-111111111111"),
                UUID.fromString("22222222-2222-4333-8444-555555555555"),
                new MaintenanceActivation(
                    f.expected.run(), UUID.fromString("44444444-2222-4333-8444-555555555555")),
                Optional.empty());
        String name =
            switch (mode) {
              case NEW_SUCCESS -> "new";
              case REUSED_SUCCESS -> "reused";
              case FAILED -> "failed";
            };
        try (var input =
            Objects.requireNonNull(
                getClass().getResourceAsStream("/ops/issuer-retention-" + name + "-golden.txt"))) {
          assertArrayEquals(
              input.readAllBytes(),
              MorningGateEvidence.retention(epoch, "a".repeat(32), "b".repeat(32), result));
        }
        assertThrows(
            NullPointerException.class,
            () -> MorningGateEvidence.retention(epoch, "a".repeat(32), "b".repeat(32), null));
        assertThrows(
            IOException.class,
            () -> MorningGateEvidence.retention(epoch, "a".repeat(32), "a".repeat(32), result));
        f.unchanged();
        f.released();
      }
    }
  }

  @Test
  void issret008PartialDeleteSyncFailureAndUnknownRootNeverBecomeProof() throws Exception {
    for (String fault : List.of("unlink", "sync", "removeEmptyDirectory")) {
      try (var f = new BackupArtifactFixture(temporary)) {
        var names = generations(f, 7);
        var nativeCalls = LinuxDirectoryCalls.create();
        var count = new AtomicInteger();
        var calls =
            (DirectoryCalls)
                java.lang.reflect.Proxy.newProxyInstance(
                    getClass().getClassLoader(),
                    new Class<?>[] {DirectoryCalls.class},
                    (proxy, method, args) -> {
                      boolean fail = method.getName().equals(fault) && count.incrementAndGet() == 1;
                      if (fail && !fault.equals("sync"))
                        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
                      Object value;
                      try {
                        value = method.invoke(nativeCalls, args);
                      } catch (java.lang.reflect.InvocationTargetException failure) {
                        throw failure.getCause();
                      }
                      if (fail) throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
                      return value;
                    });
        try (var root = OwnedTransferDirectory.open(calls, f.parent)) {
          var subject = subject(f, root, acceptsAll());
          assertThrows(
              IOException.class,
              () ->
                  subject.collect(
                      MorningBackupRetention.Mode.NEW_SUCCESS, Optional.of(f.expected)));
          assertThrows(IOException.class, subject::result);
          assertTrue(Files.isDirectory(f.parent.resolve(names.getFirst())));
          f.unchanged();
          f.released();
        }
      }
    }
    for (String field : List.of("dev", "ino")) {
      try (var f = new BackupArtifactFixture(temporary)) {
        f.metadata =
            (role, fields) -> {
              if (role.equals("parent")) fields.put(field, field.equals("dev") ? -1L : 0L);
            };
        assertThrows(
            IOException.class,
            () ->
                subject(f, f.root, acceptsAll())
                    .collect(MorningBackupRetention.Mode.FAILED, Optional.empty()));
        f.unchanged();
        f.released();
      }
    }
  }

  abstract static class ReadOnlyAccess implements MorningDatabaseSession.Access {
    @Override
    public void requireUnused(BatchRun run) {
      throw new AssertionError("not caller authority");
    }

    @Override
    public void requireConsistent(BatchRun run) {
      throw new AssertionError("not caller authority");
    }

    @Override
    public MorningDatabaseSession.BackupBegins beginBackup(
        BatchRun run, Instant now, boolean recoverAbandoned) {
      throw new AssertionError("no begin authority");
    }
  }

  static List<String> generations(BackupArtifactFixture f, int old) throws Exception {
    var names = new ArrayList<String>();
    names.add(DIR);
    for (int n = 1; n <= old; n++) {
      cloneGeneration(f, n);
      names.add(oldName(n));
    }
    Collections.sort(names);
    return List.copyOf(names);
  }

  static String oldName(int offset) {
    return LocalDate.of(2026, 9, 13).minusDays(offset).toString().replace("-", "")
        + "-000002-"
        + oldUuid(offset);
  }

  static String oldUuid(int offset) {
    return "12345678-9abc-def0-8123-" + String.format(Locale.ROOT, "%012x", offset + 100);
  }

  static void cloneGeneration(BackupArtifactFixture f, int offset) throws Exception {
    Path child = Files.createDirectory(f.parent.resolve(oldName(offset)));
    Files.setPosixFilePermissions(
        child, java.nio.file.attribute.PosixFilePermissions.fromString("rwx------"));
    for (String name : NAMES) Files.copy(f.child.resolve(name), child.resolve(name));
    String raw =
        new String(golden(), StandardCharsets.US_ASCII)
            .replace("12345678-9abc-def0-8123-456789abcdef", oldUuid(offset))
            .replace("2026-09-12", LocalDate.of(2026, 9, 12).minusDays(offset).toString())
            .replace("\"id\":90000", "\"id\":" + (90000 + (offset + 100) * 2))
            .replace("\"id\":90001", "\"id\":" + (90001 + (offset + 100) * 2));
    Files.writeString(child.resolve("MANIFEST.json"), raw, StandardCharsets.US_ASCII);
  }
}
