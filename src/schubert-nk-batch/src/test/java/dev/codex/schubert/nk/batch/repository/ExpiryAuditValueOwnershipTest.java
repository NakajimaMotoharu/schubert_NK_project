package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** EXPPORT-P001, PT-F02-EXPIRY-GRAPH: immutable observation keys and owned release ordering. */
final class ExpiryAuditValueOwnershipTest {
  private static final Instant CUTOFF = Instant.parse("2026-11-05T00:00:00Z");
  private static final Instant EXPIRY_AT = Instant.parse("2026-10-29T00:00:00Z");
  private static final Instant ENDED = Instant.parse("2026-11-05T00:00:02Z");
  private static final BatchRun RUN = new BatchRun(new UUID(0, 4), CUTOFF);
  private static final BatchStepAttempt FIRST =
      new BatchStepAttempt(7, RUN, BatchStep.CLEAN_EXPIRY, 1, CUTOFF, false);
  private static final BatchStepAttempt SECOND =
      new BatchStepAttempt(8, RUN, BatchStep.CLEAN_EXPIRY, 2, CUTOFF, false);

  @Test
  void equalObservationsCoalesceWhileDifferentRetainedAttemptsRemainDistinct() {
    var stages = new HashSet<ExpiryAuditRepository.Stage>();
    stages.add(new ExpiryAuditRepository.Stage(EXPIRY_AT, 3, 2, 200));
    stages.add(new ExpiryAuditRepository.Stage(EXPIRY_AT, 3, 2, 200));
    stages.add(new ExpiryAuditRepository.Stage(EXPIRY_AT, 3, 2, 201));
    assertEquals(2, stages.size());

    var observations = new HashSet<ExpiryAuditRepository.Snapshot>();
    observations.add(success(ENDED));
    observations.add(success(ENDED));
    observations.add(success(ENDED.plusSeconds(1)));
    assertEquals(2, observations.size());

    var priors = new HashSet<ExpiryAuditRepository.Prior>();
    priors.add(new ExpiryAuditRepository.Prior(FIRST, success(ENDED)));
    priors.add(new ExpiryAuditRepository.Prior(FIRST, success(ENDED)));
    priors.add(new ExpiryAuditRepository.Prior(SECOND, success(ENDED)));
    assertEquals(2, priors.size());
  }

  @Test
  void retainedAuditRejectsWarningAndMissingEndButAdmitsExactObservationTime() {
    var warning =
        new ExpiryAuditRepository.Snapshot(
            "WARNING", EXPIRY_AT, 3L, 1L, 2, 2, 0, 200, ENDED, null, null);
    var missingEnd =
        new ExpiryAuditRepository.Snapshot(
            "SUCCESS", EXPIRY_AT, 3L, 1L, 2, 2, 0, 200, null, null, null);
    assertThrows(
        BatchRepositoryException.class,
        () -> ExpiryAuditRepository.verifySuccessfulAudit(warning, ENDED));
    assertThrows(
        BatchRepositoryException.class,
        () -> ExpiryAuditRepository.verifySuccessfulAudit(missingEnd, ENDED));
    assertDoesNotThrow(() -> ExpiryAuditRepository.verifySuccessfulAudit(success(ENDED), ENDED));
  }

  @Test
  void ownedReleaseAfterBodyFailureKeepsPrimaryAndOneSecondary() {
    var primary = new IOException("public body fixture");
    var secondary = new SQLException("public close fixture");
    var resource = new Object();
    var observed = new ArrayList<String>();
    var failure =
        assertThrows(
            IOException.class,
            () ->
                ExpiryAuditRepository.usingJdbc(
                    () -> {
                      observed.add("acquire");
                      return resource;
                    },
                    owned -> {
                      assertSame(resource, owned);
                      observed.add("release");
                      throw secondary;
                    },
                    owned -> {
                      assertSame(resource, owned);
                      observed.add("read");
                      throw primary;
                    }));
    assertSame(primary, failure);
    assertArrayEquals(new Throwable[] {secondary}, failure.getSuppressed());
    assertEquals(List.of("acquire", "read", "release"), observed);
  }

  private static ExpiryAuditRepository.Snapshot success(Instant end) {
    return new ExpiryAuditRepository.Snapshot(
        "SUCCESS", EXPIRY_AT, 3L, 1L, 2, 2, 0, 200, end, null, null);
  }
}
