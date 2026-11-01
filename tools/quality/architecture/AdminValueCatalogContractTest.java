package dev.codex.schubert.nk.api.application.admin;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.application.question.AnswerBusinessException;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.admin.UserMutationResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserId;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** Pure SS312/323/332/351 DTO/catalog checks; no actual admin mutation, provider or transaction. */
final class AdminValueCatalogContractTest {
  private static final UUID MESSAGE = UUID.fromString("00000000-0000-0000-0000-000000000711");
  private static final UUID CORRELATION = UUID.fromString("00000000-0000-0000-0000-000000000712");

  @Test
  void adminValues001MetadataUsesUtcMicrosecondsAndOnlyFixedRedactedText() {
    String[][] times = {
      {"2026-11-01T00:00:00.123456789Z", "2026-11-01T00:00:00.123456Z"},
      {"1969-12-31T23:59:59.999999999Z", "1969-12-31T23:59:59.999999Z"}
    };
    for (String[] vector : times) {
      var metadata = new UserCommandMetadata(MESSAGE, CORRELATION, Instant.parse(vector[0]));
      assertSame(MESSAGE, metadata.messageId());
      assertSame(CORRELATION, metadata.correlationId());
      assertEquals(Instant.parse(vector[1]), metadata.at());
      assertEquals("UserCommandMetadata[REDACTED]", metadata.toString());
    }
  }

  @Test
  void adminValues002AllRequiredMetadataReferencesRejectNull() {
    var at = Instant.parse("2026-11-01T00:00:00Z");
    assertThrows(NullPointerException.class, () -> new UserCommandMetadata(null, CORRELATION, at));
    assertThrows(NullPointerException.class, () -> new UserCommandMetadata(MESSAGE, null, at));
    assertThrows(NullPointerException.class, () -> new UserCommandMetadata(MESSAGE, CORRELATION, null));
  }

  @Test
  void adminValues003SuccessProfilesRetainTheExplicitUserAndVersion() {
    for (ResultCode code : List.of(ResultCode.SUCCESS, ResultCode.IDEMPOTENT_SUCCESS)) {
      for (long version : new long[] {1, 999_999_999L}) {
        var result = UserMutationResult.accepted(new UserId(7), version, code);
        assertSame(code, result.resultCode());
        assertEquals(
            code == ResultCode.SUCCESS ? "0000" : "0200", result.resultCode().wireValue());
        assertEquals(7, result.data().orElseThrow().userId().value());
        assertEquals(version, result.data().orElseThrow().updatedVersion());
        assertEquals("UserMutationResult[REDACTED]", result.toString());
      }
    }
  }

  @Test
  void adminValues004OnlyClosedDefiniteFailuresAndConsistentPayloadProfilesAreAccepted() {
    ResultCode[] allowed = {
      ResultCode.VALIDATION_ERROR, ResultCode.NOT_FOUND, ResultCode.CONFLICT, ResultCode.RESOURCE_LIMIT
    };
    String[] wire = {"0100", "0104", "0105", "9001"};
    for (int index = 0; index < allowed.length; index++) {
      var result = UserMutationResult.rejected(allowed[index]);
      assertSame(allowed[index], result.resultCode());
      assertEquals(wire[index], result.resultCode().wireValue());
      assertTrue(result.data().isEmpty());
    }
    for (ResultCode unsupported :
        List.of(
            ResultCode.AUTHENTICATION_FAILED,
            ResultCode.SESSION_INVALID,
            ResultCode.FORBIDDEN,
            ResultCode.LOCKED,
            ResultCode.NOT_CANCELLABLE,
            ResultCode.TEMPORARY_FAILURE)) {
      var failure =
          assertThrows(
              IllegalArgumentException.class, () -> UserMutationResult.rejected(unsupported));
      assertEquals("user mutation result code is invalid", failure.getMessage());
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
    }
    for (ResultCode code : List.of(ResultCode.SUCCESS, ResultCode.IDEMPOTENT_SUCCESS))
      assertEquals(
          "user mutation result payload is inconsistent",
          assertThrows(IllegalArgumentException.class, () -> UserMutationResult.rejected(code))
              .getMessage());
    for (ResultCode code : allowed)
      assertEquals(
          "user mutation result payload is inconsistent",
          assertThrows(
                  IllegalArgumentException.class,
                  () -> UserMutationResult.accepted(new UserId(7), 1, code))
              .getMessage());
  }

  @Test
  void adminValues005ResultReferencesAreRequiredAndTheCallerPayloadIsNotReplaced() {
    var payload = new UserMutationResponseData(new UserId(7), 1);
    var data = Optional.of(payload);
    assertThrows(NullPointerException.class, () -> new UserMutationResult(null, data));
    assertThrows(
        NullPointerException.class, () -> new UserMutationResult(ResultCode.SUCCESS, null));
    assertThrows(
        NullPointerException.class, () -> UserMutationResult.accepted(null, 1, ResultCode.SUCCESS));
    var result = new UserMutationResult(ResultCode.SUCCESS, data);
    assertSame(data, result.data());
    assertSame(payload, result.data().orElseThrow());
    assertEquals(7, payload.userId().value());
    assertEquals(1, payload.updatedVersion());
    assertEquals("UserMutationResult[REDACTED]", result.toString());
  }

  @Test
  void adminValues006AnswerFailureCatalogNeverContainsProviderDetailsAtConstruction() {
    var failure = new AnswerBusinessException();
    assertEquals("answer could not be produced", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }
}
