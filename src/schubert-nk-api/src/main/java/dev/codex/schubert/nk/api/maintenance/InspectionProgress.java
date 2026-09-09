package dev.codex.schubert.nk.api.maintenance;

import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/**
 * Internal durable cursor/count projection. NK-DAT-001; DAT-009/MQ-008/OPS-009; UI212/241/251;
 * SS324 12.6/331 3.8/341 7.3; QA-046/SSC-049/PG-D-128; PT-DB-INBOX-081..088. Complete means END was
 * committed, not that all rows passed validation or the process gates passed.
 */
@NullMarked
public record InspectionProgress(
    InspectionRun run,
    Optional<UUID> cursor,
    long inspected,
    long deleted,
    long protectedRows,
    boolean complete) {
  public InspectionProgress {
    Objects.requireNonNull(run, "run");
    Objects.requireNonNull(cursor, "cursor");
    if (inspected < 0
        || deleted < 0
        || deleted > inspected
        || protectedRows < 0
        || protectedRows != inspected - deleted
        || ((inspected == 0) != cursor.isEmpty())) {
      throw new IllegalArgumentException("inspection progress is inconsistent");
    }
  }

  @Override
  public String toString() {
    return "InspectionProgress[inspected="
        + inspected
        + ", deleted="
        + deleted
        + ", protected="
        + protectedRows
        + ", complete="
        + complete
        + "]";
  }
}
