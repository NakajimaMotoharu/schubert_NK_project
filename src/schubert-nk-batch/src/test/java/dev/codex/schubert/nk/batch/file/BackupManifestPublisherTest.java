package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.BackupPublicationFixture.GID;
import static dev.codex.schubert.nk.batch.file.BackupPublicationFixture.PART;
import static dev.codex.schubert.nk.batch.file.BackupPublicationFixture.UID;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.FileTime;
import java.nio.file.attribute.PosixFilePermissions;
import java.security.MessageDigest;
import java.util.HashMap;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** NK-BAT-001/BAK/BKO/OPS009/UI251/SS341 6.8/343; SSC064/PG175; BAT242..257. */
final class BackupManifestPublisherTest {
  @TempDir Path temporary;

  @Test
  void independentGoldenPublication() throws Exception {
    try (var f = fixture()) {
      f.create();
      assertArrayEquals(
          BackupArtifactFixture.golden(), Files.readAllBytes(f.child.resolve("MANIFEST.json")));
      assertFalse(Files.exists(f.child.resolve(PART + ".part")));
      assertEquals(109, f.counts.get("clock"));
      f.released();
    }
  }

  @Test
  void privateCreationOwnership() throws Exception {
    try (var f = fixture()) {
      f.hook =
          (name, n) -> {
            if (name.equals("openWriter")) {
              try {
                assertEquals(
                    PosixFilePermissions.fromString("rw-------"),
                    Files.getPosixFilePermissions(f.child.resolve(PART + ".part")));
                assertEquals(0, Files.size(f.child.resolve(PART + ".part")));
              } catch (IOException ex) {
                throw new AssertionError(ex);
              }
            }
          };
      f.create();
      f.released();
      assertEquals(1, f.counts.get("createPrivateFile"));
      assertEquals(1, f.counts.get("publish"));
      assertEquals(1, f.counts.get("sync"));
    }
  }

  @Test
  void rootAndChildAdmission() throws Exception {
    for (long owner : new long[] {1, 0xffffffffL}) {
      try (var f = fixture()) {
        f.metadata =
            (role, values) -> {
              if (!role.equals("file")) {
                values.put("uid", (int) owner);
                values.put("gid", (int) owner);
              }
            };
        new BackupManifestPublisher(f.root, f, owner, owner, f, f::clock)
            .create(BackupArtifactFixture.expected(), PART);
        assertArrayEquals(
            BackupArtifactFixture.golden(), Files.readAllBytes(f.child.resolve("MANIFEST.json")));
        f.released();
      }
    }
    for (long owner : new long[] {0, -1, 0x100000000L}) {
      try (var f = fixture()) {
        assertThrows(
            IllegalArgumentException.class,
            () -> new BackupManifestPublisher(f.root, f, owner, GID));
        assertThrows(
            IllegalArgumentException.class,
            () -> new BackupManifestPublisher(f.root, f, UID, owner));
      }
    }
    for (String role : List.of("parent", "child")) {
      for (var change :
          Map.<String, Object>of("mode", 040755, "uid", 2, "gid", 2, "nlink", 1, "size", -1L)
              .entrySet()) {
        try (var f = fixture()) {
          f.metadata =
              (r, m) -> {
                if (r.equals(role)) m.put(change.getKey(), change.getValue());
              };
          fails(f);
        }
      }
    }
    try (var f = fixture()) {
      f.effective = 1;
      fails(f);
    }
    try (var f = fixture()) {
      f.readonly = true;
      fails(f);
    }
    try (var f = fixture()) {
      f.acl = null;
      fails(f);
    }
    try (var f = fixture()) {
      f.acl = new byte[] {1};
      fails(f);
    }
    try (var f = fixture()) {
      f.metadata =
          (r, m) -> {
            if (r.equals("child")) m.put("dev", -1L);
          };
      fails(f);
    }
  }

  @Test
  void metadataNullTypes() throws Exception {
    for (String key :
        List.of("mode", "uid", "gid", "nlink", "size", "dev", "ino", "lastModifiedTime", "ctime")) {
      for (Object value : new Object[] {null, "wrong"}) {
        for (int observation : new int[] {1, 2, 3, 4, 8, 14}) {
          try (var f = fixture()) {
            f.metadata =
                (r, m) -> {
                  if (f.counts.get("attributes") == observation) m.put(key, value);
                };
            fails(f);
          }
        }
      }
    }
    try (var f = fixture()) {
      f.nullMap = true;
      fails(f);
    }
  }

