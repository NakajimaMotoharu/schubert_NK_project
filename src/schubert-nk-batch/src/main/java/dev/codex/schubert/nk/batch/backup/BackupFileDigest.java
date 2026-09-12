package dev.codex.schubert.nk.batch.backup;

import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/** Claimed digest, not actual file verification. BAK001..008/UI251/SS341 6.4; PG165/BAT178..185. */
@NullMarked
public record BackupFileDigest(long size, String sha256) {
  public BackupFileDigest {
    Objects.requireNonNull(sha256, "digest");
    if (size <= 0 || !sha256.matches("[0-9a-f]{64}"))
      throw new IllegalArgumentException("invalid backup file claim");
  }

  @Override
  public String toString() {
    return "BackupFileDigest[claim=<redacted>]";
  }
}
