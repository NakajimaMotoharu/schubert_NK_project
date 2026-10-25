package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.platform.CleanupWorkerRequest;
import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** SS341/343 SSC125 BUG370/YKT291 EXPARENT002/005; claims are not actual native authorization. */
final class ExpiryOwnerTest {
  private static final UUID RUN = UUID.fromString("38100000-2222-4333-8444-555555555555");
  private static final UUID ACTIVATION = UUID.fromString("38100000-6666-4777-8888-999999999999");
  private static final UUID BOOT = UUID.fromString("38100000-3333-4333-8444-555555555555");
  private static final UUID EPOCH = UUID.fromString("38100000-4444-4333-8444-555555555555");
  private static final UUID OTHER = UUID.fromString("38100000-5555-4333-8444-555555555555");
  private static final Instant CUTOFF = Instant.parse("2026-09-30T00:00:00Z");
  private static final MaintenanceOwnerFrame.Parent MORNING =
      new MaintenanceOwnerFrame.Parent("1".repeat(32), 123, 456);

  private static MaintenanceOwnerFrame owner(
      UUID boot,
      UUID run,
      UUID activation,
      Instant cutoff,
      UUID epoch,
      Optional<MaintenanceOwnerFrame.Parent> cleanup) {
    return new MaintenanceOwnerFrame(
        boot, run, activation, cutoff, epoch, MORNING, cleanup, 999999999);
  }

  private static CleanupWorkerRequest.Expiry request() {
    return new CleanupWorkerRequest.Expiry(
        RUN,
        ACTIVATION,
        CUTOFF,
        BOOT,
        EPOCH,
        "2".repeat(32),
        42,
        1,
        Instant.parse("2026-09-30T00:00:01Z"),
        false);
  }

  @Test
  void exactMorningClaimsRejectEveryIndependentCorrelationMismatch() throws Exception {
    var request = request();
    CleanupExpiryExecution.requireOwner(
        owner(BOOT, RUN, ACTIVATION, CUTOFF, EPOCH, Optional.empty()), request);
    for (var changed :
        List.of(
            owner(OTHER, RUN, ACTIVATION, CUTOFF, EPOCH, Optional.empty()),
            owner(BOOT, OTHER, ACTIVATION, CUTOFF, EPOCH, Optional.empty()),
            owner(BOOT, RUN, OTHER, CUTOFF, EPOCH, Optional.empty()),
            owner(BOOT, RUN, ACTIVATION, CUTOFF.plusNanos(1000), EPOCH, Optional.empty()),
            owner(BOOT, RUN, ACTIVATION, CUTOFF, OTHER, Optional.empty()),
            owner(
                BOOT,
                RUN,
                ACTIVATION,
                CUTOFF,
                EPOCH,
                Optional.of(new MaintenanceOwnerFrame.Parent("3".repeat(32), 124, 457)))))
      assertThrows(IOException.class, () -> CleanupExpiryExecution.requireOwner(changed, request));
    assertThrows(
        NullPointerException.class, () -> CleanupExpiryExecution.requireOwner(null, request));
    assertThrows(
        NullPointerException.class,
        () ->
            CleanupExpiryExecution.requireOwner(
                owner(BOOT, RUN, ACTIVATION, CUTOFF, EPOCH, Optional.empty()), null));
  }

  @Test
  void networkBudgetRoundsDownAndUnitRequiresActualPrivateOwner() throws Exception {
    assertEquals(5000, CleanupExpiryExecution.mqTimeoutMillis(() -> 30_000_000_000L));
    assertEquals(1000, CleanupExpiryExecution.mqTimeoutMillis(() -> 1_999_999_999L));
    assertThrows(
        IOException.class, () -> CleanupExpiryExecution.mqTimeoutMillis(() -> 999_999_999L));
    assertThrows(IOException.class, () -> CleanupExpiryExecution.mqTimeoutMillis(() -> 0));
    assertThrows(NullPointerException.class, () -> CleanupExpiryExecution.mqTimeoutMillis(null));
    String unit =
        Files.readString(
            Path.of(
                System.getProperty("nk.pt.repository"),
                "src/deployment/systemd/schubert-nk-expiry-cleanup.service.template"));
    assertEquals(
        1,
        unit.lines()
            .filter(
                "LoadCredential=maintenance-owner:/run/schubert-nk/expiry-request/maintenance-owner"
                    ::equals)
            .count());
    assertTrue(unit.contains("KillMode=control-group\nSendSIGKILL=no\n"));
    assertTrue(unit.contains("RemainAfterExit=yes\n"));
  }
}
