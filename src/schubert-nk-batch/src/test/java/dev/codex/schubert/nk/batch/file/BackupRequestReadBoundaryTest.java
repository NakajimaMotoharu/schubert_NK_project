package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.batch.platform.BackupWorkerRequest;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.nio.file.attribute.PosixFilePermissions;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** SS341/343, SSC113/114, NK-OPS-001/1479: own public bytes, reject before any mutation. */
final class BackupRequestReadBoundaryTest {
  @TempDir Path temporary;
  private static final UUID RUN = UUID.fromString("11111111-2222-4333-8444-555555555555");
  private static final UUID NEXT = UUID.fromString("22222222-3333-4444-8555-666666666666");
  private static final Instant START = Instant.parse("2026-09-27T14:59:59.123456Z");
  private static final String GOLDEN =
      "NKBACKUP1\nrun=11111111-2222-4333-8444-555555555555\nstarted=2026-09-27T14:59:59.123456Z\n";

  /** PT-OPS-BREQ-READ-001: only MISSING permits publication; UNAVAILABLE must propagate. */
  @Test
  void breqRead001UnavailableIsNotMissingAndNeverPublishes() throws Exception {
    for (boolean replacement : new boolean[] {false, true}) {
      try (var f = fixture()) {
        var before = identity(f);
        f.faults.put("openReader#1", new IOException("synthetic reader unavailable"));
        var proofs = new AtomicInteger();
        var failure =
            assertThrows(StorageIoException.class, () -> attempt(f, f, replacement, proofs));
        assertEquals(StorageIoException.Reason.UNAVAILABLE, failure.reason());
        assertEquals(0, proofs.get());
        unchanged(f, before);
      }
    }
  }

  /** PT-OPS-BREQ-READ-002: independently valid second read is not the retained first record. */
  @Test
  void breqRead002SecondValidRecordMismatchNeverRetires() throws Exception {
    for (boolean replacement : new boolean[] {false, true}) {
      try (var f = fixture()) {
        var before = identity(f);
        var changed = new AtomicInteger();
        var proofs = new AtomicInteger();
        var io = new SecondReadIo(f, changed);
        assertThrows(StorageIoException.class, () -> attempt(f, io, replacement, proofs));
        assertEquals(1, changed.get(), "one valid public input substitution");
        assertEquals(replacement ? 1 : 0, proofs.get());
        unchanged(f, before);
      }
    }
  }

  /** PT-OPS-BREQ-READ-003: final directory identity mismatch is not a retirement permit. */
  @Test
  void breqRead003FinalDirectoryChangeNeverRetires() throws Exception {
    for (boolean replacement : new boolean[] {false, true}) {
      try (var f = fixture()) {
        var before = identity(f);
        var parents = new AtomicInteger();
        var proofs = new AtomicInteger();
        f.metadata =
            (role, values) -> {
              values.put("uid", 0);
              values.put("gid", 0);
              // Outer before, each read's initial/final snapshot, then outer final: six.
              if (role.equals("parent") && parents.incrementAndGet() == 6)
                values.put("ino", ((Long) values.get("ino")) + 1);
            };
        assertThrows(StorageIoException.class, () -> attempt(f, f, replacement, proofs));
        assertEquals(6, parents.get());
        assertEquals(replacement ? 1 : 0, proofs.get());
        unchanged(f, before);
      }
    }
  }

  private BackupPublicationFixture fixture() throws Exception {
    var f = new BackupPublicationFixture(temporary);
    boolean complete = false;
    try {
      f.metadata =
          (role, values) -> {
            values.put("uid", 0);
            values.put("gid", 0);
          };
      Path file = f.parent.resolve("backup-request");
      Files.writeString(file, GOLDEN);
      Files.setPosixFilePermissions(file, PosixFilePermissions.fromString("rw-------"));
      f.hook =
          (name, count) -> {
            if (Set.of("createPrivateFile", "openWriter", "publish", "unlink", "sync", "force")
                .contains(name))
              fail("read boundary must reject before any mutating call: " + name);
          };
      complete = true;
      return f;
    } finally {
      if (!complete) f.close();
    }
  }

  private static Map<String, Object> identity(BackupPublicationFixture f) throws IOException {
    return Files.readAttributes(
        f.parent.resolve("backup-request"),
        "unix:ino,ctime,size,lastModifiedTime",
        LinkOption.NOFOLLOW_LINKS);
  }

  private static void unchanged(BackupPublicationFixture f, Map<String, Object> before)
      throws IOException {
    assertEquals(GOLDEN, Files.readString(f.parent.resolve("backup-request")));
    assertEquals(before, identity(f));
    assertFalse(Files.exists(f.parent.resolve(NEXT + ".part")));
    for (String operation :
        List.of("createPrivateFile", "openWriter", "publish", "unlink", "sync", "force"))
      assertEquals(0, f.counts.getOrDefault(operation, 0), operation);
    f.released();
  }

  private static void attempt(
      BackupPublicationFixture f,
      InspectorEnvironmentPublisher.Io io,
      boolean replacement,
      AtomicInteger proofs)
      throws IOException {
    var files = new BackupWorkerRequestFiles(f.root, f, io);
    if (replacement) {
      files.prepareResumeReplacement(
          new BackupWorkerRequest(RUN, Instant.parse("2026-09-27T15:00:00Z")),
          NEXT,
          previous -> {
            assertEquals(RUN, previous.run());
            assertEquals(START, previous.started());
            proofs.incrementAndGet();
          });
    } else files.prepareResume(new BackupWorkerRequest(RUN, START), NEXT);
  }

  private static final class SecondReadIo implements InspectorEnvironmentPublisher.Io {
    private final BackupPublicationFixture fixture;
    private final AtomicInteger substitutions;
    private int readers;

    SecondReadIo(BackupPublicationFixture fixture, AtomicInteger substitutions) {
      this.fixture = fixture;
      this.substitutions = substitutions;
    }

    @Override
    public Map<String, Object> attributes(Path held) throws IOException {
      return fixture.attributes(held);
    }

    @Override
    public String filesystem(Path held) {
      return fixture.filesystem(held);
    }

    @Override
    public InspectorEnvironmentPublisher.Writer openWriter(Path held) {
      throw new AssertionError("no writer in failed read fixture");
    }

    @Override
    public SeekableByteChannel open(Path held) throws IOException {
      var delegate = Objects.requireNonNull(fixture.open(held));
      boolean second = ++readers == 2;
      return new SeekableByteChannel() {
        @Override
        public int read(ByteBuffer target) throws IOException {
          int start = target.position();
          int count = delegate.read(target);
          if (second && start == 0 && count > 14) {
            assertEquals((byte) '1', target.get(14));
            target.put(14, (byte) '2'); // Independent literal NKBACKUP1\nrun= prefix is 14 bytes.
            substitutions.incrementAndGet();
          }
          return count;
        }

        @Override
        public long size() throws IOException {
          return delegate.size();
        }

        @Override
        public void close() throws IOException {
          delegate.close();
        }

        @Override
        public boolean isOpen() {
          throw new AssertionError("unexpected channel query");
        }

        @Override
        public long position() {
          throw new AssertionError("unexpected seek query");
        }

        @Override
        public SeekableByteChannel position(long offset) {
          throw new AssertionError("unexpected seek");
        }

        @Override
        public int write(ByteBuffer value) {
          throw new AssertionError("read-only fixture");
        }

        @Override
        public SeekableByteChannel truncate(long size) {
          throw new AssertionError("read-only fixture");
        }
      };
    }
  }
}
