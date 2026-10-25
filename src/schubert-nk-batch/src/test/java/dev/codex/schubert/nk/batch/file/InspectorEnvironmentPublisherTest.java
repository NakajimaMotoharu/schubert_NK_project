package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.Metadata;
import dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.Snapshot;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Proxy;
import java.nio.ByteBuffer;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.FileTime;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.function.BiConsumer;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;
import org.junit.jupiter.api.io.TempDir;

/** PG-D-154; OPS-009/UI251/SS343 6.11; independent PUB001..012; no real root/service mutation. */
final class InspectorEnvironmentPublisherTest {
  private static final BatchRun RUN =
      new BatchRun(
          UUID.fromString("00000000-0000-0000-0000-000000000154"),
          Instant.parse("2026-09-12T00:00:00Z"));
  private static final String GOLDEN =
      "NK_INSPECTOR_RUN_ID=00000000-0000-0000-0000-000000000154\n"
          + "NK_INSPECTOR_CUTOFF=2026-09-12T00:00:00Z\n";
  private static final String NAME = "inbox-inspector.env";
  @TempDir Path temporary;

  @Test
  void inspector919002FreshnessNeverReusesFixedEntriesOrDeletesUnrelatedRoleData()
      throws Exception {
    for (String name : List.of(NAME, "11111111-1111-4111-8111-111111111111.part")) {
      try (var f = fixture()) {
        Path preserved = f.directory.resolve(name);
        Files.writeString(preserved, "independent-old-byte-vector");
        assertThrows(StorageIoException.class, f.publisher::requireFresh);
        assertEquals("independent-old-byte-vector", Files.readString(preserved));
        assertEquals(0, f.count("unlink"));
        assertEquals(0, f.count("create"));
        f.released();
      }
    }
    try (var f = fixture()) {
      Path unrelated = f.directory.resolve("other-role-observation");
      Files.writeString(unrelated, "unrelated-preserved-byte-vector");
      f.publisher.requireFresh();
      assertEquals("unrelated-preserved-byte-vector", Files.readString(unrelated));
      assertFalse(Files.exists(f.target));
      assertEquals(0, f.count("unlink"));
      assertEquals(0, f.count("create"));
      f.released();
    }
  }

  @Test
  void createAndRetire() throws Exception {
    try (var f = fixture()) {
      f.publisher.prepare(RUN);
      assertEquals(GOLDEN, Files.readString(f.target));
      assertEquals(0100600, Files.getAttribute(f.target, "unix:mode"));
      assertEquals(1, Files.getAttribute(f.target, "unix:nlink"));
      assertFalse(Files.exists(f.part));
      assertEquals(1, f.count("create"));
      assertEquals(1, f.count("publish"));
      assertEquals(1, f.count("force"));
      assertEquals(1, f.count("sync"));
      f.released();
      f.reset();
      f.publisher.retire(RUN);
      assertFalse(Files.exists(f.target));
      assertEquals(1, f.count("unlink"));
      assertEquals(1, f.count("sync"));
      f.reset();
      f.publisher.retire(RUN);
      assertEquals(0, f.count("unlink"));
      assertEquals(0, f.count("sync"));
      boolean alive = f.root.atDirectory(Files::isDirectory);
      assertTrue(alive);
    }
  }

  @Test
  void sameRunAndDifferentRun() throws Exception {
    try (var f = fixture()) {
      f.publisher.prepare(RUN);
      Object inode = Files.getAttribute(f.target, "unix:ino");
      f.reset();
      f.publisher.prepare(RUN);
      assertEquals(GOLDEN, Files.readString(f.target));
      assertEquals(inode, Files.getAttribute(f.target, "unix:ino"));
      assertEquals(0, f.count("create"));
      assertEquals(0, f.count("write"));
      assertEquals(1, f.count("force"));
      assertEquals(1, f.count("sync"));
      for (BatchRun other :
          List.of(
              new BatchRun(new UUID(1, 2), RUN.cutoff()),
              new BatchRun(RUN.id(), RUN.cutoff().minusNanos(1000)),
              new BatchRun(RUN.id(), RUN.cutoff().plusNanos(1000)))) {
        assertThrows(IllegalArgumentException.class, () -> f.publisher.prepare(other));
        assertThrows(IllegalArgumentException.class, () -> f.publisher.retire(other));
        assertEquals(GOLDEN, Files.readString(f.target));
        assertEquals(inode, Files.getAttribute(f.target, "unix:ino"));
      }
      Files.writeString(f.target, GOLDEN.replace("RUN_ID", "UNSAFE"));
      assertThrows(IllegalArgumentException.class, () -> f.publisher.prepare(RUN));
      assertThrows(IllegalArgumentException.class, () -> f.publisher.retire(RUN));
      assertEquals(GOLDEN.replace("RUN_ID", "UNSAFE"), Files.readString(f.target));
    }
  }

