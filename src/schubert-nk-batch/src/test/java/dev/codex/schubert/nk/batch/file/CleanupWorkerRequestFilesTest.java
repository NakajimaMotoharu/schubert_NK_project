package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.BackupPublicationFixture.*;
import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.batch.platform.CleanupWorkerRequest;
import dev.codex.schubert.nk.storage.*;
import java.io.IOException;
import java.nio.file.*;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-OPS-CREQFILE001..008 source-only; fixture root/tmpfs is explicitly synthetic. */
final class CleanupWorkerRequestFilesTest {
  @Test
  void expiryFixedProfileNewOnlyReadRetireAndAllResidueIsolation() throws Exception {
    String literal =
        "NKEXPIRY1\nrun=38100000-2222-4333-8444-555555555555\nactivation=38100000-6666-4777-8888-999999999999\ncutoff=2026-09-30T00:00:00Z\nboot=38100000-3333-4333-8444-555555555555\nepoch=38100000-4444-4333-8444-555555555555\nbroker=11111111111111111111111111111111\nstep_id=42\nattempt=1\nstarted=2026-09-30T00:00:01Z\nskipped=false\n";
    var expected =
        dev.codex.schubert.nk.batch.platform.CleanupWorkerRequest.Expiry.consume(
            literal.getBytes(java.nio.charset.StandardCharsets.US_ASCII));
    try (var f = emptyExpiryFixture()) {
      var expiry = CleanupWorkerRequestFiles.forExpiry(f.root, f, f);
      expiry.requireClear();
      expiry.prepareExpiry(expected, PART);
      assertEquals(literal, Files.readString(f.parent.resolve("expiry-request")));
      assertEquals(expected, expiry.readExpiry());
      assertThrows(IOException.class, expiry::requireClear);
      assertThrows(IOException.class, expiry::read);
      assertThrows(IOException.class, () -> expiry.prepare(REQUEST, PART));
      assertThrows(IOException.class, () -> expiry.retire(REQUEST));
      assertThrows(IOException.class, () -> files(f).readExpiry());
      assertThrows(IOException.class, () -> files(f).prepareExpiry(expected, PART));
      assertThrows(IOException.class, () -> files(f).retireExpiry(expected));
      expiry.retireExpiry(expected);
      expiry.requireClear();
      assertFalse(Files.exists(f.parent.resolve("expiry-request")));
      f.released();
    }
    for (String residue : java.util.List.of("expiry-request", "orphan.part", "unknown")) {
      try (var f = emptyExpiryFixture()) {
        Files.writeString(f.parent.resolve(residue), "public residue");
        try (var entries = Files.list(f.parent)) {
          assertEquals(
              java.util.List.of(residue), entries.map(p -> p.getFileName().toString()).toList());
        }
        assertThrows(
            IOException.class,
            () -> CleanupWorkerRequestFiles.forExpiry(f.root, f, f).requireClear());
        assertEquals("public residue", Files.readString(f.parent.resolve(residue)));
        f.released();
      }
    }
    try (var f = fixture()) {
      assertThrows(
          NullPointerException.class,
          () -> CleanupWorkerRequestFiles.forExpiry(f.root, f, f).prepareExpiry(null, PART));
      assertThrows(
          NullPointerException.class,
          () -> CleanupWorkerRequestFiles.forExpiry(f.root, f, f).retireExpiry(null));
      assertNotNull(CleanupWorkerRequestFiles.forExpiry(f.root, f));
    }
  }

  @TempDir Path temporary;
  private static final UUID ACTIVATION = UUID.fromString("31100027-6666-4777-8888-999999999999");
  private static final String DIGEST = "0123456789abcdef".repeat(4);
  private static final CleanupWorkerRequest REQUEST =
      new CleanupWorkerRequest(
          PART, ACTIVATION, Instant.parse("2026-09-27T14:59:59.123456Z"), DIGEST);
  private static final String GOLDEN =
      "NKCLEAN1\nrun=11111111-2222-4333-8444-555555555555\nactivation=31100027-6666-4777-8888-999999999999\ncutoff=2026-09-27T14:59:59.123456Z\nmanifest=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef\n";

  private BackupPublicationFixture fixture() throws Exception {
    var f = new BackupPublicationFixture(temporary);
    f.metadata =
        (role, m) -> {
          m.put("uid", 0);
          m.put("gid", 0);
        };
    return f;
  }

  private BackupPublicationFixture emptyExpiryFixture() throws Exception {
    var f = fixture();
    Files.delete(
        f.child); // This test's own empty Backup-only fixture child, never Production residue.
    try (var entries = Files.list(f.parent)) {
      assertEquals(0, entries.count());
    }
    return f;
  }

  private CleanupWorkerRequestFiles files(BackupPublicationFixture f) {
    return new CleanupWorkerRequestFiles(f.root, f, f);
  }

