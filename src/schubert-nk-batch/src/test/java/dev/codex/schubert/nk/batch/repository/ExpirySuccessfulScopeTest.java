package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicInteger;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** NK-BAT-001/P017-11; SS331/341/343/SSC304; PT-EXP-4956-001..024. */
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
        using(
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
              Throwable.class, () -> using(closes::incrementAndGet, () -> failBody(primary))));
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
                  using(
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
        Throwable primary = failure(body);
        Throwable secondary = failure(close);
        assertSame(
            primary,
            assertThrows(
                Throwable.class, () -> using(() -> failClose(secondary), () -> failBody(primary))));
        assertArrayEquals(new Throwable[] {secondary}, primary.getSuppressed());
        Throwable referencePrimary = failure(body);
        Throwable referenceSecondary = failure(close);
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
                using(
                    () -> {
                      events.add("statement");
                      throw statementClose;
                    },
                    () ->
                        using(
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
  void exp4956014NullAcquisitionResultKeepsOriginalAdmissionFailure() {
    var count = new AtomicInteger();
    assertThrows(
        BatchRepositoryException.class,
        () ->
            using(
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
    assertThrows(NullPointerException.class, () -> using(closes::incrementAndGet, null));
    assertEquals(0, closes.get());
  }

  @Test
  void exp4956016SelfSuppressionMatchesJavaTwrRatherThanNormalizingFailure() {
    var same = new SQLException("PUBLIC_SAME");
    var actual =
        assertThrows(
            IllegalArgumentException.class,
            () ->
                using(
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
  private static Optional<ExpiryAuditRepository.Prior> javaTwr(JdbcClose release, Read body)
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

  private static Optional<ExpiryAuditRepository.Prior> using(
      @Nullable JdbcClose release, @Nullable Read body) throws SQLException, IOException {
    ExpiryAuditRepository.@Nullable JdbcRead<JdbcClose> read =
        body == null ? null : resource -> body.read();
    return ExpiryAuditRepository.usingJdbc(() -> release, JdbcClose::close, read);
  }

  private interface Read {
    Optional<ExpiryAuditRepository.Prior> read() throws SQLException, IOException;
  }

  @Test
  void exp4956017NullReleasePortRejectsBeforeBodyAndResourceOwnership() {
    var bodies = new AtomicInteger();
    var opens = new AtomicInteger();
    assertThrows(
        NullPointerException.class,
        () ->
            ExpiryAuditRepository.usingJdbc(
                () -> {
                  opens.incrementAndGet();
                  return new Object();
                },
                null,
                resource -> {
                  bodies.incrementAndGet();
                  return Optional.empty();
                }));
    assertEquals(0, bodies.get());
    assertEquals(0, opens.get());
  }

  @Test
  void exp4956018ReleaseReceivesExactlyTheAdmittedResource() throws Exception {
    var resource = new Object();
    var closes = new AtomicInteger();
    assertEquals(
        Optional.empty(),
        ExpiryAuditRepository.usingJdbc(
            () -> resource,
            actual -> {
              assertSame(resource, actual);
              closes.incrementAndGet();
            },
            actual -> {
              assertSame(resource, actual);
              return Optional.empty();
            }));
    assertEquals(1, closes.get());
  }

  @Test
  void exp4956019NullAcquirePortFailsBeforeBodyOrClose() {
    var calls = new AtomicInteger();
    assertThrows(
        NullPointerException.class,
        () ->
            ExpiryAuditRepository.usingJdbc(
                null,
                resource -> calls.incrementAndGet(),
                resource -> {
                  calls.incrementAndGet();
                  return Optional.empty();
                }));
    assertEquals(0, calls.get());
  }

  @Test
  void exp4956020AcquireSqlRuntimeAndErrorCannotRunBodyOrClose() {
    for (int kind : new int[] {0, 2, 3}) {
      Throwable primary = failure(kind);
      var events = new ArrayList<String>();
      assertSame(
          primary,
          assertThrows(
              Throwable.class,
              () ->
                  ExpiryAuditRepository.usingJdbc(
                      () -> {
                        events.add("acquire");
                        failClose(primary);
                        return new Object();
                      },
                      resource -> events.add("close"),
                      resource -> {
                        events.add("body");
                        return Optional.empty();
                      })));
      assertEquals(List.of("acquire"), events);
      assertEquals(0, primary.getSuppressed().length);
    }
  }

  @Test
  void exp4956021AllPortsConstructedBeforeAcquisitionThenExactOrder() throws Exception {
    var events = new ArrayList<String>();
    var resource = new Object();
    events.add("make-acquire");
    ExpiryAuditRepository.JdbcAcquire<Object> acquire =
        () -> {
          events.add("acquire");
          return resource;
        };
    events.add("make-close");
    ExpiryAuditRepository.JdbcRelease<Object> release =
        actual -> {
          assertSame(resource, actual);
          events.add("close");
        };
    events.add("make-read");
    ExpiryAuditRepository.JdbcRead<Object> read =
        actual -> {
          assertSame(resource, actual);
          events.add("body");
          return Optional.empty();
        };
    assertEquals(Optional.empty(), ExpiryAuditRepository.usingJdbc(acquire, release, read));
    assertEquals(
        List.of("make-acquire", "make-close", "make-read", "acquire", "body", "close"), events);
  }

  @Test
  void exp4956022InnerSelfSuppressionStillClosesOuterAndSuppressesItsFailure() {
    var primary = new SQLException("PUBLIC_INNER_SAME");
    var outer = new AssertionError("PUBLIC_OUTER");
    var events = new ArrayList<String>();
    var result =
        assertThrows(
            IllegalArgumentException.class,
            () ->
                using(
                    () -> {
                      events.add("statement");
                      throw outer;
                    },
                    () ->
                        using(
                            () -> {
                              events.add("rows");
                              throw primary;
                            },
                            () -> {
                              throw primary;
                            })));
    assertSame(primary, result.getCause());
    assertArrayEquals(new Throwable[] {outer}, result.getSuppressed());
    assertEquals(List.of("rows", "statement"), events);
    var referencePrimary = new SQLException("PUBLIC_REFERENCE");
    var referenceOuter = new AssertionError("PUBLIC_REFERENCE_OUTER");
    var reference =
        assertThrows(
            IllegalArgumentException.class,
            () ->
                javaTwr(
                    () -> {
                      throw referenceOuter;
                    },
                    () ->
                        javaTwr(
                            () -> {
                              throw referencePrimary;
                            },
                            () -> {
                              throw referencePrimary;
                            })));
    assertSame(referencePrimary, reference.getCause());
    assertArrayEquals(new Throwable[] {referenceOuter}, reference.getSuppressed());
  }

  @Test
  void exp4956023DuplicateSecondaryIdentityIsNotDeduplicated() {
    var primary = new IOException("PUBLIC_BODY");
    var secondary = new SQLException("PUBLIC_REPEATED");
    var closes = new AtomicInteger();
    assertSame(
        primary,
        assertThrows(
            IOException.class,
            () ->
                using(
                    () -> {
                      closes.incrementAndGet();
                      throw secondary;
                    },
                    () ->
                        using(
                            () -> {
                              closes.incrementAndGet();
                              throw secondary;
                            },
                            () -> {
                              throw primary;
                            }))));
    assertEquals(2, closes.get());
    assertArrayEquals(new Throwable[] {secondary, secondary}, primary.getSuppressed());
  }

  @Test
  void exp4956024CallbackConstructionErrorHappensBeforeAnyAcquisition() {
    var primary = new AssertionError("PUBLIC_LINKAGE_CONSTRUCTION");
    var opens = new AtomicInteger();
    var closes = new AtomicInteger();
    assertSame(
        primary,
        assertThrows(
            AssertionError.class,
            () ->
                ExpiryAuditRepository.usingJdbc(
                    () -> {
                      opens.incrementAndGet();
                      return new Object();
                    },
                    resource -> closes.incrementAndGet(),
                    unavailableRead(primary))));
    assertEquals(0, opens.get());
    assertEquals(0, closes.get());
  }

  private static ExpiryAuditRepository.JdbcRead<Object> unavailableRead(AssertionError primary) {
    throw primary;
  }
}
