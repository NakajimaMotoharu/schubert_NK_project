package dev.codex.schubert.nk.api.storage;

import dev.codex.schubert.nk.api.error.CapacityExceededException;

/**
 * Atomic transfer admission including in-flight files; initialize only from a verified root scan.
 * NK-SCN-001; RD FIL/PER; UI237 §capacity; SS333 §13/351; PG-D-057; PT-SCN-008-C01..C03.
 */
final class TransferCapacity {
  private static final long WARNING_BYTES = 3_500_000_000L;
  private static final long CRITICAL_BYTES = 4_500_000_000L;
  private static final long WARNING_FILES = 5_000;
  private static final long CRITICAL_FILES = 9_000;
  private static final long MAXIMUM_FILE_BYTES = 48_000_000;
  private final java.util.concurrent.locks.ReentrantLock stateLock =
      new java.util.concurrent.locks.ReentrantLock();
  private long retainedBytes;
  private long retainedFiles;
  private long reservedBytes;
  private long reservedFiles;

  enum Level {
    NORMAL,
    WARNING,
    CRITICAL
  }

  record Snapshot(long bytes, long files, Level level) {}

  TransferCapacity(long existingBytes, long existingFiles) {
    if (existingBytes < 0 || existingFiles < 0) {
      throw new IllegalArgumentException("negative transfer usage");
    }
    retainedBytes = existingBytes;
    retainedFiles = existingFiles;
  }

  Reservation reserve(long byteLength) {
    if (byteLength < 1 || byteLength > MAXIMUM_FILE_BYTES) {
      throw new IllegalArgumentException("invalid transfer reservation size");
    }
    stateLock.lock();
    try {
      if (retainedBytes + reservedBytes >= CRITICAL_BYTES
          || retainedFiles + reservedFiles >= CRITICAL_FILES) {
        throw new CapacityExceededException();
      }
      Reservation reservation = new Reservation(byteLength);
      // Admission bounds every addition below 4.548GB/9001, including in-flight reservations.
      reservedBytes += byteLength;
      reservedFiles++;
      return reservation;
    } finally {
      stateLock.unlock();
    }
  }

  Snapshot snapshot() {
    stateLock.lock();
    try {
      long bytes = retainedBytes + reservedBytes;
      long files = retainedFiles + reservedFiles;
      Level level;
      if (bytes >= CRITICAL_BYTES || files >= CRITICAL_FILES) {
        level = Level.CRITICAL;
      } else if (bytes >= WARNING_BYTES || files >= WARNING_FILES) {
        level = Level.WARNING;
      } else {
        level = Level.NORMAL;
      }
      return new Snapshot(bytes, files, level);
    } finally {
      stateLock.unlock();
    }
  }

  /**
   * Operation-local reservation. Retain ready/undeleted-part bytes; close releases only unused
   * space.
   */
  final class Reservation implements AutoCloseable {
    private final long bytes;
    private boolean active = true;

    private Reservation(long bytes) {
      this.bytes = bytes;
    }

    void retain() {
      stateLock.lock();
      try {
        if (!active) throw new IllegalStateException("transfer reservation is no longer active");
        retainedBytes += bytes;
        retainedFiles++;
        reservedBytes -= bytes;
        reservedFiles--;
        active = false;
      } finally {
        stateLock.unlock();
      }
    }

    @Override
    public void close() {
      stateLock.lock();
      try {
        if (active) {
          reservedBytes -= bytes;
          reservedFiles--;
          active = false;
        }
      } finally {
        stateLock.unlock();
      }
    }
  }
}
