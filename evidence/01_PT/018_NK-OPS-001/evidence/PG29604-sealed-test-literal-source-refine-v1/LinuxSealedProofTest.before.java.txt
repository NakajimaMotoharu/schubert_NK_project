package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.lang.foreign.Linker;
import java.lang.foreign.MemorySegment;
import java.lang.foreign.ValueLayout;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** PT-OPS-SEAL-001..008; independent public byte vectors and actual immutable Linux memfd. */
final class LinuxSealedProofTest {
  private static final String FIXTURE_BODY_BFD4D039 = "body";
  private static final String FIXTURE_CREATE_5498A731 = "create";
  private static final String FIXTURE_CLOSE_17_F1422F88 = "close:17";
  private static final String FIXTURE_AMD64_58D0BD71 = "amd64";
  private static final String FIXTURE_LINUX_1CA133AF = "Linux";
  private static final byte[] VECTOR =
      "NKSTART1\npublic_fixture\n".getBytes(StandardCharsets.US_ASCII);

  @Test
  void opsSeal001LiteralBytesFlagsOrderAndScopedClose() throws Exception {
    var f = new Fixture(VECTOR);
    byte[] input = VECTOR.clone();
    assertEquals(
        "observed",
        f.calls()
            .withProof(
                input,
                fd -> {
                  assertEquals(129, fd);
                  f.events.add(FIXTURE_BODY_BFD4D039);
                  assertArrayEquals(VECTOR, f.written.toByteArray());
                  assertArrayEquals(VECTOR, f.calls().read(fd));
                  return "observed";
                }));
    assertArrayEquals(VECTOR, input);
    assertEquals(
        List.of(
            FIXTURE_CREATE_5498A731,
            "mode:17:384",
            "write:17",
            "fcntl:17:1033:15",
            "fcntl:17:1030:128",
            FIXTURE_BODY_BFD4D039,
            "fcntl:129:1034:0",
            "read:129:0",
            "read:129:24",
            "close:129",
            FIXTURE_CLOSE_17_F1422F88),
        f.events);
  }

  @Test
  void opsSeal002AllCreationSyscallFailuresAndCleanup() {
    for (String failed :
        List.of(
            FIXTURE_CREATE_5498A731,
            "mode",
            "write",
            "seal",
            "duplicate",
            "closeReserved",
            "closeOriginal")) {
      var f = new Fixture(VECTOR);
      f.failed = failed;
      unavailable(
          assertThrows(
              StorageIoException.class,
              () ->
                  f.calls()
                      .withProof(
                          VECTOR,
                          fd -> {
                            f.events.add(FIXTURE_BODY_BFD4D039);
                            return true;
                          })));
      if (!failed.equals(FIXTURE_CREATE_5498A731))
        assertEquals(FIXTURE_CLOSE_17_F1422F88, f.events.getLast());
      if (List.of("closeReserved", "closeOriginal").contains(failed))
        assertTrue(f.events.contains(FIXTURE_BODY_BFD4D039));
      else assertFalse(f.events.contains(FIXTURE_BODY_BFD4D039));
    }
    for (long count : List.of(0L, -1L, (long) VECTOR.length + 1)) {
      var f = new Fixture(VECTOR);
      f.writeResult = count;
      unavailable(
          assertThrows(StorageIoException.class, () -> f.calls().withProof(VECTOR, fd -> fail())));
      assertEquals(FIXTURE_CLOSE_17_F1422F88, f.events.getLast());
    }
    for (int reserved : List.of(127, 65536)) {
      var f = new Fixture(VECTOR);
      f.reserved = reserved;
      unavailable(
          assertThrows(StorageIoException.class, () -> f.calls().withProof(VECTOR, fd -> fail())));
      assertEquals(
          List.of("close:" + reserved, FIXTURE_CLOSE_17_F1422F88),
          f.events.subList(f.events.size() - 2, f.events.size()));
    }
  }

