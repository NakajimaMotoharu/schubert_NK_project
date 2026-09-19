package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.BackupPublicationFixture.*;
import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.storage.*;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.file.*;
import java.security.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** NK-BAT-001/BAK/BKO/OPS009/UI251/SS341 6.10/333 7.5; SSC066/PG177; BAT258..273. */
final class BackupBundlePublisherTest {
  @TempDir Path temporary;
  // 119 pending read operations +20 force +1 child sync +4 publish +38 reader +119 final verify.
  private static final Map<String, Integer> INVENTORY =
      Map.ofEntries(
          Map.entry("attributes", 42),
          Map.entry("acl", 42),
          Map.entry("readonly", 42),
          Map.entry("openNames", 4),
          Map.entry("iterator", 4),
          Map.entry("hasNext", 20),
          Map.entry("next", 16),
          Map.entry("closeNames", 4),
          Map.entry("openReader", 9),
          Map.entry("read", 18),
          Map.entry("size", 18),
          Map.entry("closeReader", 9),
          Map.entry("openDirectory", 7),
          Map.entry("openEntry", 18),
          Map.entry("close", 25),
          Map.entry("openWriter", 4),
          Map.entry("writerSize", 8),
          Map.entry("force", 4),
          Map.entry("closeWriter", 4),
          Map.entry("sync", 2),
          Map.entry("publish", 1));
  private static final int CLOCKS = 514;

  @Test
  void verifiedDurablePublication() throws Exception {
    try (var f = fixture()) {
      Object inode = Files.getAttribute(f.child, "unix:ino");
      var digest = f.bundlePublisher().publish(BackupArtifactFixture.expected());
      assertEquals(964, digest.size());
      assertEquals(BackupArtifactFixture.MANIFEST_HASH, digest.sha256());
      assertEquals(inode, Files.getAttribute(finalDirectory(f), "unix:ino"));
      assertFalse(Files.exists(f.child));
      goldenFinal(f);
      f.released();
      var actual = new HashMap<>(f.counts);
      actual.remove("clock");
      actual.remove("effectiveUid");
      assertEquals(INVENTORY, actual);
      assertEquals(301, f.position);
      assertEquals(CLOCKS, f.counts.get("clock"));
      assertEquals(6, f.counts.get("effectiveUid"));
    }
  }

  @Test
  void forceOrderAndRetainedInodes() throws Exception {
    try (var f = fixture()) {
      f.bundlePublisher().publish(BackupArtifactFixture.expected());
      int publish = f.events.indexOf("publish");
      assertEquals(4, Collections.frequency(f.events.subList(0, publish), "force"));
      assertEquals(4, Collections.frequency(f.events.subList(0, publish), "closeWriter"));
      assertEquals(1, Collections.frequency(f.events.subList(0, publish), "sync"));
      assertEquals("sync", f.events.get(publish + 1));
      assertEquals(0, f.counts.getOrDefault("write", 0));
      assertEquals(0, Collections.frequency(f.events.subList(publish, f.events.size()), "force"));
      assertEquals(
          5, Collections.frequency(f.events.subList(publish, f.events.size()), "openReader"));
      goldenFinal(f);
      f.released();
    }
  }

  @Test
  void pendingContentAndMetadata() throws Exception {
    for (String name : BackupArtifactFixture.NAMES) {
      try (var f = fixture()) {
        byte[] bytes = Files.readAllBytes(f.child.resolve(name));
        bytes[0] ^= 1;
        Files.write(f.child.resolve(name), bytes);
        fails(f);
        assertFalse(Files.exists(finalDirectory(f)));
        assertArrayEquals(bytes, Files.readAllBytes(f.child.resolve(name)));
      }
      try (var f = fixture()) {
        Files.delete(f.child.resolve(name));
        fails(f);
        assertFalse(Files.exists(finalDirectory(f)));
      }
    }
    try (var f = fixture()) {
      Files.write(f.child.resolve("unknown"), new byte[] {1});
      fails(f);
    }
    for (var bad :
        Map.<String, Object>of("mode", 0100644, "uid", 33, "gid", 33, "nlink", 2, "dev", -1L)
            .entrySet()) {
      try (var f = fixture()) {
        f.metadata =
            (role, values) -> {
              if (role.equals("file")) values.put(bad.getKey(), bad.getValue());
            };
        fails(f);
        assertFalse(Files.exists(finalDirectory(f)));
      }
    }
    try (var f = fixture()) {
      f.acl = new byte[] {1};
      fails(f);
    }
    try (var f = fixture()) {
      f.readonly = true;
      fails(f);
    }
  }

