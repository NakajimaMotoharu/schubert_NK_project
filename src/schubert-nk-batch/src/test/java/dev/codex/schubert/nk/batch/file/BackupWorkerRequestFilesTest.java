package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.BackupPublicationFixture.PART;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.batch.platform.BackupWorkerRequest;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-OPS-BREQFILE001..008 source-only; fixture root/tmpfs is explicitly synthetic. */
final class BackupWorkerRequestFilesTest {
  private static final String FIXTURE_UID_0C18F38C = "uid";
  private static final String FIXTURE_GID_0ACDD642 = "gid";
  private static final String FIXTURE_BACKUP_REQUEST_7ADCA59A = "backup-request";
  private static final String FIXTURE_PART_92B0D5FC = ".part";
  private static final String FIXTURE_PREPARE_1F4EE68F = "prepare";
  @TempDir Path temporary;
  private static final BackupWorkerRequest REQUEST =
      new BackupWorkerRequest(PART, Instant.parse("2026-09-27T14:59:59.123456Z"));
  private static final String GOLDEN =
      "NKBACKUP1\nrun=11111111-2222-4333-8444-555555555555\nstarted=2026-09-27T14:59:59.123456Z\n";

  private BackupPublicationFixture fixture() throws Exception {
    var f = new BackupPublicationFixture(temporary);
    f.metadata =
        (role, m) -> {
          m.put(FIXTURE_UID_0C18F38C, 0);
          m.put(FIXTURE_GID_0ACDD642, 0);
        };
    return f;
  }

  private BackupWorkerRequestFiles files(BackupPublicationFixture f) {
    return new BackupWorkerRequestFiles(f.root, f, f);
  }

  private void prepare(BackupPublicationFixture f) throws IOException {
    files(f).prepare(REQUEST, PART);
  }

  @Test
  void literalPublicationReadAndRetirement() throws Exception {
    try (var f = fixture()) {
      f.chunk = 7;
      prepare(f);
      assertEquals(GOLDEN, Files.readString(f.parent.resolve(FIXTURE_BACKUP_REQUEST_7ADCA59A)));
      assertFalse(Files.exists(f.parent.resolve(PART + FIXTURE_PART_92B0D5FC)));
      assertEquals(REQUEST, files(f).read());
      files(f).retire(REQUEST);
      assertFalse(Files.exists(f.parent.resolve(FIXTURE_BACKUP_REQUEST_7ADCA59A)));
      f.released();
    }
  }

  @Test
  void breqfile009ExplicitSameRequestResumeNeverRewritesOrAcceptsForeign() throws Exception {
    try (var f = fixture()) {
      var subject = files(f);
      subject.prepareResume(REQUEST, PART);
      Path source = f.parent.resolve(FIXTURE_BACKUP_REQUEST_7ADCA59A);
      var before =
          Files.readAttributes(
              source, "unix:ino,ctime,size,lastModifiedTime", LinkOption.NOFOLLOW_LINKS);
      var counts = new HashMap<>(f.counts);
      UUID next = UUID.fromString("22222222-3333-4444-8555-666666666666");
      subject.prepareResume(REQUEST, next);
      assertEquals(GOLDEN, Files.readString(source));
      assertEquals(
          before,
          Files.readAttributes(
              source, "unix:ino,ctime,size,lastModifiedTime", LinkOption.NOFOLLOW_LINKS));
      assertEquals(counts.get("publish"), f.counts.get("publish"));
      assertFalse(Files.exists(f.parent.resolve(next + FIXTURE_PART_92B0D5FC)));
      assertThrows(
          StorageIoException.class,
          () -> subject.prepareResume(new BackupWorkerRequest(next, REQUEST.started()), next));
      assertThrows(
          StorageIoException.class,
          () ->
              subject.prepareResume(
                  new BackupWorkerRequest(PART, Instant.parse("2026-09-27T15:00:00Z")), next));
      f.acl = new byte[] {1};
      assertThrows(StorageIoException.class, () -> subject.prepareResume(REQUEST, next));
      f.acl = new byte[0];
      assertThrows(NullPointerException.class, () -> subject.prepareResume(null, next));
      assertThrows(NullPointerException.class, () -> subject.prepareResume(REQUEST, null));
      f.released();
    }
  }

