package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.BackupPublicationFixture.GID;
import static dev.codex.schubert.nk.batch.file.BackupPublicationFixture.PART;
import static dev.codex.schubert.nk.batch.file.BackupPublicationFixture.UID;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Callable;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** NK-OPS-001/BAK/BKO/UI251/SS3416.1/SSC090/091; PT-OPS-DBCP001..008. */
final class BackupDatabaseCopyTest {
  @TempDir Path temporary;

  private static byte[] golden() {
    return "127.0.0.1:5432:schubert_nk:schubert_backup:PUBLIC_FIXTURE\n"
        .getBytes(StandardCharsets.US_ASCII);
  }

  private BackupPublicationFixture fixture() throws Exception {
    var f = new BackupPublicationFixture(temporary);
    f.effective = UID;
    f.metadata =
        (role, m) -> {
          m.put("uid", (int) UID);
          m.put("gid", (int) GID);
        };
    return f;
  }

  private BackupDatabaseCopy copy(BackupPublicationFixture f) {
    return new BackupDatabaseCopy(f.root, f, UID, GID, f);
  }

  private void create(BackupPublicationFixture f) throws IOException {
    byte[] owned = golden();
    copy(f)
        .dump(
            owned,
            PART,
            p -> {
              assertArrayEquals(golden(), Files.readAllBytes(p));
              assertArrayEquals(new byte[owned.length], owned, "heap cleared before child");
              assertEquals(
                  PosixFilePermissions.fromString("rw-------"), Files.getPosixFilePermissions(p));
              assertEquals(0, f.channels);
            });
    assertArrayEquals(new byte[owned.length], owned);
  }

  private void fails(BackupPublicationFixture f) {
    byte[] owned = golden();
    assertThrows(StorageIoException.class, () -> copy(f).dump(owned, PART, p -> {}));
    assertArrayEquals(new byte[owned.length], owned);
    f.released();
  }

  @Test
  void literalCreationErasureAndBorrowing() throws Exception {
    try (var f = fixture()) {
      f.chunk = 7;
      create(f);
      f.released();
      assertFalse(Files.exists(f.parent.resolve(PART + ".part")));
      assertEquals(2, f.counts.get("force"));
      assertEquals(2, f.counts.get("closeWriter"));
      assertEquals(2, f.counts.get("closeReader"));
      assertEquals(1, f.counts.get("unlink"));
      assertEquals(1, f.counts.get("sync"));
    }
  }

  @Test
  void boundaryAndNullContracts() throws Exception {
    for (int size : List.of(1, 65536))
      try (var f = fixture()) {
        byte[] raw = new byte[size];
        Arrays.fill(raw, (byte) 65);
        copy(f)
            .dump(
                raw,
                PART,
                p -> {
                  assertEquals(size, Files.size(p));
                  assertArrayEquals(new byte[size], raw);
                });
        f.released();
      }
    for (int size : List.of(0, 65537))
      try (var f = fixture()) {
        byte[] raw = new byte[size];
        Arrays.fill(raw, (byte) 65);
        assertThrows(StorageIoException.class, () -> copy(f).dump(raw, PART, p -> fail()));
        assertArrayEquals(new byte[size], raw);
        assertFalse(f.counts.containsKey("createPrivateFile"));
      }
    try (var f = fixture()) {
      assertThrows(NullPointerException.class, () -> new BackupDatabaseCopy(null, f, UID, GID));
      assertThrows(
          NullPointerException.class, () -> new BackupDatabaseCopy(f.root, null, UID, GID));
      assertThrows(
          NullPointerException.class, () -> new BackupDatabaseCopy(f.root, f, UID, GID, null));
      assertThrows(NullPointerException.class, () -> copy(f).dump(null, PART, p -> {}));
      for (boolean part : List.of(true, false)) {
        byte[] raw = golden();
        assertThrows(
            NullPointerException.class,
            () -> copy(f).dump(raw, part ? null : PART, part ? p -> {} : null));
        assertArrayEquals(new byte[raw.length], raw);
      }
      for (long owner : new long[] {0, -1, 0x100000000L}) {
        assertThrows(
            IllegalArgumentException.class, () -> new BackupDatabaseCopy(f.root, f, owner, GID));
        assertThrows(
            IllegalArgumentException.class, () -> new BackupDatabaseCopy(f.root, f, UID, owner));
      }
    }
    try (var f = fixture()) {
      f.effective = 0xffff_ffffL;
      f.metadata =
          (role, m) -> {
            m.put("uid", -1);
            m.put("gid", -1);
          };
      new BackupDatabaseCopy(f.root, f, 0xffff_ffffL, 0xffff_ffffL, f)
          .dump(golden(), PART, p -> {});
      f.released();
    }
  }

