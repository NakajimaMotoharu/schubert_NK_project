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

import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Proxy;
import java.nio.ByteBuffer;
import java.nio.channels.SeekableByteChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.nio.file.attribute.FileTime;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.BrokenBarrierException;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.function.BiConsumer;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;
import org.junit.jupiter.api.io.TempDir;

/**
 * SSC055/SS343 6.14; PT-BAT-046..057. Literal oracle and synthetic admission, real inode/native IO.
 */
final class DurableRecordFilesTest {
  private static final String RUN_ID = "12345678-9abc-def0-8123-456789abcdef";
  private static final String ACT_ID = "fedcba98-7654-3210-8fed-cba987654321";
  private static final UUID PART = UUID.fromString("11111111-2222-3333-4444-555555555555");
  private static final String NAME = RUN_ID + ".run";
  private static final String GOLDEN = "NKRUN1\n" + RUN_ID + "\n2026-09-12T04:05:06.123456Z\n";
  private static final String BEGIN =
      "NKACT1\n" + RUN_ID + "\n2026-09-12T04:05:06.123456Z\n" + ACT_ID + "\n";
  private static final String DONE =
      "NKDONE1\n"
          + RUN_ID
          + "\n2026-09-12T04:05:06.123456Z\n"
          + ACT_ID
          + "\n2026-09-12T05:06:07.234567Z\n";
  @TempDir Path temporary;

  private static byte[] bytes(String text) {
    return text.getBytes(StandardCharsets.US_ASCII);
  }

  private static Map<String, String> records() {
    return Map.of(
        NAME, GOLDEN, ACT_ID + ".begin", BEGIN, "active", BEGIN, ACT_ID + ".done", DONE + "10\n");
  }

  @Test
  void literalReads() throws Exception {
    try (var f = fixture()) {
      assertTrue(f.records.read(NAME).isEmpty());
      for (var record : records().entrySet()) {
        Files.writeString(f.directory.resolve(record.getKey()), record.getValue());
        byte[] result = f.records.read(record.getKey()).orElseThrow();
        assertArrayEquals(bytes(record.getValue()), result);
        Arrays.fill(result, (byte) 0);
        assertArrayEquals(bytes(record.getValue()), f.records.read(record.getKey()).orElseThrow());
        assertEquals(record.getValue(), Files.readString(f.directory.resolve(record.getKey())));
      }
      Files.writeString(f.directory.resolve(ACT_ID + ".done"), DONE + "0\n");
      assertArrayEquals(bytes(DONE + "0\n"), f.records.read(ACT_ID + ".done").orElseThrow());
      assertEquals(0, f.count("write"));
      assertEquals(0, f.count("unlink"));
      f.released();
    }
  }

  @Test
  void newPublication() throws Exception {
    for (var record : records().entrySet())
      try (var f = fixture()) {
        f.writeLimit = 7;
        f.readLimit = 9;
        byte[] input = bytes(record.getValue());
        f.records.publish(record.getKey(), input, PART);
        String label =
            record.getKey().equals(NAME)
                ? "anchor"
                : record.getKey().equals("active")
                    ? "active"
                    : record.getKey().endsWith(".begin") ? "begin" : "done-10";
        Path traces = Path.of("target/durable-record-traces");
        Files.createDirectories(traces);
        Files.copy(
            f.directory.resolve(record.getKey()),
            traces.resolve("PT-BAT-047-" + label + ".txt"),
            StandardCopyOption.REPLACE_EXISTING);
        assertArrayEquals(bytes(record.getValue()), input);
        assertEquals(record.getValue(), Files.readString(f.directory.resolve(record.getKey())));
        assertEquals(
            0100600, Files.getAttribute(f.directory.resolve(record.getKey()), "unix:mode"));
        assertFalse(Files.exists(f.part));
        assertEquals(1, f.count("create"));
        assertEquals(1, f.count("publish"));
        assertEquals(1, f.count("sync"));
        assertEquals(1, f.count("force"));
        f.released();
      }
  }

