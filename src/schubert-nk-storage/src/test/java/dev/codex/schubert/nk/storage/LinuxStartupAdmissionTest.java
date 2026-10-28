package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import java.io.IOException;
import java.lang.foreign.Linker;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;

/** PT-OPS-CHILDFD-001..008; independent root metadata/syscall vectors, native positive in VM015. */
final class LinuxStartupAdmissionTest {
  private static final String FIXTURE_UID_0C18F38C = "uid";
  private static final String FIXTURE_NLINK_3DDD828B = "nlink";
  private static final String FIXTURE_SIZE_EB1E91E4 = "size";
  private static final String FIXTURE_DEV_8A17302D = "dev";
  private static final String FIXTURE_INO_4BE7C1E0 = "ino";
  private static final String FIXTURE_PRIVATE_D45CA6F9 = "PRIVATE";
  private static final String FIXTURE_AMD64_58D0BD71 = "amd64";
  private static final String FIXTURE_LINUX_1CA133AF = "Linux";
  static final int A = 128;
  static final int P = 129;

  static Map<String, Object> attrs(boolean proof) {
    return new HashMap<>(
        Map.of(
            "mode",
            0100600,
            FIXTURE_UID_0C18F38C,
            0,
            "gid",
            0,
            FIXTURE_NLINK_3DDD828B,
            proof ? 0 : 1,
            FIXTURE_SIZE_EB1E91E4,
            proof ? 3L : 0L,
            FIXTURE_DEV_8A17302D,
            2L,
            FIXTURE_INO_4BE7C1E0,
            proof ? 3L : 4L));
  }

  static class Fixture implements LinuxStartupAdmission.Io {
    final Map<Integer, Map<String, Object>> attrs =
        new HashMap<>(Map.of(A, attrs(false), P, attrs(true)));
    final List<String> calls = new ArrayList<>();
    final List<Integer> closed = new ArrayList<>();
    byte[] payload = {65, 66, 67};
    int syscall;
    int fault;
    int seal = 15;
    int flags;
    int initial;
    int failClose;
    Throwable unknown;
    boolean readIo;
    boolean attrsIo;

    public int fcntl(int fd, int cmd, int arg) {
      calls.add(fd + ":" + cmd + ":" + arg);
      syscall++;
      if (syscall == fault) return -1;
      if (cmd == 1) return initial;
      if (cmd == 1034) return seal;
      if (cmd == 3) return flags;
      return 0;
    }

    public int close(int fd) {
      closed.add(fd);
      if (fd == failClose) {
        if (unknown instanceof Error e) throw e;
        if (unknown instanceof RuntimeException r) throw r;
        return -1;
      }
      return 0;
    }

    public Map<String, Object> attributes(int fd) throws IOException {
      if (attrsIo) throw new IOException(FIXTURE_PRIVATE_D45CA6F9);
      return attrs.get(fd);
    }

    public byte[] proof(int fd) throws IOException {
      assertEquals(P, fd);
      if (readIo) throw new IOException(FIXTURE_PRIVATE_D45CA6F9);
      return payload;
    }

    LinuxStartupAdmission subject() {
      return new LinuxStartupAdmission(this);
    }
  }

  static void reject(Fixture f) {
    StorageIoException e =
        assertThrows(
            StorageIoException.class,
            () ->
                f.subject()
                    .withAdmitted(
                        A,
                        P,
                        (lease, bytes) -> {
                          fail("callback before admission");
                          return 1;
                        }));
    assertEquals(StorageIoException.Reason.UNAVAILABLE, e.reason());
    assertNull(e.getCause());
    assertEquals(List.of(P, A), f.closed);
  }

