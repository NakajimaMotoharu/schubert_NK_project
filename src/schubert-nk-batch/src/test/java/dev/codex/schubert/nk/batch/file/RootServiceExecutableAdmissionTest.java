package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.Path;
import java.nio.file.attribute.FileTime;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import org.junit.jupiter.api.Test;

/** ROOTELF001..006: independent public ELF literal/hash/typed metadata, no native authority. */
final class RootServiceExecutableAdmissionTest {
  private static final String FIXTURE_SIZE_EB1E91E4 = "size";
  private static final String FIXTURE_UID_0C18F38C = "uid";
  private static final String FIXTURE_GID_0ACDD642 = "gid";
  private static final String FIXTURE_MODE_B6D5C2C3 = "mode";
  private static final String FIXTURE_NLINK_3DDD828B = "nlink";

  @Test
  void exactIndependentAlternativesTargetsAndNoRelativeOrExtraChain() throws Exception {
    for (String literal : List.of("/etc/alternatives/java", "/opt/jdk-25.0.4/bin/java")) {
      Path expected = Path.of(literal);
      RootServiceExecutableAdmission.requireSelectorTarget(expected, Path.of(literal));
      for (String wrong :
          List.of(
              "java",
              "../java",
              "/etc/alternatives/other",
              "/opt/other/bin/java",
              literal + ".part")) {
        assertThrows(
            IOException.class,
            () -> RootServiceExecutableAdmission.requireSelectorTarget(expected, Path.of(wrong)));
      }
      assertThrows(
          NullPointerException.class,
          () -> RootServiceExecutableAdmission.requireSelectorTarget(expected, null));
    }
    assertThrows(
        NullPointerException.class,
        () ->
            RootServiceExecutableAdmission.requireSelectorTarget(
                null, Path.of("/etc/alternatives/java")));
  }

  static byte[] elf() {
    byte[] bytes = new byte[64];
    byte[] prefix = {127, 69, 76, 70, 2, 1, 1};
    System.arraycopy(prefix, 0, bytes, 0, prefix.length);
    bytes[18] = 62;
    return bytes;
  }

  static final class Input implements SeekableByteChannel {
    final byte[] bytes;
    String fault = "";
    int position;
    int chunk = 7;
    final List<byte[]> borrowed = new ArrayList<>();

    Input(byte[] bytes) {
      this.bytes = bytes;
    }

    public int read(ByteBuffer target) throws IOException {
      borrowed.add(target.array());
      if (fault.equals("io")) throw new IOException("PUBLIC_FIXED_FAILURE");
      if (fault.equals("zero")) return 0;
      if (fault.equals("negative")) return -2;
      if (fault.equals("count")) return 1;
      if (position == bytes.length) {
        if (fault.equals("eof-position")) target.put((byte) 1);
        return -1;
      }
      int count = Math.min(Math.min(chunk, target.remaining()), bytes.length - position);
      target.put(bytes, position, count);
      position += count;
      return count;
    }

    public long size() {
      return bytes.length + (fault.equals(FIXTURE_SIZE_EB1E91E4) ? 1 : 0);
    }

    public boolean isOpen() {
      return true;
    }

    public void close() {}

    public int write(ByteBuffer b) {
      throw new UnsupportedOperationException();
    }

    public long position() {
      return position;
    }

    public SeekableByteChannel position(long p) {
      throw new UnsupportedOperationException();
    }

    public SeekableByteChannel truncate(long n) {
      throw new UnsupportedOperationException();
    }

    void wiped() {
      for (byte[] buffer : borrowed) assertArrayEquals(new byte[buffer.length], buffer);
    }
  }

  @Test
  void wholeGoldenChunkedHashAndEveryHeaderMismatch() throws Exception {
    var normal = new Input(elf());
    assertEquals(
        "caa6f4f58ad3ed35afa011abfdb3ef06a7799b5545082b32685f75cc9c454fe8",
        RootServiceExecutableAdmission.digest(normal));
    assertEquals(64, normal.position);
    normal.wiped();
    for (int offset : new int[] {0, 1, 2, 3, 4, 5, 6, 18, 19}) {
      byte[] bytes = elf();
      bytes[offset]++;
      var input = new Input(bytes);
      assertThrows(IOException.class, () -> RootServiceExecutableAdmission.digest(input));
      input.wiped();
    }
    for (int length : new int[] {0, 1, 63, 8 * 1024 * 1024 + 1}) {
      byte[] bytes = Arrays.copyOf(elf(), length);
      var input = new Input(bytes);
      input.chunk = 8192;
      assertThrows(IOException.class, () -> RootServiceExecutableAdmission.digest(input));
      input.wiped();
    }
    assertThrows(NullPointerException.class, () -> RootServiceExecutableAdmission.digest(null));
  }

