package dev.codex.schubert.nk.batch.repository;

import java.time.LocalDate;
import java.time.ZoneId;
import java.util.Objects;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/**
 * An activation is not a new deletion cutoff. NK-BAT-001; OPS-009/UI251/SS331/341/343 6.13;
 * SSC-055/PG-D-156; PT-BAT-038..045. The file store, not this value, proves freshness/ownership.
 */
@NullMarked
public record MaintenanceActivation(BatchRun run, UUID id) {
  private static final ZoneId BUSINESS_ZONE = ZoneId.of("Asia/Tokyo");

  public MaintenanceActivation {
    Objects.requireNonNull(run, "fixed run");
    Objects.requireNonNull(id, "activation ID");
  }

  /** Same civil-date conversion as the existing PostgreSQL backup guard. */
  public LocalDate businessDate() {
    return run.cutoff().atZone(BUSINESS_ZONE).toLocalDate();
  }

  @Override
  public String toString() {
    return "MaintenanceActivation[identity/cutoff=<redacted>]";
  }
}
