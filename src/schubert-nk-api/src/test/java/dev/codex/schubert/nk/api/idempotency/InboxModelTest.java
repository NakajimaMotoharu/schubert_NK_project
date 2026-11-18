package dev.codex.schubert.nk.api.idempotency;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.OptionalLong;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-IDEM-004..006 boundary, null-contract and redaction tests for Inbox value objects. */
class InboxModelTest {
  private static final String LAYOUT_VERSION = "001";
  private static final String QUESTION_REQUEST_LAYOUT = "QSTREQ01";
  private static final String READ_TARGET = "read";
  private static final String QUESTION_RESPONSE_LAYOUT = "QSTRSP01";
  private static final UUID MESSAGE = UUID.fromString("10000000-0000-0000-0000-000000000001");
  private static final UUID CORRELATION = UUID.fromString("20000000-0000-0000-0000-000000000001");
  private static final UUID TOKEN = UUID.fromString("30000000-0000-0000-0000-000000000001");
  private static final UUID RESULT_UUID = UUID.fromString("40000000-0000-0000-0000-000000000001");
  private static final Instant RECEIVED = Instant.parse("2026-09-05T00:00:00Z");
  private static final Instant EXPIRES = Instant.parse("2026-09-12T00:00:00Z");

  @Test
  void requestAcceptsAnonymousAuthenticatedAndEveryTokenLayout() {
    InboxRequest anonymous =
        request(
            OptionalLong.empty(),
            Optional.empty(),
            canonical("ANONYMOUS", "LGNREQ01", LAYOUT_VERSION, "login"));
    InboxRequest read =
        request(
            OptionalLong.of(7),
            Optional.empty(),
            canonical("7", QUESTION_REQUEST_LAYOUT, LAYOUT_VERSION, READ_TARGET));

    assertEquals(OptionalLong.empty(), anonymous.ownerUserId());
    assertEquals(OptionalLong.of(7), read.ownerUserId());
    for (String layout :
        List.of(
            "UCRREQ01",
            "USTREQ01",
            "URLREQ01",
            "UPWREQ01",
            "ULKREQ01",
            "QSBREQ01",
            "NTCREQ01",
            "QDLREQ01")) {
      assertEquals(
          Optional.of(TOKEN),
          request(
                  OptionalLong.of(7),
                  Optional.of(TOKEN),
                  canonical("7", layout, LAYOUT_VERSION, "update"))
              .operationToken());
    }
    assertEquals(
        "InboxRequest[message/correlation/owner/token/request/time=<redacted>]",
        anonymous.toString());
  }

