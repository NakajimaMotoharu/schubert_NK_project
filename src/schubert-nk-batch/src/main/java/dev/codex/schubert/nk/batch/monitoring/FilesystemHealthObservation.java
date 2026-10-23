package dev.codex.schubert.nk.batch.monitoring;

import java.io.IOException;
import java.nio.file.FileStore;
import java.util.Objects;
import java.util.OptionalDouble;

/**
 * Borrowed filesystem health input, not a custom metric/exporter or path admission authority.
 * NK-OPS-001/P018-09; RD171/UI252/SS351; PG-D529/FSINPUT001..007/spec1582.
 */
public final class FilesystemHealthObservation {
  private final HealthUsageRatio ratio = new HealthUsageRatio();
  private final FileStore store;

  public FilesystemHealthObservation(FileStore store) {
    this.store = Objects.requireNonNull(store, "filesystem health source");
  }

  /** IOException/invalid provider statistics are UNKNOWN, never invented zero usage. */
  public OptionalDouble read() {
    final long total;
    final long usable;
    try {
      total = store.getTotalSpace();
      usable = store.getUsableSpace();
    } catch (IOException unavailable) {
      return OptionalDouble.empty();
    }
    if (total <= 0 || usable < 0 || usable > total) return OptionalDouble.empty();
    return ratio.fromUsed(total - usable, total);
  }
}
