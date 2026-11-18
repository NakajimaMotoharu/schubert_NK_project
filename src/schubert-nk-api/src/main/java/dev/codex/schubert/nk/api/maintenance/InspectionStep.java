package dev.codex.schubert.nk.api.maintenance;

import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/** Internal cursor only; external diagnostics aggregate outcomes, never IDs. SS341; PT033..040. */
@NullMarked
public record InspectionStep(Outcome outcome, Optional<UUID> cursor) {
  public enum Outcome {
    DELETED,
    PROTECTED,
    END
  }

  public InspectionStep {
    Objects.requireNonNull(outcome, "outcome");
    Objects.requireNonNull(cursor, "cursor");
    if ((outcome == Outcome.END) != cursor.isEmpty()) {
      throw new IllegalArgumentException("inspection outcome and cursor disagree");
    }
  }

  @Override
  public String toString() {
    return "InspectionStep[<redacted>]";
  }
}