  @Test
  void filePermissionsAndLinks() throws Exception {
    try (var f = fixture()) {
      f.metadata =
          (r, m) -> {
            if (f.counts.get("attributes") == 4) m.put("size", 963L);
          };
      fails(f);
    }
    for (var change :
        Map.<String, Object>of(
                "mode", 0100644, "uid", 1, "gid", 1, "nlink", 2, "size", -1L, "dev", -1L)
            .entrySet()) {
      try (var f = fixture()) {
        f.metadata =
            (r, m) -> {
              if (r.equals("file")) m.put(change.getKey(), change.getValue());
            };
        fails(f);
      }
    }
    for (long size : new long[] {1, 4097}) {
      try (var f = fixture()) {
        f.metadata =
            (r, m) -> {
              if (r.equals("file")) m.put("size", size);
            };
        fails(f);
      }
    }
  }

  @Test
  void writeProgressBoundaries() throws Exception {
    for (int at = 1; at <= 3; at++) {
      try (var f = fixture()) {
        f.changedSize = "writerSize#" + at;
        fails(f);
      }
    }
    try (var f = fixture()) {
      f.chunk = 17;
      f.create();
      f.released();
      assertArrayEquals(
          BackupArtifactFixture.golden(), Files.readAllBytes(f.child.resolve("MANIFEST.json")));
    }
    for (String mode : List.of("zero", "negative", "large", "position")) {
      try (var f = fixture()) {
        f.writeMode = mode;
        fails(f);
      }
    }
    try (var f = fixture()) {
      f.nullWriter = true;
      fails(f);
    }
  }

  @Test
  void readbackAndIdentity() throws Exception {
    for (int at = 1; at <= 4; at++) {
      try (var f = fixture()) {
        f.changedSize = "size#" + at;
        fails(f);
      }
    }
    for (String mode : List.of("extra", "eof-position")) {
      try (var f = fixture()) {
        f.readMode = mode;
        fails(f);
      }
    }
    for (String mode : List.of("zero", "short", "large", "position", "content")) {
      try (var f = fixture()) {
        f.readMode = mode;
        fails(f);
      }
    }
    try (var f = fixture()) {
      f.nullReader = true;
      fails(f);
    }
    try (var f = fixture()) {
      f.metadata =
          (r, m) -> {
            if (f.counts.get("attributes") == 6) m.put("ctime", FileTime.fromMillis(0));
          };
      fails(f);
    }
  }

  @Test
  void namespaceReplacement() throws Exception {
    for (String boundary : List.of("publish", "openReader")) {
      try (var f = fixture()) {
        f.hook =
            (name, n) -> {
              if ((boundary.equals("publish") && name.equals("publish"))
                  || (boundary.equals("openReader") && name.equals("openReader") && n == 2)) {
                try {
                  String target = boundary.equals("publish") ? PART + ".part" : "MANIFEST.json";
                  Files.move(f.child.resolve(target), f.child.resolve("preserved-original"));
                  Files.write(f.child.resolve(target), BackupArtifactFixture.golden());
                  Files.setPosixFilePermissions(
                      f.child.resolve(target), PosixFilePermissions.fromString("rw-------"));
                } catch (IOException failure) {
                  throw new AssertionError(failure);
                }
              }
            };
        fails(f);
        assertArrayEquals(
            BackupArtifactFixture.golden(),
            Files.readAllBytes(f.child.resolve("preserved-original")));
      }
    }
    try (var f = fixture()) {
      f.hook =
          (name, n) -> {
            if (name.equals("openReader") && n == 1) {
              try {
                Files.move(f.child, f.parent.resolve("preserved-child"));
                Files.createDirectory(
                    f.child,
                    PosixFilePermissions.asFileAttribute(
                        PosixFilePermissions.fromString("rwx------")));
              } catch (IOException failure) {
                throw new AssertionError(failure);
              }
            }
          };
      fails(f);
      assertArrayEquals(
          BackupArtifactFixture.golden(),
          Files.readAllBytes(f.parent.resolve("preserved-child/MANIFEST.json")));
    }
    for (var change :
        Map.<String, Object>of("size", 963L, "lastModifiedTime", FileTime.fromMillis(0), "dev", -1L)
            .entrySet()) {
      try (var f = fixture()) {
        f.metadata =
            (r, m) -> {
              if (f.counts.get("attributes") == 8) m.put(change.getKey(), change.getValue());
            };
        fails(f);
      }
    }
    for (int observation : new int[] {4, 7, 8, 11, 12, 13, 14}) {
      try (var f = fixture()) {
        f.metadata =
            (r, m) -> {
              if (f.counts.get("attributes") == observation) m.put("ino", -1L);
            };
        fails(f);
      }
    }
  }

