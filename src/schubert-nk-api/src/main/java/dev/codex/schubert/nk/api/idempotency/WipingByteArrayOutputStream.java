package dev.codex.schubert.nk.api.idempotency;

import java.io.ByteArrayOutputStream;
import java.util.Arrays;
import java.util.Objects;

/**
 * Owned, bounded temporary secret bytes; copies returned to callers retain caller ownership.
 * NK-MSG-002; DAT-009/MQ-006; UI241; SS324 §3/6/352; BUG-027/YKT-024; PT-IDEM-WIPE-001. Resizing
 * wipes the superseded array; reset/close wipe all current capacity, not just count.
 */
class WipingByteArrayOutputStream extends ByteArrayOutputStream {
  private static final int MAXIMUM = 1_050_000;

  WipingByteArrayOutputStream() {
    super(8192);
  }

  @Override
  public synchronized void write(int value) {
    reserve(1);
    buf[count] = (byte) value;
    count++;
  }

  @Override
  public synchronized void write(byte[] bytes, int offset, int length) {
    Objects.checkFromIndexSize(offset, length, bytes.length);
    reserve(length);
    System.arraycopy(bytes, offset, buf, count, length);
    count += length;
  }

  private void reserve(int length) {
    if (length > MAXIMUM - count) {
      throw new IllegalArgumentException("temporary secret buffer exceeds its bounded capacity");
    }
    int required = count + length;
    if (required > buf.length) {
      byte[] old = buf;
      buf = Arrays.copyOf(old, Math.min(MAXIMUM, Math.max(required, old.length * 2)));
      Arrays.fill(old, (byte) 0);
    }
  }

  @Override
  public synchronized void reset() {
    Arrays.fill(buf, (byte) 0);
    count = 0;
  }

  @Override
  public void close() {
    reset();
  }

  @Override
  public synchronized String toString() {
    return "WipingByteArrayOutputStream[<redacted>]";
  }
}