  @Test
  void sameRecordReuse() throws Exception {
    try (var f = fixture()) {
      Files.writeString(f.directory.resolve(ACT_ID + ".done"), DONE + "0\n");
      failure(() -> f.records.publish(ACT_ID + ".done", bytes(DONE + "10\n"), PART));
      assertEquals(DONE + "0\n", Files.readString(f.directory.resolve(ACT_ID + ".done")));
      assertEquals(0, f.count("openWriter"));
      f.released();
    }
    try (var f = fixture()) {
      f.seed();
      Map<String, Object> before = f.nativeIo.attributes(f.target);
      f.records.publish(NAME, bytes(GOLDEN), PART);
      assertEquals(before, f.nativeIo.attributes(f.target));
      assertEquals(0, f.count("write"));
      assertEquals(0, f.count("create"));
      assertEquals(0, f.count("publish"));
      assertEquals(1, f.count("force"));
      assertEquals(1, f.count("sync"));
      failure(() -> f.records.publish(NAME, bytes(GOLDEN.replace("123456Z", "123457Z")), PART));
      assertEquals(GOLDEN, Files.readString(f.target));
      f.released();
    }
  }

  @Test
  void expectedRetirement() throws Exception {
    try (var f = fixture()) {
      f.seed();
      f.fail = "sync";
      failure(() -> f.records.remove(NAME, bytes(GOLDEN)));
      assertFalse(Files.exists(f.target));
      f.reset();
      f.fail = "sync";
      failure(() -> f.records.remove(NAME, bytes(GOLDEN)));
      assertFalse(Files.exists(f.target));
      assertEquals(1, f.count("sync"));
      assertEquals(0, f.count("unlink"));
      f.reset();
      f.records.remove(NAME, bytes(GOLDEN));
      assertEquals(1, f.count("sync"));
      f.released();
    }
    try (var f = fixture()) {
      f.seed();
      Files.writeString(f.directory.resolve("unrelated"), "preserve");
      failure(() -> f.records.remove(NAME, bytes(GOLDEN.replace("123456Z", "123457Z"))));
      assertTrue(Files.exists(f.target));
      f.reset();
      f.records.remove(NAME, bytes(GOLDEN));
      assertFalse(Files.exists(f.target));
      assertEquals(1, f.count("unlink"));
      assertEquals(1, f.count("sync"));
      f.reset();
      f.records.remove(NAME, bytes(GOLDEN));
      assertEquals(0, f.count("unlink"));
      assertEquals(1, f.count("sync"), "absence after a failed unlink sync must be sealed");
      assertEquals("preserve", Files.readString(f.directory.resolve("unrelated")));
      f.released();
    }
  }

  @Test
  void nameContentAndNull() throws Exception {
    try (var f = fixture()) {
      assertThrows(NullPointerException.class, () -> new DurableRecordFiles(null, f, f));
      assertThrows(NullPointerException.class, () -> new DurableRecordFiles(f.root, null, f));
      assertThrows(NullPointerException.class, () -> new DurableRecordFiles(f.root, f, null));
      assertThrows(NullPointerException.class, () -> f.records.read(null));
      assertThrows(NullPointerException.class, () -> f.records.publish(NAME, null, PART));
      assertThrows(NullPointerException.class, () -> f.records.publish(NAME, bytes(GOLDEN), null));
      assertThrows(NullPointerException.class, () -> f.records.remove(NAME, null));
      for (String name :
          List.of(
              "",
              ".",
              "..",
              "/active",
              "../active",
              "Active",
              NAME.toUpperCase(Locale.ROOT),
              RUN_ID + ".part",
              RUN_ID + ".run\n",
              "a.run")) {
        assertThrows(IllegalArgumentException.class, () -> f.records.read(name));
        assertThrows(
            IllegalArgumentException.class, () -> f.records.publish(name, bytes(GOLDEN), PART));
        assertThrows(IllegalArgumentException.class, () -> f.records.remove(name, bytes(GOLDEN)));
      }
      for (var r : records().entrySet()) {
        failure(() -> f.records.publish(r.getKey(), bytes("invalid"), PART));
        failure(() -> f.records.remove(r.getKey(), bytes("invalid")));
      }
      for (String suffix : List.of(".run", ".begin", ".done")) {
        String name = PART + suffix;
        String value =
            suffix.equals(".run") ? GOLDEN : suffix.equals(".begin") ? BEGIN : DONE + "0\n";
        failure(() -> f.records.publish(name, bytes(value), PART));
      }
      assertEquals(0, f.count("create"));
      assertEquals(0, f.count("openEntry"));
      f.released();
    }
  }