  @Test
  void childfd009OwnerSetAdoptsBothAndConsumesProofBeforeAdmissionOnce() throws Exception {
    Fixture first = new Fixture();
    var owners = new LinuxStartupAdmission.FdOwners(A, P, first);
    assertTrue(first.closed.isEmpty());
    assertTrue(first.calls.isEmpty());
    owners.close();
    owners.close();
    assertEquals(List.of(P, A), first.closed);
    Fixture early = new Fixture();
    var earlyOwners = new LinuxStartupAdmission.FdOwners(A, P, early);
    earlyOwners.closeProof();
    assertEquals(List.of(P), early.closed);
    earlyOwners.close();
    earlyOwners.closeProof();
    assertEquals(List.of(P, A), early.closed);
    assertThrows(NullPointerException.class, () -> new LinuxStartupAdmission.FdOwners(A, P, null));
  }

  @Test
  void childfd010OwnerSetCompoundFailuresKeepIndependentPriorityAndBothConsumption() {
    for (int primary = 0; primary < 4; primary++) {
      for (int secondary = 0; secondary < 4; secondary++) {
        int firstKind = primary;
        int lastKind = secondary;
        RuntimeException p = new IllegalStateException("PRIVATE-P");
        RuntimeException a = new IllegalArgumentException("PRIVATE-A");
        Error pe = new AssertionError("PRIVATE-P-FATAL");
        Error ae = new AssertionError("PRIVATE-A-FATAL");
        Fixture fixture =
            new Fixture() {
              @Override
              public int close(int fd) {
                closed.add(fd);
                int kind = fd == P ? firstKind : lastKind;
                if (kind == 1) return -1;
                if (kind == 2) throw fd == P ? p : a;
                if (kind == 3) throw fd == P ? pe : ae;
                return 0;
              }
            };
        var owners = new LinuxStartupAdmission.FdOwners(A, P, fixture);
        if (primary == 0 && secondary == 0) {
          assertDoesNotThrow(owners::close);
        } else {
          Throwable actual = assertThrows(Throwable.class, owners::close);
          if (primary >= 2) {
            assertSame(primary == 2 ? p : pe, actual);
            assertEquals(secondary == 0 ? 0 : 1, actual.getSuppressed().length);
            if (secondary != 0) {
              StorageIoException redacted =
                  assertInstanceOf(StorageIoException.class, actual.getSuppressed()[0]);
              assertEquals("transfer storage operation failed", redacted.getMessage());
              assertNull(redacted.getCause());
            }
          } else if (secondary >= 2) {
            assertSame(secondary == 2 ? a : ae, actual);
            assertEquals(0, actual.getSuppressed().length);
          } else {
            StorageIoException redacted = assertInstanceOf(StorageIoException.class, actual);
            assertEquals(StorageIoException.Reason.UNAVAILABLE, redacted.reason());
            assertEquals("transfer storage operation failed", redacted.getMessage());
            assertNull(redacted.getCause());
            assertEquals(0, redacted.getSuppressed().length);
          }
        }
        assertEquals(List.of(P, A), fixture.closed);
        assertDoesNotThrow(owners::close);
        assertEquals(List.of(P, A), fixture.closed);
      }
    }
  }

  @Test
  void childfd001RootSealsImmediateCloexecAndEarlyProofClose() {
    var f = new Fixture();
    var retained = new AtomicReference<byte[]>();
    assertEquals(
        (Object) 7,
        assertDoesNotThrow(
            () ->
                f.subject()
                    .withAdmitted(
                        A,
                        P,
                        (lease, bytes) -> {
                          assertEquals(List.of(P), f.closed);
                          assertEquals(
                              List.of(
                                  "128:1:0",
                                  "129:1:0",
                                  "128:2:1",
                                  "129:2:1",
                                  "129:1034:0",
                                  "128:3:0"),
                              f.calls);
                          assertEquals(
                              new LinuxStartupAdmission.Identity(A, 2, 4), lease.identity());
                          assertArrayEquals(new byte[] {65, 66, 67}, bytes);
                          retained.set(bytes);
                          return 7;
                        })));
    assertEquals(List.of(P, A), f.closed);
    assertArrayEquals(new byte[3], retained.get());
    var own = new Fixture();
    assertEquals(
        (Object) 8,
        assertDoesNotThrow(
            () ->
                own.subject()
                    .withAdmitted(
                        A,
                        P,
                        (lease, bytes) -> {
                          lease.close();
                          lease.close();
                          assertEquals(List.of(P, A), own.closed);
                          return 8;
                        })));
    assertEquals(List.of(P, A), own.closed);
  }