  @Test
  void privatePartCollisions() throws Exception {
    for (String content :
        List.of("", "NK_INSPECTOR_", GOLDEN, GOLDEN.replace("00:00:00Z", "00:00:01Z")))
      try (var f = fixture()) {
        Files.writeString(f.part, content);
        failure(() -> f.publisher.prepare(RUN));
        assertEquals(content, Files.readString(f.part));
        assertFalse(Files.exists(f.target));
        assertEquals(0, f.count("openWriter"));
      }
    try (var f = fixture()) {
      Path outside = Files.writeString(f.directory.resolve("outside"), "outside unchanged");
      Files.createSymbolicLink(f.part, outside);
      failure(() -> f.publisher.prepare(RUN));
      assertEquals("outside unchanged", Files.readString(outside));
      assertTrue(Files.isSymbolicLink(f.part));
      assertFalse(Files.exists(f.target));
    }
  }

  @Test
  void permissionsAndNull() throws Exception {
    for (String role : List.of("dir", "file")) {
      for (String key :
          List.of("mode", "uid", "gid", "nlink", "size", "dev", "ino", "lastModifiedTime", "ctime"))
        for (Object wrong : Arrays.asList(null, "wrong type"))
          try (var f = fixture()) {
            f.change =
                (observed, values) -> {
                  if (observed.equals(role)) values.put(key, wrong);
                };
            failure(() -> f.publisher.prepare(RUN));
            assertEquals(0, f.count("write"));
          }
      for (String field : List.of("mode", "uid", "gid", "nlink", "size"))
        try (var f = fixture()) {
          f.change =
              (observed, values) -> {
                if (observed.equals(role))
                  values.put(field, field.equals("size") ? (Object) (-1L) : 0);
                if (observed.equals(role) && (field.equals("uid") || field.equals("gid")))
                  values.put(field, 99);
              };
          failure(() -> f.publisher.prepare(RUN));
          assertEquals(0, f.count("write"));
        }
      for (String invalid :
          List.of("nullAttributes", "nullAcl", "acl", "nullFilesystem", "filesystem", "readonly"))
        try (var f = fixture()) {
          f.badRole = role;
          f.invalid = invalid;
          failure(() -> f.publisher.prepare(RUN));
          assertEquals(0, f.count("write"));
        }
    }
    try (var f = fixture()) {
      f.change =
          (role, values) -> {
            if (role.equals("file")) values.put("dev", Long.MAX_VALUE);
          };
      failure(() -> f.publisher.prepare(RUN));
      assertEquals(0, f.count("write"));
    }
    // Independent value-object comparisons: mutation must not be hidden by allowed ctime changes.
    FileTime time = FileTime.fromMillis(1);
    Metadata original = new Metadata(0100600, 0, 0, 1, 90, 2, 3, time, time);
    Snapshot before = new Snapshot(original, "tmpfs", false);
    List<Metadata> different =
        List.of(
            new Metadata(0100640, 0, 0, 1, 90, 2, 3, time, time),
            new Metadata(0100600, 1, 0, 1, 90, 2, 3, time, time),
            new Metadata(0100600, 0, 1, 1, 90, 2, 3, time, time),
            new Metadata(0100600, 0, 0, 2, 90, 2, 3, time, time),
            new Metadata(0100600, 0, 0, 1, 90, 4, 3, time, time),
            new Metadata(0100600, 0, 0, 1, 90, 2, 4, time, time));
    for (Metadata other : different) {
      Snapshot changed = new Snapshot(other, "tmpfs", false);
      assertFalse(before.sameIdentity(changed));
      assertFalse(before.samePublishedFile(changed));
    }
    assertFalse(before.sameIdentity(new Snapshot(original, "ext4", false)));
    assertFalse(before.sameIdentity(new Snapshot(original, "tmpfs", true)));
    assertFalse(
        before.samePublishedFile(
            new Snapshot(new Metadata(0100600, 0, 0, 1, 91, 2, 3, time, time), "tmpfs", false)));
    assertFalse(
        before.samePublishedFile(
            new Snapshot(
                new Metadata(0100600, 0, 0, 1, 90, 2, 3, FileTime.fromMillis(2), time),
                "tmpfs",
                false)));
    assertTrue(
        before.samePublishedFile(
            new Snapshot(
                new Metadata(0100600, 0, 0, 1, 90, 2, 3, time, FileTime.fromMillis(2)),
                "tmpfs",
                false)));
  }

