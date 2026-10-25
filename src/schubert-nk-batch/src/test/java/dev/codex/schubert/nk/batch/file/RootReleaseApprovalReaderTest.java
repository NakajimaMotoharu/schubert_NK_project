package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** Real retained FD/IO, public literal approval, explicitly synthetic root metadata/context. */
final class RootReleaseApprovalReaderTest {
  @TempDir Path temporary;
  private static final String SHA = "b".repeat(64);
  private static final String GOLDEN =
      "NKRELEASEAPPROVAL1\nversion=1.2.3-PG313\nmanifest_sha256=" + SHA + "\n";

  private BackupPublicationFixture fixture() throws Exception {
    var f = new BackupPublicationFixture(temporary);
    var app = Files.createDirectory(f.parent.resolve("schubert-nk"));
    var approval = Files.createDirectory(app.resolve("release-approval"));
    Files.writeString(approval.resolve("current"), GOLDEN);
    long appInode = (Long) Files.getAttribute(app, "unix:ino");
    f.metadata =
        (role, m) -> {
          m.put("uid", 0);
          m.put("gid", 0);
          if (role.equals("parent")) m.put("mode", 040755);
          else if (role.equals("child")) {
            boolean application = m.get("ino").equals(appInode);
            m.put("mode", application ? 040750 : 040700);
            if (application) m.put("gid", 2001);
          } else m.put("mode", 0100400);
        };
    return f;
  }

  private static Path original(BackupPublicationFixture f) {
    return f.parent.resolve("schubert-nk/release-approval/current");
  }

  private RootReleaseApprovalReader reader(BackupPublicationFixture f) {
    return new RootReleaseApprovalReader(
        f.parent,
        2001,
        f.calls,
        f,
        new RootReleaseApprovalReader.Io() {
          public Map<String, Object> attributes(Path held) throws IOException {
            return f.attributes(held);
          }

          public java.nio.channels.SeekableByteChannel open(Path held) throws IOException {
            return f.open(held);
          }
        },
        () -> f.point("gate"));
  }

  private void success(BackupPublicationFixture f) throws Exception {
    var a = reader(f).read();
    assertEquals("1.2.3-PG313", a.version());
    assertEquals(SHA, a.manifestSha256());
    f.released();
  }

  @Test
  void approvalRead001FixedLiteralAndClosedOwners() throws Exception {
    try (var f = fixture()) {
      f.chunk = 2;
      success(f);
      assertTrue(f.counts.get("read") > 1);
      assertEquals("1.2.3-PG313", reader(f).execute(a -> a.version()));
      f.released();
      assertEquals(GOLDEN, Files.readString(original(f)));
    }
  }

  @Test
  void approvalRead002NullAndNoFallback() throws Exception {
    try (var f = fixture()) {
      assertThrows(
          NullPointerException.class,
          () -> new RootReleaseApprovalReader(null, 2001, f.calls, f, null, () -> {}));
      assertThrows(
          NullPointerException.class,
          () -> new RootReleaseApprovalReader(f.parent, 2001, null, f, null, () -> {}));
      assertThrows(
          NullPointerException.class,
          () -> new RootReleaseApprovalReader(f.parent, 2001, f.calls, null, null, () -> {}));
      assertThrows(
          NullPointerException.class,
          () -> new RootReleaseApprovalReader(f.parent, 2001, f.calls, f, null, () -> {}));
      var io = new RootReleaseApprovalReader.NativeIo();
      assertThrows(
          NullPointerException.class,
          () -> new RootReleaseApprovalReader(f.parent, 2001, f.calls, f, io, null));
      for (Path p : List.of(Path.of("/"), Path.of("relative"), Path.of("/a/../b")))
        assertThrows(
            IllegalArgumentException.class,
            () -> new RootReleaseApprovalReader(p, 2001, f.calls, f, io, () -> {}));
      for (long group : List.of(0L, -1L, 4294967295L))
        assertThrows(
            IllegalArgumentException.class,
            () -> new RootReleaseApprovalReader(f.parent, group, f.calls, f, io, () -> {}));
      assertThrows(NullPointerException.class, () -> reader(f).execute(null));
      assertThrows(NullPointerException.class, () -> reader(f).execute(a -> null));
      f.released();
      f.nullReader = true;
      assertThrows(NullPointerException.class, () -> reader(f).read());
      f.released();
    }
    try (var f = fixture()) {
      Files.move(original(f), original(f).resolveSibling("candidate"));
      assertThrows(IOException.class, () -> reader(f).read());
      f.released();
    }
  }

