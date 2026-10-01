package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.storage.*;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.Path;
import java.nio.file.attribute.FileTime;
import java.util.*;
import org.junit.jupiter.api.Test;

/** ROOTELF001..006: independent public ELF literal/hash/typed metadata, no native authority. */
final class RootServiceExecutableAdmissionTest {
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
      return bytes.length + (fault.equals("size") ? 1 : 0);
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
    for (String fault : List.of("zero", "negative", "count", "eof-position", "size", "io")) {
      var input = new Input(elf());
      input.fault = fault;
      assertThrows(IOException.class, () -> RootServiceExecutableAdmission.digest(input), fault);
      input.wiped();
    }
  }

  static Map<String, Object> metadata(int mode) {
    var a = new HashMap<String, Object>();
    a.put("uid", 0);
    a.put("gid", 0);
    a.put("mode", mode);
    a.put("nlink", mode == 040755 ? 2 : 1);
    a.put("dev", 3L);
    a.put("ino", 4L);
    a.put("size", 64L);
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
    for (String key : List.of("uid", "gid", "mode", "nlink", "dev", "ino", "size")) {
      var a = metadata(0100755);
      a.put(
          key,
          Set.of("uid", "gid", "mode", "nlink").contains(key)
              ? Integer.valueOf(1)
              : Long.valueOf(0));
      if (key.equals("nlink")) a.put(key, 2);
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
}
