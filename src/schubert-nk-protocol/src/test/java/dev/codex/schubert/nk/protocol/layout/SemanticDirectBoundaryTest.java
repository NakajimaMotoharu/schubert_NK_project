package dev.codex.schubert.nk.protocol.layout;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

/**
 * Independent direct component boundaries, not authentication, HTTP or business execution. Trace:
 * NK-PRO-002; MSG001-011; UI234-236/SS322 section 9; Program002/011; SEM001-003.
 */
final class SemanticDirectBoundaryTest {
  private static final String USERNAME = "FixtureOwner";
  private static final String LOG_REQUEST = "LGSREQ01";
  private static final String START = "20260101000000000";
  private static final String METHOD = "HTTP method";
  private static final String QUESTION = "質問本文";

  @Test
  void sem001PasswordCharacterByteAndUsernameLimits() {
    // Fixed independent counts: ASCII 12/128 and 64 four-byte codepoints are accepted.
    for (String password : List.of("A".repeat(12), "A".repeat(128), "😀".repeat(64))) {
      assertDoesNotThrow(() -> validate(user(USERNAME, password)));
    }
    for (String password :
        List.of(
            "A".repeat(11),
            "A".repeat(129),
            "😀".repeat(65),
            "A".repeat(11) + " ",
            USERNAME,
            "FIXTUREOWNER")) {
      assertThrows(LayoutValidationException.class, () -> validate(user(USERNAME, password)));
    }
    assertThrows(LayoutValidationException.class, () -> validate(user("bad!", "A".repeat(12))));
    for (String password : List.of("A".repeat(128), "😀".repeat(64))) {
      assertDoesNotThrow(
          () -> validate(values("UPWREQ01", Map.of("New Password", text(password)))));
    }
  }

  @Test
  void sem002InclusiveDateLimitsAndOneSidedFilters() {
    assertDoesNotThrow(() -> validate(dates(LOG_REQUEST, text(START), text("20260201000000000"))));
    assertThrows(
        LayoutValidationException.class,
        () -> validate(dates(LOG_REQUEST, text(START), text("20260201000000001"))));
    assertThrows(
        LayoutValidationException.class,
        () -> validate(dates(LOG_REQUEST, text("20260201000000000"), text(START))));
    assertDoesNotThrow(() -> validate(dates("NTSREQ01", text(START), text("20270102000000000"))));
    assertThrows(
        LayoutValidationException.class,
        () -> validate(dates("NTSREQ01", text(START), text("20270102000000001"))));
    assertDoesNotThrow(
        () -> validate(dates(LOG_REQUEST, FieldValue.Unset.INSTANCE, FieldValue.Unset.INSTANCE)));
    assertDoesNotThrow(() -> validate(dates(LOG_REQUEST, text(START), FieldValue.Unset.INSTANCE)));
    assertDoesNotThrow(() -> validate(dates(LOG_REQUEST, FieldValue.Unset.INSTANCE, text(START))));
  }

  @Test
  void sem003QuestionAndWebLogTextContracts() {
    assertDoesNotThrow(
        () -> validate(values("QSBREQ01", Map.of(QUESTION, text("independent question")))));
    for (String question : List.of("", "question ")) {
      assertThrows(
          LayoutValidationException.class,
          () -> validate(values("QSBREQ01", Map.of(QUESTION, text(question)))));
    }
    for (String method : List.of("GET", "ABCDEFGH")) {
      assertDoesNotThrow(() -> validate(log(method, "/safe")));
    }
    for (String method : List.of("get", "GE", "ABCDEFGHI")) {
      assertThrows(LayoutValidationException.class, () -> validate(log(method, "/safe")));
    }
    for (String path : List.of("relative", "/safe?q=fixture")) {
      assertThrows(LayoutValidationException.class, () -> validate(log("GET", path)));
    }
  }

  private static TypedPayloadValues user(String username, String password) {
    return values(
        "UCRREQ01", Map.of("Username", text(username), "Initial Password", text(password)));
  }

  private static TypedPayloadValues dates(String layout, FieldValue from, FieldValue to) {
    boolean log = layout.equals(LOG_REQUEST);
    return values(
        layout,
        Map.of(
            "Page",
            new FieldValue.Numeric(1),
            "Page size",
            new FieldValue.Numeric(log ? 100 : 50),
            log ? "From日時" : "受付日時From",
            from,
            log ? "To日時" : "受付日時To",
            to));
  }

  private static TypedPayloadValues log(String method, String path) {
    return values("WLGEVT01", Map.of(METHOD, text(method), "Path", text(path)));
  }

  private static FieldValue text(String value) {
    return new FieldValue.Text(value);
  }

  private static TypedPayloadValues values(String layout, Map<String, FieldValue> fields) {
    FieldValueSet input = new FieldValueSet(fields);
    PayloadData data = () -> input;
    return new TypedPayloadValues(new LayoutId(layout), data, List.of());
  }

  private static void validate(TypedPayloadValues input) {
    PayloadSemanticValidator.validate(input);
  }
}