  @Test
  void collisionAndPartRetention() throws Exception {
    for (String name : List.of(PART + ".part", "MANIFEST.json")) {
      try (var f = fixture()) {
        Files.writeString(f.child.resolve(name), "existing public sentinel");
        var failure = assertThrows(StorageIoException.class, f::create);
        assertEquals(StorageIoException.Reason.COLLISION, failure.reason());
        assertEquals("existing public sentinel", Files.readString(f.child.resolve(name)));
        if (name.equals("MANIFEST.json"))
          assertArrayEquals(
              BackupArtifactFixture.golden(), Files.readAllBytes(f.child.resolve(PART + ".part")));
        f.released();
      }
    }
  }

  @Test
  void everyIoFailure() throws Exception {
    // Explicit operations, independent from production execution; every occurrence of this fixed
    // inventory.
    Map<String, Integer> inventory =
        Map.ofEntries(
            Map.entry("attributes", 14),
            Map.entry("acl", 14),
            Map.entry("readonly", 14),
            Map.entry("openDirectory", 2),
            Map.entry("createPrivateFile", 1),
            Map.entry("openEntry", 5),
            Map.entry("close", 8),
            Map.entry("openWriter", 1),
            Map.entry("writerSize", 3),
            Map.entry("write", 1),
            Map.entry("force", 1),
            Map.entry("closeWriter", 1),
            Map.entry("openReader", 2),
            Map.entry("read", 4),
            Map.entry("size", 4),
            Map.entry("closeReader", 2),
            Map.entry("publish", 1),
            Map.entry("sync", 1));
    try (var f = fixture()) {
      f.create();
      var counts = new HashMap<>(f.counts);
      counts.remove("clock");
      counts.remove("effectiveUid");
      assertEquals(inventory, counts);
      f.released();
    }
    for (var entry : inventory.entrySet())
      for (int at = 1; at <= entry.getValue(); at++) {
        try (var f = fixture()) {
          f.faults.put(entry.getKey() + "#" + at, new IOException("public synthetic failure"));
          fails(f);
        }
        for (Throwable unknown :
            List.of(new IllegalStateException("synthetic"), new AssertionError("synthetic"))) {
          try (var f = fixture()) {
            f.faults.put(entry.getKey() + "#" + at, unknown);
            assertSame(unknown, assertThrows(unknown.getClass(), f::create));
            f.released();
          }
        }
      }
  }

  @Test
  void deadlineAndInterrupt() throws Exception {
    for (int at = 2; at <= 109; at++) {
      int selected = at;
      try (var f = fixture()) {
        f.hook =
            (n, c) -> {
              if (n.equals("clock") && c == selected) f.time += 1_800_000_000_000L;
            };
        fails(f);
      }
      try (var f = fixture()) {
        f.hook =
            (n, c) -> {
              if (n.equals("clock") && c == selected) Thread.currentThread().interrupt();
            };
        try {
          fails(f);
          assertTrue(Thread.currentThread().isInterrupted());
        } finally {
          Thread.interrupted();
        }
      }
    }
    for (long initial : new long[] {100, Long.MAX_VALUE - 2}) {
      try (var f = fixture()) {
        f.time = initial;
        f.hook =
            (n, c) -> {
              if (n.equals("clock") && c == 2) f.time += 1_799_999_999_999L;
            };
        f.create();
        f.released();
      }
    }
    try (var f = fixture()) {
      f.hook =
          (n, c) -> {
            if (n.equals("effectiveUid") && c == 2) f.effective = 1;
          };
      fails(f);
    }
    for (long elapsed : new long[] {-1, 1_800_000_000_000L}) {
      try (var f = fixture()) {
        f.hook =
            (n, c) -> {
              if (n.equals("clock") && c == 2) f.time += elapsed;
            };
        fails(f);
      }
    }
    try (var f = fixture()) {
      Thread.currentThread().interrupt();
      try {
        fails(f);
        assertTrue(Thread.currentThread().isInterrupted());
      } finally {
        Thread.interrupted();
      }
    }
    try (var f = fixture()) {
      f.hook =
          (n, c) -> {
            if (n.equals("clock") && c == 2) Thread.currentThread().interrupt();
          };
      try {
        fails(f);
        assertTrue(Thread.currentThread().isInterrupted());
      } finally {
        Thread.interrupted();
      }
    }
  }

  @Test
  void compoundAndBufferWipe() throws Exception {
    for (Throwable primary :
        List.of(new IllegalStateException("synthetic"), new AssertionError("synthetic"))) {
      try (var f = fixture()) {
        f.faults.put("write#1", primary);
        f.faults.put("closeWriter#1", primary);
        Throwable actual = assertThrows(primary.getClass(), f::create);
        assertSame(primary, actual);
        assertEquals(1, actual.getSuppressed().length);
        assertInstanceOf(StorageIoException.class, actual.getSuppressed()[0]);
        f.released();
      }
    }
    try (var f = fixture()) {
      Error fatal = new AssertionError("synthetic");
      f.faults.put("write#1", new IOException("synthetic"));
      f.faults.put("closeWriter#1", fatal);
      assertSame(fatal, assertThrows(AssertionError.class, f::create));
      f.released();
    }
  }

