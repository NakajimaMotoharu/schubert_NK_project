package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.batch.platform.ExpiryReceiptFixture;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** NK-BAT-001 / DAT009 OPS009 / UI251 / SS331341343 / EXP-1749. Data is not ownership. */
final class MorningExpiryObservationInvariantTest {
  private static final BatchRun RUN =
      new BatchRun(
          UUID.fromString("17490000-0000-4000-8000-000000000001"),
          Instant.parse("2026-09-27T15:00:00Z"));
  private static final Instant START = Instant.parse("2026-09-28T02:00:00Z");
  private static final Instant END = Instant.parse("2026-09-28T02:00:03Z");
  private static final BatchStepResult SUCCESS =
      new BatchStepResult(
          BatchStepResult.Status.SUCCESS, 2, 2, 0, 200, BatchStepResult.Reason.NONE);
  private static final BatchStepResult SKIP =
      new BatchStepResult(
          BatchStepResult.Status.SKIPPED, 0, 0, 0, 0, BatchStepResult.Reason.ALREADY_SUCCESSFUL);

  private static BatchStepAttempt attempt(boolean skip) {
    return new BatchStepAttempt(1749001, RUN, BatchStep.CLEAN_EXPIRY, 1, START, skip);
  }

  private static ExpiryAuditRepository.Snapshot audit(
      String status, long target, long success, long failure, long bytes, Instant end) {
    return new ExpiryAuditRepository.Snapshot(
        status,
        Instant.parse("2026-09-05T15:00:00Z"),
        3L,
        1L,
        target,
        success,
        failure,
        bytes,
        end,
        null,
        null);
  }

  private static ExpiryAuditRepository.Snapshot audit() {
    return audit("SUCCESS", 2, 2, 0, 200, END);
  }

  private static MorningDatabaseSession.ExpiryBegins begins(boolean skip) {
    return new MorningDatabaseSession.ExpiryBegins(
        attempt(skip),
        skip
            ? Optional.of(new ExpiryAuditRepository.Prior(attempt(false), audit()))
            : Optional.empty());
  }

  @Test
  void expiry1749001FreshAndSkipCarryLiteralFieldsNotReceiptAuthority() throws Exception {
    var receipt = ExpiryReceiptFixture.receipt(0);
    var fresh =
        new MorningDatabaseSession.ExpiryObservation(begins(false), END, SUCCESS, audit(), receipt);
    assertEquals(END, fresh.ended());
    assertEquals(2, fresh.result().target());
    assertEquals(200, fresh.audit().estimatedBytes());
    assertSame(receipt, fresh.receipt());
    var skipped =
        new MorningDatabaseSession.ExpiryObservation(begins(true), START, SKIP, audit(), receipt);
    assertEquals(START, skipped.ended());
    assertEquals(BatchStepResult.Status.SKIPPED, skipped.result().status());
    assertEquals(END, skipped.audit().ended());
    assertEquals("ExpiryObservation[actual=<redacted>]", fresh.toString());
  }

  @Test
  void expiry1749002EveryFreshProjectionMismatchAndWrongReceiptTargetRejects() throws Exception {
    var receipt = ExpiryReceiptFixture.receipt(0);
    var begins = begins(false);
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new MorningDatabaseSession.ExpiryObservation(
                begins, START.minusSeconds(1), SUCCESS, audit(), receipt));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new MorningDatabaseSession.ExpiryObservation(
                begins, END, SUCCESS, audit(), ExpiryReceiptFixture.backupReceipt(0)));
    assertThrows(
        IllegalArgumentException.class,
        () -> new MorningDatabaseSession.ExpiryObservation(begins, END, SKIP, audit(), receipt));
    for (var bad :
        List.of(
            audit("SUCCESS", 2, 2, 0, 200, START),
            audit("WARNING", 2, 2, 0, 200, END),
            audit("SUCCESS", 3, 2, 0, 200, END),
            audit("SUCCESS", 2, 1, 0, 200, END),
            audit("SUCCESS", 2, 2, 1, 200, END),
            audit("SUCCESS", 2, 2, 0, 201, END))) {
      assertThrows(
          IllegalArgumentException.class,
          () -> new MorningDatabaseSession.ExpiryObservation(begins, END, SUCCESS, bad, receipt));
    }
  }

  @Test
  void expiry1749003EverySkipObservationBindingCounterexampleRejects() throws Exception {
    var begins = begins(true);
    var receipt = ExpiryReceiptFixture.receipt(0);
    assertThrows(
        IllegalArgumentException.class,
        () -> new MorningDatabaseSession.ExpiryObservation(begins, END, SKIP, audit(), receipt));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new MorningDatabaseSession.ExpiryObservation(begins, START, SUCCESS, audit(), receipt));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new MorningDatabaseSession.ExpiryObservation(
                begins, START, SKIP, audit("WARNING", 2, 2, 0, 200, END), receipt));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new MorningDatabaseSession.ExpiryObservation(
                begins, START, SKIP, audit(), ExpiryReceiptFixture.receipt(10)));
  }

  @Test
  void expiry1749004BeginRoleAndPresenceNullTimeContractsRejectBeforeIo() throws Exception {
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new MorningDatabaseSession.ExpiryBegins(
                new BatchStepAttempt(1749002, RUN, BatchStep.BACKUP_DB, 1, START, false),
                Optional.empty()));
    assertThrows(
        IllegalArgumentException.class,
        () -> new MorningDatabaseSession.ExpiryBegins(attempt(true), Optional.empty()));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new MorningDatabaseSession.ExpiryBegins(
                attempt(false),
                Optional.of(new ExpiryAuditRepository.Prior(attempt(false), audit()))));
    assertThrows(
        NullPointerException.class,
        () -> new MorningDatabaseSession.ExpiryBegins(null, Optional.empty()));
    assertThrows(
        NullPointerException.class,
        () -> new MorningDatabaseSession.ExpiryBegins(attempt(false), null));
    var receipt = ExpiryReceiptFixture.receipt(0);
    var begins = begins(false);
    assertThrows(
        NullPointerException.class,
        () -> new MorningDatabaseSession.ExpiryObservation(null, END, SUCCESS, audit(), receipt));
    assertThrows(
        NullPointerException.class,
        () ->
            new MorningDatabaseSession.ExpiryObservation(begins, null, SUCCESS, audit(), receipt));
    assertThrows(
        NullPointerException.class,
        () -> new MorningDatabaseSession.ExpiryObservation(begins, END, null, audit(), receipt));
    assertThrows(
        NullPointerException.class,
        () -> new MorningDatabaseSession.ExpiryObservation(begins, END, SUCCESS, null, receipt));
    assertThrows(
        NullPointerException.class,
        () -> new MorningDatabaseSession.ExpiryObservation(begins, END, SUCCESS, audit(), null));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new MorningDatabaseSession.ExpiryObservation(
                begins, END.plusNanos(1), SUCCESS, audit(), receipt));
  }
}