  @Test
  void metadataAndFilesystems() throws Exception {
    for (String fs : List.of("ext2", "ext3", "ext4", "xfs", "btrfs"))
      try (var f = fixture()) {
        f.filesystem = fs;
        f.seed();
        assertArrayEquals(bytes(GOLDEN), f.records.read(NAME).orElseThrow());
      }
    for (String role : List.of("dir", "file")) {
      for (String bad :
          List.of("nullAttributes", "nullFilesystem", "filesystem", "nullAcl", "acl", "readonly"))
        try (var f = fixture()) {
          f.seed();
          f.badRole = role;
          f.invalid = bad;
          failure(() -> f.records.read(NAME));
          f.released();
        }
      for (String key :
          List.of(
              "mode", "uid", "gid", "nlink", "size", "dev", "ino", "lastModifiedTime", "ctime")) {
        for (boolean missing : List.of(false, true))
          try (var f = fixture()) {
            f.seed();
            f.change =
                (r, m) -> {
                  if (r.equals(role)) {
                    if (missing) m.remove(key);
                    else m.put(key, "wrong type");
                  }
                };
            failure(() -> f.records.read(NAME));
            f.released();
          }
      }
      for (var entry :
          Map.<String, Object>of("mode", 0100644, "uid", 1, "gid", 1, "nlink", 0, "size", -1L)
              .entrySet())
        try (var f = fixture()) {
          f.seed();
          f.change =
              (r, m) -> {
                if (r.equals(role)) m.put(entry.getKey(), entry.getValue());
              };
          failure(() -> f.records.read(NAME));
          f.released();
        }
    }
    for (String fs : List.of("tmpfs", "nfs", "overlay", "unknown", ""))
      try (var f = fixture()) {
        f.seed();
        f.filesystem = fs;
        failure(() -> f.records.read(NAME));
      }
    for (var entry : Map.<String, Object>of("size", 142L, "nlink", 2, "dev", -1L).entrySet())
      try (var f = fixture()) {
        f.seed();
        f.change =
            (r, m) -> {
              if (r.equals("file")) m.put(entry.getKey(), entry.getValue());
            };
        failure(() -> f.records.read(NAME));
        f.released();
      }
  }

  @Test
  void boundedChannels() throws Exception {
    // BUG-158: metadata is an independent observation, not channel.size().
    for (int at : List.of(2, 3))
      try (var f = fixture()) {
        f.on(
            "attributes",
            at,
            () ->
                f.change =
                    (role, values) -> {
                      if (role.equals("file")) values.put("size", at == 2 ? 1L : 73L);
                    });
        failure(() -> f.records.publish(NAME, bytes(GOLDEN), PART));
        assertTrue(Files.exists(f.part));
        assertFalse(Files.exists(f.target));
        f.released();
      }
    try (var f = fixture()) {
      f.seed();
      f.on("read", 1, () -> Files.write(f.target, new byte[142]));
      failure(() -> f.records.read(NAME));
      assertEquals(142, Files.size(f.target));
      f.released();
    }
    for (String bad : List.of("zero", "negative", "overflow", "early", "position"))
      try (var f = fixture()) {
        f.seed();
        f.readBehavior = bad;
        failure(() -> f.records.read(NAME));
        f.released();
      }
    for (int at : List.of(1, 2))
      try (var f = fixture()) {
        f.seed();
        f.badReadSizeAt = at;
        failure(() -> f.records.read(NAME));
        f.released();
      }
    try (var f = fixture()) {
      f.seed();
      f.nullReader = true;
      failure(() -> f.records.read(NAME));
      f.released();
    }
    for (String bad : List.of("zero", "negative", "overflow", "position"))
      try (var f = fixture()) {
        f.writeBehavior = bad;
        failure(() -> f.records.publish(NAME, bytes(GOLDEN), PART));
        assertTrue(Files.exists(f.part));
        f.released();
      }
    for (boolean existing : List.of(false, true)) {
      try (var f = fixture()) {
        if (existing) f.seed();
        f.nullWriter = true;
        failure(() -> f.records.publish(NAME, bytes(GOLDEN), PART));
        f.released();
      }
      for (int at : List.of(1, 2))
        try (var f = fixture()) {
          if (existing) f.seed();
          f.badSizeAt = at;
          failure(() -> f.records.publish(NAME, bytes(GOLDEN), PART));
          f.released();
        }
    }
    try (var f = fixture()) {
      f.seed();
      f.on("openRead", 1, () -> Files.write(f.target, new byte[142]));
      failure(() -> f.records.read(NAME));
      f.released();
    }
    try (var f = fixture()) {
      f.seed();
      f.rawRead = true;
      f.rawClose = true;
      failure(() -> f.records.read(NAME));
      f.released();
    }
  }

