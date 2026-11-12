package dev.codex.schubert.nk.api.application.question;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.application.question.QuestionCommandService.CancelResult;
import dev.codex.schubert.nk.api.application.question.QuestionCommandService.DeleteResult;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationState;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.OptionalLong;
import org.junit.jupiter.api.Test;

/** PT-QRY-CMDVAL001..005; SS323/332. Public DTO invariants only; no command, DB or replay. */
final class QuestionCommandResultContractTest {
  private static final long MAXIMUM_JOB_ID = 999_999_999_999L;
  private static final Instant AT = Instant.parse("2026-10-01T00:00:00.123456Z");

  @Test
  void cancelSuccessPreservesIndependentN12BoundariesAndFixedRendering() {
    for (ResultCode code : List.of(ResultCode.SUCCESS, ResultCode.IDEMPOTENT_SUCCESS)) {
      for (long id : new long[] {1, MAXIMUM_JOB_ID}) {
        var result =
            assertDoesNotThrow(
                () ->
                    new CancelResult(
                        code,
                        OptionalLong.of(id),
                        Optional.of(NotificationState.CANCELLED),
                        Optional.of(AT)));
        assertSame(code, result.code());
        assertEquals(OptionalLong.of(id), result.jobId());
        assertEquals(Optional.of(NotificationState.CANCELLED), result.state());
        assertEquals(Optional.of(AT), result.cancelledAt());
        assertEquals("CancelResult[REDACTED]", result.toString());
      }
    }
  }