  @Test
  void boundedWrites() throws Exception {
    for (int length : List.of(0, 110, 111))
      try (var f = fixture()) {
        Files.write(f.target, new byte[length]);
        if (length == 110)
          assertThrows(IllegalArgumentException.class, () -> f.publisher.prepare(RUN));
        else failure(() -> f.publisher.prepare(RUN));
        assertEquals(length, Files.size(f.target));
        assertEquals(0, f.count("openWriter"));
      }
    // BUG-151/YKT-117: inode metadata and channel sizes are independent observations.
    for (int at : List.of(2, 3))
      try (var f = fixture()) {
        f.change =
            (role, values) -> {
              if (role.equals("file") && f.count("attributes") == at)
                values.put("size", at == 2 ? 1L : (long) GOLDEN.length() + 1);
            };
        failure(() -> f.publisher.prepare(RUN));
        assertFalse(Files.exists(f.target));
        assertTrue(Files.exists(f.part));
        assertEquals(at == 2 ? "" : GOLDEN, Files.readString(f.part));
        assertEquals(at == 2 ? 0 : 1, f.count("write"));
      }
    try (var f = fixture()) {
      f.writeLimit = 7;
      f.publisher.prepare(RUN);
      assertEquals(GOLDEN, Files.readString(f.target));
      assertTrue(f.count("write") > 1);
    }
    for (String behavior : List.of("zero", "negative", "overflow", "position"))
      try (var f = fixture()) {
        f.writeBehavior = behavior;
        failure(() -> f.publisher.prepare(RUN));
        assertFalse(Files.exists(f.target));
        assertTrue(Files.exists(f.part));
      }
    for (int at : List.of(1, 2))
      for (boolean reuse : List.of(false, true))
        try (var f = fixture()) {
          if (reuse) f.seed();
          f.badSizeAt = at;
          failure(() -> f.publisher.prepare(RUN));
          assertEquals(reuse, Files.exists(f.target));
        }
    for (boolean reuse : List.of(false, true))
      try (var f = fixture()) {
        if (reuse) f.seed();
        f.nullWriter = true;
        failure(() -> f.publisher.prepare(RUN));
      }
    for (String stamp : List.of("0001-01-01T00:00:00Z", "9999-12-31T23:59:59.999999Z"))
      try (var f = fixture()) {
        f.publisher.prepare(new BatchRun(RUN.id(), Instant.parse(stamp)));
        String expected = GOLDEN.replace("2026-09-12T00:00:00Z", stamp);
        assertEquals(expected, Files.readString(f.target));
        assertEquals(expected.length(), Files.size(f.target));
        assertTrue(expected.length() <= 110);
      }
  }