  @Test
  void namespaceAndReplacement() throws Exception {
    for (boolean symbolic : List.of(false, true))
      try (var f = fixture()) {
        Path other = f.directory.resolve("preserve");
        Files.writeString(other, GOLDEN);
        if (symbolic) Files.createSymbolicLink(f.target, other);
        else Files.createLink(f.target, other);
        failure(() -> f.records.read(NAME));
        failure(() -> f.records.remove(NAME, bytes(GOLDEN)));
        assertEquals(GOLDEN, Files.readString(other));
        assertEquals(0, f.count("openRead"));
        assertEquals(0, f.count("unlink"));
        f.released();
      }
    for (String op : List.of("read", "reuse", "remove"))
      try (var f = fixture()) {
        f.seed();
        f.on(
            "readClose",
            1,
            () -> {
              Files.move(f.target, f.directory.resolve("retained"));
              Files.writeString(f.target, GOLDEN);
            });
        failure(() -> operate(f, op));
        assertEquals(GOLDEN, Files.readString(f.target));
        f.released();
      }
    try (var f = fixture()) {
      Files.writeString(f.part, "preserve");
      failure(() -> operate(f, "new"));
      assertEquals("preserve", Files.readString(f.part));
      assertFalse(Files.exists(f.target));
    }
    try (var f = fixture()) {
      f.on("publish", 1, () -> Files.writeString(f.target, "other"));
      failure(() -> operate(f, "new"));
      assertEquals("other", Files.readString(f.target));
      assertEquals(GOLDEN, Files.readString(f.part));
    }
    for (String attribute :
        List.of("ino", "dev", "ctime", "lastModifiedTime", "mode", "uid", "gid", "nlink", "size"))
      try (var f = fixture()) {
        f.seed();
        f.on(
            "readClose",
            1,
            () ->
                f.change =
                    (r, m) -> {
                      if (r.equals("file")) {
                        Object v = m.get(attribute);
                        m.put(
                            attribute,
                            v instanceof FileTime
                                ? FileTime.fromMillis(1)
                                : v instanceof Long number ? number + 1 : ((Integer) v) + 1);
                      }
                    });
        failure(() -> f.records.read(NAME));
        f.released();
      }
    try (var f = fixture()) {
      f.on(
          "readClose",
          2,
          () ->
              f.change =
                  (r, m) -> {
                    if (r.equals("file")) m.put("ctime", FileTime.fromMillis(1));
                  });
      failure(() -> operate(f, "new"));
      assertTrue(Files.exists(f.target));
      f.released();
    }
    try (var f = fixture()) {
      f.seed();
      f.on(
          "readClose",
          1,
          () ->
              f.change =
                  (r, m) -> {
                    if (r.equals("dir")) m.put("ino", -1L);
                  });
      failure(() -> f.records.read(NAME));
      f.released();
    }
  }