  @Test
  void finalManifestAndArtifactChecks() throws Exception {
    for (String name : BackupArtifactFixture.NAMES) {
      try (var f = fixture()) {
        f.hook =
            (event, n) -> {
              if (event.equals("sync") && n == 2)
                action(
                    () -> {
                      Path file = finalDirectory(f).resolve(name);
                      if (name.equals("MANIFEST.json"))
                        Files.writeString(file, Files.readString(file).replace("nk-pt", "NK-PT"));
                      else {
                        byte[] bytes = Files.readAllBytes(file);
                        bytes[0] ^= 1;
                        Files.write(file, bytes);
                      }
                    });
            };
        fails(f);
        assertTrue(Files.isDirectory(finalDirectory(f)));
        assertFalse(Files.exists(f.child));
      }
    }
    try (var f = fixture()) {
      AtomicInteger sequence = new AtomicInteger();
      BackupArtifactVerifier.Digests digests =
          () ->
              sequence.incrementAndGet() == 5
                  ? new MessageDigest("public test hash") {
                    @Override
                    protected void engineUpdate(byte input) {}

                    @Override
                    protected void engineUpdate(byte[] input, int off, int len) {}

                    @Override
                    protected byte[] engineDigest() {
                      return new byte[32];
                    }

                    @Override
                    protected void engineReset() {}
                  }
                  : MessageDigest.getInstance("SHA-256");
      var publisher = new BackupBundlePublisher(f.root, f, UID, GID, f, f::clock, digests);
      assertThrows(
          StorageIoException.class, () -> publisher.publish(BackupArtifactFixture.expected()));
      assertEquals(8, sequence.get());
      goldenFinal(f);
      f.released();
    }
  }

  @Test
  void forceSizeAndNullBoundaries() throws Exception {
    for (int at = 1; at <= 8; at++) {
      try (var f = fixture()) {
        f.changedSize = "writerSize#" + at;
        fails(f);
      }
    }
    try (var f = fixture()) {
      f.nullWriter = true;
      fails(f);
    }
    try (var f = fixture()) {
      f.faults.put("openDirectory#1", new UnsupportedOperationException("public unsupported"));
      fails(f);
    }
  }

  @Test
  void everyIoFailure() throws Exception {
    for (var entry : INVENTORY.entrySet())
      for (int at = 1; at <= entry.getValue(); at++) {
        try (var f = fixture()) {
          f.faults.put(entry.getKey() + "#" + at, new IOException("public IO fault"));
          fails(f);
          assertTrue(Files.isDirectory(f.child) ^ Files.isDirectory(finalDirectory(f)));
        }
      }
  }

