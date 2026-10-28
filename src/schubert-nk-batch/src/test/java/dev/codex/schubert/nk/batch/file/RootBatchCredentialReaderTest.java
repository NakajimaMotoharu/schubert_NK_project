package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** RBCR001..012. Public bytes, real held IO, explicitly synthetic root/readonly/tmpfs metadata. */
final class RootBatchCredentialReaderTest {
  private static final String FIXTURE_CLEANUP_REQUEST_EE39FE0F = "cleanup-request";
  private static final String FIXTURE_31100027_2222_4333_8444_555555555555_2B6EB22D =
      "31100027-2222-4333-8444-555555555555";
  private static final String FIXTURE_UID_0C18F38C = "uid";
  private static final String FIXTURE_MODE_B6D5C2C3 = "mode";
  private static final String FIXTURE_DB_BATCH_118430FD = "db-batch";

  @Test
  void cfreq005PrivateCopyChoosesClosedProfileAndRedactsMalformedFrame() throws Exception {
    String failed =
        """
        NKCLEANFAIL1
        run=11111111-2222-4333-8444-555555555555
        activation=21111111-2222-4333-8444-555555555555
        cutoff=2026-09-27T15:00:00Z
        boot=31111111-2222-4333-8444-555555555555
        epoch=41111111-2222-4333-8444-555555555555
        backup_invocation=51111111-2222-4333-8444-555555555555
        backup_started_monotonic=1000000000
        backup_ended_monotonic=2000000000
        backup_exit=30
        database=7,4,2026-09-28,2026-09-30T01:02:03Z,2026-09-30T01:02:05Z,FAILED,1,0,1,0,COMMAND_FAILURE,batch command failed
        configuration=8,4,2026-09-28,2026-09-30T01:02:03Z,2026-09-30T01:02:05Z,FAILED,1,0,1,0,COMMAND_FAILURE,batch command failed
        """;
    try (var f = fixture()) {
      Files.writeString(f.parent.resolve(FIXTURE_CLEANUP_REQUEST_EE39FE0F), CLEANUP_REQUEST);
      assertInstanceOf(
          dev.codex.schubert.nk.batch.platform.CleanupWorkerRequest.class,
          reader(f).readCleanupProfile());
      Files.writeString(f.parent.resolve(FIXTURE_CLEANUP_REQUEST_EE39FE0F), failed);
      var result =
          assertInstanceOf(
              dev.codex.schubert.nk.batch.platform.CleanupFailedBackupRequest.class,
              reader(f).readCleanupProfile());
      assertEquals(7, result.failure().database().id());
      assertEquals(8, result.failure().configuration().id());
      assertEquals(30, result.backupExit());
      assertThrows(IOException.class, () -> reader(f).readCleanupRequest());
      for (String invalid :
          List.of("", "x".repeat(1025), failed.replace("NKCLEANFAIL1", "NKCLEANFAIL2"))) {
        Files.writeString(f.parent.resolve(FIXTURE_CLEANUP_REQUEST_EE39FE0F), invalid);
        var exception = assertThrows(IOException.class, () -> reader(f).readCleanupProfile());
        assertFalse(exception.toString().contains("NKCLEANFAIL"));
      }
      f.released();
    }
    try (var f = fixture()) {
      assertThrows(IOException.class, () -> reader(f).readCleanupProfile());
      f.released();
    }
  }