  @Test
  void allReadFailures() throws Exception {
    faults("read", inventory(7, 3, 3, 1, 2, 2, 0, 0, 0, 0, 0, 0, 0));
    for (String point :
        List.of("attributes", "acl", "filesystem", "readonly", "entryClose", "readClose"))
      try (var f = fixture()) {
        f.seed();
        f.fail = point;
        f.failAt = point.equals("entryClose") || point.equals("readClose") ? 1 : 2;
        f.reason = StorageIoException.Reason.MISSING;
        failure(() -> f.records.read(NAME));
        f.released();
      }
    try (var f = fixture()) {
      f.seed();
      f.fail = "openEntry";
      f.failAt = 2;
      f.reason = StorageIoException.Reason.MISSING;
      failure(() -> f.records.read(NAME));
      f.released();
    }
  }

  @Test
  void allWriteRetireFailures() throws Exception {
    faults("new", inventory(13, 8, 8, 2, 4, 4, 1, 1, 1, 1, 2, 1, 0));
    faults("reuse", inventory(13, 8, 8, 2, 4, 4, 0, 0, 1, 1, 2, 0, 0));
    faults("remove", inventory(7, 4, 4, 1, 2, 2, 0, 0, 0, 1, 0, 0, 1));
  }

  @Test
  void interruptionsAndUnknownRuntime() throws Exception {
    for (String op : List.of("read", "new", "reuse"))
      for (boolean known : List.of(false, true))
        for (Throwable unknown :
            List.of(
                new IllegalStateException("public compound"),
                new NullPointerException("public compound"),
                new AssertionError("public compound")))
          try (var f = fixture()) {
            if (!op.equals("new")) f.seed();
            String body = op.equals("read") ? "read" : op.equals("new") ? "write" : "force";
            String close = op.equals("read") ? "readClose" : "writerClose";
            int bodyAt = op.equals("read") ? 2 : 1;
            if (known) {
              f.fail = body;
              f.failAt = bodyAt;
            }
            f.compound =
                (name, count) -> {
                  if ((count == 1 && name.equals(close))
                      || (!known && count == bodyAt && name.equals(body))) {
                    if (unknown instanceof RuntimeException failure) throw failure;
                    throw (Error) unknown;
                  }
                };
            assertSame(unknown, assertThrows(unknown.getClass(), () -> operate(f, op)));
            assertEquals(bodyAt, f.count(body));
            assertEquals(1, f.count(close));
            assertEquals(known ? 0 : 1, unknown.getSuppressed().length);
            for (Throwable secondary : unknown.getSuppressed())
              failure(
                  () -> {
                    throw secondary;
                  });
            f.released();
            assertFalse(f.compoundBuffers.isEmpty());
            for (byte[] bytes : f.compoundBuffers) assertArrayEquals(new byte[bytes.length], bytes);
            if (op.equals("new")) {
              assertFalse(Files.exists(f.target));
              assertTrue(Files.exists(f.part));
              assertEquals(0, Files.size(f.part));
            } else assertEquals(GOLDEN, Files.readString(f.target));
          }
    for (String op : List.of("read", "new", "reuse", "remove")) {
      try (var f = fixture()) {
        if (!op.equals("new")) f.seed();
        Thread.currentThread().interrupt();
        try {
          failure(() -> operate(f, op));
          assertTrue(Thread.currentThread().isInterrupted());
          assertTrue(f.counts.isEmpty());
        } finally {
          Thread.interrupted();
        }
      }
      try (var f = fixture()) {
        if (!op.equals("new")) f.seed();
        f.uid = 1000;
        failure(() -> operate(f, op));
        assertTrue(f.counts.isEmpty());
      }
      try (var f = fixture()) {
        if (!op.equals("new")) f.seed();
        f.on("readClose", 1, () -> Thread.currentThread().interrupt());
        try {
          failure(() -> operate(f, op));
          assertTrue(Thread.currentThread().isInterrupted());
          f.released();
        } finally {
          Thread.interrupted();
        }
      }
      for (RuntimeException error :
          List.of(new IllegalStateException("synthetic"), new NullPointerException("synthetic")))
        try (var f = fixture()) {
          if (!op.equals("new")) f.seed();
          f.fail = "attributes";
          f.failAt = 2;
          f.runtime = error;
          assertSame(error, assertThrows(error.getClass(), () -> operate(f, op)));
          f.released();
        }
    }
  }