  @Test
  void replacementsAndRetention() throws Exception {
    // BUG-152/YKT-118: lower-level read stability does not establish the caller's original inode.
    for (boolean reuse : List.of(false, true))
      for (int point : List.of(11, 16))
        try (var f = fixture()) {
          if (reuse) f.seed();
          f.on(
              "attributes",
              point,
              () -> {
                Files.move(f.target, f.directory.resolve("before-read"));
                Files.writeString(f.target, GOLDEN);
              });
          failure(() -> f.publisher.prepare(RUN));
          assertEquals(GOLDEN, Files.readString(f.target));
          assertEquals(GOLDEN, Files.readString(f.directory.resolve("before-read")));
        }
    for (String kind : List.of("symlink", "directory", "hardlink"))
      try (var f = fixture()) {
        if (kind.equals("symlink"))
          Files.createSymbolicLink(f.target, f.directory.resolve("absent"));
        else if (kind.equals("directory")) Files.createDirectory(f.target);
        else {
          Files.writeString(f.target, GOLDEN);
          Files.createLink(f.directory.resolve("linked"), f.target);
        }
        failure(() -> f.publisher.prepare(RUN));
        failure(() -> f.publisher.retire(RUN));
        assertEquals(0, f.count("openWriter"));
      }
    try (var f = fixture()) {
      f.on(
          "writerClose",
          1,
          () -> {
            Files.move(f.part, f.directory.resolve("saved"));
            Files.writeString(f.part, GOLDEN);
          });
      failure(() -> f.publisher.prepare(RUN));
      assertFalse(Files.exists(f.target));
      assertEquals(GOLDEN, Files.readString(f.directory.resolve("saved")));
    }
    try (var f = fixture()) {
      f.on("publish", 1, () -> Files.writeString(f.target, GOLDEN));
      failure(() -> f.publisher.prepare(RUN));
      assertEquals(GOLDEN, Files.readString(f.target));
      assertEquals(GOLDEN, Files.readString(f.part));
    }
    try (var f = fixture()) {
      f.on(
          "sync",
          1,
          () -> {
            Files.move(f.target, f.directory.resolve("saved"));
            Files.writeString(f.target, GOLDEN);
          });
      failure(() -> f.publisher.prepare(RUN));
      assertEquals(GOLDEN, Files.readString(f.target));
    }
    try (var f = fixture()) {
      f.on(
          "sync",
          1,
          () ->
              f.change =
                  (role, values) -> {
                    if (role.equals("dir")) values.put("ino", Long.MAX_VALUE);
                  });
      failure(() -> f.publisher.prepare(RUN));
      assertEquals(GOLDEN, Files.readString(f.target));
    }
    try (var f = fixture()) {
      f.seed();
      f.on(
          "openEntry",
          4,
          () -> {
            Files.move(f.target, f.directory.resolve("saved"));
            Files.writeString(f.target, GOLDEN);
          });
      failure(() -> f.publisher.retire(RUN));
      assertEquals(GOLDEN, Files.readString(f.target));
      assertEquals(0, f.count("unlink"));
    }
  }

  @Test
  void createFailureMatrix() throws Exception {
    matrix(
        false,
        false,
        Map.ofEntries(
            Map.entry("attributes", 17),
            Map.entry("acl", 17),
            Map.entry("filesystem", 17),
            Map.entry("readonly", 17),
            Map.entry("openEntry", 8),
            Map.entry("entryClose", 8),
            Map.entry("create", 1),
            Map.entry("publish", 1),
            Map.entry("sync", 1),
            Map.entry("openWriter", 1),
            Map.entry("writeSize", 2),
            Map.entry("write", 1),
            Map.entry("force", 1),
            Map.entry("writerClose", 1),
            Map.entry("openRead", 2),
            Map.entry("readSize", 4),
            Map.entry("read", 4),
            Map.entry("readClose", 2)));
    try (var f = fixture()) {
      f.fail = "sync";
      failure(() -> f.publisher.prepare(RUN));
      assertFalse(Files.exists(f.part));
      assertEquals(GOLDEN, Files.readString(f.target));
      f.reset();
      f.publisher.prepare(RUN);
      assertEquals(GOLDEN, Files.readString(f.target));
    }
    try (var f = fixture()) {
      f.fail = "write";
      f.rawClose = true;
      failure(() -> f.publisher.prepare(RUN));
      assertTrue(Files.exists(f.part));
    }
  }