  @Test
  void metadataSecurityAndNamespace() throws Exception {
    for (String vector : List.of("1:size", "2:size", "7:size", "7:ino", "2:dev", "parent:dev")) {
      try (var f = fixture()) {
        var files = new AtomicInteger();
        var parents = new AtomicInteger();
        f.metadata =
            (role, m) -> {
              m.put("uid", (int) UID);
              m.put("gid", (int) GID);
              if (role.equals("parent")
                  && parents.incrementAndGet() == 2
                  && vector.equals("parent:dev")) m.put("dev", -1L);
              if (role.equals("file")) {
                int at = files.incrementAndGet();
                if (vector.startsWith(at + ":")) {
                  String key = vector.substring(vector.indexOf(':') + 1);
                  m.put(key, key.equals("size") ? at == 1 ? 1L : 0L : -1L);
                }
              }
            };
        fails(f);
      }
    }
    for (String role : List.of("parent", "file"))
      for (var change :
          Map.<String, Object>of("mode", 0, "uid", 1, "gid", 1, "nlink", 0, "size", -1L).entrySet())
        try (var f = fixture()) {
          f.metadata =
              (r, m) -> {
                m.put("uid", (int) UID);
                m.put("gid", (int) GID);
                if (r.equals(role)) m.put(change.getKey(), change.getValue());
              };
          fails(f);
        }
    for (String key :
        List.of("mode", "uid", "gid", "nlink", "size", "dev", "ino", "lastModifiedTime", "ctime"))
      for (Object value : new Object[] {null, "wrong"})
        try (var f = fixture()) {
          f.metadata =
              (role, m) -> {
                m.put("uid", (int) UID);
                m.put("gid", (int) GID);
                m.put(key, value);
              };
          fails(f);
        }
    for (String kind :
        List.of("nullMap", "aclNull", "acl", "readonly", "fs", "fsNull", "actor", "dev", "size"))
      try (var f = fixture()) {
        switch (kind) {
          case "nullMap" -> f.nullMap = true;
          case "aclNull" -> f.acl = null;
          case "acl" -> f.acl = new byte[] {1};
          case "readonly" -> f.readonly = true;
          case "fs" -> f.copyFilesystem = "ext4";
          case "fsNull" -> f.copyFilesystem = null;
          case "actor" -> f.effective = 0;
          default ->
              f.metadata =
                  (role, m) -> {
                    m.put("uid", (int) UID);
                    m.put("gid", (int) GID);
                    if (role.equals("file"))
                      m.put(kind.equals("dev") ? "dev" : "size", kind.equals("dev") ? -1L : 65537L);
                  };
        }
        fails(f);
      }
    try (var f = fixture()) {
      var n = new AtomicInteger();
      f.metadata =
          (role, m) -> {
            m.put("uid", (int) UID);
            m.put("gid", (int) GID);
            if (role.equals("file") && n.incrementAndGet() > 1) m.put("ino", -1L);
          };
      fails(f);
    }
    try (var f = fixture()) {
      var n = new AtomicInteger();
      f.metadata =
          (role, m) -> {
            m.put("uid", (int) UID);
            m.put("gid", (int) GID);
            if (role.equals("file") && n.incrementAndGet() > 2)
              m.put("ctime", java.nio.file.attribute.FileTime.fromMillis(0));
          };
      fails(f);
    }
  }

  @Test
  void everyIoPositionAndProgress() throws Exception {
    int points;
    try (var f = fixture()) {
      create(f);
      points = f.position;
    }
    for (int at = 1; at <= points; at++)
      try (var f = fixture()) {
        f.faultAt = at;
        fails(f);
      }
    for (String mode : List.of("zero", "negative", "large", "position"))
      try (var f = fixture()) {
        f.writeMode = mode;
        fails(f);
      }
    for (String mode :
        List.of("zero", "short", "large", "position", "extra", "eof-position", "content"))
      try (var f = fixture()) {
        f.readMode = mode;
        fails(f);
      }
    for (String kind : List.of("nullWriter", "nullReader"))
      try (var f = fixture()) {
        f.nullWriter = kind.equals("nullWriter");
        f.nullReader = kind.equals("nullReader");
        fails(f);
      }
    for (String point : List.of("writerSize#1", "writerSize#2", "writerSize#3", "size#1", "size#2"))
      try (var f = fixture()) {
        f.changedSize = point;
        fails(f);
      }
  }