  @Test
  void boundedReadEofProgressAndIoCannotBecomeAHash() {
    for (String fault :
        List.of("zero", "negative", "count", "eof-position", FIXTURE_SIZE_EB1E91E4, "io")) {
      var input = new Input(elf());
      input.fault = fault;
      assertThrows(IOException.class, () -> RootServiceExecutableAdmission.digest(input), fault);
      input.wiped();
    }
  }

  static Map<String, Object> metadata(int mode) {
    var a = new HashMap<String, Object>();
    a.put(FIXTURE_UID_0C18F38C, 0);
    a.put(FIXTURE_GID_0ACDD642, 0);
    a.put(FIXTURE_MODE_B6D5C2C3, mode);
    a.put(FIXTURE_NLINK_3DDD828B, mode == 040755 ? 2 : 1);
    a.put("dev", 3L);
    a.put("ino", 4L);
    a.put(FIXTURE_SIZE_EB1E91E4, 64L);
    a.put("lastModifiedTime", FileTime.fromMillis(1));
    a.put("ctime", FileTime.fromMillis(2));
    return a;
  }

  static final Path HELD = Path.of("/proc/self/fd/7");

  static InodeSecurityCalls security(byte[] acl) {
    return new InodeSecurityCalls() {
      public byte[] accessAcl(Path p, int maximum) {
        assertEquals(HELD, p);
        assertEquals(44, maximum);
        return acl;
      }

      public boolean readOnlyFilesystem(Path p) {
        throw new AssertionError("not an inode fact");
      }

      public long effectiveUid() {
        return 0;
      }
    };
  }

  @Test
  void typedOwnerModeLinkSizeTimeAndAclContract() throws Exception {
    for (int mode : new int[] {040755, 0100755, 0120777}) {
      var a = metadata(mode);
      assertEquals(
          a,
          RootServiceExecutableAdmission.checkedAttributes(HELD, mode, a, security(new byte[0])));
      for (String key : a.keySet()) {
        var missing = new HashMap<>(a);
        missing.remove(key);
        assertThrows(
            IOException.class,
            () ->
                RootServiceExecutableAdmission.checkedAttributes(
                    HELD, mode, missing, security(new byte[0])),
            key);
        var wrong = new HashMap<>(a);
        wrong.put(key, "UNKNOWN");
        assertThrows(
            IOException.class,
            () ->
                RootServiceExecutableAdmission.checkedAttributes(
                    HELD, mode, wrong, security(new byte[0])),
            key);
      }
    }
    for (String key :
        List.of(
            FIXTURE_UID_0C18F38C,
            FIXTURE_GID_0ACDD642,
            FIXTURE_MODE_B6D5C2C3,
            FIXTURE_NLINK_3DDD828B,
            "dev",
            "ino",
            FIXTURE_SIZE_EB1E91E4)) {
      var a = metadata(0100755);
      // BUG1312: a numeric conditional promotes Integer/Long to boxed Long before put.
      Object invalid;
      Class<?> expectedType;
      if (Set.of(
              FIXTURE_UID_0C18F38C,
              FIXTURE_GID_0ACDD642,
              FIXTURE_MODE_B6D5C2C3,
              FIXTURE_NLINK_3DDD828B)
          .contains(key)) {
        invalid = Integer.valueOf(1);
        expectedType = Integer.class;
      } else {
        invalid = Long.valueOf(0);
        expectedType = Long.class;
      }
      a.put(key, invalid);
      if (key.equals(FIXTURE_NLINK_3DDD828B)) a.put(key, 2);
      assertEquals(expectedType, a.get(key).getClass(), key);
      assertThrows(
          IOException.class,
          () ->
              RootServiceExecutableAdmission.checkedAttributes(
                  HELD, 0100755, a, security(new byte[0])),
          key);
    }
    assertThrows(
        IOException.class,
        () ->
            RootServiceExecutableAdmission.checkedAttributes(
                HELD, 0100755, metadata(0100755), security(new byte[] {1})));
    assertThrows(
        NullPointerException.class,
        () ->
            RootServiceExecutableAdmission.checkedAttributes(
                HELD, 0100755, null, security(new byte[0])));
  }