  @Test
  void unknownAndCompoundFailures() throws Exception {
    for (String[] pair :
        List.of(
            new String[] {"writerSize#1", "closeWriter#1"},
            new String[] {"read#1", "closeReader#1"},
            new String[] {"publish#1", "close#11"})) {
      for (int kind = 0; kind < 3; kind++) {
        try (var f = fixture()) {
          Throwable primary =
              kind == 0
                  ? new IOException("public known")
                  : kind == 1
                      ? new IllegalStateException("public unknown")
                      : new AssertionError("public fatal");
          Throwable cleanup = kind == 0 ? new AssertionError("public cleanup") : primary;
          f.faults.put(pair[0], primary);
          f.faults.put(pair[1], cleanup);
          Throwable expected = kind == 0 ? cleanup : primary;
          assertSame(
              expected,
              assertThrows(
                  expected.getClass(),
                  () -> f.bundlePublisher().publish(BackupArtifactFixture.expected())));
          assertEquals(kind == 0 ? 0 : 1, expected.getSuppressed().length);
          f.released();
        }
      }
    }
    for (var entry : INVENTORY.entrySet())
      for (int at = 1; at <= entry.getValue(); at++) {
        try (var f = fixture()) {
          RuntimeException unknown = new IllegalStateException("public provider");
          f.faults.put(entry.getKey() + "#" + at, unknown);
          assertSame(
              unknown,
              assertThrows(
                  IllegalStateException.class,
                  () -> f.bundlePublisher().publish(BackupArtifactFixture.expected())));
          f.released();
        }
      }
  }

  @Test
  void deadlineAcrossPhases() throws Exception {
    for (int at = 2; at <= CLOCKS; at++) {
      int selected = at;
      try (var f = fixture()) {
        f.hook =
            (name, n) -> {
              if (name.equals("clock") && n == selected) f.time += 1_800_000_000_000L;
            };
        fails(f);
      }
    }
    for (long initial : new long[] {100, Long.MAX_VALUE - 2}) {
      try (var f = fixture()) {
        f.time = initial;
        f.hook =
            (name, n) -> {
              if (name.equals("clock") && n == 2) f.time += 1_799_999_999_999L;
            };
        f.bundlePublisher().publish(BackupArtifactFixture.expected());
        goldenFinal(f);
        f.released();
      }
    }
    try (var f = fixture()) {
      f.hook =
          (name, n) -> {
            if (name.equals("clock") && n == 2) f.time--;
          };
      fails(f);
    }
  }

  @Test
  void interruptionAcrossPhases() throws Exception {
    for (int at = 1; at <= CLOCKS; at++) {
      int selected = at;
      try (var f = fixture()) {
        f.hook =
            (name, n) -> {
              if (name.equals("clock") && n == selected) Thread.currentThread().interrupt();
            };
        try {
          fails(f);
          assertTrue(Thread.currentThread().isInterrupted());
        } finally {
          Thread.interrupted();
        }
      }
    }
  }

  @Test
  void existingFinalAndMissingPending() throws Exception {
    try (var f = fixture()) {
      Files.createDirectory(finalDirectory(f));
      Files.writeString(finalDirectory(f).resolve("sentinel"), "existing");
      var failure =
          assertThrows(
              StorageIoException.class,
              () -> f.bundlePublisher().publish(BackupArtifactFixture.expected()));
      assertEquals(StorageIoException.Reason.COLLISION, failure.reason());
      assertEquals("existing", Files.readString(finalDirectory(f).resolve("sentinel")));
      assertArrayEquals(
          BackupArtifactFixture.golden(), Files.readAllBytes(f.child.resolve("MANIFEST.json")));
      f.released();
    }
    try (var f = fixture()) {
      Files.move(f.child, f.parent.resolve("preserved"));
      var failure =
          assertThrows(
              StorageIoException.class,
              () -> f.bundlePublisher().publish(BackupArtifactFixture.expected()));
      assertEquals(StorageIoException.Reason.MISSING, failure.reason());
      f.released();
    }
  }