  @Test
  void breqfile010NewRealStartRequiresIndependentPriorPairProofBeforeRetirement() throws Exception {
    UUID next = UUID.fromString("22222222-3333-4444-8555-666666666666");
    var later = new BackupWorkerRequest(PART, Instant.parse("2026-09-27T15:00:00Z"));
    try (var f = fixture()) {
      var subject = files(f);
      subject.prepare(REQUEST, PART);
      assertThrows(
          java.io.IOException.class,
          () ->
              subject.prepareResumeReplacement(
                  later,
                  next,
                  old -> {
                    throw new java.io.IOException("actual DB unknown");
                  }));
      assertEquals(GOLDEN, Files.readString(f.parent.resolve(FIXTURE_BACKUP_REQUEST_7ADCA59A)));
      assertFalse(Files.exists(f.parent.resolve(next + FIXTURE_PART_92B0D5FC)));
      var proof = new AtomicInteger();
      subject.prepareResumeReplacement(
          later,
          next,
          old -> {
            assertEquals(PART, old.run());
            assertEquals(Instant.parse("2026-09-27T14:59:59.123456Z"), old.started());
            assertEquals(
                GOLDEN, Files.readString(f.parent.resolve(FIXTURE_BACKUP_REQUEST_7ADCA59A)));
            proof.incrementAndGet();
          });
      assertEquals(1, proof.get());
      assertEquals(
          "NKBACKUP1\nrun=11111111-2222-4333-8444-555555555555\nstarted=2026-09-27T15:00:00Z\n",
          Files.readString(f.parent.resolve(FIXTURE_BACKUP_REQUEST_7ADCA59A)));
      subject.prepareResumeReplacement(
          later, next, old -> fail("same-byte is not a prior generation"));
      assertThrows(
          StorageIoException.class,
          () ->
              subject.prepareResumeReplacement(
                  REQUEST, next, old -> fail("clock reversal must be refused first")));
      assertThrows(
          StorageIoException.class,
          () ->
              subject.prepareResumeReplacement(
                  new BackupWorkerRequest(next, Instant.parse("2026-09-27T15:01:00Z")),
                  next,
                  old -> fail("foreign run")));
      assertThrows(
          NullPointerException.class,
          () -> subject.prepareResumeReplacement(null, next, old -> {}));
      assertThrows(
          NullPointerException.class,
          () -> subject.prepareResumeReplacement(later, null, old -> {}));
      assertThrows(
          NullPointerException.class, () -> subject.prepareResumeReplacement(later, next, null));
      f.released();
    }
    try (var f = fixture()) {
      files(f).prepareResumeReplacement(later, next, old -> fail("no prior file exists"));
      assertEquals(later, files(f).read());
      f.released();
    }
  }

