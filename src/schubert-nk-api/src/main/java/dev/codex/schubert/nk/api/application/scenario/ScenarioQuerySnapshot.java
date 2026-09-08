package dev.codex.schubert.nk.api.application.scenario;

import dev.codex.schubert.nk.api.persistence.ScenarioDetailSnapshot;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import java.util.Objects;
import java.util.Optional;

/**
 * Pre-file immutable query outcome, not a committed response or authorization grant. NK-SCN-001;
 * FUN-003..005; UI234/237; SS323 §9.1/332 §4; PT-SCN-009-Q03/Q04.
 */
public sealed interface ScenarioQuerySnapshot {
  record Inline(TypedPayloadValues value) implements ScenarioQuerySnapshot {
    public Inline {
      Objects.requireNonNull(value, "value");
    }
  }

  /** Empty means missing file; caller maps 0104, never an empty successful detail. */
  record Detail(Optional<ScenarioDetailSnapshot> value) implements ScenarioQuerySnapshot {
    public Detail {
      Objects.requireNonNull(value, "value");
    }
  }
}
