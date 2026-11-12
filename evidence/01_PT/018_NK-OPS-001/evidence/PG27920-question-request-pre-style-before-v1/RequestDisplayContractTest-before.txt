package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.LayoutValidationException;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.AnswerState;
import dev.codex.schubert.nk.protocol.layout.semantic.QuestionId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.form.QuestionSubmitForm;
import dev.codex.schubert.nk.web.form.UserCreateForm;
import dev.codex.schubert.nk.web.receipt.ReceiptReference;
import dev.codex.schubert.nk.web.session.SessionOperationToken;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** UI224/225, SS313/314/331, QA048/049; REQUEST-DISPLAY001..010. Pure values only. */
final class RequestDisplayContractTest {
  private static final String RECEIPT = "0".repeat(26);
  private static final UUID TOKEN = new UUID(0, 77);
  private static final String TOKEN_TEXT = "00000000-0000-0000-0000-00000000004d";
  private static final Instant TIME = Instant.parse("2026-11-01T00:00:00.123Z");

  private static SessionPrincipal actor(UserRole role) {
    return new SessionPrincipal("PUBLIC_DISPLAY", role,
        AuthenticationContext.of("a".repeat(64)), TIME);
  }

  private static QuestionDetailResponseData data(
      long id, String receipt, String username, String question, Instant time) {
    return new QuestionDetailResponseData(new QuestionId(id), receipt, username,
        AnswerState.UNANSWERED, question, Optional.empty(), time, Optional.empty());
  }

  private static Map<String, List<String>> userFields(String role) {
    return Map.of("username", List.of("PUBLIC_USER"), "password", List.of("PUBLIC_ONLY_123"),
        "password_confirmation", List.of("PUBLIC_ONLY_123"), "role", List.of(role),
        "enabled", List.of("false"), "operation_token", List.of(TOKEN_TEXT));
  }

  @Test
  void requestDisplay001ReceiptRetainsOnlyPublicLocatorValuesAtBothIdLimits() {
    for (long id : new long[] {1, 999_999_999_999L}) {
      var value = new ReceiptReference(RECEIPT, id, TIME);
      assertSame(RECEIPT, value.receiptId());
      assertEquals(id, value.questionId());
      assertSame(TIME, value.submittedAt());
      assertEquals("ReceiptReference[redacted]", value.toString());
    }
    ReceiptReference.requireReceiptId("0123456789ABCDEFGHJKMNPQRS");
  }

  @Test
  void requestDisplay002ReceiptRejectsAllSyntaxNullIdAndSubmillisecondBoundaries() {
    assertThrows(NullPointerException.class, () -> new ReceiptReference(null, 1, TIME));
    assertThrows(NullPointerException.class, () -> new ReceiptReference(RECEIPT, 1, null));
    assertThrows(NullPointerException.class, () -> ReceiptReference.requireReceiptId(null));
    for (String id : List.of("", "0".repeat(25), "0".repeat(27), "I".repeat(26),
        "L".repeat(26), "O".repeat(26), "U".repeat(26), "a".repeat(26), "_".repeat(26), "\n".repeat(26))) {
      assertEquals("receipt identifier is invalid", assertThrows(IllegalArgumentException.class,
          () -> ReceiptReference.requireReceiptId(id)).getMessage());
    }
    for (long id : new long[] {-1, 0, 1_000_000_000_000L, Long.MAX_VALUE}) {
      assertEquals("receipt reference is invalid", assertThrows(IllegalArgumentException.class,
          () -> new ReceiptReference(RECEIPT, id, TIME)).getMessage());
    }
    for (int nano : new int[] {1, 999_999, 123_456_789}) {
      assertThrows(IllegalArgumentException.class,
          () -> new ReceiptReference(RECEIPT, 1, Instant.ofEpochSecond(0, nano)));
    }
  }

