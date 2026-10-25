package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import java.time.Instant;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-OPS-DATA-511001 / SS343: synthetic immutable data only, no permit publication/authority. */
final class CurrentObservationValueTest {
  @Test
  void data511001WrapperRetainsValuesButNeverPrintsPublicBindings() {
    for (String digit : new String[] {"1", "2"}) {
      var boot = UUID.fromString(digit.repeat(8) + "-1111-4111-8111-111111111111");
      var epoch = UUID.fromString(digit.repeat(8) + "-2222-4222-8222-222222222222");
      var activation =
          new MaintenanceActivation(
              new BatchRun(
                  UUID.fromString("33333333-3333-4333-8333-333333333333"),
                  Instant.parse("2026-09-29T00:00:00Z")),
              UUID.fromString("44444444-4444-4444-8444-444444444444"));
      var current =
          new StartupPermitRecords.Epoch(
              StartupPermitRecords.State.ISSUED,
              boot,
              epoch,
              activation,
              Optional.of("a".repeat(64)));
      var permit =
          new StartupPermitRecords.Permit(
              boot,
              epoch,
              activation,
              digit.repeat(32),
              "a".repeat(64),
              "b".repeat(64),
              "c".repeat(64),
              "d".repeat(64),
              "e".repeat(64));
      var value = new RootCurrentPermitPreflight.Observed(current, permit);
      assertSame(current, value.current());
      assertSame(permit, value.permit());
      assertEquals("RootIssued[identity=<redacted>]", value.toString());
      assertThrows(
          NullPointerException.class, () -> new RootCurrentPermitPreflight.Observed(null, permit));
      assertThrows(
          NullPointerException.class, () -> new RootCurrentPermitPreflight.Observed(current, null));
    }
  }
}