  @Test
  void reuseFailureMatrix() throws Exception {
    matrix(
        true,
        false,
        Map.ofEntries(
            Map.entry("attributes", 17),
            Map.entry("acl", 17),
            Map.entry("filesystem", 17),
            Map.entry("readonly", 17),
            Map.entry("openEntry", 8),
            Map.entry("entryClose", 8),
            Map.entry("sync", 1),
            Map.entry("openWriter", 1),
            Map.entry("writeSize", 2),
            Map.entry("force", 1),
            Map.entry("writerClose", 1),
            Map.entry("openRead", 2),
            Map.entry("readSize", 4),
            Map.entry("read", 4),
            Map.entry("readClose", 2)));
    try (var f = fixture()) {
      f.seed();
      f.rawRead = true;
      f.rawClose = true;
      failure(() -> f.publisher.prepare(RUN));
      assertEquals(GOLDEN, Files.readString(f.target));
    }
  }

  @Test
  void retireFailureMatrix() throws Exception {
    matrix(
        true,
        true,
        Map.ofEntries(
            Map.entry("attributes", 9),
            Map.entry("acl", 9),
            Map.entry("filesystem", 9),
            Map.entry("readonly", 9),
            Map.entry("openEntry", 4),
            Map.entry("entryClose", 4),
            Map.entry("unlink", 1),
            Map.entry("sync", 1),
            Map.entry("openRead", 1),
            Map.entry("readSize", 2),
            Map.entry("read", 2),
            Map.entry("readClose", 1)));
    for (String point : List.of("attributes", "entryClose", "openEntry"))
      try (var f = fixture()) {
        f.seed();
        f.fail = point;
        f.reason = StorageIoException.Reason.MISSING;
        f.failAt = point.equals("entryClose") ? 1 : 2;
        failure(() -> f.publisher.retire(RUN));
        assertEquals(GOLDEN, Files.readString(f.target));
        assertEquals(0, f.count("unlink"));
      }
    try (var f = fixture()) {
      f.seed();
      f.fail = "sync";
      failure(() -> f.publisher.retire(RUN));
      assertFalse(Files.exists(f.target));
      f.reset();
      f.publisher.retire(RUN);
    }
  }

  @Test
  void interruptionAndRuntime() throws Exception {
    for (boolean reuse : List.of(false, true))
      for (boolean known : List.of(false, true))
        for (Throwable unknown :
            List.of(
                new IllegalStateException("public compound"),
                new NullPointerException("public compound"),
                new AssertionError("public compound")))
          try (var f = fixture()) {
            if (reuse) f.seed();
            String body = reuse ? "force" : "write";
            if (known) f.fail = body;
            f.compound =
                (name, count) -> {
                  if (count == 1 && (name.equals("writerClose") || (!known && name.equals(body)))) {
                    if (unknown instanceof RuntimeException failure) throw failure;
                    throw (Error) unknown;
                  }
                };
            assertSame(unknown, assertThrows(unknown.getClass(), () -> f.publisher.prepare(RUN)));
            assertEquals(1, f.count(body));
            assertEquals(1, f.count("writerClose"));
            assertEquals(known ? 0 : 1, unknown.getSuppressed().length);
            for (Throwable secondary : unknown.getSuppressed())
              failure(
                  () -> {
                    throw secondary;
                  });
            f.released();
            assertFalse(f.compoundBuffers.isEmpty());
            for (byte[] bytes : f.compoundBuffers) assertArrayEquals(new byte[bytes.length], bytes);
            if (reuse) assertEquals(GOLDEN, Files.readString(f.target));
            else {
              assertFalse(Files.exists(f.target));
              assertTrue(Files.exists(f.part));
              assertEquals(0, Files.size(f.part));
            }
          }
    for (boolean retire : List.of(false, true))
      try (var f = fixture()) {
        Thread.currentThread().interrupt();
        try {
          failure(
              () -> {
                if (retire) f.publisher.retire(RUN);
                else f.publisher.prepare(RUN);
              });
          assertTrue(Thread.currentThread().isInterrupted());
          assertEquals(0, f.count("attributes"));
        } finally {
          Thread.interrupted();
        }
      }
    for (String path : List.of("new", "reuse", "retire"))
      for (boolean late : List.of(false, true))
        try (var f = fixture()) {
          if (!path.equals("new")) f.seed();
          f.on(
              late ? "readonly" : "openRead",
              late ? (path.equals("retire") ? 9 : 17) : 1,
              () -> Thread.currentThread().interrupt());
          try {
            failure(
                () -> {
                  if (path.equals("retire")) f.publisher.retire(RUN);
                  else f.publisher.prepare(RUN);
                });
            assertTrue(Thread.currentThread().isInterrupted());
          } finally {
            Thread.interrupted();
          }
        }
    for (String path : List.of("new", "reuse", "retire"))
      try (var f = fixture()) {
        if (!path.equals("new")) f.seed();
        var expected = new IllegalStateException("synthetic runtime failure");
        f.on(
            "attributes",
            3,
            () -> {
              throw expected;
            });
        assertSame(
            expected,
            assertThrows(
                IllegalStateException.class,
                () -> {
                  if (path.equals("retire")) f.publisher.retire(RUN);
                  else f.publisher.prepare(RUN);
                }));
        f.released();
      }
  }