  private void prepare(BackupPublicationFixture f) throws IOException {
    files(f).prepare(REQUEST, PART);
  }

  @Test
  void creqfile001LiteralPublicationReadAndRetirement() throws Exception {
    try (var f = fixture()) {
      f.chunk = 7;
      prepare(f);
      assertEquals(GOLDEN, Files.readString(f.parent.resolve("cleanup-request")));
      assertFalse(Files.exists(f.parent.resolve(PART + ".part")));
      assertEquals(REQUEST, files(f).read());
      files(f).retire(REQUEST);
      assertFalse(Files.exists(f.parent.resolve("cleanup-request")));
      f.released();
    }
  }

  @Test
  void creqfile002NullActorAndPrivateMetadata() throws Exception {
    try (var f = fixture()) {
      assertThrows(NullPointerException.class, () -> new CleanupWorkerRequestFiles(null, f));
      assertThrows(NullPointerException.class, () -> new CleanupWorkerRequestFiles(f.root, null));
      assertThrows(
          NullPointerException.class, () -> new CleanupWorkerRequestFiles(f.root, f, null));
      assertThrows(NullPointerException.class, () -> files(f).prepare(null, PART));
      assertThrows(NullPointerException.class, () -> files(f).prepare(REQUEST, null));
      assertThrows(NullPointerException.class, () -> files(f).retire(null));
      f.effective = 1;
      assertThrows(StorageIoException.class, () -> new CleanupWorkerRequestFiles(f.root, f).read());
      assertThrows(StorageIoException.class, () -> files(f).prepare(REQUEST, PART));
    }
    for (String kind : List.of("owner", "mode", "acl", "readonly", "fs", "map"))
      try (var f = fixture()) {
        switch (kind) {
          case "owner" -> f.metadata = (r, m) -> m.put("uid", 1);
          case "mode" ->
              f.metadata =
                  (r, m) -> {
                    m.put("uid", 0);
                    m.put("gid", 0);
                    m.put("mode", 040755);
                  };
          case "acl" -> f.acl = new byte[] {1};
          case "readonly" -> f.readonly = true;
          case "fs" -> f.copyFilesystem = "ext4";
          default -> f.nullMap = true;
        }
        assertThrows(StorageIoException.class, () -> prepare(f));
        f.released();
      }
  }

  @Test
  void creqfile003CollisionMissingAndFixedNameOnly() throws Exception {
    try (var f = fixture()) {
      Files.writeString(f.parent.resolve("other"), GOLDEN);
      assertThrows(StorageIoException.class, () -> files(f).read());
      assertThrows(StorageIoException.class, () -> files(f).retire(REQUEST));
      assertEquals(GOLDEN, Files.readString(f.parent.resolve("other")));
    }
    try (var f = fixture()) {
      prepare(f);
      assertThrows(StorageIoException.class, () -> prepare(f));
      assertEquals(GOLDEN, Files.readString(f.parent.resolve("cleanup-request")));
      assertTrue(Files.exists(f.parent.resolve(PART + ".part")));
      f.released();
    }
    try (var f = fixture()) {
      Files.writeString(f.parent.resolve(PART + ".part"), "PUBLIC_EXISTING");
      assertThrows(StorageIoException.class, () -> prepare(f));
      assertEquals("PUBLIC_EXISTING", Files.readString(f.parent.resolve(PART + ".part")));
    }
  }

  @Test
  void creqfile004AllIoPositionsAndProgress() throws Exception {
    for (String operation : List.of("prepare", "read", "retire")) {
      int positions;
      try (var f = fixture()) {
        if (!operation.equals("prepare")) prepare(f);
        f.position = 0;
        operate(f, operation);
        positions = f.position;
      }
      for (int position = 1; position <= positions; position++)
        try (var f = fixture()) {
          if (!operation.equals("prepare")) prepare(f);
          f.position = 0;
          f.faultAt = position;
          assertThrows(StorageIoException.class, () -> operate(f, operation));
          f.released();
        }
    }
    for (String mode : List.of("zero", "negative", "large", "position"))
      try (var f = fixture()) {
        f.writeMode = mode;
        assertThrows(StorageIoException.class, () -> prepare(f));
        f.released();
      }
    for (String mode :
        List.of("zero", "short", "large", "position", "extra", "eof-position", "content"))
      try (var f = fixture()) {
        f.readMode = mode;
        assertThrows(StorageIoException.class, () -> prepare(f));
        f.released();
      }
    for (boolean writer : List.of(true, false))
      try (var f = fixture()) {
        f.nullWriter = writer;
        f.nullReader = !writer;
        assertThrows(StorageIoException.class, () -> prepare(f));
        f.released();
      }
    for (String point : List.of("writerSize#1", "writerSize#2", "writerSize#3", "size#1", "size#2"))
      try (var f = fixture()) {
        f.changedSize = point;
        assertThrows(StorageIoException.class, () -> prepare(f));
        f.released();
      }
  }