  @Test
  void childfd002EveryDescriptorInputAndNullContractBeforeOwnership() {
    for (int fd : List.of(-1, 0, 127, 65536, Integer.MAX_VALUE)) {
      var f = new Fixture();
      assertThrows(
          IllegalArgumentException.class, () -> f.subject().withAdmitted(fd, P, (a, p) -> 1));
      assertTrue(f.closed.isEmpty());
      assertThrows(
          IllegalArgumentException.class, () -> f.subject().withAdmitted(A, fd, (a, p) -> 1));
      assertTrue(f.calls.isEmpty());
    }
    var f = new Fixture();
    assertThrows(IllegalArgumentException.class, () -> f.subject().withAdmitted(A, A, (a, p) -> 1));
    assertThrows(NullPointerException.class, () -> f.subject().withAdmitted(A, P, null));
    assertThrows(NullPointerException.class, () -> new LinuxStartupAdmission(null));
    assertTrue(f.closed.isEmpty());
  }

  @Test
  void childfd003BothFdInitialFlagsAllSyscallsAndReadonlyAccess() {
    for (int i = 1; i <= 6; i++) {
      var f = new Fixture();
      f.fault = i;
      reject(f);
    }
    for (int initial : List.of(-1, 1, 2)) {
      var f = new Fixture();
      f.initial = initial;
      reject(f);
    }
    for (int seal : List.of(-1, 0, 1, 7, 31)) {
      var f = new Fixture();
      f.seal = seal;
      reject(f);
    }
    for (int flags : List.of(-1, 1, 2, 1024, 2048, 16384, 2097152, 32769)) {
      var f = new Fixture();
      f.flags = flags;
      reject(f);
    }
    var f = new Fixture();
    f.flags = 32768;
    assertEquals((Object) 1, assertDoesNotThrow(() -> f.subject().withAdmitted(A, P, (a, p) -> 1)));
  }

  @Test
  void childfd004EveryTypedAttributeRootModeLinkSizeAndUnsignedIdentity() {
    for (int fd : List.of(A, P))
      for (String key :
          List.of(
              "mode",
              FIXTURE_UID_0C18F38C,
              "gid",
              FIXTURE_NLINK_3DDD828B,
              FIXTURE_SIZE_EB1E91E4,
              FIXTURE_DEV_8A17302D,
              FIXTURE_INO_4BE7C1E0)) {
        var f = new Fixture();
        f.attrs.get(fd).remove(key);
        reject(f);
        f = new Fixture();
        f.attrs.get(fd).put(key, "wrong type");
        reject(f);
      }
    for (int fd : List.of(A, P))
      for (var bad :
          List.of(
              Map.entry("mode", (Object) 0100640),
              Map.entry(FIXTURE_UID_0C18F38C, (Object) 1),
              Map.entry("gid", (Object) 1),
              Map.entry(FIXTURE_DEV_8A17302D, (Object) 0L),
              Map.entry(FIXTURE_INO_4BE7C1E0, (Object) 0L))) {
        var f = new Fixture();
        f.attrs.get(fd).put(bad.getKey(), bad.getValue());
        reject(f);
      }
    for (int fd : List.of(A, P)) {
      var f = new Fixture();
      f.attrs.remove(fd);
      reject(f);
    }
    for (int links : List.of(-1, 0, 2)) {
      var f = new Fixture();
      f.attrs.get(A).put(FIXTURE_NLINK_3DDD828B, links);
      reject(f);
    }
    for (long size : List.of(-1L, 1L, 8192L)) {
      var f = new Fixture();
      f.attrs.get(A).put(FIXTURE_SIZE_EB1E91E4, size);
      reject(f);
    }
    for (int links : List.of(-1, 1, 2)) {
      var f = new Fixture();
      f.attrs.get(P).put(FIXTURE_NLINK_3DDD828B, links);
      reject(f);
    }
    for (long size : List.of(-1L, 0L, 8193L)) {
      var f = new Fixture();
      f.attrs.get(P).put(FIXTURE_SIZE_EB1E91E4, size);
      reject(f);
    }
    for (int size : List.of(1, 8192)) {
      var f = new Fixture();
      f.attrs.get(P).put(FIXTURE_SIZE_EB1E91E4, (long) size);
      f.payload = new byte[size];
      assertEquals(
          (Object) size,
          assertDoesNotThrow(() -> f.subject().withAdmitted(A, P, (a, p) -> p.length)));
    }
    var f = new Fixture();
    f.attrs.get(A).put(FIXTURE_DEV_8A17302D, -1L);
    f.attrs.get(A).put(FIXTURE_INO_4BE7C1E0, -2L);
    assertEquals(
        new LinuxStartupAdmission.Identity(A, -1, -2),
        assertDoesNotThrow(() -> f.subject().withAdmitted(A, P, (a, p) -> a.identity())));
  }