  @Test
  void nullActorAndPrivateMetadata() throws Exception {
    try (var f = fixture()) {
      assertThrows(NullPointerException.class, () -> new BackupWorkerRequestFiles(null, f));
      assertThrows(NullPointerException.class, () -> new BackupWorkerRequestFiles(f.root, null));
      assertThrows(NullPointerException.class, () -> new BackupWorkerRequestFiles(f.root, f, null));
      assertThrows(NullPointerException.class, () -> files(f).prepare(null, PART));
      assertThrows(NullPointerException.class, () -> files(f).prepare(REQUEST, null));
      assertThrows(NullPointerException.class, () -> files(f).retire(null));
      f.effective = 1;
      assertThrows(StorageIoException.class, () -> new BackupWorkerRequestFiles(f.root, f).read());
      assertThrows(StorageIoException.class, () -> files(f).prepare(REQUEST, PART));
    }
    for (String kind : List.of("owner", "mode", "acl", "readonly", "fs", "map"))
      try (var f = fixture()) {
        switch (kind) {
          case "owner" -> f.metadata = (r, m) -> m.put(FIXTURE_UID_0C18F38C, 1);
          case "mode" ->
              f.metadata =
                  (r, m) -> {
                    m.put(FIXTURE_UID_0C18F38C, 0);
                    m.put(FIXTURE_GID_0ACDD642, 0);
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
  void collisionMissingAndFixedNameOnly() throws Exception {
    try (var f = fixture()) {
      Files.writeString(f.parent.resolve("other"), GOLDEN);
      assertThrows(StorageIoException.class, () -> files(f).read());
      assertThrows(StorageIoException.class, () -> files(f).retire(REQUEST));
      assertEquals(GOLDEN, Files.readString(f.parent.resolve("other")));
    }
    try (var f = fixture()) {
      prepare(f);
      assertThrows(StorageIoException.class, () -> prepare(f));
      assertEquals(GOLDEN, Files.readString(f.parent.resolve(FIXTURE_BACKUP_REQUEST_7ADCA59A)));
      assertTrue(Files.exists(f.parent.resolve(PART + FIXTURE_PART_92B0D5FC)));
      f.released();
    }
    try (var f = fixture()) {
      Files.writeString(f.parent.resolve(PART + FIXTURE_PART_92B0D5FC), "PUBLIC_EXISTING");
      assertThrows(StorageIoException.class, () -> prepare(f));
      assertEquals(
          "PUBLIC_EXISTING", Files.readString(f.parent.resolve(PART + FIXTURE_PART_92B0D5FC)));
    }
  }

  @Test
  void allIoPositionsAndProgress() throws Exception {
    for (String operation : List.of(FIXTURE_PREPARE_1F4EE68F, "read", "retire")) {
      int positions;
      try (var f = fixture()) {
        if (!operation.equals(FIXTURE_PREPARE_1F4EE68F)) prepare(f);
        f.position = 0;
        operate(f, operation);
        positions = f.position;
      }
      for (int position = 1; position <= positions; position++)
        try (var f = fixture()) {
          if (!operation.equals(FIXTURE_PREPARE_1F4EE68F)) prepare(f);
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
      case FIXTURE_PREPARE_1F4EE68F -> prepare(f);
      case "read" -> files(f).read();
      default -> files(f).retire(REQUEST);
    }
  }

  @Test
  void sourceCanonicalAndOriginalBinding() throws Exception {
    try (var f = fixture()) {
      f.metadata =
          (role, m) -> {
            m.put(FIXTURE_UID_0C18F38C, 0);
            m.put(FIXTURE_GID_0ACDD642, 0);
            if (role.equals("file")) m.put("size", 1L);
          };
      assertThrows(StorageIoException.class, () -> prepare(f));
      f.released();
    }
    try (var f = fixture()) {
      prepare(f);
      Files.writeString(f.parent.resolve(FIXTURE_BACKUP_REQUEST_7ADCA59A), "PUBLIC_BAD_REQUEST\n");
      assertThrows(IllegalArgumentException.class, () -> files(f).read());
      f.released();
    }
    try (var f = fixture()) {
      prepare(f);
      assertThrows(
          StorageIoException.class,
          () -> files(f).retire(new BackupWorkerRequest(UUID.randomUUID(), REQUEST.started())));
      assertEquals(GOLDEN, Files.readString(f.parent.resolve(FIXTURE_BACKUP_REQUEST_7ADCA59A)));
      f.released();
    }
    for (String mutation : List.of("dev", "ino", "size", "lastModifiedTime"))
      try (var f = fixture()) {
        var seen = new AtomicInteger();
        f.metadata =
            (role, m) -> {
              m.put(FIXTURE_UID_0C18F38C, 0);
              m.put(FIXTURE_GID_0ACDD642, 0);
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
            m.put(FIXTURE_UID_0C18F38C, 0);
            m.put(FIXTURE_GID_0ACDD642, 0);
            if (r.equals("file")) m.put("dev", -1L);
          };
      assertThrows(StorageIoException.class, () -> prepare(f));
      f.released();
    }
  }

  @Test
  void unknownCompoundAndInterrupt() throws Exception {
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
  void parallelBorrowedScopesAndNoRepair() throws Exception {
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
  void namespaceReadAndRetireUncertainty() throws Exception {
    try (var f = fixture()) {
      prepare(f);
      f.faults.put("sync#2", new IOException("uncertain retire sync"));
      assertThrows(StorageIoException.class, () -> files(f).retire(REQUEST));
      assertFalse(Files.exists(f.parent.resolve(FIXTURE_BACKUP_REQUEST_7ADCA59A)));
      f.released();
    }
    try (var f = fixture()) {
      prepare(f);
      f.hook =
          (name, n) -> {
            if (name.equals("openReader")) {
              try {
                Files.move(
                    f.parent.resolve(FIXTURE_BACKUP_REQUEST_7ADCA59A),
                    f.parent.resolve("retained"));
                Files.writeString(f.parent.resolve(FIXTURE_BACKUP_REQUEST_7ADCA59A), GOLDEN);
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
