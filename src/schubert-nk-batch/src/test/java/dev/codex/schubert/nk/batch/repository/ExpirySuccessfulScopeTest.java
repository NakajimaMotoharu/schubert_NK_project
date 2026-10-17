package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.*;

import java.io.IOException;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicInteger;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** NK-BAT-001/P017-11; SS331/341/343/SSC304; PT-EXP-4956-001..016. */
final class ExpirySuccessfulScopeTest {
  private static final Instant OBSERVED = Instant.parse("2026-10-17T00:00:02Z");

  private static ExpiryAuditRepository.Snapshot audit(
      String status, @Nullable Instant end, @Nullable String code, @Nullable String summary) {
    return new ExpiryAuditRepository.Snapshot(
        status, Instant.parse("2026-10-10T00:00:00Z"), 3L, 1L, 2, 2, 0, 200, end, code, summary);
  }

  @Test
  void exp4956001LiteralSuccessfulBoundaryAndEarlierEndAreAccepted() {
    for (Instant end : List.of(OBSERVED, OBSERVED.minusNanos(1))) {
      assertDoesNotThrow(
          () ->
              ExpiryAuditRepository.verifySuccessfulAudit(
                  audit("SUCCESS", end, null, null), OBSERVED));
    }
  }

  @Test
  void exp4956002UnknownAndNonSuccessStatusesAreRejected() {
    for (String status : List.of("WARNING", "FAILED", "RUNNING", "UNKNOWN", "", "success")) {
      denied(audit(status, OBSERVED, null, null));
    }
  }

  @Test
  void exp4956003AbsentEndIsRejectedIndependentlyOfEarlierDbValidation() {
    denied(audit("SUCCESS", null, null, null));
  }

  @Test
  void exp4956004OneNanosecondFutureIsRejected() {
    denied(audit("SUCCESS", OBSERVED.plusNanos(1), null, null));
  }

  @Test
  void exp4956005EvenEmptyErrorCodeIsRejected() {
    for (String code : List.of("", "INDEPENDENT_CODE"))
      denied(audit("SUCCESS", OBSERVED, code, null));
  }

  @Test
  void exp4956006EvenEmptyErrorSummaryIsRejected() {
    for (String text : List.of("", "INDEPENDENT_SUMMARY"))
      denied(audit("SUCCESS", OBSERVED, null, text));
  }

  @Test
  void exp4956007NullAuditIsContractFailure() {
    assertThrows(
        NullPointerException.class,
        () -> ExpiryAuditRepository.verifySuccessfulAudit(null, OBSERVED));
  }

  @Test
  void exp4956008NullObservationIsContractFailure() {
    assertThrows(
        NullPointerException.class,
        () ->
            ExpiryAuditRepository.verifySuccessfulAudit(
                audit("SUCCESS", OBSERVED, null, null), null));
  }

  @Test
  void exp4956009NormalBodyReturnsSameValueOnlyAfterOneClose() throws Exception {
    var events = new ArrayList<String>();
    Optional<ExpiryAuditRepository.Prior> expected = Optional.empty();
    var actual =
        ExpiryAuditRepository.usingJdbc(
            () -> events.add("close"),
            () -> {
              events.add("body");
              return expected;
            });
    assertSame(expected, actual);
    assertEquals(List.of("body", "close"), events);
  }

  @Test
  void exp4956010EachBodyFailureKeepsIdentityAndClosesExactlyOnce() {
    for (int kind = 0; kind < 4; kind++) {
      Throwable primary = failure(kind);
      var closes = new AtomicInteger();
      assertSame(
          primary,
          assertThrows(
              Throwable.class,
              () ->
                  ExpiryAuditRepository.usingJdbc(
                      closes::incrementAndGet, () -> failBody(primary))));
      assertEquals(1, closes.get());
      assertEquals(0, primary.getSuppressed().length);
    }
  }

  @Test
  void exp4956011CloseOnlyFailuresKeepIdentityAndCannotReturnSuccess() {
    for (int kind : new int[] {0, 2, 3}) {
      Throwable secondary = failure(kind);
      var bodies = new AtomicInteger();
      assertSame(
          secondary,
          assertThrows(
              Throwable.class,
              () ->
                  ExpiryAuditRepository.usingJdbc(
                      () -> failClose(secondary),
                      () -> {
                        bodies.incrementAndGet();
                        return Optional.empty();
                      })));
      assertEquals(1, bodies.get());
      assertEquals(0, secondary.getSuppressed().length);
    }
  }

  @Test
  void exp4956012CompoundFailuresMatchActualJavaTwrForAllTwelvePairs() {
    for (int body = 0; body < 4; body++) {
      for (int close : new int[] {0, 2, 3}) {
        Throwable primary = failure(body), secondary = failure(close);
        assertSame(
            primary,
            assertThrows(
                Throwable.class,
                () ->
                    ExpiryAuditRepository.usingJdbc(
                        () -> failClose(secondary), () -> failBody(primary))));
        assertArrayEquals(new Throwable[] {secondary}, primary.getSuppressed());
        Throwable referencePrimary = failure(body), referenceSecondary = failure(close);
        assertSame(
            referencePrimary,
            assertThrows(
                Throwable.class,
                () ->
                    javaTwr(
                        () -> failClose(referenceSecondary), () -> failBody(referencePrimary))));
        assertArrayEquals(new Throwable[] {referenceSecondary}, referencePrimary.getSuppressed());
        assertEquals(referencePrimary.getClass(), primary.getClass());
        assertEquals(referenceSecondary.getClass(), primary.getSuppressed()[0].getClass());
      }
    }
  }