  @Test
  void concurrentInvocations() throws Exception {
    try (var f = fixture();
        var executor = Executors.newFixedThreadPool(8)) {
      var pending = new ArrayList<Future<?>>();
      for (int i = 0; i < 32; i++)
        pending.add(
            executor.submit(
                () -> {
                  f.publisher.prepare(RUN);
                  return true;
                }));
      for (var future : pending) future.get(10, TimeUnit.SECONDS);
      assertEquals(1, f.count("create"));
      assertEquals(1, f.count("publish"));
      assertEquals(GOLDEN, Files.readString(f.target));
      pending.clear();
      for (int i = 0; i < 32; i++)
        pending.add(
            executor.submit(
                () -> {
                  f.publisher.retire(RUN);
                  return true;
                }));
      for (var future : pending) future.get(10, TimeUnit.SECONDS);
      assertEquals(1, f.count("unlink"));
      assertFalse(Files.exists(f.target));
      f.publisher.prepare(RUN);
      pending.clear();
      for (int i = 1; i <= 32; i++) {
        var wrong = new BatchRun(new UUID(5, i), RUN.cutoff());
        pending.add(
            executor.submit(
                () ->
                    assertThrows(
                        IllegalArgumentException.class, () -> f.publisher.prepare(wrong))));
      }
      for (var future : pending) future.get(10, TimeUnit.SECONDS);
      assertEquals(GOLDEN, Files.readString(f.target));
    }
  }

  @Test
  void nativeAndConstructor() throws Exception {
    try (var f = fixture()) {
      assertThrows(NullPointerException.class, () -> new InspectorEnvironmentPublisher(null, f));
      assertThrows(
          NullPointerException.class, () -> new InspectorEnvironmentPublisher(f.root, null));
      assertThrows(
          NullPointerException.class, () -> new InspectorEnvironmentPublisher(f.root, f, null));
      assertThrows(NullPointerException.class, () -> f.publisher.prepare(null));
      assertThrows(NullPointerException.class, () -> f.publisher.retire(null));
      assertEquals(0, f.count("attributes"));
      var nativeSecurity = LinuxInodeSecurity.create();
      assertNotEquals(
          0, nativeSecurity.effectiveUid(), "local PT runs unprivileged; root deployment is IT");
      failure(() -> new InspectorEnvironmentPublisher(f.root, nativeSecurity).prepare(RUN));
      f.uid = 1;
      failure(() -> f.publisher.retire(RUN));
      assertEquals(0, f.count("attributes"));
    }
    var f = fixture();
    try {
      f.root.close();
      failure(() -> f.publisher.prepare(RUN));
      failure(() -> f.publisher.retire(RUN));
    } finally {
      f.close();
    }
  }

  private void matrix(boolean existing, boolean retire, Map<String, Integer> expected)
      throws Exception {
    try (var f = fixture()) {
      if (existing) f.seed();
      if (retire) f.publisher.retire(RUN);
      else f.publisher.prepare(RUN);
      assertEquals(expected, f.counts, "independent SS call-position inventory");
    }
    for (var entry : expected.entrySet())
      for (int occurrence = 1; occurrence <= entry.getValue(); occurrence++)
        try (var f = fixture()) {
          if (existing) f.seed();
          f.fail = entry.getKey();
          f.failAt = occurrence;
          failure(
              () -> {
                if (retire) f.publisher.retire(RUN);
                else f.publisher.prepare(RUN);
              });
          assertEquals(occurrence, f.count(entry.getKey()));
          if (existing && !retire) assertEquals(GOLDEN, Files.readString(f.target));
          f.released();
        }
  }