  @Test
  void requestDisplay003QuestionNewFormUsesOnlyCorrectPurposeAndPublicSnapshot() {
    var principal = actor(UserRole.USER);
    var page = QuestionSubmitViewModel.newForm(principal,
        new SessionOperationToken("QSBREQ01", TOKEN, TIME));
    assertEquals(Map.of("question", "", "operationToken", TOKEN_TEXT), page.getValues());
    assertTrue(page.getIssues().isEmpty());
    assertEquals("", page.getNotice());
    assertEquals("PUBLIC_DISPLAY", page.getTopBar().getUsername());
    assertEquals("QuestionSubmitViewModel[REDACTED]", page.toString());
    assertThrows(UnsupportedOperationException.class, () -> page.getValues().clear());
    assertThrows(UnsupportedOperationException.class, () -> page.getIssues().put("x", "y"));
    assertEquals("question form purpose is invalid", assertThrows(IllegalArgumentException.class,
        () -> QuestionSubmitViewModel.newForm(principal,
            new SessionOperationToken("UCRREQ01", TOKEN, TIME))).getMessage());
    assertThrows(NullPointerException.class, () -> QuestionSubmitViewModel.newForm(principal, null));
    assertThrows(NullPointerException.class, () -> QuestionSubmitViewModel.newForm(null,
        new SessionOperationToken("QSBREQ01", TOKEN, TIME)));
  }

  @Test
  void requestDisplay004QuestionRedisplayKeepsSameTokenRequestOnlyBodyAndIssueCopy() {
    var principal = actor(UserRole.USER);
    for (String body : List.of("PUBLIC_QUESTION", "PUBLIC\nQUESTION")) {
      try (var form = QuestionSubmitForm.bind(Map.of("question", List.of(body),
          "operation_token", List.of(TOKEN_TEXT)))) {
        var page = QuestionSubmitViewModel.redisplay(principal, form, "PUBLIC_NOTICE");
        assertEquals(Map.of("question", body.contains("\n") ? "" : "PUBLIC_QUESTION",
            "operationToken", TOKEN_TEXT), page.getValues());
        assertEquals(body.contains("\n") ? Set.of("question") : Set.of(), page.getIssues().keySet());
        assertEquals("PUBLIC_NOTICE", page.getNotice());
        assertThrows(UnsupportedOperationException.class, () -> page.getIssues().clear());
        assertThrows(NullPointerException.class,
            () -> QuestionSubmitViewModel.redisplay(principal, form, null));
        assertThrows(NullPointerException.class,
            () -> QuestionSubmitViewModel.redisplay(null, form, ""));
      }
    }
    assertThrows(NullPointerException.class,
        () -> QuestionSubmitViewModel.redisplay(principal, null, ""));
  }

  @Test
  void requestDisplay005AcceptanceDisplaysJstAndAtMostTwoHundredUnicodeCodePoints() {
    var reference = new ReceiptReference(RECEIPT, 12, TIME);
    for (String body : List.of("PUBLIC_QUESTION", "x".repeat(199), "x".repeat(200),
        "x".repeat(201), "😀".repeat(199) + "XTAIL")) {
      var page = QuestionAcceptedViewModel.from(actor(UserRole.USER), reference,
          data(12, RECEIPT, "PUBLIC_DISPLAY", body, TIME));
      String expected = body.startsWith("😀") ? "😀".repeat(199) + "X"
          : body.length() > 200 ? "x".repeat(200) : body;
      assertEquals(Map.of("receiptId", RECEIPT, "submittedAt", "2026-11-01 09:00:00",
          "question", expected), page.getValues());
      assertEquals("PUBLIC_DISPLAY", page.getTopBar().getUsername());
      assertEquals("QuestionAcceptedViewModel[REDACTED]", page.toString());
      assertThrows(UnsupportedOperationException.class, () -> page.getValues().clear());
    }
  }

  @Test
  void requestDisplay006AcceptanceRejectsEachIndependentLocatorAndUsernameMismatch() {
    var principal = actor(UserRole.USER);
    var reference = new ReceiptReference(RECEIPT, 12, TIME);
    for (var value : List.of(
        data(13, RECEIPT, "PUBLIC_DISPLAY", "PUBLIC", TIME),
        data(12, "1".repeat(26), "PUBLIC_DISPLAY", "PUBLIC", TIME),
        data(12, RECEIPT, "PUBLIC_DISPLAY", "PUBLIC", TIME.plusMillis(1)),
        data(12, RECEIPT, "OTHER", "PUBLIC", TIME))) {
      assertEquals("invalid acceptance projection", assertThrows(IllegalArgumentException.class,
          () -> QuestionAcceptedViewModel.from(principal, reference, value)).getMessage());
    }
  }