  @Test
  void rbcr013FixedOwnerCopyIndependentLiteralAndBoundedFailure() throws Exception {
    String literal =
        "NKMAINTOWNER1\nboot=31100027-3333-4333-8444-555555555555\n"
            + "run=31100027-2222-4333-8444-555555555555\nactivation=31100027-6666-4777-8888-999999999999\n"
            + "cutoff=2026-09-27T15:00:00Z\nepoch=31100027-4444-4333-8444-555555555555\n"
            + "morning_invocation=11111111111111111111111111111111\nmorning_pid=200\nmorning_start_ticks=100\n"
            + "cleanup_invocation=-\ncleanup_pid=-\ncleanup_start_ticks=-\ndeadline_nanos=1800000000001\n";
    try (var f = fixture()) {
      Files.writeString(f.parent.resolve("maintenance-owner"), literal);
      f.chunk = 3;
      var owner = reader(f).readMaintenanceOwner();
      assertEquals(FIXTURE_31100027_2222_4333_8444_555555555555_2B6EB22D, owner.run().toString());
      assertEquals(200L, owner.morning().pid());
      assertEquals(100L, owner.morning().startTicks());
      assertEquals(1800000000001L, owner.deadlineNanos());
      assertTrue(owner.cleanup().isEmpty());
      success(f);
      f.released();
    }
    for (String invalid :
        List.of(
            "",
            literal.replace("NKMAINTOWNER1", "NKMAINTOWNER2"),
            literal + "\n",
            "X".repeat(1025))) {
      try (var f = fixture()) {
        Files.writeString(f.parent.resolve("maintenance-owner"), invalid);
        var failure = assertThrows(IOException.class, () -> reader(f).readMaintenanceOwner());
        assertFalse(failure.toString().contains("NKMAINTOWNER"));
        f.released();
      }
    }
    try (var f = fixture()) {
      assertThrows(IOException.class, () -> reader(f).readMaintenanceOwner());
      f.released();
    }
  }

  @TempDir Path temporary;
  private static final String CLEANUP_REQUEST =
      "NKCLEAN1\n"
          + "run=31100027-2222-4333-8444-555555555555\n"
          + "activation=31100027-6666-4777-8888-999999999999\n"
          + "cutoff=2026-09-27T15:00:00Z\n"
          + "manifest=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef\n";

  private BackupPublicationFixture fixture() throws Exception {
    var f = new BackupPublicationFixture(temporary);
    f.readonly = true;
    f.metadata =
        (role, m) -> {
          m.put(FIXTURE_UID_0C18F38C, 0);
          m.put("gid", 0);
          m.put(FIXTURE_MODE_B6D5C2C3, role.equals("parent") ? 040500 : 0100400);
        };
    Files.writeString(f.parent.resolve(FIXTURE_DB_BATCH_118430FD), "PUBLIC_é\n");
    return f;
  }

  private RootBatchCredentialReader reader(BackupPublicationFixture f) {
    return new RootBatchCredentialReader(
        f.root,
        f,
        new RootBatchCredentialReader.Io() {
          public Map<String, Object> attributes(Path p) throws IOException {
            return f.attributes(p);
          }

          public String filesystem(Path p) {
            return f.filesystem(p);
          }

          public java.nio.channels.SeekableByteChannel open(Path p) throws IOException {
            return f.open(p);
          }
        });
  }

  private void success(BackupPublicationFixture f) throws Exception {
    try (var c = reader(f).read()) {
      char[] password = c.copyPassword();
      try {
        assertArrayEquals("PUBLIC_é".toCharArray(), password);
      } finally {
        Arrays.fill(password, '\0');
      }
    }
    f.released();
  }

  @Test
  void literalUtf8AndOwnedBuffers() throws Exception {
    try (var f = fixture()) {
      f.chunk = 2;
      success(f);
      assertTrue(f.counts.get("read") > 1);
    }
    for (int size : List.of(1, 65536))
      try (var f = fixture()) {
        Files.write(
            f.parent.resolve(FIXTURE_DB_BATCH_118430FD),
            "P".repeat(size).getBytes(StandardCharsets.UTF_8));
        try (var c = reader(f).read()) {
          char[] p = c.copyPassword();
          assertEquals(size, p.length);
          assertEquals('P', p[size - 1]);
          Arrays.fill(p, '\0');
        }
        f.released();
      }
  }

  @Test
  void nullAndFixedName() throws Exception {
    try (var f = fixture()) {
      assertThrows(NullPointerException.class, () -> new RootBatchCredentialReader(null, f));
      assertThrows(NullPointerException.class, () -> new RootBatchCredentialReader(f.root, null));
      assertThrows(
          NullPointerException.class, () -> new RootBatchCredentialReader(f.root, f, null));
      f.nullReader = true;
      assertThrows(NullPointerException.class, () -> reader(f).read());
      f.released();
    }
    try (var f = fixture()) {
      Files.move(f.parent.resolve(FIXTURE_DB_BATCH_118430FD), f.parent.resolve("db-api"));
      assertThrows(IOException.class, () -> reader(f).read());
      f.released();
    }
  }