  @Test
  void concurrencyAndNative() throws Exception {
    try (var first = fixture();
        var second = new Fixture(first.directory);
        var pool = Executors.newFixedThreadPool(2)) {
      var barrier = new CyclicBarrier(2);
      Action rendezvous =
          () -> {
            try {
              barrier.await(5, TimeUnit.SECONDS);
            } catch (InterruptedException | BrokenBarrierException | TimeoutException e) {
              throw new IOException("fixture rendezvous failed");
            }
          };
      first.on("publish", 1, rendezvous);
      second.on("publish", 1, rendezvous);
      UUID otherPart = UUID.fromString("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee");
      List<Future<Boolean>> results = new ArrayList<>();
      for (var pair : List.of(Map.entry(first, PART), Map.entry(second, otherPart))) {
        results.add(
            pool.submit(
                () -> {
                  try {
                    pair.getKey().records.publish(NAME, bytes(GOLDEN), pair.getValue());
                    return true;
                  } catch (StorageIoException e) {
                    assertEquals(StorageIoException.Reason.UNAVAILABLE, e.reason());
                    assertNull(e.getCause());
                    assertEquals(0, e.getSuppressed().length);
                    return false;
                  }
                }));
      }
      int successes = 0;
      for (var result : results) if (result.get(10, TimeUnit.SECONDS)) successes++;
      assertEquals(1, successes);
      assertEquals(GOLDEN, Files.readString(first.target));
      assertNotEquals(
          Files.exists(first.part), Files.exists(first.directory.resolve(otherPart + ".part")));
      Path retained =
          Files.exists(first.part) ? first.part : first.directory.resolve(otherPart + ".part");
      assertEquals(GOLDEN, Files.readString(retained));
      first.released();
      second.released();
    }
    try (var f = fixture();
        var pool = Executors.newFixedThreadPool(8)) {
      List<Future<?>> futures = new ArrayList<>();
      for (int i = 0; i < 32; i++)
        futures.add(
            pool.submit(
                () -> {
                  f.records.publish(NAME, bytes(GOLDEN), PART);
                  return null;
                }));
      for (var future : futures) future.get(10, TimeUnit.SECONDS);
      assertEquals(GOLDEN, Files.readString(f.target));
      assertEquals(1, f.count("create"));
      assertEquals(32, f.count("force"));
      f.released();
      var nativeRecords = new DurableRecordFiles(f.root, f);
      // Real UID/mode/filesystem admission is not replaced by the successful synthetic fixture.
      failure(() -> nativeRecords.read(NAME));
    }
  }

  private static Map<String, Integer> inventory(
      int attributes,
      int open,
      int close,
      int readers,
      int reads,
      int readSizes,
      int creates,
      int publishes,
      int writers,
      int syncs,
      int writeSizes,
      int writes,
      int unlinks) {
    Map<String, Integer> result = new HashMap<>();
    for (String p : List.of("attributes", "acl", "filesystem", "readonly"))
      result.put(p, attributes);
    result.put("openEntry", open);
    result.put("entryClose", close);
    result.put("openRead", readers);
    result.put("readClose", readers);
    result.put("read", reads);
    result.put("readSize", readSizes);
    if (creates > 0) result.put("create", creates);
    if (publishes > 0) result.put("publish", publishes);
    if (writers > 0) {
      result.put("openWriter", writers);
      result.put("writerClose", writers);
      result.put("force", writers);
    }
    if (syncs > 0) result.put("sync", syncs);
    if (writeSizes > 0) result.put("writeSize", writeSizes);
    if (writes > 0) result.put("write", writes);
    if (unlinks > 0) result.put("unlink", unlinks);
    return result;
  }