  @Test
  void nullAndClosedContracts() throws Exception {
    try (var f = fixture()) {
      assertThrows(NullPointerException.class, () -> f.publisher().create(null, PART));
      assertThrows(
          NullPointerException.class,
          () -> f.publisher().create(BackupArtifactFixture.expected(), null));
      assertThrows(
          NullPointerException.class, () -> new BackupManifestPublisher(null, f, UID, GID));
      assertThrows(
          NullPointerException.class, () -> new BackupManifestPublisher(f.root, null, UID, GID));
      assertThrows(
          NullPointerException.class,
          () -> new BackupManifestPublisher(f.root, f, UID, GID, null, () -> 0));
      assertThrows(
          NullPointerException.class,
          () -> new BackupManifestPublisher(f.root, f, UID, GID, f, null));
      f.released();
    }
    var f = fixture();
    try {
      f.root.close();
      assertThrows(StorageIoException.class, f::create);
    } finally {
      f.close();
    }
  }

  @Test
  void concurrentNoReplace() throws Exception {
    try (var f = fixture();
        var executor = Executors.newVirtualThreadPerTaskExecutor()) {
      var publisher = f.publisher();
      Callable<Boolean> action =
          () -> {
            try {
              publisher.create(BackupArtifactFixture.expected(), PART);
              return true;
            } catch (StorageIoException collision) {
              assertEquals(StorageIoException.Reason.COLLISION, collision.reason());
              return false;
            }
          };
      var a = executor.submit(action);
      var b = executor.submit(action);
      assertNotEquals(a.get(), b.get());
      f.released();
      assertArrayEquals(
          BackupArtifactFixture.golden(), Files.readAllBytes(f.child.resolve("MANIFEST.json")));
    }
    // Different instances require the caller's common exclusion, per SS341 6.8.
    try (var f = fixture();
        var executor = Executors.newVirtualThreadPerTaskExecutor()) {
      Object callerExclusion = new Object();
      var sequence = new java.util.concurrent.atomic.AtomicInteger();
      Callable<Boolean> action =
          () -> {
            synchronized (callerExclusion) {
              try {
                f.publisher()
                    .create(
                        BackupArtifactFixture.expected(), new UUID(1, sequence.incrementAndGet()));
                return true;
              } catch (StorageIoException collision) {
                assertEquals(StorageIoException.Reason.COLLISION, collision.reason());
                return false;
              }
            }
          };
      var a = executor.submit(action);
      var b = executor.submit(action);
      assertNotEquals(a.get(), b.get());
      assertArrayEquals(
          BackupArtifactFixture.golden(), Files.readAllBytes(f.child.resolve("MANIFEST.json")));
      f.released();
    }
  }

  @Test
  void nativeIoAndFactory() throws Exception {
    try (var f = fixture()) {
      f.effective = 1;
      assertThrows(
          StorageIoException.class,
          () ->
              new BackupManifestPublisher(f.root, f, UID, GID)
                  .create(BackupArtifactFixture.expected(), PART));
      f.released();
    }
  }

  @Test
  void independentPublicationTrace() throws Exception {
    try (var f = fixture()) {
      f.create();
      byte[] actual = Files.readAllBytes(f.child.resolve("MANIFEST.json"));
      assertEquals(964, actual.length);
      assertEquals(
          BackupArtifactFixture.MANIFEST_HASH,
          HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(actual)));
      Path trace = Path.of("target", "backup-publication-traces");
      Files.createDirectories(trace);
      Files.writeString(
          trace.resolve("PT-BAT-257-publication.txt"),
          actual.length
              + "|"
              + HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(actual))
              + "\n"
              + "create="
              + f.counts.get("createPrivateFile")
              + "|publish="
              + f.counts.get("publish")
              + "|sync="
              + f.counts.get("sync")
              + "\n"
              + "io="
              + f.position
              + "|clock="
              + f.counts.get("clock")
              + "\n");
      f.released();
    }
  }

  private BackupPublicationFixture fixture() throws Exception {
    return new BackupPublicationFixture(temporary);
  }

  private static void fails(BackupPublicationFixture f) {
    var failure = assertThrows(StorageIoException.class, f::create);
    assertEquals(StorageIoException.Reason.UNAVAILABLE, failure.reason());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    f.released();
  }
}