  @Test
  void everyMetadataAndPolicyBoundary() throws Exception {
    for (String role : List.of("parent", "file"))
      for (String field :
          List.of(
              FIXTURE_MODE_B6D5C2C3,
              FIXTURE_UID_0C18F38C,
              "gid",
              "nlink",
              "size",
              "dev",
              "ino",
              "lastModifiedTime",
              "ctime"))
        for (String kind : List.of("missing", "wrong", "invalid"))
          try (var f = fixture()) {
            var valid = f.metadata;
            f.metadata =
                (r, m) -> {
                  valid.accept(r, m);
                  if (r.equals(role))
                    switch (kind) {
                      case "missing" -> m.remove(field);
                      case "wrong" -> m.put(field, "wrong");
                      default -> {
                        if (Set.of("lastModifiedTime", "ctime").contains(field)) m.remove(field);
                        else if (Set.of("size", "dev", "ino").contains(field)) m.put(field, -1L);
                        else m.put(field, -1);
                      }
                    }
                };
            assertThrows(IOException.class, () -> reader(f).read(), role + field + kind);
            f.released();
          }
    for (String kind :
        List.of("acl", "nullAcl", "readonly", "filesystem", "map", FIXTURE_UID_0C18F38C, "device"))
      try (var f = fixture()) {
        switch (kind) {
          case "acl" -> f.acl = new byte[] {1};
          case "nullAcl" -> f.acl = null;
          case "readonly" -> f.readonly = false;
          case "filesystem" -> f.copyFilesystem = "ext4";
          case "map" -> f.nullMap = true;
          case FIXTURE_UID_0C18F38C -> f.effective = 1;
          default -> {
            var valid = f.metadata;
            f.metadata =
                (r, m) -> {
                  valid.accept(r, m);
                  if (r.equals("file")) m.put("dev", 123L);
                };
          }
        }
        assertThrows(IOException.class, () -> reader(f).read(), kind);
        f.released();
      }
  }

  @Test
  void allIoAndUnknownPositionsCloseExactlyOnce() throws Exception {
    List<String> events;
    try (var f = fixture()) {
      success(f);
      events = List.copyOf(f.events);
    }
    for (String event : new HashSet<>(events))
      for (Throwable failure :
          List.of(
              new IOException("PRIVATE"),
              new IllegalStateException("PRIVATE"),
              new AssertionError("PRIVATE")))
        try (var f = fixture()) {
          // effectiveUid is a non-throwing native observation; its fixture translates IO to Error.
          f.faults.put(event + "#1", failure);
          Throwable actual = assertThrows(Throwable.class, () -> reader(f).read());
          if (!(failure instanceof IOException)) assertSame(failure, actual);
          f.released();
        }
  }

  @Test
  void progressSizeAndIndependentCodecNegatives() throws Exception {
    try (var f = fixture()) {
      Files.writeString(f.parent.resolve(FIXTURE_DB_BATCH_118430FD), "P".repeat(65536));
      f.readMode = "extra";
      assertThrows(IOException.class, () -> reader(f).read());
      f.released();
    }
    for (String mode : List.of("zero", "short", "large", "position", "content"))
      try (var f = fixture()) {
        f.readMode = mode;
        assertThrows(Exception.class, () -> reader(f).read(), mode);
        f.released();
      }
    for (String size : List.of("size#1", "size#2"))
      try (var f = fixture()) {
        f.changedSize = size;
        assertThrows(IOException.class, () -> reader(f).read());
        f.released();
      }
    for (byte[] bytes :
        List.of(
            new byte[0],
            new byte[65537],
            new byte[] {(byte) 0xff},
            new byte[] {'P', 0, 'Q'},
            new byte[] {'P', '\n', 'Q'}))
      try (var f = fixture()) {
        Files.write(f.parent.resolve(FIXTURE_DB_BATCH_118430FD), bytes);
        assertThrows(Exception.class, () -> reader(f).read());
        f.released();
      }
  }

