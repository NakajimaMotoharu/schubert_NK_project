package dev.codex.schubert.nk.api.maintenance;

import java.nio.ByteBuffer;
import java.nio.CharBuffer;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Owned UTF-8 database password; no file access or connection authority. NK-DAT-001;
 * DAT-009/OPS-009; UI212/241/251; SS343 6.6/352 11.1; QA-046/SSC-049/PG-D-142;
 * PT-DB-INBOX-193..196. Only owned buffers are explicitly erased, not JVM/driver internal copies.
 */
@NullMarked
public final class InspectorDbCredential implements AutoCloseable {
  private final java.util.concurrent.locks.ReentrantLock stateLock =
      new java.util.concurrent.locks.ReentrantLock();
  private final char[] password;
  private boolean closed;

  private InspectorDbCredential(char[] ownedPassword) {
    password = ownedPassword;
  }

  /** Exclusive input ownership transfers even on failure; strips one terminal LF or CRLF only. */
  public static InspectorDbCredential consume(byte[] input) {
    Objects.requireNonNull(input, "database credential input");
    // BUG-130/YKT-103: reject oversize input without proportional decode allocation.
    char[] decoded = new char[Math.min(input.length, 65536)];
    CharBuffer target = CharBuffer.wrap(decoded);
    try {
      if (input.length < 1 || input.length > 65536) throw invalid();
      int length = input.length;
      if (input[length - 1] == '\n') {
        length--;
        if (length > 0 && input[length - 1] == '\r') length--;
      }
      if (length == 0) throw invalid();
      var decoder = StandardCharsets.UTF_8.newDecoder();
      var outcome = decoder.decode(ByteBuffer.wrap(input, 0, length), target, true);
      if (outcome.isError()) throw invalid();
      // UTF-8 is stateless; this final flush has no pending character output.
      decoder.flush(target);
      int characters = target.position();
      if (decoded[0] == '\ufeff') throw invalid();
      for (int i = 0; i < characters; i++) {
        char value = decoded[i];
        if (value == 0 || value == '\r' || value == '\n') throw invalid();
      }
      return new InspectorDbCredential(Arrays.copyOf(decoded, characters));
    } finally {
      Arrays.fill(input, (byte) 0);
      Arrays.fill(decoded, '\0');
    }
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("inspector database credential format is invalid");
  }

  /** Caller owns this copy and must erase it; no immutable password String is retained here. */
  public char[] copyPassword() {
    stateLock.lock();
    try {
      if (closed) throw new IllegalStateException("inspector database credential is closed");
      return password.clone();
    } finally {
      stateLock.unlock();
    }
  }

  @Override
  public void close() {
    stateLock.lock();
    try {
      if (!closed) {
        Arrays.fill(password, '\0');
        closed = true;
      }
    } finally {
      stateLock.unlock();
    }
  }

  @Override
  public String toString() {
    return "InspectorDbCredential[REDACTED]";
  }
}