  @Test
  void cancelSuccessRejectsOutOfRangeJobsAndEveryMissingSuccessComponent() {
    for (long invalid : new long[] {0, MAXIMUM_JOB_ID + 1, Long.MIN_VALUE, Long.MAX_VALUE}) {
      assertThrows(
          IllegalArgumentException.class,
          () ->
              new CancelResult(
                  ResultCode.SUCCESS,
                  OptionalLong.of(invalid),
                  Optional.of(NotificationState.CANCELLED),
                  Optional.of(AT)));
    }
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new CancelResult(
                ResultCode.SUCCESS,
                OptionalLong.empty(),
                Optional.of(NotificationState.CANCELLED),
                Optional.of(AT)));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new CancelResult(
                ResultCode.SUCCESS, OptionalLong.of(1), Optional.empty(), Optional.of(AT)));
    for (NotificationState invalid :
        List.of(
            NotificationState.RECEIVED,
            NotificationState.PROCESSING,
            NotificationState.COMPLETED,
            NotificationState.ERROR)) {
      assertThrows(
          IllegalArgumentException.class,
          () ->
              new CancelResult(
                  ResultCode.SUCCESS, OptionalLong.of(1), Optional.of(invalid), Optional.of(AT)));
    }
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new CancelResult(
                ResultCode.IDEMPOTENT_SUCCESS,
                OptionalLong.of(1),
                Optional.of(NotificationState.CANCELLED),
                Optional.empty()));
  }

  @Test
  void cancellationConflictAndDefiniteDenialsUseClosedPresenceTables() {
    for (NotificationState state :
        List.of(
            NotificationState.PROCESSING, NotificationState.COMPLETED, NotificationState.ERROR)) {
      var result =
          new CancelResult(
              ResultCode.NOT_CANCELLABLE, OptionalLong.of(1), Optional.of(state), Optional.empty());
      assertSame(ResultCode.NOT_CANCELLABLE, result.code());
      assertEquals(OptionalLong.of(1), result.jobId());
      assertEquals(Optional.of(state), result.state());
      assertTrue(result.cancelledAt().isEmpty());
    }
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new CancelResult(
                ResultCode.NOT_CANCELLABLE,
                OptionalLong.empty(),
                Optional.of(NotificationState.PROCESSING),
                Optional.empty()));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new CancelResult(
                ResultCode.NOT_CANCELLABLE,
                OptionalLong.of(1),
                Optional.empty(),
                Optional.empty()));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new CancelResult(
                ResultCode.NOT_CANCELLABLE,
                OptionalLong.of(1),
                Optional.of(NotificationState.PROCESSING),
                Optional.of(AT)));
    for (NotificationState invalid :
        List.of(NotificationState.RECEIVED, NotificationState.CANCELLED)) {
      assertThrows(
          IllegalArgumentException.class,
          () ->
              new CancelResult(
                  ResultCode.NOT_CANCELLABLE,
                  OptionalLong.of(1),
                  Optional.of(invalid),
                  Optional.empty()));
    }
    for (ResultCode code : List.of(ResultCode.NOT_FOUND, ResultCode.RESOURCE_LIMIT)) {
      var result = new CancelResult(code, OptionalLong.empty(), Optional.empty(), Optional.empty());
      assertSame(code, result.code());
      assertTrue(result.jobId().isEmpty());
      assertTrue(result.state().isEmpty());
      assertTrue(result.cancelledAt().isEmpty());
      assertEquals("CancelResult[REDACTED]", result.toString());
      assertThrows(
          IllegalArgumentException.class,
          () -> new CancelResult(code, OptionalLong.of(1), Optional.empty(), Optional.empty()));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              new CancelResult(
                  code,
                  OptionalLong.empty(),
                  Optional.of(NotificationState.RECEIVED),
                  Optional.empty()));
      assertThrows(
          IllegalArgumentException.class,
          () -> new CancelResult(code, OptionalLong.empty(), Optional.empty(), Optional.of(AT)));
    }
    for (ResultCode invalid :
        List.of(ResultCode.TEMPORARY_FAILURE, ResultCode.VALIDATION_ERROR, ResultCode.CONFLICT)) {
      assertThrows(
          IllegalArgumentException.class,
          () ->
              new CancelResult(invalid, OptionalLong.empty(), Optional.empty(), Optional.empty()));
    }
  }

  @Test
  void bothPublicDtosRejectNullContainersAtTheirNamedBoundary() {
    assertEquals(
        "code",
        assertThrows(
                NullPointerException.class,
                () ->
                    new CancelResult(
                        null, OptionalLong.empty(), Optional.empty(), Optional.empty()))
            .getMessage());
    assertEquals(
        "jobId",
        assertThrows(
                NullPointerException.class,
                () ->
                    new CancelResult(
                        ResultCode.NOT_FOUND, null, Optional.empty(), Optional.empty()))
            .getMessage());
    assertEquals(
        "state",
        assertThrows(
                NullPointerException.class,
                () ->
                    new CancelResult(
                        ResultCode.NOT_FOUND, OptionalLong.empty(), null, Optional.empty()))
            .getMessage());
    assertEquals(
        "cancelledAt",
        assertThrows(
                NullPointerException.class,
                () ->
                    new CancelResult(
                        ResultCode.NOT_FOUND, OptionalLong.empty(), Optional.empty(), null))
            .getMessage());
    assertEquals(
        "code",
        assertThrows(NullPointerException.class, () -> new DeleteResult(null, Optional.empty()))
            .getMessage());
    assertEquals(
        "deletedAt",
        assertThrows(NullPointerException.class, () -> new DeleteResult(ResultCode.NOT_FOUND, null))
            .getMessage());
  }

  @Test
  void deletionAllowsOnlySuccessWithTimeOrDefiniteEmptyDenials() {
    for (ResultCode code : List.of(ResultCode.SUCCESS, ResultCode.IDEMPOTENT_SUCCESS)) {
      var result = new DeleteResult(code, Optional.of(AT));
      assertSame(code, result.code());
      assertEquals(Optional.of(AT), result.deletedAt());
      assertEquals("DeleteResult[REDACTED]", result.toString());
      assertThrows(IllegalArgumentException.class, () -> new DeleteResult(code, Optional.empty()));
    }
    for (ResultCode code : List.of(ResultCode.NOT_FOUND, ResultCode.RESOURCE_LIMIT)) {
      var result = new DeleteResult(code, Optional.empty());
      assertSame(code, result.code());
      assertFalse(result.deletedAt().isPresent());
      assertEquals("DeleteResult[REDACTED]", result.toString());
      assertThrows(IllegalArgumentException.class, () -> new DeleteResult(code, Optional.of(AT)));
    }
    for (ResultCode invalid :
        List.of(
            ResultCode.NOT_CANCELLABLE,
            ResultCode.CONFLICT,
            ResultCode.VALIDATION_ERROR,
            ResultCode.TEMPORARY_FAILURE)) {
      assertThrows(
          IllegalArgumentException.class, () -> new DeleteResult(invalid, Optional.empty()));
    }
  }
}