  @Test
  void childfd005PayloadNullSizeIoAndProofCloseBeforeCallback() {
    var f = new Fixture();
    f.payload = new byte[2];
    reject(f);
    f = new Fixture();
    f.readIo = true;
    reject(f);
    f = new Fixture();
    f.attrsIo = true;
    reject(f);
    f = new Fixture();
    f.failClose = P;
    reject(f);
    assertArrayEquals(new byte[3], f.payload);
    var nullIo =
        new Fixture() {
          @Override
          public byte[] proof(int fd) {
            return null;
          }
        };
    assertThrows(
        NullPointerException.class, () -> nullIo.subject().withAdmitted(A, P, (a, p) -> 1));
    assertEquals(List.of(P, A), nullIo.closed);
  }

  @Test
  void childfd006UnknownAndCompoundFailurePriorityAndOneClose() {
    for (int fd : List.of(A, P))
      for (Throwable unknown :
          List.of(
              new AssertionError(FIXTURE_PRIVATE_D45CA6F9),
              new IllegalStateException(FIXTURE_PRIVATE_D45CA6F9))) {
        var f = new Fixture();
        f.failClose = fd;
        f.unknown = unknown;
        assertSame(
            unknown,
            assertThrows(unknown.getClass(), () -> f.subject().withAdmitted(A, P, (a, p) -> 1)));
        assertEquals(List.of(P, A), f.closed);
        assertArrayEquals(new byte[3], f.payload);
      }
    for (int closeFd : List.of(0, A)) {
      var f = new Fixture();
      f.failClose = closeFd;
      var primary = new AssertionError("PRIMARY");
      assertSame(
          primary,
          assertThrows(
              AssertionError.class,
              () ->
                  f.subject()
                      .withAdmitted(
                          A,
                          P,
                          (a, p) -> {
                            throw primary;
                          })));
      assertEquals(List.of(P, A), f.closed);
    }
    var f = new Fixture();
    f.failClose = A;
    var fatal = new AssertionError(FIXTURE_PRIVATE_D45CA6F9);
    f.unknown = fatal;
    assertSame(
        fatal,
        assertThrows(
            AssertionError.class,
            () ->
                f.subject()
                    .withAdmitted(
                        A,
                        P,
                        (a, p) -> {
                          throw new IOException(FIXTURE_PRIVATE_D45CA6F9);
                        })));
    assertEquals(List.of(P, A), f.closed);
    var ordinary = new Fixture();
    ordinary.failClose = A;
    assertThrows(
        StorageIoException.class,
        () ->
            ordinary
                .subject()
                .withAdmitted(
                    A,
                    P,
                    (a, p) -> {
                      a.close();
                      return 1;
                    }));
    assertEquals(List.of(P, A), ordinary.closed);
  }