  @Test
  void opsSeal003ReadSealEmptyOversizeAndNativeErrors() {
    for (int seal : List.of(-1, 0, 1, 7, 14, 31)) {
      var f = new Fixture(VECTOR);
      f.seals = seal;
      unavailable(assertThrows(StorageIoException.class, () -> f.calls().read(129)));
      assertEquals(List.of("fcntl:129:1034:0"), f.events);
    }
    for (byte[] bytes : List.of(new byte[0], new byte[8193])) {
      var f = new Fixture(bytes);
      unavailable(assertThrows(StorageIoException.class, () -> f.calls().read(129)));
      assertFalse(f.events.stream().anyMatch(event -> event.startsWith("close:")));
    }
    for (long result : List.of(-1L, 8194L)) {
      var f = new Fixture(VECTOR);
      f.readResult = result;
      unavailable(assertThrows(StorageIoException.class, () -> f.calls().read(129)));
    }
    unavailable(
        assertThrows(StorageIoException.class, () -> LinuxSealedProof.create().read(65535)));
  }

  @Test
  void opsSeal004BoundaryAndPartialIoIndependentVector() throws Exception {
    for (int size : List.of(1, 8192)) {
      byte[] vector = new byte[size];
      Arrays.fill(vector, (byte) 'a');
      var f = new Fixture(vector);
      f.chunk = 3;
      assertArrayEquals(vector, f.calls().withProof(vector, fd -> f.calls().read(fd)));
      assertArrayEquals(vector, f.written.toByteArray());
      assertEquals(FIXTURE_CLOSE_17_F1422F88, f.events.getLast());
    }
    var f = new Fixture(VECTOR);
    f.reserved = 65535;
    boolean boundary =
        f.calls()
            .withProof(
                VECTOR,
                fd -> {
                  assertEquals(65535, fd);
                  return true;
                });
    assertTrue(boundary);
  }

  @Test
  void opsSeal005NullAndPlatformContracts() {
    var f = new Fixture(VECTOR);
    var calls = f.calls();
    assertThrows(NullPointerException.class, () -> calls.withProof(null, fd -> true));
    assertThrows(NullPointerException.class, () -> calls.withProof(VECTOR, null));
    for (byte[] bytes : List.of(new byte[0], new byte[8193]))
      assertThrows(IllegalArgumentException.class, () -> calls.withProof(bytes, fd -> true));
    for (int fd : List.of(127, 65536))
      assertThrows(IllegalArgumentException.class, () -> calls.read(fd));
    assertTrue(f.events.isEmpty());
    var symbols = Linker.nativeLinker().defaultLookup();
    assertThrows(
        NullPointerException.class,
        () -> LinuxSealedProof.create(null, FIXTURE_AMD64_58D0BD71, symbols));
    assertThrows(
        NullPointerException.class,
        () -> LinuxSealedProof.create(FIXTURE_LINUX_1CA133AF, null, symbols));
    assertThrows(
        NullPointerException.class,
        () -> LinuxSealedProof.create(FIXTURE_LINUX_1CA133AF, FIXTURE_AMD64_58D0BD71, null));
    for (String os : List.of("Windows", "linux", ""))
      assertThrows(
          IllegalStateException.class,
          () -> LinuxSealedProof.create(os, FIXTURE_AMD64_58D0BD71, symbols));
    assertThrows(
        IllegalStateException.class,
        () -> LinuxSealedProof.create(FIXTURE_LINUX_1CA133AF, "unknown", symbols));
    for (String missing : List.of("memfd_create", "write", "pread", "fcntl", "fchmod", "close"))
      assertThrows(
          IllegalStateException.class,
          () ->
              LinuxSealedProof.create(
                  FIXTURE_LINUX_1CA133AF,
                  FIXTURE_AMD64_58D0BD71,
                  name -> name.equals(missing) ? Optional.empty() : symbols.find(name)));
    for (String arch : List.of(FIXTURE_AMD64_58D0BD71, "x86_64", "aarch64"))
      assertNotNull(LinuxSealedProof.create(FIXTURE_LINUX_1CA133AF, arch, symbols));
    LinuxSealedProof.CreateCall create = (n, flags) -> 17;
    LinuxSealedProof.WriteCall write = (d, b, n) -> n;
    LinuxSealedProof.ReadCall read = (d, b, n, o) -> 0;
    LinuxSealedProof.FcntlCall fcntl = (d, c, a) -> 0;
    LinuxSealedProof.ModeCall mode = (d, m) -> 0;
    LinuxSealedProof.CloseCall close = d -> 0;
    assertThrows(
        NullPointerException.class,
        () -> new LinuxSealedProof(null, write, read, fcntl, mode, close));
    assertThrows(
        NullPointerException.class,
        () -> new LinuxSealedProof(create, null, read, fcntl, mode, close));
    assertThrows(
        NullPointerException.class,
        () -> new LinuxSealedProof(create, write, null, fcntl, mode, close));
    assertThrows(
        NullPointerException.class,
        () -> new LinuxSealedProof(create, write, read, null, mode, close));
    assertThrows(
        NullPointerException.class,
        () -> new LinuxSealedProof(create, write, read, fcntl, null, close));
    assertThrows(
        NullPointerException.class,
        () -> new LinuxSealedProof(create, write, read, fcntl, mode, null));
  }

