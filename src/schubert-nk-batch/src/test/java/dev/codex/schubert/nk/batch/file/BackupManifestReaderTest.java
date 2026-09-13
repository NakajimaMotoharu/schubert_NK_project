package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.*;
import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.batch.backup.*;
import dev.codex.schubert.nk.batch.repository.*;
import dev.codex.schubert.nk.storage.*;
import java.io.*;
import java.nio.ByteBuffer;
import java.nio.file.*;
import java.nio.file.attribute.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** NK-BAT-001/BAK/BKO/UI251/SS341 6.7/343; SSC062/PG169; BAT226..241; independent017046. */
final class BackupManifestReaderTest {
  @TempDir Path temporary;
  static final Map<String, Integer> INVENTORY =
      Map.ofEntries(
          Map.entry("attributes", 8),
          Map.entry("acl", 8),
          Map.entry("readonly", 8),
          Map.entry("openChannel", 1),
          Map.entry("size", 2),
          Map.entry("read", 2),
          Map.entry("closeChannel", 1),
          Map.entry("openDirectory", 2),
          Map.entry("closeDirectory", 2),
          Map.entry("openEntry", 2),
          Map.entry("closeEntry", 2),
          Map.entry("effectiveUid", 2),
          Map.entry("clock", 63));

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
    for (String role : List.of("parent", "child"))
      for (var bad :
          List.<Map.Entry<String, Object>>of(
              Map.entry("mode", 040750),
              Map.entry("mode", 0100700),
              Map.entry("uid", 0),
              Map.entry("gid", 0),
              Map.entry("nlink", 1),
              Map.entry("size", -1L))) {
        try (var f = fixture()) {
          f.selectedRole = role;
          f.metadata = (r, m) -> m.put(bad.getKey(), bad.getValue());
          denied(() -> read(f));
          f.released();
          f.unchanged();
        }
      }
    try (var f = fixture()) {
      f.selectedRole = "child";
      f.metadata = (r, m) -> m.put("dev", Long.MIN_VALUE);
      denied(() -> read(f));
      f.released();
    }
    for (String role : List.of("parent", "child")) {
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
              if (r.equals("parent") || r.equals("child")) {
                m.put("uid", (int) boundary);
                m.put("gid", (int) boundary);
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
            Map.entry("mode", 0100640),
            Map.entry("mode", 0120600),
            Map.entry("uid", (int) UID),
            Map.entry("gid", (int) GID),
            Map.entry("nlink", 2),
            Map.entry("size", 0L),
            Map.entry("size", 4097L),
            Map.entry("dev", Long.MIN_VALUE))) {
      try (var f = fixture()) {
        f.selectedRole = "MANIFEST.json";
        f.metadata = (r, m) -> m.put(bad.getKey(), bad.getValue());
        denied(() -> read(f));
        f.released();
        f.unchanged();
      }
    }
    for (String field :
        List.of("mode", "uid", "gid", "nlink", "size", "dev", "ino", "lastModifiedTime", "ctime"))
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
    for (String role : List.of("parent", "child", "MANIFEST.json"))
      for (byte[] acl : Arrays.asList(null, new byte[1], new byte[44])) {
        try (var f = fixture()) {
          f.selectedRole = role;
          f.acl = acl;
          denied(() -> read(f));
          f.released();
        }
      }
    try (var f = fixture()) {
      f.selectedRole = "MANIFEST.json";
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
            if (name.equals("closeDirectory") && n == 2)
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
                      Path p = f.child.resolve("MANIFEST.json");
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
        Path p = f.child.resolve("MANIFEST.json"), saved = f.child.resolve("saved");
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
            if (name.equals("read") && n == 2)
              io(
                  () -> {
                    Files.write(f.child.resolve("MANIFEST.json"), golden());
                    Files.setLastModifiedTime(
                        f.child.resolve("MANIFEST.json"), FileTime.fromMillis(1));
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
        Files.write(f.child.resolve("MANIFEST.json"), new byte[size]);
        denied(() -> read(f));
        f.released();
      }
    for (String mode : List.of("zero", "short", "count", "position", "extra", "eof-position"))
      try (var f = fixture()) {
        f.selectedRole = "MANIFEST.json";
        f.readMode = mode;
        denied(() -> read(f));
        f.released();
      }
    for (String mode : List.of("first", "last"))
      try (var f = fixture()) {
        f.selectedRole = "MANIFEST.json";
        f.sizeMode = mode;
        denied(() -> read(f));
        f.released();
      }
    for (int chunk : new int[] {1, 7, 963, 964})
      try (var f = fixture()) {
        f.smallRead = chunk;
        assertEquals(f.expected, read(f));
        assertEquals((964 + chunk - 1) / chunk + 1, f.counts.get("read"));
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
        Files.write(f.child.resolve("MANIFEST.json"), invalid);
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
      Files.writeString(f.child.resolve("MANIFEST.json"), changed);
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
          assertSame(primary, assertThrows(primary.getClass(), () -> read(f)));
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
      assertSame(fatal, assertThrows(AssertionError.class, () -> read(f)));
      f.released();
    }
    for (String close : List.of("closeChannel", "closeEntry", "closeDirectory"))
      for (int kind = 0; kind < 4; kind++)
        try (var f = fixture()) {
          Throwable primary =
              switch (kind) {
                case 0 -> new IOException("public primary");
                case 1 -> new IllegalStateException("public primary");
                case 2 -> new NullPointerException("public primary");
                default -> new AssertionError("public primary");
              };
          f.extraFaults.add("read#1");
          f.faultTypes.put("read#1", primary);
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
          assertEquals(1, f.counts.get("read"));
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
        f.extraFaults.add("closeChannel#1");
        f.faultTypes.put("closeChannel#1", cleanup);
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
              if (name.equals("clock") && n == 2) f.clockValue = 100 + elapsed;
            };
        denied(() -> read(f));
        f.released();
      }
    try (var f = fixture()) {
      f.hook =
          (name, n) -> {
            if (name.equals("clock") && n == 2) f.clockValue = 100 + 1799999999999L;
          };
      assertEquals(f.expected, read(f));
      f.released();
    }
    try (var f = fixture()) {
      f.clockValue = Long.MAX_VALUE - 50;
      f.hook =
          (name, n) -> {
            if (name.equals("clock") && n == 2) f.clockValue = Long.MIN_VALUE + 49;
          };
      assertEquals(f.expected, read(f));
      f.released();
    }
    for (int point = 1; point <= 63; point++) {
      int selected = point;
      try (var f = fixture()) {
        f.hook =
            (name, n) -> {
              if (name.equals("clock") && n == selected) Thread.currentThread().interrupt();
            };
        try {
          denied(() -> read(f));
          assertTrue(Thread.currentThread().isInterrupted());
        } finally {
          Thread.interrupted();
        }
        assertEquals(selected, f.counts.get("clock"));
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
    for (String point : List.of("attributes", "openChannel", "read"))
      for (Throwable problem :
          List.of(
              new IllegalArgumentException("public unknown"),
              new IllegalStateException("public unknown"),
              new NullPointerException("public unknown"),
              new AssertionError("public unknown"))) {
        try (var f = fixture()) {
          f.extraFaults.add(point + "#1");
          f.faultTypes.put(point + "#1", problem);
          assertSame(problem, assertThrows(problem.getClass(), () -> read(f)));
          f.released();
          f.unchanged();
        }
      }
    try (var f = fixture()) {
      f.extraFaults.add("attributes#1");
      f.faultTypes.put("attributes#1", new UnsupportedOperationException("public unavailable"));
      denied(() -> read(f));
      f.released();
    }
    try (var f = fixture()) {
      f.extraFaults.add("attributes#1");
      f.faultTypes.put(
          "attributes#1", new DirectoryIteratorException(new IOException("public unavailable")));
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
      var attributes = nio.attributes(f.child.resolve("MANIFEST.json"));
      assertEquals(964L, attributes.get("size"));
      assertEquals(0100600, attributes.get("mode"));
      try (var channel = nio.open(f.child.resolve("MANIFEST.json"))) {
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