  @Test
  void childfd007ConcurrentReadyAndOuterCleanupConsumeAExactlyOnce() throws Exception {
    var f = new Fixture();
    var subject = f.subject();
    var executor = Executors.newFixedThreadPool(8);
    try {
      assertEquals(
          (Object) 1,
          subject.withAdmitted(
              A,
              P,
              (lease, bytes) -> {
                var jobs = new ArrayList<Callable<Void>>();
                for (int i = 0; i < 32; i++)
                  jobs.add(
                      () -> {
                        lease.close();
                        return null;
                      });
                try {
                  for (var future : executor.invokeAll(jobs)) future.get();
                } catch (InterruptedException e) {
                  Thread.currentThread().interrupt();
                  throw new IOException();
                } catch (ExecutionException e) {
                  throw new IOException();
                }
                return 1;
              }));
    } finally {
      executor.shutdownNow();
    }
    assertEquals(List.of(P, A), f.closed);
  }

  @Test
  void childfd008NativeFactoryBindingsAndOrdinaryUidCannotForgeRootMetadata() throws Exception {
    var symbols = Linker.nativeLinker().defaultLookup();
    for (String os : List.of("Windows", "linux"))
      assertThrows(
          IllegalStateException.class,
          () -> LinuxStartupAdmission.create(os, FIXTURE_AMD64_58D0BD71, symbols));
    assertThrows(
        IllegalStateException.class,
        () -> LinuxStartupAdmission.create(FIXTURE_LINUX_1CA133AF, "x86", symbols));
    assertThrows(
        IllegalStateException.class,
        () ->
            LinuxStartupAdmission.create(
                FIXTURE_LINUX_1CA133AF, FIXTURE_AMD64_58D0BD71, name -> Optional.empty()));
    assertThrows(
        IllegalStateException.class,
        () ->
            LinuxStartupAdmission.create(
                FIXTURE_LINUX_1CA133AF,
                FIXTURE_AMD64_58D0BD71,
                name -> name.equals("close") ? Optional.empty() : symbols.find(name)));
    assertThrows(
        NullPointerException.class,
        () -> LinuxStartupAdmission.create(null, FIXTURE_AMD64_58D0BD71, symbols));
    assertThrows(
        NullPointerException.class,
        () -> LinuxStartupAdmission.create(FIXTURE_LINUX_1CA133AF, null, symbols));
    assertThrows(
        NullPointerException.class,
        () -> LinuxStartupAdmission.create(FIXTURE_LINUX_1CA133AF, FIXTURE_AMD64_58D0BD71, null));
    var reader = LinuxSealedProof.create();
    var nativeIo = new LinuxStartupAdmission.NativeIo((fd, cmd, arg) -> 3, fd -> 4, reader);
    assertEquals(3, nativeIo.fcntl(128, 1, 0));
    assertEquals(4, nativeIo.close(128));
    assertThrows(
        NullPointerException.class,
        () -> new LinuxStartupAdmission.NativeIo(null, fd -> 0, reader));
    assertThrows(
        NullPointerException.class,
        () -> new LinuxStartupAdmission.NativeIo((f, c, a) -> 0, null, reader));
    assertThrows(
        NullPointerException.class,
        () -> new LinuxStartupAdmission.NativeIo((f, c, a) -> 0, fd -> 0, null));
    reader.withProof(
        "PUBLIC".getBytes(StandardCharsets.US_ASCII),
        fd -> {
          assertArrayEquals("PUBLIC".getBytes(StandardCharsets.US_ASCII), nativeIo.proof(fd));
          assertNotEquals(0, nativeIo.attributes(fd).get(FIXTURE_UID_0C18F38C));
          return 1;
        });
    assertThrows(IOException.class, () -> nativeIo.attributes(65535));
    assertThrows(
        StorageIoException.class,
        () -> LinuxStartupAdmission.create().withAdmitted(65534, 65535, (a, p) -> 1));
  }
}