  @Test
  void namespaceReplacement() throws Exception {
    for (String field : List.of("dev", "nlink", "size", "lastModifiedTime", "file-inode")) {
      try (var f = fixture()) {
        f.metadata =
            (role, values) -> {
              if (f.counts.get("attributes") < 26) return;
              if (field.equals("dev")) values.put("dev", (Long) values.get("dev") + 1);
              else if (field.equals("file-inode")) {
                if (role.equals("file")) values.put("ino", (Long) values.get("ino") + 1);
              } else if (role.equals("child")) {
                if (field.equals("nlink")) values.put("nlink", (Integer) values.get("nlink") + 1);
                if (field.equals("size")) values.put("size", (Long) values.get("size") + 1);
                if (field.equals("lastModifiedTime"))
                  values.put("lastModifiedTime", java.nio.file.attribute.FileTime.fromMillis(0));
              }
            };
        fails(f);
        goldenFinal(f);
      }
    }
    try (var f = fixture()) {
      f.hook =
          (name, n) -> {
            if (name.equals("publish"))
              action(
                  () -> {
                    Path saved = f.parent.resolve("preserved-bundle");
                    Files.move(f.child, saved);
                    Files.createDirectory(
                        f.child,
                        java.nio.file.attribute.PosixFilePermissions.asFileAttribute(
                            java.nio.file.attribute.PosixFilePermissions.fromString("rwx------")));
                    for (String file : BackupArtifactFixture.NAMES) {
                      Files.copy(saved.resolve(file), f.child.resolve(file));
                      Files.setPosixFilePermissions(
                          f.child.resolve(file),
                          java.nio.file.attribute.PosixFilePermissions.fromString("rw-------"));
                    }
                  });
          };
      fails(f);
      goldenFinal(f);
      assertArrayEquals(
          BackupArtifactFixture.golden(),
          Files.readAllBytes(f.parent.resolve("preserved-bundle/MANIFEST.json")));
    }
    try (var f = fixture()) {
      f.hook =
          (name, n) -> {
            if (name.equals("force") && n == 1)
              action(
                  () -> {
                    Files.move(
                        f.child.resolve("MANIFEST.json"), f.parent.resolve("preserved-manifest"));
                    Files.write(f.child.resolve("MANIFEST.json"), BackupArtifactFixture.golden());
                    Files.setPosixFilePermissions(
                        f.child.resolve("MANIFEST.json"),
                        java.nio.file.attribute.PosixFilePermissions.fromString("rw-------"));
                  });
          };
      fails(f);
      assertFalse(Files.exists(finalDirectory(f)));
      assertArrayEquals(
          BackupArtifactFixture.golden(),
          Files.readAllBytes(f.parent.resolve("preserved-manifest")));
    }
  }

  @Test
  void nullAndOwnerContracts() throws Exception {
    try (var f = fixture()) {
      assertThrows(NullPointerException.class, () -> f.bundlePublisher().publish(null));
      assertThrows(NullPointerException.class, () -> new BackupBundlePublisher(null, f, UID, GID));
      assertThrows(
          NullPointerException.class, () -> new BackupBundlePublisher(f.root, null, UID, GID));
      assertThrows(
          NullPointerException.class,
          () -> new BackupBundlePublisher(f.root, f, UID, GID, null, f::clock));
      assertThrows(
          NullPointerException.class,
          () -> new BackupBundlePublisher(f.root, f, UID, GID, f, null));
      assertThrows(
          NullPointerException.class,
          () -> new BackupBundlePublisher(f.root, f, UID, GID, f, f::clock, null));
      for (long owner : new long[] {0, -1, 0x100000000L}) {
        assertThrows(
            IllegalArgumentException.class, () -> new BackupBundlePublisher(f.root, f, owner, GID));
        assertThrows(
            IllegalArgumentException.class, () -> new BackupBundlePublisher(f.root, f, UID, owner));
      }
      f.released();
    }
    for (long owner : new long[] {1, 0xffffffffL}) {
      try (var f = fixture()) {
        f.metadata =
            (role, values) -> {
              if (values.get("uid").equals((int) UID)) values.put("uid", (int) owner);
              if (values.get("gid").equals((int) GID)) values.put("gid", (int) owner);
            };
        new BackupBundlePublisher(f.root, f, owner, owner, f, f::clock)
            .publish(BackupArtifactFixture.expected());
        goldenFinal(f);
        f.released();
      }
    }
    var f = fixture();
    try {
      f.root.close();
      assertThrows(
          StorageIoException.class,
          () -> f.bundlePublisher().publish(BackupArtifactFixture.expected()));
    } finally {
      f.close();
    }
  }