  /** PT-ROOTELF-3678-002: Unix literals, not values computed by the subject. */
  @Test
  void typedValueBoundariesAreRejectedBeforeAclAndCorrectLimitsRemainAdmitted() throws Exception {
    for (int mode : new int[] {040755, 0100755, 0120777}) {
      for (var fault :
          Map.<String, Object>of(
                  FIXTURE_UID_0C18F38C,
                  1,
                  FIXTURE_GID_0ACDD642,
                  1,
                  FIXTURE_MODE_B6D5C2C3,
                  0100644,
                  "dev",
                  0L,
                  "ino",
                  0L,
                  FIXTURE_SIZE_EB1E91E4,
                  -1L)
              .entrySet()) {
        var a = metadata(mode);
        a.put(fault.getKey(), fault.getValue());
        Class<?> expectedType =
            Set.of(FIXTURE_UID_0C18F38C, FIXTURE_GID_0ACDD642, FIXTURE_MODE_B6D5C2C3)
                    .contains(fault.getKey())
                ? Integer.class
                : Long.class;
        assertEquals(expectedType, a.get(fault.getKey()).getClass(), fault.getKey());
        var calls = new java.util.concurrent.atomic.AtomicInteger();
        assertThrows(
            IOException.class,
            () ->
                RootServiceExecutableAdmission.checkedAttributes(
                    HELD, mode, a, countingSecurity(calls, null)),
            fault.getKey());
        assertEquals(0, calls.get(), fault.getKey());
      }
      var links = metadata(mode);
      links.put(FIXTURE_NLINK_3DDD828B, mode == 040755 ? 1 : 2);
      var calls = new java.util.concurrent.atomic.AtomicInteger();
      assertThrows(
          IOException.class,
          () ->
              RootServiceExecutableAdmission.checkedAttributes(
                  HELD, mode, links, countingSecurity(calls, null)));
      assertEquals(0, calls.get());
      for (long size : mode == 0100755 ? new long[] {1, 8_388_608} : new long[] {0, 8_388_609}) {
        var a = metadata(mode);
        a.put(FIXTURE_SIZE_EB1E91E4, size);
        if (mode == 040755) a.put(FIXTURE_NLINK_3DDD828B, Integer.MAX_VALUE);
        assertEquals(
            a,
            RootServiceExecutableAdmission.checkedAttributes(
                HELD, mode, a, countingSecurity(calls, null)));
      }
      assertEquals(mode == 0120777 ? 0 : 2, calls.get());
    }
    for (long size : new long[] {0, 8_388_609, Long.MAX_VALUE}) {
      var a = metadata(0100755);
      a.put(FIXTURE_SIZE_EB1E91E4, size);
      var calls = new java.util.concurrent.atomic.AtomicInteger();
      assertThrows(
          IOException.class,
          () ->
              RootServiceExecutableAdmission.checkedAttributes(
                  HELD, 0100755, a, countingSecurity(calls, null)));
      assertEquals(0, calls.get());
    }
  }

  /** PT-ROOTELF-3678-003: IO identity and null boundary cannot produce admission. */
  @Test
  void aclFailureIdentityAndRequiredBoundaryValuesCannotBeAccepted() {
    var calls = new java.util.concurrent.atomic.AtomicInteger();
    var failure = new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    assertSame(
        failure,
        assertThrows(
            IOException.class,
            () ->
                RootServiceExecutableAdmission.checkedAttributes(
                    HELD, 0100755, metadata(0100755), countingSecurity(calls, failure))));
    assertEquals(1, calls.get());
    assertThrows(
        NullPointerException.class,
        () ->
            RootServiceExecutableAdmission.checkedAttributes(
                null, 0100755, metadata(0100755), countingSecurity(calls, null)));
    assertThrows(
        NullPointerException.class,
        () ->
            RootServiceExecutableAdmission.checkedAttributes(
                HELD, 0100755, metadata(0100755), null));
    assertEquals(1, calls.get());
  }

  private static InodeSecurityCalls countingSecurity(
      java.util.concurrent.atomic.AtomicInteger calls,
      @org.jspecify.annotations.Nullable StorageIoException failure) {
    return new InodeSecurityCalls() {
      public byte[] accessAcl(Path path, int maximum) throws StorageIoException {
        assertEquals(HELD, path);
        assertEquals(44, maximum);
        calls.incrementAndGet();
        if (failure != null) throw failure;
        return new byte[0];
      }

      public boolean readOnlyFilesystem(Path path) {
        throw new AssertionError("not an executable inode fact");
      }

      public long effectiveUid() {
        throw new AssertionError("not used by the typed metadata boundary");
      }
    };
  }
}