  private Fixture fixture() throws Exception {
    return new Fixture(Files.createTempDirectory(temporary, "publish-"));
  }

  private static void failure(Executable operation) {
    var failure = assertThrows(StorageIoException.class, operation);
    assertEquals(StorageIoException.Reason.UNAVAILABLE, failure.reason());
    assertEquals("transfer storage operation failed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  @FunctionalInterface
  interface Action {
    void execute() throws IOException;
  }

  private static final class Fixture
      implements AutoCloseable, InspectorEnvironmentPublisher.Io, InodeSecurityCalls {
    final Path directory;
    final Path target;
    final Path part;
    final OwnedTransferDirectory root;
    final InspectorEnvironmentPublisher publisher;
    final InspectorEnvironmentPublisher.NioIo nativeIo = new InspectorEnvironmentPublisher.NioIo();
    final Map<String, Integer> counts = new ConcurrentHashMap<>();
    final Set<Integer> entries = ConcurrentHashMap.newKeySet();
    int writers;
    int readers;
    String fail = "";
    String hookName = "";
    String invalid = "";
    String badRole = "";
    String writeBehavior = "normal";
    int failAt = 1;
    int hookAt = 1;
    int badSizeAt;
    int writeLimit = Integer.MAX_VALUE;
    long uid;
    boolean nullWriter;
    boolean rawRead;
    boolean rawClose;
    StorageIoException.Reason reason = StorageIoException.Reason.UNAVAILABLE;
    BiConsumer<String, Map<String, Object>> change = (role, values) -> {};
    Action hook = () -> {};
    BiConsumer<String, Integer> compound = (name, count) -> {};
    final List<byte[]> compoundBuffers = Collections.synchronizedList(new ArrayList<>());

    Fixture(Path directory) throws Exception {
      this.directory = directory;
      target = directory.resolve(NAME);
      part = directory.resolve(RUN.id() + ".part");
      DirectoryCalls delegate = LinuxDirectoryCalls.create();
      DirectoryCalls calls =
          (DirectoryCalls)
              Proxy.newProxyInstance(
                  getClass().getClassLoader(),
                  new Class<?>[] {DirectoryCalls.class},
                  (proxy, method, args) -> {
                    String name = method.getName();
                    String point =
                        switch (name) {
                          case "createPrivateFile" -> "create";
                          case "openEntry", "publish", "unlink", "sync" -> name;
                          default -> "";
                        };
                    if (!point.isEmpty()) point(point);
                    boolean ownedClose = name.equals("close") && entries.remove((Integer) args[0]);
                    Object result;
                    try {
                      result = method.invoke(delegate, args);
                    } catch (InvocationTargetException failure) {
                      throw failure.getCause();
                    }
                    if (name.equals("createPrivateFile") || name.equals("openEntry"))
                      entries.add((Integer) result);
                    if (ownedClose) point("entryClose");
                    return result;
                  });
      root = OwnedTransferDirectory.open(calls, directory);
      publisher = new InspectorEnvironmentPublisher(root, this, this);
      reset();
    }

    void seed() throws IOException {
      Files.writeString(target, GOLDEN);
      reset();
    }

    void reset() {
      counts.clear();
      fail = "";
      hookName = "";
      rawClose = false;
      rawRead = false;
    }

    void on(String name, int at, Action action) {
      hookName = name;
      hookAt = at;
      hook = action;
    }

    int count(String name) {
      return counts.getOrDefault(name, 0);
    }

    void point(String name) throws StorageIoException {
      int at = counts.merge(name, 1, Integer::sum);
      compound.accept(name, at);
      if (hookName.equals(name) && hookAt == at) {
        try {
          hook.execute();
        } catch (IOException failure) {
          throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
        }
      }
      if (fail.equals(name) && failAt == at) throw new StorageIoException(reason);
    }

    String role(Path held) throws IOException {
      int mode = (Integer) nativeIo.attributes(held).get("mode");
      return (mode & 0170000) == 040000 ? "dir" : "file";
    }

    boolean selected(Path held) throws IOException {
      return badRole.equals(role(held));
    }

    @Override
    public Map<String, Object> attributes(Path held) throws IOException {
      point("attributes");
      if (invalid.equals("nullAttributes") && selected(held)) return null;
      var result = new HashMap<>(nativeIo.attributes(held));
      String role = role(held);
      int type = (Integer) result.get("mode") & 0170000;
      result.put("mode", type | (role.equals("dir") ? 0700 : 0600));
      result.put("uid", 0);
      result.put("gid", 0);
      change.accept(role, result);
      return result;
    }

    @Override
    public String filesystem(Path held) throws IOException {
      point("filesystem");
      assertNotNull(nativeIo.filesystem(held));
      if (selected(held)) {
        if (invalid.equals("nullFilesystem")) return null;
        if (invalid.equals("filesystem")) return "nfs";
      }
      return "tmpfs";
    }

    @Override
    public byte[] accessAcl(Path held, int maximum) throws StorageIoException {
      point("acl");
      assertEquals(44, maximum);
      try {
        if (selected(held)) {
          if (invalid.equals("nullAcl")) return null;
          if (invalid.equals("acl")) return new byte[] {2, 0, 0, 0};
        }
      } catch (IOException failure) {
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      }
      return new byte[0];
    }

    @Override
    public boolean readOnlyFilesystem(Path held) throws StorageIoException {
      point("readonly");
      try {
        return selected(held) && invalid.equals("readonly");
      } catch (IOException failure) {
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      }
    }

    @Override
    public long effectiveUid() {
      return uid;
    }

    @Override
    public InspectorEnvironmentPublisher.Writer openWriter(Path held) throws IOException {
      point("openWriter");
      if (nullWriter) return null;
      var writer = nativeIo.openWriter(held);
      writers++;
      return new InspectorEnvironmentPublisher.Writer() {
        @Override
        public int write(ByteBuffer source) throws IOException {
          compoundBuffers.add(source.array());
          point("write");
          int start = source.position();
          int remaining = source.remaining();
          if (writeBehavior.equals("zero")) return 0;
          if (writeBehavior.equals("negative")) return -1;
          if (writeBehavior.equals("overflow")) return remaining + 1;
          int end = source.limit();
          source.limit(start + Math.min(remaining, writeLimit));
          int count = writer.write(source);
          source.limit(end);
          if (writeBehavior.equals("position")) source.position(start);
          return count;
        }

        @Override
        public long size() throws IOException {
          point("writeSize");
          return writer.size() + (count("writeSize") == badSizeAt ? 1 : 0);
        }

        @Override
        public void force() throws IOException {
          point("force");
          writer.force();
        }

        @Override
        public void close() throws IOException {
          writer.close();
          writers--;
          point("writerClose");
          if (rawClose) throw new IOException("synthetic private write close diagnostic");
        }
      };
    }

    @Override
    public SeekableByteChannel open(Path held) throws IOException {
      point("openRead");
      var channel = nativeIo.open(held);
      readers++;
      return new SeekableByteChannel() {
        @Override
        public int read(ByteBuffer bytes) throws IOException {
          compoundBuffers.add(bytes.array());
          point("read");
          if (rawRead) throw new IOException("synthetic private read diagnostic");
          return channel.read(bytes);
        }

        @Override
        public long size() throws IOException {
          point("readSize");
          return channel.size();
        }

        @Override
        public void close() throws IOException {
          channel.close();
          readers--;
          point("readClose");
          if (rawClose) throw new IOException("synthetic private read close diagnostic");
        }

        @Override
        public boolean isOpen() {
          return channel.isOpen();
        }

        @Override
        public int write(ByteBuffer bytes) {
          throw new AssertionError("readonly");
        }

        @Override
        public long position() {
          throw new AssertionError("no seek");
        }

        @Override
        public SeekableByteChannel position(long p) {
          throw new AssertionError("no seek");
        }

        @Override
        public SeekableByteChannel truncate(long p) {
          throw new AssertionError("no truncate");
        }
      };
    }

    void released() {
      assertEquals(0, writers);
      assertEquals(0, readers);
      assertTrue(entries.isEmpty());
    }

    @Override
    public void close() throws StorageIoException {
      root.close();
      released();
    }
  }
}