  private void operate(BackupPublicationFixture f, String operation) throws IOException {
    switch (operation) {
      case "prepare" -> prepare(f);
      case "read" -> files(f).read();
      default -> files(f).retire(REQUEST);
    }
  }

  @Test
  void creqfile005SourceCanonicalAndOriginalBinding() throws Exception {
    try (var f = fixture()) {
      f.metadata =
          (role, m) -> {
            m.put("uid", 0);
            m.put("gid", 0);
            if (role.equals("file")) m.put("size", 1L);
          };
      assertThrows(StorageIoException.class, () -> prepare(f));
      f.released();
    }
    try (var f = fixture()) {
      prepare(f);
      Files.writeString(f.parent.resolve("cleanup-request"), "PUBLIC_BAD_REQUEST\n");
      assertThrows(IllegalArgumentException.class, () -> files(f).read());
      f.released();
    }
    try (var f = fixture()) {
      prepare(f);
      assertThrows(
          StorageIoException.class,
          () ->
              files(f)
                  .retire(
                      new CleanupWorkerRequest(
                          UUID.randomUUID(),
                          REQUEST.activation(),
                          REQUEST.cutoff(),
                          REQUEST.manifestSha256())));
      assertEquals(GOLDEN, Files.readString(f.parent.resolve("cleanup-request")));
      f.released();
    }
    for (String mutation : List.of("dev", "ino", "size", "lastModifiedTime"))
      try (var f = fixture()) {
        var seen = new AtomicInteger();
        f.metadata =
            (role, m) -> {
              m.put("uid", 0);
              m.put("gid", 0);
              if (role.equals("file")
                  && seen.incrementAndGet() > (mutation.equals("lastModifiedTime") ? 2 : 1))
                m.put(
                    mutation,
                    mutation.equals("lastModifiedTime")
                        ? java.nio.file.attribute.FileTime.fromMillis(0)
                        : mutation.equals("size") ? 1L : -1L);
            };
        assertThrows(StorageIoException.class, () -> prepare(f));
        f.released();
      }
    try (var f = fixture()) {
      f.metadata =
          (r, m) -> {
            m.put("uid", 0);
            m.put("gid", 0);
            if (r.equals("file")) m.put("dev", -1L);
          };
      assertThrows(StorageIoException.class, () -> prepare(f));
      f.released();
    }
  }

  @Test
  void creqfile006UnknownCompoundAndInterrupt() throws Exception {
    for (Throwable primary :
        List.of(new IllegalStateException("public"), new AssertionError("public")))
      try (var f = fixture()) {
        f.faults.put("write#1", primary);
        assertSame(primary, assertThrows(Throwable.class, () -> prepare(f)));
        f.released();
      }
    try (var f = fixture()) {
      f.faults.put("write#1", new IOException("private diagnostic"));
      var unknown = new IllegalStateException("public unknown close");
      f.faults.put("closeWriter#1", unknown);
      assertSame(unknown, assertThrows(Throwable.class, () -> prepare(f)));
      f.released();
    }
    try (var f = fixture()) {
      Thread.currentThread().interrupt();
      try {
        assertThrows(StorageIoException.class, () -> prepare(f));
        assertTrue(Thread.currentThread().isInterrupted());
      } finally {
        Thread.interrupted();
      }
      f.released();
    }
  }

  @Test
  void creqfile007ParallelBorrowedScopesAndNoRepair() throws Exception {
    try (var executor = Executors.newFixedThreadPool(4)) {
      var tasks = new ArrayList<Callable<Boolean>>();
      for (int i = 0; i < 16; i++)
        tasks.add(
            () -> {
              try (var f = fixture()) {
                prepare(f);
                assertEquals(REQUEST, files(f).read());
                files(f).retire(REQUEST);
                f.released();
                return true;
              }
            });
      for (var result : executor.invokeAll(tasks)) assertTrue(result.get());
    }
  }

  @Test
  void creqfile008NamespaceReadAndRetireUncertainty() throws Exception {
    try (var f = fixture()) {
      prepare(f);
      f.faults.put("sync#2", new IOException("uncertain retire sync"));
      assertThrows(StorageIoException.class, () -> files(f).retire(REQUEST));
      assertFalse(Files.exists(f.parent.resolve("cleanup-request")));
      f.released();
    }
    try (var f = fixture()) {
      prepare(f);
      f.hook =
          (name, n) -> {
            if (name.equals("openReader")) {
              try {
                Files.move(f.parent.resolve("cleanup-request"), f.parent.resolve("retained"));
                Files.writeString(f.parent.resolve("cleanup-request"), GOLDEN);
              } catch (IOException e) {
                throw new AssertionError(e);
              }
            }
          };
      assertThrows(StorageIoException.class, () -> files(f).read());
      assertTrue(Files.exists(f.parent.resolve("retained")));
      f.released();
    }
  }
}