  @Test
  void exp4956013NestedResourcesCloseRowsBeforeStatementWithOrderedSuppression() {
    var events = new ArrayList<String>();
    var primary = new IOException("PUBLIC_BODY");
    var rowClose = new SQLException("PUBLIC_ROWS");
    var statementClose = new AssertionError("PUBLIC_STATEMENT");
    assertSame(
        primary,
        assertThrows(
            IOException.class,
            () ->
                ExpiryAuditRepository.usingJdbc(
                    () -> {
                      events.add("statement");
                      throw statementClose;
                    },
                    () ->
                        ExpiryAuditRepository.usingJdbc(
                            () -> {
                              events.add("rows");
                              throw rowClose;
                            },
                            () -> {
                              events.add("body");
                              throw primary;
                            }))));
    assertEquals(List.of("body", "rows", "statement"), events);
    assertArrayEquals(new Throwable[] {rowClose, statementClose}, primary.getSuppressed());
    var reference = new ArrayList<String>();
    assertSame(
        primary,
        assertThrows(
            IOException.class,
            () ->
                javaTwr(
                    () -> reference.add("statement"),
                    () ->
                        javaTwr(
                            () -> reference.add("rows"),
                            () -> {
                              reference.add("body");
                              throw primary;
                            }))));
    assertEquals(reference, events);
  }

  @Test
  void exp4956014NullReleaseRejectsBeforeBody() {
    var count = new AtomicInteger();
    assertThrows(
        NullPointerException.class,
        () ->
            ExpiryAuditRepository.usingJdbc(
                null,
                () -> {
                  count.incrementAndGet();
                  return Optional.empty();
                }));
    assertEquals(0, count.get());
  }

  @Test
  void exp4956015NullBodyRejectsBeforeOwnershipAcceptance() {
    var closes = new AtomicInteger();
    assertThrows(
        NullPointerException.class,
        () -> ExpiryAuditRepository.usingJdbc(closes::incrementAndGet, null));
    assertEquals(0, closes.get());
  }

  @Test
  void exp4956016SelfSuppressionMatchesJavaTwrRatherThanNormalizingFailure() {
    var same = new SQLException("PUBLIC_SAME");
    var actual =
        assertThrows(
            IllegalArgumentException.class,
            () ->
                ExpiryAuditRepository.usingJdbc(
                    () -> {
                      throw same;
                    },
                    () -> {
                      throw same;
                    }));
    assertSame(same, actual.getCause());
    assertEquals(0, same.getSuppressed().length);
    var reference = new SQLException("PUBLIC_REFERENCE");
    var expected =
        assertThrows(
            IllegalArgumentException.class,
            () ->
                javaTwr(
                    () -> {
                      throw reference;
                    },
                    () -> {
                      throw reference;
                    }));
    assertSame(reference, expected.getCause());
    assertEquals(0, reference.getSuppressed().length);
    assertEquals(expected.getClass(), actual.getClass());
  }

  private static void denied(ExpiryAuditRepository.Snapshot value) {
    var error =
        assertThrows(
            BatchRepositoryException.class,
            () -> ExpiryAuditRepository.verifySuccessfulAudit(value, OBSERVED));
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
    assertFalse(error.toString().contains("INDEPENDENT"));
  }

  private static Throwable failure(int kind) {
    return switch (kind) {
      case 0 -> new SQLException("PUBLIC_SQL");
      case 1 -> new IOException("PUBLIC_IO");
      case 2 -> new IllegalStateException("PUBLIC_RUNTIME");
      case 3 -> new AssertionError("PUBLIC_ERROR");
      default -> throw new AssertionError("bad test fixture");
    };
  }

  private static Optional<ExpiryAuditRepository.Prior> failBody(Throwable error)
      throws SQLException, IOException {
    if (error instanceof SQLException sql) throw sql;
    if (error instanceof IOException io) throw io;
    if (error instanceof RuntimeException runtime) throw runtime;
    throw (Error) error;
  }

  private static void failClose(Throwable error) throws SQLException {
    if (error instanceof SQLException sql) throw sql;
    if (error instanceof RuntimeException runtime) throw runtime;
    throw (Error) error;
  }

  /** Independent compiler-generated reference, not the production helper. */
  private static Optional<ExpiryAuditRepository.Prior> javaTwr(
      ExpiryAuditRepository.JdbcRelease release, ExpiryAuditRepository.JdbcRead body)
      throws SQLException, IOException {
    try (JdbcClose owned = release::close) {
      assertNotNull(owned, "independent TWR reference owns a nonnull resource");
      return body.read();
    }
  }

  private interface JdbcClose extends AutoCloseable {
    @Override
    void close() throws SQLException;
  }
}