  @Test
  void opsSeal006UnknownCompoundAndAllOwnedClose() {
    for (boolean cleanupUnknown : List.of(false, true))
      for (boolean knownBody : List.of(false, true))
        for (Throwable unknown :
            List.of(
                new IllegalStateException("public unknown"),
                new AssertionError("public unknown"))) {
          var f = new Fixture(VECTOR);
          f.cleanupUnknown = cleanupUnknown ? unknown : null;
          Class<? extends Throwable> expectedType =
              knownBody && !cleanupUnknown ? StorageIoException.class : unknown.getClass();
          var actual =
              assertThrows(
                  expectedType,
                  () ->
                      f.calls()
                          .withProof(
                              VECTOR,
                              fd -> {
                                if (knownBody) throw new IOException("private fixture diagnostic");
                                if (unknown instanceof RuntimeException failure) throw failure;
                                throw (Error) unknown;
                              }));
          if (knownBody && !cleanupUnknown) unavailable((StorageIoException) actual);
          else assertSame(unknown, actual);
          assertEquals(
              List.of("close:129", FIXTURE_CLOSE_17_F1422F88),
              f.events.subList(f.events.size() - 2, f.events.size()));
        }
  }

  @Test
  void opsSeal007RealMemfdModeSealsAndMutationRefusal() throws Exception {
    var proof = LinuxSealedProof.create();
    var saved = new int[] {-1};
    assertEquals(
        "verified",
        proof.withProof(
            VECTOR,
            fd -> {
              saved[0] = fd;
              var path = Path.of("/proc/self/fd/" + fd);
              var metadata = Files.readAttributes(path, "unix:mode,nlink,size");
              assertEquals(0x8180 /* POSIX 0100600 */, metadata.get("mode"));
              assertEquals(0, metadata.get("nlink"));
              assertEquals((long) VECTOR.length, metadata.get("size"));
              assertArrayEquals(VECTOR, proof.read(fd));
              assertThrows(IOException.class, () -> Files.write(path, new byte[] {1}));
              try (var channel = Files.newByteChannel(path, StandardOpenOption.WRITE)) {
                assertThrows(IOException.class, () -> channel.truncate(1));
                assertThrows(
                    IOException.class,
                    () -> channel.write(java.nio.ByteBuffer.wrap(new byte[] {1})));
                channel.position(VECTOR.length);
                assertThrows(
                    IOException.class,
                    () -> channel.write(java.nio.ByteBuffer.wrap(new byte[] {1})));
              }
              assertArrayEquals(VECTOR, proof.read(fd));
              return "verified";
            }));
    unavailable(assertThrows(StorageIoException.class, () -> proof.read(saved[0])));
  }