  @Test
  void concurrentPublication() throws Exception {
    try (var f = fixture();
        var executor = Executors.newVirtualThreadPerTaskExecutor()) {
      var publisher = f.bundlePublisher();
      Callable<Boolean> action =
          () -> {
            try {
              publisher.publish(BackupArtifactFixture.expected());
              return true;
            } catch (StorageIoException failure) {
              assertEquals(StorageIoException.Reason.MISSING, failure.reason());
              return false;
            }
          };
      var a = executor.submit(action);
      var b = executor.submit(action);
      assertNotEquals(a.get(), b.get());
      goldenFinal(f);
      f.released();
    }
  }

  @Test
  void nativePortsAndFactory() throws Exception {
    try (var f = fixture()) {
      var io = new BackupBundlePublisher.NioIo();
      try (var child = f.root.openExistingChild(BackupArtifactFixture.DIR + ".part")) {
        child.atExistingEntryHandle(
            "MANIFEST.json",
            held -> {
              assertEquals(0100600, io.attributes(held).get("mode"));
              assertEquals(964L, io.attributes(held).get("size"));
              try (var channel = io.open(held)) {
                ByteBuffer buffer = ByteBuffer.allocate(964);
                while (buffer.hasRemaining()) assertTrue(channel.read(buffer) > 0);
                assertArrayEquals(BackupArtifactFixture.golden(), buffer.array());
              }
              try (var writer = io.openWriter(held)) {
                assertEquals(964, writer.size());
                writer.force();
                assertEquals(964, writer.size());
              }
              return Boolean.TRUE;
            });
        child.atDirectory(
            held -> {
              var names = new HashSet<String>();
              try (var stream = io.openNames(held)) {
                for (Path p : stream) names.add(p.getFileName().toString());
              }
              assertEquals(new HashSet<>(BackupArtifactFixture.NAMES), names);
              return Boolean.TRUE;
            });
      }
      f.effective = 1;
      assertThrows(
          StorageIoException.class,
          () ->
              new BackupBundlePublisher(f.root, f, UID, GID)
                  .publish(BackupArtifactFixture.expected()));
      f.released();
    }
  }

  @Test
  void readonlyCompatibility() throws Exception {
    try (var f = fixture()) {
      var verifier = new BackupArtifactVerifier(f.root, f, UID, GID, f, f::clock);
      var proof =
          verifier.forcePending(
              BackupArtifactFixture.expected(),
              (held, size) -> {
                try (var writer = f.nativeIo.openWriter(held)) {
                  assertEquals(size, writer.size());
                  writer.force();
                }
              },
              100);
      assertEquals(040700, proof.directory().mode());
      assertEquals(UID, proof.directory().uid());
      assertEquals(new HashSet<>(BackupArtifactFixture.NAMES), proof.files().keySet());
      assertThrows(UnsupportedOperationException.class, () -> proof.files().clear());
      var source = new HashMap<>(proof.files());
      var copied =
          new BackupArtifactVerifier.BundleSnapshot(proof.manifest(), proof.directory(), source);
      source.clear();
      assertEquals(4, copied.files().size());
      assertTrue(proof.samePublished(copied));
      assertThrows(NullPointerException.class, () -> proof.samePublished(null));
      assertThrows(
          NullPointerException.class,
          () -> new BackupArtifactVerifier.BundleSnapshot(null, proof.directory(), proof.files()));
      assertThrows(
          NullPointerException.class,
          () -> new BackupArtifactVerifier.BundleSnapshot(proof.manifest(), null, proof.files()));
      assertThrows(
          NullPointerException.class,
          () ->
              new BackupArtifactVerifier.BundleSnapshot(proof.manifest(), proof.directory(), null));
      var reader = new BackupManifestReader(f.root, f, UID, GID, f, f::clock);
      assertThrows(
          NullPointerException.class,
          () ->
              reader.readWithin(
                  null,
                  BackupArtifactFixture.expected().databaseStep(),
                  BackupArtifactFixture.expected().configurationStep(),
                  100));
      assertThrows(
          NullPointerException.class,
          () ->
              reader.readWithin(
                  BackupArtifactFixture.DIR,
                  null,
                  BackupArtifactFixture.expected().configurationStep(),
                  100));
      assertThrows(
          NullPointerException.class,
          () ->
              reader.readWithin(
                  BackupArtifactFixture.DIR,
                  BackupArtifactFixture.expected().databaseStep(),
                  null,
                  100));
      f.released();
    }
    try (var f = fixture()) {
      var verifier = new BackupArtifactVerifier(f.root, f, UID, GID, f, f::clock);
      var reader = new BackupManifestReader(f.root, f, UID, GID, f, f::clock);
      assertThrows(
          StorageIoException.class, () -> verifier.verify(BackupArtifactFixture.expected()));
      assertThrows(
          StorageIoException.class,
          () ->
              reader.read(
                  BackupArtifactFixture.DIR,
                  BackupArtifactFixture.expected().databaseStep(),
                  BackupArtifactFixture.expected().configurationStep()));
      assertThrows(
          NullPointerException.class, () -> verifier.forcePending(null, (p, s) -> {}, 100));
      assertThrows(
          NullPointerException.class,
          () -> verifier.forcePending(BackupArtifactFixture.expected(), null, 100));
      assertThrows(NullPointerException.class, () -> verifier.verifyWithin(null, 100));
      assertEquals(0, f.counts.getOrDefault("force", 0));
      f.bundlePublisher().publish(BackupArtifactFixture.expected());
      verifier.verify(BackupArtifactFixture.expected());
      reader.read(
          BackupArtifactFixture.DIR,
          BackupArtifactFixture.expected().databaseStep(),
          BackupArtifactFixture.expected().configurationStep());
      assertEquals(4, f.counts.get("force"));
      goldenFinal(f);
      f.released();
    }
  }