  @Test
  void requestDisplay007AcceptanceRejectsNullAbsentBodyAndInvalidWireSemantic() {
    var principal = actor(UserRole.USER);
    var reference = new ReceiptReference(RECEIPT, 12, TIME);
    var value = data(12, RECEIPT, "PUBLIC_DISPLAY", "PUBLIC", TIME);
    assertThrows(NullPointerException.class,
        () -> QuestionAcceptedViewModel.from(null, reference, value));
    assertThrows(NullPointerException.class,
        () -> QuestionAcceptedViewModel.from(principal, null, value));
    assertThrows(NullPointerException.class,
        () -> QuestionAcceptedViewModel.from(principal, reference, null));
    assertEquals("question projection body is absent", assertThrows(IllegalArgumentException.class,
        () -> QuestionAcceptedViewModel.from(principal, reference,
            data(12, RECEIPT, "PUBLIC_DISPLAY", "", TIME))).getMessage());
    var inconsistent = new QuestionDetailResponseData(new QuestionId(12), RECEIPT,
        "PUBLIC_DISPLAY", AnswerState.ANSWERED, "PUBLIC", Optional.of("PUBLIC_ANSWER"),
        TIME, Optional.empty());
    assertThrows(LayoutValidationException.class,
        () -> QuestionAcceptedViewModel.from(principal, reference, inconsistent));
    assertThrows(IllegalArgumentException.class,
        () -> QuestionAcceptedViewModel.from(principal, reference,
            data(12, RECEIPT, "PUBLIC_DISPLAY", "PUBLIC", TIME.plusNanos(1))));
  }

  @Test
  void requestDisplay008UserNewFormHasApprovedDefaultsNoPasswordAndImmutableFields() {
    var page = UserCreateViewModel.newForm(actor(UserRole.ADMIN), TOKEN);
    var values = page.getValues();
    assertEquals(Set.of("topBar", "fields", "issues", "token", "message"), values.keySet());
    assertEquals(Map.of("username", "", "role", "USER", "enabled", true), values.get("fields"));
    assertEquals(Map.of(), values.get("issues"));
    assertEquals(TOKEN_TEXT, values.get("token"));
    assertEquals("", values.get("message"));
    assertFalse(values.containsKey("password"));
    assertEquals("UserCreateViewModel[REDACTED]", page.toString());
    assertThrows(UnsupportedOperationException.class, () -> values.clear());
    assertThrows(UnsupportedOperationException.class, () -> ((Map<?, ?>) values.get("fields")).clear());
  }

  @Test
  void requestDisplay009UserRedisplayPreservesPublicFieldsAndConflictIssueOnly() {
    for (boolean conflict : new boolean[] {false, true}) {
      try (var form = UserCreateForm.bind(userFields("ADMIN"))) {
        var values = UserCreateViewModel.redisplay(actor(UserRole.ADMIN), form, TOKEN,
            "PUBLIC_NOTICE", conflict).getValues();
        assertEquals(Map.of("username", "PUBLIC_USER", "role", "ADMIN", "enabled", false),
            values.get("fields"));
        assertEquals(conflict ? Map.of("username", "Username又は操作の整合性を確認してください。")
            : Map.of(), values.get("issues"));
        assertEquals(TOKEN_TEXT, values.get("token"));
        assertEquals("PUBLIC_NOTICE", values.get("message"));
        assertThrows(UnsupportedOperationException.class, () -> ((Map<?, ?>) values.get("issues")).clear());
      }
    }
    try (var form = UserCreateForm.bind(userFields("UNKNOWN"))) {
      var values = UserCreateViewModel.redisplay(actor(UserRole.ADMIN), form, TOKEN, "", false).getValues();
      assertEquals(Set.of("role"), ((Map<?, ?>) values.get("issues")).keySet());
      assertEquals(Map.of("username", "PUBLIC_USER", "role", "USER", "enabled", false),
          values.get("fields"));
    }
  }

  @Test
  void requestDisplay010UserDisplayRejectsNullWithoutAuthenticationOrApiActions() {
    var principal = actor(UserRole.ADMIN);
    assertThrows(NullPointerException.class, () -> UserCreateViewModel.newForm(null, TOKEN));
    assertThrows(NullPointerException.class, () -> UserCreateViewModel.newForm(principal, null));
    assertThrows(NullPointerException.class,
        () -> UserCreateViewModel.redisplay(principal, null, TOKEN, "", false));
    try (var form = UserCreateForm.bind(userFields("USER"))) {
      assertThrows(NullPointerException.class,
          () -> UserCreateViewModel.redisplay(null, form, TOKEN, "", false));
      assertThrows(NullPointerException.class,
          () -> UserCreateViewModel.redisplay(principal, form, null, "", false));
      assertThrows(NullPointerException.class,
          () -> UserCreateViewModel.redisplay(principal, form, TOKEN, null, false));
    }
  }
}
