package dev.codex.schubert.nk.batch.repository;

import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;

/** File recovery state, not parent success. NK-BAT-001/OPS-009/UI251/SS343 6.15/PT-BAT-058..081. */
@NullMarked
public record MaintenanceRunState(
    MaintenanceActivation activation, Optional<MaintenanceCompletion> completion) {
  public MaintenanceRunState {
    Objects.requireNonNull(activation, "activation");
    Objects.requireNonNull(completion, "optional completion");
    if (completion.isPresent() && !completion.orElseThrow().activation().equals(activation))
      throw new IllegalArgumentException("maintenance completion identity differs");
  }

  @Override
  public String toString() {
    return "MaintenanceRunState[redacted]";
  }
}
