package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import java.io.IOException;
import java.time.Instant;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** NK-OPS-001/OPS009/UI251/SS343/PG371; PT-OPS-RPERMIT001..006. */
final class RootCurrentPermitPreflightTest {
  private static final UUID BOOT = UUID.fromString("11111111-1111-4111-8111-111111111111");
  private static final String RELEASE = "a".repeat(64);

  @Test
  void rpermit001WebBootAndReleaseAgree() {
    assertDoesNotThrow(
        () ->
            RootCurrentPermitPreflight.verify(
                snapshot(RootStartupContext.Service.WEB), RELEASE, permit(RELEASE)));
  }

  @Test
  void rpermit002ApiHasSameFixedCorrelationWithoutWebAlias() {
    assertDoesNotThrow(
        () ->
            RootCurrentPermitPreflight.verify(
                snapshot(RootStartupContext.Service.API), RELEASE, permit(RELEASE)));
  }

  @Test
  void rpermit003OldBootOrReleaseCannotPass() {
    var wrongBoot =
        new RootStartupContext.Snapshot(
            RootStartupContext.Service.WEB,
            "22222222-2222-4222-8222-222222222222",
            "1".repeat(32),
            42,
            43,
            44,
            "/system.slice/schubert-nk-web.service");
    assertThrows(
        IOException.class,
        () -> RootCurrentPermitPreflight.verify(wrongBoot, RELEASE, permit(RELEASE)));
    assertThrows(
        IOException.class,
        () ->
            RootCurrentPermitPreflight.verify(
                snapshot(RootStartupContext.Service.WEB), RELEASE, permit("b".repeat(64))));
  }

  @Test
  void rpermit004OnlyServiceActorAndNonnullInputs() {
    for (var actor :
        new RootStartupContext.Service[] {
          RootStartupContext.Service.MORNING, RootStartupContext.Service.CLEANUP
        })
      assertThrows(
          IOException.class,
          () -> RootCurrentPermitPreflight.verify(snapshot(actor), RELEASE, permit(RELEASE)));
    assertThrows(
        NullPointerException.class,
        () -> RootCurrentPermitPreflight.verify(null, RELEASE, permit(RELEASE)));
    assertThrows(
        NullPointerException.class,
        () ->
            RootCurrentPermitPreflight.verify(
                snapshot(RootStartupContext.Service.API), null, permit(RELEASE)));
    assertThrows(
        NullPointerException.class,
        () ->
            RootCurrentPermitPreflight.verify(
                snapshot(RootStartupContext.Service.API), RELEASE, null));
    assertThrows(
        NullPointerException.class,
        () ->
            RootCurrentPermitPreflight.verifyNative(
                null, snapshot(RootStartupContext.Service.API), RELEASE));
  }

  @Test
  void rpermit005NoPermitIsNeverSubstitutedWithInvalidOrMissing() {
    assertThrows(
        NullPointerException.class,
        () ->
            RootCurrentPermitPreflight.verify(
                snapshot(RootStartupContext.Service.API), RELEASE, null));
    assertThrows(IllegalArgumentException.class, () -> permit("not-a-sha256"));
  }

  @Test
  void rpermit006RootEntryStillRejectsEvenIfSyntheticGateAgrees() {
    var calls = new AtomicInteger();
    assertEquals(
        30, RootServiceLauncher.run(new String[] {"WEB"}, ignored -> calls.incrementAndGet()));
    assertEquals(1, calls.get());
  }

  private static RootStartupContext.Snapshot snapshot(RootStartupContext.Service service) {
    return new RootStartupContext.Snapshot(
        service, BOOT.toString(), "1".repeat(32), 42, 43, 44, "/system.slice/" + service.unit());
  }

  private static StartupPermitRecords.Permit permit(String release) {
    var run =
        new BatchRun(
            UUID.fromString("33333333-3333-4333-8333-333333333333"),
            Instant.parse("2026-09-29T00:00:00Z"));
    var activation =
        new MaintenanceActivation(run, UUID.fromString("44444444-4444-4444-8444-444444444444"));
    return new StartupPermitRecords.Permit(
        BOOT,
        UUID.fromString("22222222-2222-4222-8222-222222222222"),
        activation,
        "5".repeat(32),
        release,
        "6".repeat(64),
        "7".repeat(64),
        "8".repeat(64),
        "9".repeat(64));
  }
}