  @Test
  void independentBundleTrace() throws Exception {
    try (var f = fixture()) {
      var digest = f.bundlePublisher().publish(BackupArtifactFixture.expected());
      goldenFinal(f);
      f.released();
      Path folder = Path.of("target", "backup-bundle-traces");
      Files.createDirectories(folder);
      Files.writeString(
          folder.resolve("PT-BAT-273-bundle.txt"),
          digest.size()
              + "|"
              + digest.sha256()
              + "\n"
              + "force="
              + f.counts.get("force")
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
    }
  }

  private BackupPublicationFixture fixture() throws Exception {
    var f = new BackupPublicationFixture(temporary);
    f.seedBundle();
    return f;
  }

  private static Path finalDirectory(BackupPublicationFixture f) {
    return f.parent.resolve(BackupArtifactFixture.DIR);
  }

  private static void goldenFinal(BackupPublicationFixture f)
      throws IOException, NoSuchAlgorithmException {
    assertArrayEquals(
        BackupArtifactFixture.golden(),
        Files.readAllBytes(finalDirectory(f).resolve("MANIFEST.json")));
    for (var expected :
        Map.of(
                "schubert_nk.dump",
                BackupArtifactFixture.DUMP_HASH,
                "config.tar",
                BackupArtifactFixture.CONFIG_HASH,
                "credentials.tar.age",
                BackupArtifactFixture.CREDS_HASH)
            .entrySet())
      assertEquals(
          expected.getValue(),
          HexFormat.of()
              .formatHex(
                  MessageDigest.getInstance("SHA-256")
                      .digest(Files.readAllBytes(finalDirectory(f).resolve(expected.getKey())))));
  }

  private static void fails(BackupPublicationFixture f) {
    var failure =
        assertThrows(
            StorageIoException.class,
            () -> f.bundlePublisher().publish(BackupArtifactFixture.expected()));
    assertEquals(StorageIoException.Reason.UNAVAILABLE, failure.reason());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    f.released();
  }

  @FunctionalInterface
  interface CheckedAction {
    void run() throws IOException;
  }

  private static void action(CheckedAction action) {
    try {
      action.run();
    } catch (IOException failure) {
      throw new AssertionError(failure);
    }
  }
}
