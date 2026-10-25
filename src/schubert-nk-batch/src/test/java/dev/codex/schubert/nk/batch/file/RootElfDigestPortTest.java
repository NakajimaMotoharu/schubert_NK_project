package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.SeekableByteChannel;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** PT-ROOTELF-SSC306-001..008: literal vectors and borrowed lifetime, no OS authority. */
final class RootElfDigestPortTest {
  private static final String GOLDEN =
      "caa6f4f58ad3ed35afa011abfdb3ef06a7799b5545082b32685f75cc9c454fe8";

  @Test
  void fixedDigestFactoryIsCalledOnceAndBorrowedChannelStaysOpen() throws Exception {
    var input = new Input(elf(64));
    var calls = new AtomicInteger();
    assertEquals(
        GOLDEN,
        RootServiceExecutableAdmission.digest(
            input,
            () -> {
              calls.incrementAndGet();
              return MessageDigest.getInstance("SHA-256");
            }));
    assertEquals(1, calls.get());
    assertEquals(64, input.position);
    assertTrue(input.reads > 0);
    input.assertBorrowedAndWiped();
  }

  @Test
  void unavailableAlgorithmIsRedactedAndDoesNotReadOrClose() {
    var input = new Input(elf(64));
    var calls = new AtomicInteger();
    IOException failure =
        assertThrows(
            IOException.class,
            () ->
                RootServiceExecutableAdmission.digest(
                    input,
                    () -> {
                      calls.incrementAndGet();
                      throw new NoSuchAlgorithmException("PUBLIC_UNAVAILABLE_MARKER");
                    }));
    assertEquals("root executable unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    assertEquals(1, calls.get());
    assertEquals(0, input.reads);
    input.assertBorrowedAndWiped();
  }

  @Test
  void unexpectedRuntimeAndErrorPreserveIdentityWithoutIo() {
    var input = new Input(elf(64));
    var runtime = new IllegalStateException("PUBLIC_RUNTIME_MARKER");
    var error = new AssertionError("PUBLIC_ERROR_MARKER");
    assertSame(
        runtime,
        assertThrows(
            IllegalStateException.class,
            () ->
                RootServiceExecutableAdmission.digest(
                    input,
                    () -> {
                      throw runtime;
                    })));
    assertSame(
        error,
        assertThrows(
            AssertionError.class,
            () ->
                RootServiceExecutableAdmission.digest(
                    input,
                    () -> {
                      throw error;
                    })));
    assertEquals(0, input.reads);
    input.assertBorrowedAndWiped();
  }

  @Test
  void nullContractsFailBeforeInputReads() {
    var input = new Input(elf(64));
    var calls = new AtomicInteger();
    assertThrows(
        NullPointerException.class,
        () ->
            RootServiceExecutableAdmission.digest(
                null,
                () -> {
                  calls.incrementAndGet();
                  return MessageDigest.getInstance("SHA-256");
                }));
    assertEquals(0, calls.get());
    assertThrows(
        NullPointerException.class, () -> RootServiceExecutableAdmission.digest(input, null));
    assertThrows(
        NullPointerException.class, () -> RootServiceExecutableAdmission.digest(input, () -> null));
    assertEquals(0, input.reads);
    input.assertBorrowedAndWiped();
  }

  @Test
  void oversizedReadReportIsRejectedAndBufferIsWiped() {
    var input = new Input(elf(8192));
    input.overreport = true;
    var failure =
        assertThrows(
            dev.codex.schubert.nk.storage.StorageIoException.class,
            () -> RootServiceExecutableAdmission.digest(input));
    assertEquals("transfer storage operation failed", failure.getMessage());
    assertEquals(
        dev.codex.schubert.nk.storage.StorageIoException.Reason.UNAVAILABLE, failure.reason());
    assertNull(failure.getCause());
    assertEquals(1, input.reads);
    assertEquals(8192, input.position);
    input.assertBorrowedAndWiped();
  }

  @Test
  void exactBufferBoundaryAndSplitHeaderKeepLiteralDigest() throws Exception {
    for (int chunk : new int[] {1, 7, 64, 8192}) {
      var input = new Input(elf(64));
      input.chunk = chunk;
      assertEquals(GOLDEN, RootServiceExecutableAdmission.digest(input));
      assertEquals(64, input.position);
      input.assertBorrowedAndWiped();
    }
  }

  @Test
  void readFailurePreservesIdentityAndWipesWithoutClose() {
    for (Throwable failure :
        List.of(
            new IOException("PUBLIC_IO_MARKER"),
            new IllegalStateException("PUBLIC_RUNTIME_MARKER"),
            new AssertionError("PUBLIC_ERROR_MARKER"))) {
      var input = new Input(elf(64));
      input.failure = failure;
      assertSame(
          failure,
          assertThrows(failure.getClass(), () -> RootServiceExecutableAdmission.digest(input)));
      assertEquals(1, input.reads);
      input.assertBorrowedAndWiped();
    }
  }

  @Test
  void exactMaximumElfHasIndependentFixedHash() throws Exception {
    var input = new Input(elf(8_388_608));
    input.chunk = 8192;
    assertEquals(
        "9c75e29938e99e5c154bf35e94a362e3e4de159e98ca02b25a032956e98aeca0",
        RootServiceExecutableAdmission.digest(input));
    assertEquals(8_388_608, input.position);
    input.assertBorrowedAndWiped();
  }

  private static byte[] elf(int length) {
    byte[] value = new byte[length];
    byte[] prefix = {127, 69, 76, 70, 2, 1, 1};
    System.arraycopy(prefix, 0, value, 0, prefix.length);
    value[18] = 62;
    return value;
  }

  private static final class Input implements SeekableByteChannel {
    private final byte[] value;
    private final List<byte[]> borrowed = new ArrayList<>();
    private int position;
    private int chunk = 7;
    private int reads;
    private int closes;
    private boolean overreport;
    private @org.jspecify.annotations.Nullable Throwable failure;

    Input(byte[] value) {
      this.value = value;
    }

    @Override
    public int read(ByteBuffer target) throws IOException {
      reads++;
      borrowed.add(target.array());
      target.put((byte) 23);
      target.clear();
      if (failure instanceof IOException io) throw io;
      if (failure instanceof RuntimeException runtime) throw runtime;
      if (failure instanceof Error error) throw error;
      if (position == value.length) return -1;
      int count = Math.min(Math.min(chunk, target.remaining()), value.length - position);
      if (overreport) count = target.remaining();
      target.put(value, position, count);
      position += count;
      return overreport ? 8193 : count;
    }

    void assertBorrowedAndWiped() {
      assertEquals(0, closes);
      assertTrue(isOpen());
      for (byte[] buffer : borrowed) assertArrayEquals(new byte[buffer.length], buffer);
    }

    @Override
    public long size() {
      return value.length;
    }

    @Override
    public long position() {
      return position;
    }

    @Override
    public boolean isOpen() {
      return closes == 0;
    }

    @Override
    public void close() {
      closes++;
    }

    @Override
    public int write(ByteBuffer value) {
      throw new UnsupportedOperationException();
    }

    @Override
    public SeekableByteChannel position(long value) {
      throw new UnsupportedOperationException();
    }

    @Override
    public SeekableByteChannel truncate(long value) {
      throw new UnsupportedOperationException();
    }
  }
}