  @Test
  void approvalRead003AllMetadataContracts() throws Exception {
    for (String role : List.of("parent", "child", "file"))
      for (String field :
          List.of("mode", "uid", "gid", "nlink", "size", "dev", "ino", "lastModifiedTime", "ctime"))
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
                        if (Set.of("size", "dev", "ino").contains(field)) m.put(field, -1L);
                        else if (Set.of("mode", "uid", "gid", "nlink").contains(field))
                          m.put(field, -1);
                        else m.remove(field);
                      }
                    }
                };
            assertThrows(IOException.class, () -> reader(f).read(), role + field + kind);
            f.released();
          }
    for (String kind :
        List.of(
            "acl",
            "nullAcl",
            "map",
            "uid",
            "device",
            "length0",
            "length193",
            "link2",
            "inode0",
            "directoryDevice"))
      try (var f = fixture()) {
        switch (kind) {
          case "acl" -> f.acl = new byte[] {1};
          case "nullAcl" -> f.acl = null;
          case "map" -> f.nullMap = true;
          case "uid" -> f.effective = 1;
          case "directoryDevice" -> {
            var valid = f.metadata;
            f.metadata =
                (r, m) -> {
                  valid.accept(r, m);
                  if (r.equals("child") && m.get("mode").equals(040700)) m.put("dev", 123L);
                };
          }
          default -> {
            var valid = f.metadata;
            f.metadata =
                (r, m) -> {
                  valid.accept(r, m);
                  if (r.equals("file"))
                    switch (kind) {
                      case "device" -> m.put("dev", 123L);
                      case "length0" -> m.put("size", 0L);
                      case "length193" -> m.put("size", 193L);
                      case "link2" -> m.put("nlink", 2);
                      default -> m.put("ino", 0L);
                    }
                };
          }
        }
        assertThrows(IOException.class, () -> reader(f).read(), kind);
        f.released();
      }
  }

  @Test
  void approvalRead004EveryIoFaultAndCompoundIdentity() throws Exception {
    List<String> events;
    try (var f = fixture()) {
      success(f);
      events = List.copyOf(f.events);
    }
    for (int position = 1; position <= events.size(); position++)
      try (var f = fixture()) {
        f.faultAt = position;
        assertThrows(Throwable.class, () -> reader(f).read());
        f.released();
      }
    for (String event : new HashSet<>(events))
      for (Throwable failure :
          List.of(new IllegalStateException("PRIVATE"), new AssertionError("PRIVATE")))
        try (var f = fixture()) {
          f.faults.put(event + "#1", failure);
          assertSame(failure, assertThrows(Throwable.class, () -> reader(f).read()));
          f.released();
        }
    for (Throwable primary :
        List.of(
            new IOException("PRIVATE"),
            new IllegalStateException("PRIVATE"),
            new AssertionError("PRIVATE")))
      for (Throwable close :
          List.of(
              new IOException("PRIVATE"),
              new IllegalStateException("PRIVATE"),
              new AssertionError("PRIVATE"),
              primary))
        try (var f = fixture()) {
          var actual =
              assertThrows(
                  Throwable.class,
                  () ->
                      reader(f)
                          .execute(
                              a -> {
                                f.faults.put(
                                    "close#" + (f.counts.getOrDefault("close", 0) + 1), close);
                                if (primary instanceof IOException e) throw e;
                                if (primary instanceof RuntimeException e) throw e;
                                throw (Error) primary;
                              }));
          if (!(primary instanceof IOException)) assertSame(primary, actual);
          else if (!(close instanceof IOException)) assertSame(close, actual);
          else assertInstanceOf(IOException.class, actual);
          f.released();
        }
  }

  @Test
  void approvalRead005ReadProgressAndCanonicalMaterial() throws Exception {
    for (String mode : List.of("zero", "short", "large", "position", "content", "eof-position-any"))
      try (var f = fixture()) {
        f.readMode = mode;
        assertThrows(IOException.class, () -> reader(f).read(), mode);
        if (mode.equals("eof-position-any")) assertEquals(1, f.counts.get("eofPositionInjected"));
        f.released();
      }
    for (String size : List.of("size#1", "size#2"))
      try (var f = fixture()) {
        f.changedSize = size;
        assertThrows(IOException.class, () -> reader(f).read());
        f.released();
      }
    for (String text :
        List.of(
            "", GOLDEN + "\n", GOLDEN.replace("\n", "\r\n"), "\ufeff" + GOLDEN, "P".repeat(193)))
      try (var f = fixture()) {
        Files.writeString(original(f), text);
        assertThrows(IOException.class, () -> reader(f).read());
        f.released();
      }
    try (var f = fixture()) {
      Files.writeString(original(f), "P".repeat(192));
      f.readMode = "extra";
      assertThrows(IOException.class, () -> reader(f).read());
      f.released();
    }
  }

  @Test
  void approvalRead006NamespaceAndHeldInodeChanges() throws Exception {
    int observations;
    try (var f = fixture()) {
      success(f);
      observations = f.counts.get("attributes");
    }
    for (int changed = 2; changed <= observations; changed++)
      try (var f = fixture()) {
        int at = changed;
        var valid = f.metadata;
        f.metadata =
            (r, m) -> {
              valid.accept(r, m);
              if (f.counts.get("attributes") == at) m.put("ino", 1234567L);
            };
        assertThrows(IOException.class, () -> reader(f).read());
        f.released();
      }
    try (var f = fixture()) {
      assertThrows(
          IOException.class,
          () ->
              reader(f)
                  .execute(
                      a -> {
                        Files.move(original(f), original(f).resolveSibling("previous"));
                        Files.writeString(original(f), GOLDEN);
                        return true;
                      }));
      f.released();
    }
  }

  @Test
  void approvalRead007InterruptRootAndParallel() throws Exception {
    try (var f = fixture()) {
      Thread.currentThread().interrupt();
      try {
        assertThrows(IOException.class, () -> reader(f).read());
        assertTrue(Thread.currentThread().isInterrupted());
      } finally {
        Thread.interrupted();
      }
      f.released();
    }
    try (var f = fixture()) {
      try {
        assertThrows(
            IOException.class,
            () ->
                reader(f)
                    .execute(
                        a -> {
                          Thread.currentThread().interrupt();
                          return true;
                        }));
      } finally {
        Thread.interrupted();
      }
      f.released();
    }
    try (var f = fixture()) {
      assertThrows(
          IOException.class,
          () ->
              reader(f)
                  .execute(
                      a -> {
                        f.effective = 1;
                        return true;
                      }));
      f.released();
    }
    try (var pool = Executors.newFixedThreadPool(4)) {
      var barrier = new CyclicBarrier(4);
      var futures = new ArrayList<Future<String>>();
      for (int i = 0; i < 4; i++)
        futures.add(
            pool.submit(
                () -> {
                  try (var f = fixture()) {
                    barrier.await(5, TimeUnit.SECONDS);
                    var result = reader(f).read();
                    f.released();
                    return result.manifestSha256();
                  }
                }));
      for (var future : futures) assertEquals(SHA, future.get(5, TimeUnit.SECONDS));
    }
  }

  @Test
  void approvalRead008NativePortAndRealContextRefusal() throws Exception {
    Path p = temporary.resolve("public");
    Files.writeString(p, GOLDEN);
    var io = new RootReleaseApprovalReader.NativeIo();
    assertEquals((long) GOLDEN.length(), io.attributes(p).get("size"));
    try (var channel = io.open(p)) {
      var buffer = ByteBuffer.allocate(GOLDEN.length());
      assertEquals(GOLDEN.length(), channel.read(buffer));
      assertArrayEquals(GOLDEN.getBytes(StandardCharsets.US_ASCII), buffer.array());
    }
    var expected =
        new RootStartupContext.Snapshot(
            RootStartupContext.Service.MORNING, "boot", "invocation", 2, 1, 1, "group");
    assertThrows(
        NullPointerException.class, () -> RootReleaseApprovalReader.create(null, expected));
    assertThrows(
        NullPointerException.class,
        () -> RootReleaseApprovalReader.create(RootStartupContext.create(), null));
    assertThrows(
        IOException.class,
        () -> RootReleaseApprovalReader.create(RootStartupContext.create(), expected));
    // Genuine root Unit positive is a separate native VM test, not inferred from this host refusal.
  }
}
