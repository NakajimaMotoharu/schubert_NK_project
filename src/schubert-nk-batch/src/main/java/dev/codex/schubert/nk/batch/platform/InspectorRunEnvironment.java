package dev.codex.schubert.nk.batch.platform;

import dev.codex.schubert.nk.batch.repository.BatchRun;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Canonical nonsecret run-file bytes only. NK-OPS-001; OPS-009; UI251; SS311/343§6.8;
 * SSC-049/PG-D-149; PT-OPS-ENV-001..004. Caller supplies the authoritative run and owns all
 * root/inode/bounded-read/lock/atomic-publication/backup/child-lifecycle checks. No clock or file
 * IO.
 */
@NullMarked
public final class InspectorRunEnvironment {
  private InspectorRunEnvironment() {}

  /** Fresh caller-owned ASCII bytes; no alternate run, timestamp rounding, quoting or expansion. */
  public static byte[] encode(BatchRun run) {
    Objects.requireNonNull(run, "run");
    return ("NK_INSPECTOR_RUN_ID=" + run.id() + "\nNK_INSPECTOR_CUTOFF=" + run.cutoff() + "\n")
        .getBytes(StandardCharsets.US_ASCII);
  }

  /** Exact nonsecret byte match, not proof of the observed file's provenance or continued state. */
  public static void requireMatches(BatchRun run, byte[] observed) {
    Objects.requireNonNull(observed, "observed bytes");
    if (!Arrays.equals(encode(run), observed))
      throw new IllegalArgumentException("inspector run environment mismatch");
  }
}