  @Test
  void callbackFailureAndRetainedCapability() throws Exception {
    for (Throwable expected :
        List.of(
            new IOException("private diagnostic"),
            new IllegalStateException("public unknown"),
            new AssertionError("public fatal")))
      try (var f = fixture()) {
        byte[] raw = golden();
        Throwable actual =
            assertThrows(
                Throwable.class,
                () ->
                    copy(f)
                        .dump(
                            raw,
                            PART,
                            p -> {
                              assertArrayEquals(new byte[raw.length], raw);
                              if (expected instanceof IOException io) throw io;
                              if (expected instanceof Error fatal) throw fatal;
                              throw (RuntimeException) expected;
                            }));
        if (expected instanceof IOException) assertInstanceOf(StorageIoException.class, actual);
        else assertSame(expected, actual);
        assertArrayEquals(golden(), Files.readAllBytes(f.parent.resolve(PART + ".part")));
        assertFalse(f.counts.containsKey("unlink"));
        f.released();
      }
    try (var f = fixture();
        var executor = Executors.newSingleThreadExecutor()) {
      var entered = new CountDownLatch(1);
      var release = new CountDownLatch(1);
      var result =
          executor.submit(
              () -> {
                copy(f)
                    .dump(
                        golden(),
                        PART,
                        p -> {
                          entered.countDown();
                          try {
                            assertTrue(release.await(5, TimeUnit.SECONDS));
                          } catch (InterruptedException failure) {
                            throw new AssertionError(failure);
                          }
                        });
                return true;
              });
      try {
        assertTrue(entered.await(2, TimeUnit.SECONDS));
        assertFalse(result.isDone());
        assertFalse(f.counts.containsKey("unlink"));
        assertArrayEquals(golden(), Files.readAllBytes(f.parent.resolve(PART + ".part")));
      } finally {
        release.countDown();
      }
      assertTrue(result.get(5, TimeUnit.SECONDS));
      f.released();
    }
  }

  @Test
  void erasureAndNameBindings() throws Exception {
    try (var f = fixture()) {
      assertThrows(
          StorageIoException.class,
          () ->
              copy(f)
                  .dump(
                      golden(),
                      PART,
                      p -> {
                        f.readMode = "nonzero";
                      }));
      assertTrue(Files.exists(f.parent.resolve(PART + ".part")));
      f.released();
    }
    try (var f = fixture()) {
      assertThrows(
          StorageIoException.class,
          () ->
              copy(f)
                  .dump(
                      golden(),
                      PART,
                      p -> {
                        Files.move(f.parent.resolve(PART + ".part"), f.parent.resolve("retained"));
                        Files.write(f.parent.resolve(PART + ".part"), golden());
                      }));
      assertArrayEquals(golden(), Files.readAllBytes(f.parent.resolve("retained")));
      assertFalse(f.counts.containsKey("unlink"));
      f.released();
    }
    try (var f = fixture()) {
      f.faults.put("sync#1", new IOException("public uncertain sync"));
      fails(f);
      assertFalse(
          Files.exists(f.parent.resolve(PART + ".part")), "no recreation after uncertain unlink");
    }
    try (var f = fixture()) {
      f.hook =
          (name, n) -> {
            if (name.equals("openWriter") && n == 2) f.writeMode = "zero";
          };
      fails(f);
      assertArrayEquals(golden(), Files.readAllBytes(f.parent.resolve(PART + ".part")));
    }
    try (var f = fixture()) {
      try {
        assertThrows(
            StorageIoException.class,
            () -> copy(f).dump(golden(), PART, p -> Thread.currentThread().interrupt()));
        assertTrue(Thread.currentThread().isInterrupted());
      } finally {
        Thread.interrupted();
      }
      f.released();
    }
  }

  @Test
  void repeatedCollisionAndConcurrentRoots() throws Exception {
    try (var f = fixture()) {
      Files.write(f.parent.resolve(PART + ".part"), golden());
      fails(f);
      assertArrayEquals(golden(), Files.readAllBytes(f.parent.resolve(PART + ".part")));
    }
    try (var f = fixture()) {
      create(f);
      create(f);
      f.released();
    }
    try (var executor = Executors.newFixedThreadPool(4)) {
      var tasks = new ArrayList<Callable<Boolean>>();
      for (int n = 0; n < 16; n++)
        tasks.add(
            () -> {
              try (var f = fixture()) {
                create(f);
                f.released();
                return true;
              }
            });
      for (var result : executor.invokeAll(tasks)) assertTrue(result.get());
    }
  }

  @Test
  void nativePrivateTmpfsPublicBytes() throws Exception {
    Path runtime = Files.createTempDirectory(Path.of("/dev/shm"), "pgpt-dbcopy-");
    Files.setPosixFilePermissions(runtime, PosixFilePermissions.fromString("rwx------"));
    try (var root = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), runtime)) {
      long uid = Integer.toUnsignedLong((int) Files.getAttribute(runtime, "unix:uid"));
      long gid = Integer.toUnsignedLong((int) Files.getAttribute(runtime, "unix:gid"));
      byte[] raw = golden();
      new BackupDatabaseCopy(root, LinuxInodeSecurity.create(), uid, gid)
          .dump(
              raw,
              PART,
              p -> {
                assertArrayEquals(golden(), Files.readAllBytes(p));
                assertArrayEquals(new byte[raw.length], raw);
              });
      assertFalse(Files.exists(runtime.resolve(PART + ".part")));
    } finally {
      Files.delete(runtime);
    }
  }
}