  @Test
  void requestRejectsNullsScopeTokenOwnerAndTimeViolations() {
    try (CanonicalRequest login = canonical("ANONYMOUS", "LGNREQ01", LAYOUT_VERSION, "login");
        CanonicalRequest read =
            canonical("7", QUESTION_REQUEST_LAYOUT, LAYOUT_VERSION, READ_TARGET)) {

      assertThrows(
          NullPointerException.class,
          () ->
              new InboxRequest(
                  null,
                  CORRELATION,
                  OptionalLong.empty(),
                  Optional.empty(),
                  login,
                  RECEIVED,
                  EXPIRES));
      assertThrows(
          NullPointerException.class,
          () ->
              new InboxRequest(
                  MESSAGE, null, OptionalLong.empty(), Optional.empty(), login, RECEIVED, EXPIRES));
      assertThrows(
          NullPointerException.class,
          () ->
              new InboxRequest(
                  MESSAGE, CORRELATION, null, Optional.empty(), login, RECEIVED, EXPIRES));
      assertThrows(
          NullPointerException.class,
          () ->
              new InboxRequest(
                  MESSAGE, CORRELATION, OptionalLong.empty(), null, login, RECEIVED, EXPIRES));
      assertThrows(
          NullPointerException.class,
          () ->
              new InboxRequest(
                  MESSAGE,
                  CORRELATION,
                  OptionalLong.empty(),
                  Optional.empty(),
                  null,
                  RECEIVED,
                  EXPIRES));
      assertThrows(
          NullPointerException.class,
          () ->
              new InboxRequest(
                  MESSAGE,
                  CORRELATION,
                  OptionalLong.empty(),
                  Optional.empty(),
                  login,
                  null,
                  EXPIRES));
      assertThrows(
          NullPointerException.class,
          () ->
              new InboxRequest(
                  MESSAGE,
                  CORRELATION,
                  OptionalLong.empty(),
                  Optional.empty(),
                  login,
                  RECEIVED,
                  null));
      assertThrows(
          IllegalArgumentException.class,
          () -> request(OptionalLong.of(7), Optional.empty(), login));
      assertThrows(
          IllegalArgumentException.class,
          () -> request(OptionalLong.empty(), Optional.empty(), read));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              request(
                  OptionalLong.of(0),
                  Optional.empty(),
                  canonical("0", QUESTION_REQUEST_LAYOUT, LAYOUT_VERSION, READ_TARGET)));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              request(
                  OptionalLong.of(1_000_000_000_000L),
                  Optional.empty(),
                  canonical(
                      "1000000000000", QUESTION_REQUEST_LAYOUT, LAYOUT_VERSION, READ_TARGET)));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              request(
                  OptionalLong.of(7),
                  Optional.empty(),
                  canonical("8", QUESTION_REQUEST_LAYOUT, LAYOUT_VERSION, READ_TARGET)));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              request(
                  OptionalLong.of(7),
                  Optional.empty(),
                  canonical("7", "QSBREQ01", LAYOUT_VERSION, "write")));
      assertThrows(
          IllegalArgumentException.class,
          () -> request(OptionalLong.of(7), Optional.of(TOKEN), read));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              new InboxRequest(
                  MESSAGE,
                  CORRELATION,
                  OptionalLong.empty(),
                  Optional.empty(),
                  login,
                  RECEIVED,
                  RECEIVED));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              new InboxRequest(
                  MESSAGE,
                  CORRELATION,
                  OptionalLong.empty(),
                  Optional.empty(),
                  login,
                  EXPIRES,
                  RECEIVED));
    }
  }

  @Test
  void resultReferencesEnforcePhysicalReferenceUnion() {
    assertEquals(InboxResultReferenceType.NONE, InboxResultReference.none().type());
    assertEquals(Optional.of(RESULT_UUID), InboxResultReference.authSession(RESULT_UUID).uuid());
    for (InboxResultReferenceType type :
        List.of(
            InboxResultReferenceType.USER,
            InboxResultReferenceType.QUESTION,
            InboxResultReferenceType.JOB,
            InboxResultReferenceType.SCENARIO_FILE)) {
      assertEquals(
          OptionalLong.of(999_999_999_999L),
          InboxResultReference.numeric(type, 999_999_999_999L).numericId());
    }
    assertEquals(
        "InboxResultReference[type=NONE, value=<redacted>]",
        InboxResultReference.none().toString());
    assertThrows(NullPointerException.class, () -> InboxResultReference.authSession(null));
    assertThrows(NullPointerException.class, () -> InboxResultReference.numeric(null, 1));
    assertThrows(
        NullPointerException.class,
        () -> new InboxResultReference(null, OptionalLong.empty(), Optional.empty()));
    assertThrows(
        NullPointerException.class,
        () -> new InboxResultReference(InboxResultReferenceType.NONE, null, Optional.empty()));
    assertThrows(
        NullPointerException.class,
        () -> new InboxResultReference(InboxResultReferenceType.NONE, OptionalLong.empty(), null));
    assertInvalidReference(InboxResultReferenceType.NONE, OptionalLong.of(1), Optional.empty());
    assertInvalidReference(
        InboxResultReferenceType.NONE, OptionalLong.empty(), Optional.of(RESULT_UUID));
    assertInvalidReference(
        InboxResultReferenceType.AUTH_SESSION, OptionalLong.of(1), Optional.of(RESULT_UUID));
    assertInvalidReference(
        InboxResultReferenceType.AUTH_SESSION, OptionalLong.empty(), Optional.empty());
    assertInvalidReference(InboxResultReferenceType.USER, OptionalLong.empty(), Optional.empty());
    assertInvalidReference(InboxResultReferenceType.USER, OptionalLong.of(0), Optional.empty());
    assertInvalidReference(
        InboxResultReferenceType.USER, OptionalLong.of(1_000_000_000_000L), Optional.empty());
    assertInvalidReference(
        InboxResultReferenceType.USER, OptionalLong.of(1), Optional.of(RESULT_UUID));
  }

  @Test
  void completionAndExecutionValidateMetadataPresenceAndRedact() {
    InboxCompletion completion = completion(InboxCompletionState.COMPLETED);
    InboxCompletion error = completion(InboxCompletionState.ERROR);
    assertEquals(InboxCompletionState.ERROR, error.state());
    assertEquals("InboxCompletion[<redacted>]", completion.toString());
    assertEquals(InboxExecutionStatus.EXECUTED, InboxExecution.executed(completion).status());
    assertEquals(InboxExecutionStatus.REPLAY, InboxExecution.replay(error).status());
    assertEquals(InboxExecutionStatus.IN_PROGRESS, InboxExecution.inProgress().status());
    assertEquals("InboxExecution[<redacted>]", InboxExecution.executed(completion).toString());
    assertThrows(NullPointerException.class, () -> InboxExecution.executed(null));
    assertThrows(NullPointerException.class, () -> InboxExecution.replay(null));
    assertThrows(NullPointerException.class, () -> new InboxExecution(null, Optional.empty()));
    assertThrows(
        NullPointerException.class,
        () -> new InboxExecution(InboxExecutionStatus.IN_PROGRESS, null));
    assertThrows(
        IllegalArgumentException.class,
        () -> new InboxExecution(InboxExecutionStatus.EXECUTED, Optional.empty()));
    assertThrows(
        IllegalArgumentException.class,
        () -> new InboxExecution(InboxExecutionStatus.IN_PROGRESS, Optional.of(completion)));

    assertCompletionNull(
        null,
        InboxResultReference.none(),
        QUESTION_RESPONSE_LAYOUT,
        LAYOUT_VERSION,
        Optional.empty(),
        RECEIVED);
    assertCompletionNull(
        InboxCompletionState.COMPLETED,
        null,
        QUESTION_RESPONSE_LAYOUT,
        LAYOUT_VERSION,
        Optional.empty(),
        RECEIVED);
    assertCompletionNull(
        InboxCompletionState.COMPLETED,
        InboxResultReference.none(),
        null,
        LAYOUT_VERSION,
        Optional.empty(),
        RECEIVED);
    assertCompletionNull(
        InboxCompletionState.COMPLETED,
        InboxResultReference.none(),
        QUESTION_RESPONSE_LAYOUT,
        null,
        Optional.empty(),
        RECEIVED);
    assertCompletionNull(
        InboxCompletionState.COMPLETED,
        InboxResultReference.none(),
        QUESTION_RESPONSE_LAYOUT,
        LAYOUT_VERSION,
        null,
        RECEIVED);
    assertCompletionNull(
        InboxCompletionState.COMPLETED,
        InboxResultReference.none(),
        QUESTION_RESPONSE_LAYOUT,
        LAYOUT_VERSION,
        Optional.empty(),
        null);
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new InboxCompletion(
                InboxCompletionState.COMPLETED,
                InboxResultReference.none(),
                "bad",
                LAYOUT_VERSION,
                Optional.empty(),
                RECEIVED));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new InboxCompletion(
                InboxCompletionState.COMPLETED,
                InboxResultReference.none(),
                QUESTION_RESPONSE_LAYOUT,
                "bad",
                Optional.empty(),
                RECEIVED));
  }

  @Test
  void inboxExceptionUsesBoundedReasonAndSqlState() {
    assertException(InboxException.Reason.MESSAGE_ID_REUSE, "23000");
    assertException(InboxException.Reason.OPERATION_TOKEN_REUSE, "23000");
    assertException(InboxException.Reason.FINGERPRINT_KEY_UNAVAILABLE, "55000");
    assertException(InboxException.Reason.STATE_CORRUPT, "XX000");
    assertException(InboxException.Reason.TRANSACTION_REQUIRED, "25000");
    assertThrows(NullPointerException.class, () -> new InboxException(null, "bounded"));
  }

  private static InboxRequest request(
      OptionalLong owner, Optional<UUID> token, CanonicalRequest canonicalRequest) {
    return new InboxRequest(
        MESSAGE, CORRELATION, owner, token, canonicalRequest, RECEIVED, EXPIRES);
  }

  private static CanonicalRequest canonical(
      String owner, String layout, String version, String target) {
    return new CanonicalRequest(owner, layout, version, target, List.of());
  }

  private static InboxCompletion completion(InboxCompletionState state) {
    return new InboxCompletion(
        state,
        InboxResultReference.none(),
        QUESTION_RESPONSE_LAYOUT,
        LAYOUT_VERSION,
        Optional.empty(),
        RECEIVED);
  }

  private static void assertInvalidReference(
      InboxResultReferenceType type, OptionalLong id, Optional<UUID> uuid) {
    assertThrows(IllegalArgumentException.class, () -> new InboxResultReference(type, id, uuid));
  }

  private static void assertCompletionNull(
      InboxCompletionState state,
      InboxResultReference reference,
      String layout,
      String version,
      Optional<EncryptedResponseSnapshot> snapshot,
      Instant completedAt) {
    assertThrows(
        NullPointerException.class,
        () -> new InboxCompletion(state, reference, layout, version, snapshot, completedAt));
  }

  private static void assertException(InboxException.Reason reason, String sqlState) {
    InboxException exception = new InboxException(reason, "bounded");
    assertEquals(reason, exception.reason());
    assertEquals(sqlState, exception.getSQLState());
    assertEquals("bounded", exception.getMessage());
  }
}