  @Test
  void mutationAndInterruption() throws Exception {
    for (int occurrence : List.of(2, 3, 4))
      try (var f = fixture()) {
        var valid = f.metadata;
        f.metadata =
            (r, m) -> {
              valid.accept(r, m);
              if (f.counts.getOrDefault("attributes", 0) == occurrence) m.put("ino", 12345L);
            };
        assertThrows(IOException.class, () -> reader(f).read());
        f.released();
      }
    try (var f = fixture()) {
      Thread.currentThread().interrupt();
      try {
        assertThrows(IOException.class, () -> reader(f).read());
      } finally {
        Thread.interrupted();
      }
      f.released();
    }
    try (var f = fixture()) {
      f.hook =
          (n, i) -> {
            if (n.equals("closeReader")) Thread.currentThread().interrupt();
          };
      try {
        assertThrows(IOException.class, () -> reader(f).read());
      } finally {
        Thread.interrupted();
      }
      f.released();
    }
    try (var f = fixture()) {
      f.hook =
          (n, i) -> {
            if (n.equals("closeReader")) f.effective = 1;
          };
      assertThrows(IOException.class, () -> reader(f).read());
      f.released();
    }
  }

  @Test
  void sharedOwnerConcurrentIndependentMaterial() throws Exception {
    // Native IO/Directory owner is real; synthetic root policy is stateless, without fixture
    // counters.
    try (var f = fixture();
        var executor = Executors.newFixedThreadPool(2)) {
      var nativeIo = new RootBatchCredentialReader.NativeIo();
      var security =
          (dev.codex.schubert.nk.storage.InodeSecurityCalls)
              java.lang.reflect.Proxy.newProxyInstance(
                  getClass().getClassLoader(),
                  new Class<?>[] {dev.codex.schubert.nk.storage.InodeSecurityCalls.class},
                  (p, m, a) ->
                      switch (m.getName()) {
                        case "effectiveUid" -> 0L;
                        case "accessAcl" -> new byte[0];
                        case "readOnlyFilesystem" -> true;
                        default -> throw new AssertionError(m.getName());
                      });
      var reader =
          new RootBatchCredentialReader(
              f.root,
              security,
              new RootBatchCredentialReader.Io() {
                public Map<String, Object> attributes(Path p) throws IOException {
                  var m = new HashMap<>(nativeIo.attributes(p));
                  boolean dir = ((Integer) m.get(FIXTURE_MODE_B6D5C2C3) & 0170000) == 040000;
                  m.put(FIXTURE_MODE_B6D5C2C3, dir ? 040500 : 0100400);
                  m.put(FIXTURE_UID_0C18F38C, 0);
                  m.put("gid", 0);
                  return m;
                }

                public String filesystem(Path p) {
                  return "tmpfs";
                }

                public java.nio.channels.SeekableByteChannel open(Path p) throws IOException {
                  return nativeIo.open(p);
                }
              });
      var futures = new ArrayList<Future<String>>();
      for (int i = 0; i < 4; i++)
        futures.add(
            executor.submit(
                () -> {
                  try (var c = reader.read()) {
                    char[] p = c.copyPassword();
                    try {
                      return new String(p);
                    } finally {
                      Arrays.fill(p, '\0');
                    }
                  }
                }));
      for (var future : futures) assertEquals("PUBLIC_é", future.get(5, TimeUnit.SECONDS));
      f.released();
    }
  }

  @Test
  void nativePortPublicFileOnlyAndWrongActor() throws Exception {
    Path p = temporary.resolve("public.txt");
    Files.writeString(p, "PUBLIC");
    var io = new RootBatchCredentialReader.NativeIo();
    assertEquals(6L, io.attributes(p).get("size"));
    assertFalse(io.filesystem(p).isEmpty());
    try (var channel = io.open(p)) {
      var b = java.nio.ByteBuffer.allocate(6);
      assertEquals(6, channel.read(b));
      assertArrayEquals("PUBLIC".getBytes(StandardCharsets.US_ASCII), b.array());
    }
    try (var f = fixture()) {
      f.effective = 1;
      assertThrows(IOException.class, () -> new RootBatchCredentialReader(f.root, f).read());
    }
  }