  private void faults(String op, Map<String, Integer> expected) throws Exception {
    try (var f = fixture()) {
      if (!op.equals("new")) f.seed();
      operate(f, op);
      assertEquals(expected, f.counts, op);
      f.released();
    }
    for (var point : expected.entrySet())
      for (int at = 1; at <= point.getValue(); at++)
        try (var f = fixture()) {
          if (!op.equals("new")) f.seed();
          f.fail = point.getKey();
          f.failAt = at;
          failure(() -> operate(f, op));
          f.released();
          if (op.equals("new") && Files.exists(f.target))
            assertEquals(GOLDEN, Files.readString(f.target));
          if (op.equals("new") && Files.exists(f.part)) {
            String retained = Files.readString(f.part);
            assertTrue(retained.isEmpty() || retained.equals(GOLDEN));
          }
          if (op.equals("read") || op.equals("reuse"))
            assertEquals(GOLDEN, Files.readString(f.target));
          if (op.equals("new")) assertFalse(Files.exists(f.target) && Files.exists(f.part));
        }
  }

  private static void operate(Fixture f, String operation) throws Exception {
    switch (operation) {
      case "read" -> assertArrayEquals(bytes(GOLDEN), f.records.read(NAME).orElseThrow());
      case "new", "reuse" -> f.records.publish(NAME, bytes(GOLDEN), PART);
      case "remove" -> f.records.remove(NAME, bytes(GOLDEN));
      default -> throw new AssertionError(operation);
    }
  }

  private Fixture fixture() throws Exception {
    return new Fixture(Files.createTempDirectory(temporary, "durable-"));
  }

  private static void failure(Executable action) {
    var e = assertThrows(StorageIoException.class, action);
    assertEquals(StorageIoException.Reason.UNAVAILABLE, e.reason());
    assertEquals("transfer storage operation failed", e.getMessage());
    assertNull(e.getCause());
    assertEquals(0, e.getSuppressed().length);
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
    final DurableRecordFiles records;
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
    boolean nullReader;
    boolean rawRead;
    boolean rawClose;
    String filesystem = "ext4";
    String readBehavior = "normal";
    int readLimit = Integer.MAX_VALUE;
    int badReadSizeAt;
    RuntimeException runtime;
    StorageIoException.Reason reason = StorageIoException.Reason.UNAVAILABLE;
    BiConsumer<String, Map<String, Object>> change = (role, values) -> {};
    Action hook = () -> {};
    BiConsumer<String, Integer> compound = (name, count) -> {};
    final List<byte[]> compoundBuffers = Collections.synchronizedList(new ArrayList<>());

    Fixture(Path directory) throws Exception {
      this.directory = directory;
      target = directory.resolve(NAME);
      part = directory.resolve(PART + ".part");
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
      records = new DurableRecordFiles(root, this, this);
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
      if (fail.equals(name) && failAt == at) {
        if (runtime != null) throw runtime;
        throw new StorageIoException(reason);
      }
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
      return filesystem;
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
      if (nullReader) return null;
      var channel = nativeIo.open(held);
      readers++;
      return new SeekableByteChannel() {
        @Override
        public int read(ByteBuffer bytes) throws IOException {
          compoundBuffers.add(bytes.array());
          point("read");
          if (rawRead) throw new IOException("synthetic private read diagnostic");
          int start = bytes.position();
          int remaining = bytes.remaining();
          int end = bytes.limit();
          if (readBehavior.equals("zero")) return 0;
          if (readBehavior.equals("negative")) return -2;
          if (readBehavior.equals("overflow")) return remaining + 1;
          if (readBehavior.equals("early")) return -1;
          bytes.limit(start + Math.min(remaining, readLimit));
          int result = channel.read(bytes);
          bytes.limit(end);
          if (readBehavior.equals("position") && result > 0) bytes.position(start);
          return result;
        }

        @Override
        public long size() throws IOException {
          point("readSize");
          return channel.size() + (count("readSize") == badReadSizeAt ? 1 : 0);
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
