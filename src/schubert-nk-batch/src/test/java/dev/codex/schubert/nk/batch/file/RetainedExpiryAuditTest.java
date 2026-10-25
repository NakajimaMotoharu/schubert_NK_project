package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.batch.platform.CleanupWorkerRequest;
import dev.codex.schubert.nk.batch.repository.ExpiryAuditRepository;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.time.Instant;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/**
 * PT-OPS-EXPIRY-AUDIT-SSC302001..014; DAT009/OPS009, UI251, SS331/341/343. Literal data-only
 * counterexamples do not claim an invalid row passes the DDL or DAO.
 */
final class RetainedExpiryAuditTest {
  private static final UUID RUN = UUID.fromString("38100000-2222-4333-8444-555555555555");
  private static final Instant CUTOFF = Instant.parse("2026-09-30T00:00:00Z");
  private static final Instant START = Instant.parse("2026-09-30T00:00:01Z");
  private static final Instant END = Instant.parse("2026-09-30T00:00:02Z");
  private static final Instant EXPIRY = Instant.parse("2026-09-23T00:00:00Z");

  private static CleanupWorkerRequest.Expiry.PriorExpiry reference() {
    return new CleanupWorkerRequest.Expiry.PriorExpiry(RUN, CUTOFF, 42, 1, START, END);
  }

  private static ExpiryAuditRepository.Snapshot audit(String fault) {
    return new ExpiryAuditRepository.Snapshot(
        fault.equals("STATUS") ? "WARNING" : "SUCCESS",
        fault.equals("CUTOFF") ? EXPIRY.plusSeconds(1) : EXPIRY,
        fault.equals("BEFORE_NULL") ? null : fault.equals("ORDER") ? 0L : 3L,
        fault.equals("AFTER_NULL") ? null : fault.equals("DIFFERENCE") ? 0L : 1L,
        fault.equals("TARGET") ? 3 : 2,
        2,
        fault.equals("FAILURE") ? 1 : 0,
        200,
        fault.equals("ENDED") ? END.plusSeconds(1) : END,
        fault.equals("CODE") ? "UNTRUSTED" : null,
        fault.equals("SUMMARY") ? "UNTRUSTED" : null);
  }

  private static void rejected(ExpiryAuditRepository.Snapshot value) {
    var failure =
        assertThrows(
            StorageIoException.class,
            () -> CleanupExpiryExecution.verifyPriorAudit(reference(), value));
    assertEquals(StorageIoException.Reason.UNAVAILABLE, failure.reason());
    assertEquals("transfer storage operation failed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  @Test
  void ssc302001ExactAuditAndIndependentArithmeticBoundaries() throws Exception {
    CleanupExpiryExecution.verifyPriorAudit(reference(), audit("VALID"));
    for (long count : new long[] {0, Long.MAX_VALUE}) {
      var value =
          new ExpiryAuditRepository.Snapshot(
              "SUCCESS", EXPIRY, count, 0L, count, count, 0, 0, END, null, null);
      assertDoesNotThrow(() -> CleanupExpiryExecution.verifyPriorAudit(reference(), value));
    }
  }

  @Test
  void ssc302002StatusMustBeSuccess() {
    rejected(audit("STATUS"));
  }

  @Test
  void ssc302003EndedMustMatchRetainedReference() {
    rejected(audit("ENDED"));
  }

  @Test
  void ssc302004ExactSevenDayCutoffMustMatch() {
    rejected(audit("CUTOFF"));
  }

  @Test
  void ssc302005BeforeNullIsNotZero() {
    rejected(audit("BEFORE_NULL"));
  }

  @Test
  void ssc302006AfterNullIsNotZero() {
    rejected(audit("AFTER_NULL"));
  }

  @Test
  void ssc302007BeforeCannotBeBelowAfter() {
    rejected(audit("ORDER"));
  }

  @Test
  void ssc302008BeforeMinusAfterMustEqualSuccess() {
    rejected(audit("DIFFERENCE"));
  }

  @Test
  void ssc302009TargetMustEqualSuccess() {
    rejected(audit("TARGET"));
  }

  @Test
  void ssc302010FailureCountMustBeZero() {
    rejected(audit("FAILURE"));
  }

  @Test
  void ssc302011SuccessfulAuditCannotCarryErrorCode() {
    rejected(audit("CODE"));
  }

  @Test
  void ssc302012SuccessfulAuditCannotCarryErrorSummary() {
    rejected(audit("SUMMARY"));
  }

  @Test
  void ssc302013NullReferenceAndAuditAreContractViolations() {
    assertThrows(
        NullPointerException.class,
        () -> CleanupExpiryExecution.verifyPriorAudit(null, audit("VALID")));
    assertThrows(
        NullPointerException.class,
        () -> CleanupExpiryExecution.verifyPriorAudit(reference(), null));
  }

  private static CleanupWorkerRequest.Expiry request(boolean skipped) {
    return new CleanupWorkerRequest.Expiry(
        RUN,
        UUID.fromString("38100000-6666-4777-8888-999999999999"),
        CUTOFF,
        UUID.fromString("38100000-3333-4333-8444-555555555555"),
        UUID.fromString("38100000-4444-4333-8444-555555555555"),
        "1".repeat(32),
        43,
        2,
        Instant.parse("2026-09-30T00:00:03Z"),
        skipped,
        skipped ? Optional.of(reference()) : Optional.empty());
  }

  @Test
  void ssc302014NonSkipAndNonzeroSelectedRejectBeforeAnyJdbc() {
    var calls = new AtomicInteger();
    var connection =
        (Connection)
            Proxy.newProxyInstance(
                Connection.class.getClassLoader(),
                new Class<?>[] {Connection.class},
                (proxy, method, arguments) -> {
                  calls.incrementAndGet();
                  throw new AssertionError("JDBC before skip/selection validation");
                });
    assertThrows(
        StorageIoException.class,
        () -> CleanupExpiryExecution.verifyPriorExpiry(connection, request(false), 0));
    assertThrows(
        StorageIoException.class,
        () -> CleanupExpiryExecution.verifyPriorExpiry(connection, request(true), 1));
    assertThrows(
        NullPointerException.class,
        () -> CleanupExpiryExecution.verifyPriorExpiry(null, request(true), 0));
    assertThrows(
        NullPointerException.class,
        () -> CleanupExpiryExecution.verifyPriorExpiry(connection, null, 0));
    assertEquals(0, calls.get());
  }
}