  @Test
  void rbcr009FixedCleanupCopyCanonicalAndSeparateBatchPassword() throws Exception {
    try (var f = fixture()) {
      Files.writeString(f.parent.resolve(FIXTURE_CLEANUP_REQUEST_EE39FE0F), CLEANUP_REQUEST);
      var request = reader(f).readCleanupRequest();
      assertEquals(FIXTURE_31100027_2222_4333_8444_555555555555_2B6EB22D, request.run().toString());
      assertEquals("31100027-6666-4777-8888-999999999999", request.activation().toString());
      assertEquals("2026-09-27T15:00:00Z", request.cutoff().toString());
      assertEquals("0123456789abcdef".repeat(4), request.manifestSha256());
      success(f);
      f.released();
    }
    try (var f = fixture()) {
      assertThrows(IOException.class, () -> reader(f).readCleanupRequest());
      f.released();
    }
  }

  @Test
  void rbcr010CleanupLengthCodecAndUnknownNameFailClosed() throws Exception {
    for (String invalid :
        List.of(
            "",
            CLEANUP_REQUEST + "\n",
            CLEANUP_REQUEST.replace("NKCLEAN1", "NKCLEAN2"),
            CLEANUP_REQUEST.replace("manifest=0", "manifest=A"),
            "X".repeat(257)))
      try (var f = fixture()) {
        Files.write(
            f.parent.resolve(FIXTURE_CLEANUP_REQUEST_EE39FE0F),
            invalid.getBytes(StandardCharsets.US_ASCII));
        assertEquals(
            "root cleanup request unavailable",
            assertThrows(IOException.class, () -> reader(f).readCleanupRequest()).getMessage());
        f.released();
      }
    try (var f = fixture()) {
      Files.writeString(f.parent.resolve("db-api"), CLEANUP_REQUEST);
      assertThrows(IOException.class, () -> reader(f).readCleanupRequest());
      f.released();
    }
  }

  @Test
  void rbcr011CleanupHeldFileFaultAndRootPolicy() throws Exception {
    for (String mode : List.of("short", "zero", "position"))
      try (var f = fixture()) {
        Files.writeString(f.parent.resolve(FIXTURE_CLEANUP_REQUEST_EE39FE0F), CLEANUP_REQUEST);
        f.readMode = mode;
        assertThrows(Exception.class, () -> reader(f).readCleanupRequest());
        f.released();
      }
    try (var f = fixture()) {
      Files.writeString(f.parent.resolve(FIXTURE_CLEANUP_REQUEST_EE39FE0F), CLEANUP_REQUEST);
      f.effective = 1;
      assertThrows(IOException.class, () -> reader(f).readCleanupRequest());
      f.released();
    }
    try (var f = fixture()) {
      Files.writeString(f.parent.resolve(FIXTURE_CLEANUP_REQUEST_EE39FE0F), CLEANUP_REQUEST);
      f.acl = new byte[] {1};
      assertThrows(IOException.class, () -> reader(f).readCleanupRequest());
      f.released();
    }
  }

  @Test
  void rbcr012CleanupReplayAfterBadCopyNeverFallsBackToSource() throws Exception {
    try (var f = fixture()) {
      Path copy = f.parent.resolve(FIXTURE_CLEANUP_REQUEST_EE39FE0F);
      Files.writeString(copy, CLEANUP_REQUEST.replace("NKCLEAN1", "NKCLEAN2"));
      var subject = reader(f);
      assertThrows(IOException.class, subject::readCleanupRequest);
      Files.writeString(copy, CLEANUP_REQUEST);
      assertEquals(
          FIXTURE_31100027_2222_4333_8444_555555555555_2B6EB22D,
          subject.readCleanupRequest().run().toString());
      assertEquals(
          FIXTURE_31100027_2222_4333_8444_555555555555_2B6EB22D,
          subject.readCleanupRequest().run().toString());
      f.released();
    }
  }
}