  @Test
  void opsSeal008NativeConcurrentProofsNeverMix() throws Exception {
    var proof = LinuxSealedProof.create();
    try (var executor = Executors.newFixedThreadPool(8)) {
      var work = new ArrayList<Callable<Boolean>>();
      for (int i = 0; i < 32; i++) {
        byte[] literal = ("PUBLIC-" + i).getBytes(StandardCharsets.US_ASCII);
        work.add(
            () ->
                proof.withProof(
                    literal,
                    fd -> {
                      assertArrayEquals(literal, proof.read(fd));
                      return true;
                    }));
      }
      for (var result : executor.invokeAll(work, 30, TimeUnit.SECONDS))
        assertTrue(result.get(10, TimeUnit.SECONDS));
    }
  }

  /** PT-OPS-SEAL-009: alias results create no second owner; native Test HOLD remains. */
  @Test
  void opsSeal009SameDescriptorResultNeverCreatesSecondOwner() {
    for (int original : List.of(128, 129, 65535)) {
      var fixture = new Fixture(VECTOR);
      fixture.original = original;
      fixture.reserved = original;
      unavailable(
          assertThrows(
              StorageIoException.class,
              () -> fixture.calls().withProof(VECTOR, fd -> fail("aliased owner callback"))));
      assertArrayEquals(VECTOR, fixture.written.toByteArray());
      assertEquals(
          List.of(
              FIXTURE_CREATE_5498A731,
              "mode:" + original + ":384",
              "write:" + original,
              "fcntl:" + original + ":1033:15",
              "fcntl:" + original + ":1030:128",
              "close:" + original),
          fixture.events);
    }
  }

  private static void unavailable(StorageIoException failure) {
    assertEquals(StorageIoException.Reason.UNAVAILABLE, failure.reason());
    assertEquals("transfer storage operation failed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static final class Fixture {
    final byte[] vector;
    final List<String> events = new ArrayList<>();
    final ByteArrayOutputStream written = new ByteArrayOutputStream();
    String failed = "";
    long writeResult = Long.MIN_VALUE;
    long readResult = Long.MIN_VALUE;
    int seals = 15;
    int reserved = 129;
    int original = 17;
    int chunk = 8193;
    Throwable cleanupUnknown;

    Fixture(byte[] vector) {
      this.vector = vector.clone();
    }

    LinuxSealedProof calls() {
      return new LinuxSealedProof(
          (name, flags) -> {
            assertEquals("schubert-startup-proof", name.getString(0));
            assertEquals(3, flags);
            events.add(FIXTURE_CREATE_5498A731);
            return failed.equals(FIXTURE_CREATE_5498A731) ? -1 : original;
          },
          (fd, buffer, count) -> {
            events.add("write:" + fd);
            if (failed.equals("write")) return -1;
            if (writeResult != Long.MIN_VALUE) return writeResult;
            int n = (int) Math.min(count, chunk);
            written.writeBytes(buffer.asSlice(0, n).toArray(ValueLayout.JAVA_BYTE));
            return n;
          },
          (fd, buffer, count, offset) -> {
            events.add("read:" + fd + ":" + offset);
            if (readResult != Long.MIN_VALUE) return readResult;
            int n = (int) Math.min(Math.min(count, chunk), vector.length - offset);
            MemorySegment.copy(vector, (int) offset, buffer, ValueLayout.JAVA_BYTE, 0, n);
            return n;
          },
          (fd, cmd, arg) -> {
            events.add("fcntl:" + fd + ":" + cmd + ":" + arg);
            return switch (cmd) {
              case 1033 -> failed.equals("seal") ? -1 : 0;
              case 1030 -> failed.equals("duplicate") ? -1 : reserved;
              case 1034 -> seals;
              default -> throw new AssertionError("unknown fixture command");
            };
          },
          (fd, permissions) -> {
            events.add("mode:" + fd + ":" + permissions);
            return failed.equals("mode") ? -1 : 0;
          },
          fd -> {
            events.add("close:" + fd);
            if (fd == 129 && cleanupUnknown != null) {
              if (cleanupUnknown instanceof RuntimeException failure) throw failure;
              throw (Error) cleanupUnknown;
            }
            return (fd == 129 && failed.equals("closeReserved"))
                    || (fd == 17 && failed.equals("closeOriginal"))
                ? -1
                : 0;
          });
    }
  }
}
