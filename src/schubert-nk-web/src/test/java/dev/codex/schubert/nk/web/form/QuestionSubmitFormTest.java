package dev.codex.schubert.nk.web.form;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadValues;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** UI224/236 independent 4144-byte oracle; PG-D351/016065/PT-QST-FORM001..008. */
class QuestionSubmitFormTest {
  private static final String QUESTION_FIELD = "question";
  private static final String OPERATION_TOKEN_FIELD = "operation_token";
  private static final String TOKEN = "12345678-1234-4234-8234-123456789abc";

  private static Map<String, List<String>> input(String question) {
    return new HashMap<>(
        Map.of(QUESTION_FIELD, List.of(question), OPERATION_TOKEN_FIELD, List.of(TOKEN)));
  }

  private static byte[] golden(String question, String token) {
    byte[] result = new byte[4144];
    Arrays.fill(result, (byte) ' ');
    byte[] body = question.getBytes(StandardCharsets.UTF_8);
    byte[] identifier = token.getBytes(StandardCharsets.US_ASCII);
    System.arraycopy(body, 0, result, 0, body.length);
    System.arraycopy(identifier, 0, result, 4096, identifier.length);
    return result;
  }

  private static byte[] actual(QuestionSubmitForm form) {
    return PayloadCodec.standard()
        .encode(
            new PayloadValues(new LayoutId("QSBREQ01"), form.toRequest().fields(), List.of()),
            false)
        .copyData();
  }

  private static void invalid(String field, String value) {
    var parameters = input("質問");
    parameters.put(field, List.of(value));
    try (var form = QuestionSubmitForm.bind(parameters)) {
      assertFalse(form.isValid());
      assertTrue(form.getIssues().containsKey(field));
      assertEquals("入力項目を確認してください。", form.getIssues().get(field));
      var failure = assertThrows(IllegalArgumentException.class, form::toRequest);
      assertEquals("invalid question submit form", failure.getMessage());
    }
  }

  @Test
  void qstForm001IndependentGoldenAndNoQuestionTrimming() {
    for (String body : List.of("x", "質問", " leading", "<script>&界", "e\u0301")) {
      String expected = body.equals("e\u0301") ? "é" : body;
      try (var form = QuestionSubmitForm.bind(input(body))) {
        assertTrue(form.isValid());
        assertEquals(expected, form.toRequest().questionText());
        assertEquals(UUID.fromString(TOKEN), form.toRequest().operationToken());
        assertEquals(Map.of(QUESTION_FIELD, expected), form.displayValues());
        assertArrayEquals(golden(expected, TOKEN), actual(form));
      }
    }
  }

  @Test
  void qstForm002ByteBoundariesAfterNfcWithoutTruncation() {
    for (String body :
        List.of(
            "a", "a".repeat(4096), "界".repeat(1365) + "a", "😀".repeat(1024), "é".repeat(2048))) {
      var parameters = input(body.equals("é".repeat(2048)) ? "e\u0301".repeat(2048) : body);
      try (var form = QuestionSubmitForm.bind(parameters)) {
        assertTrue(form.isValid());
        assertArrayEquals(golden(body, TOKEN), actual(form));
      }
    }
    for (String body :
        List.of("", "a".repeat(4097), "界".repeat(1366), "😀".repeat(1025), "é".repeat(2049)))
      invalid(QUESTION_FIELD, body);
    try (var form = QuestionSubmitForm.bind(input("a".repeat(4097)))) {
      assertEquals("a".repeat(4097), form.displayValues().get(QUESTION_FIELD));
    }
  }

  @Test
  void qstForm003ControlsUnicodeAndTrailingSpaceAreNotTrimmed() {
    for (String body :
        List.of(
            " ", "x ", "x\r", "x\n", "x\t", "x\0", "x\u001f", "x\u007f", "x\u0085", "x\ud800",
            "x\udfff")) invalid(QUESTION_FIELD, body);
    for (String body : List.of("x\n", "\ud800", "\udfff"))
      try (var form = QuestionSubmitForm.bind(input(body))) {
        assertEquals("", form.displayValues().get(QUESTION_FIELD));
      }
    for (String body : List.of(" x", "x\u00a0", "x\u3000", "\ue000", "😀"))
      try (var form = QuestionSubmitForm.bind(input(body))) {
        assertTrue(form.isValid());
        assertEquals(body, form.toRequest().questionText());
      }
  }

  @Test
  void qstForm004CanonicalUuidSyntaxWithoutIssuingAuthorization() {
    for (String token :
        List.of(
            "",
            TOKEN.toUpperCase(Locale.ROOT),
            " " + TOKEN,
            TOKEN + " ",
            TOKEN.substring(1),
            TOKEN + "0",
            "g" + TOKEN.substring(1))) invalid(OPERATION_TOKEN_FIELD, token);
    for (String token :
        List.of(
            TOKEN,
            "00000000-0000-0000-0000-000000000000",
            "ffffffff-ffff-ffff-ffff-ffffffffffff")) {
      var parameters = input("x");
      parameters.put(OPERATION_TOKEN_FIELD, List.of(token));
      try (var form = QuestionSubmitForm.bind(parameters)) {
        assertTrue(form.isValid());
        assertEquals(UUID.fromString(token), form.toRequest().operationToken());
        assertArrayEquals(golden("x", token), actual(form));
      }
    }
  }

  @Test
  void qstForm005ClosedBindingMissingDuplicateAndNullContracts() {
    for (String field : List.of(QUESTION_FIELD, OPERATION_TOKEN_FIELD)) {
      var parameters = input("x");
      parameters.remove(field);
      try (var form = QuestionSubmitForm.bind(parameters)) {
        assertFalse(form.isValid());
        assertTrue(form.getIssues().containsKey(field));
      }
      for (List<String> list : List.of(List.<String>of(), List.of("a", "b"))) {
        parameters = input("x");
        parameters.put(field, list);
        try (var form = QuestionSubmitForm.bind(parameters)) {
          assertFalse(form.isValid());
          assertTrue(form.getIssues().containsKey(field));
          assertTrue(form.getIssues().containsKey("form"));
        }
      }
    }
    for (String field : List.of("unknown", "_csrf")) {
      var parameters = input("x");
      parameters.put(field, List.of("synthetic-csrf-canary"));
      try (var form = QuestionSubmitForm.bind(parameters)) {
        assertEquals(field.equals("_csrf"), form.isValid());
        assertFalse(form.displayValues().toString().contains("synthetic-csrf-canary"));
      }
      for (List<String> list : List.of(List.<String>of(), List.of("a", "b"))) {
        parameters.put(field, list);
        try (var form = QuestionSubmitForm.bind(parameters)) {
          assertFalse(form.isValid());
          assertTrue(form.getIssues().containsKey("form"));
        }
      }
    }
    assertThrows(NullPointerException.class, () -> QuestionSubmitForm.bind(null));
    var parameters = input("x");
    parameters.put(null, List.of("x"));
    assertThrows(NullPointerException.class, () -> QuestionSubmitForm.bind(parameters));
    parameters.remove(null);
    for (String field : List.of(QUESTION_FIELD, OPERATION_TOKEN_FIELD)) {
      var nullable = input("x");
      nullable.put(field, null);
      assertThrows(NullPointerException.class, () -> QuestionSubmitForm.bind(nullable));
      nullable.put(field, Arrays.asList((String) null));
      assertThrows(NullPointerException.class, () -> QuestionSubmitForm.bind(nullable));
    }
  }

  @Test
  void qstForm006ImmutableSnapshotsAndRedaction() {
    var body = new ArrayList<>(List.of("質問"));
    var parameters = input("unused");
    parameters.put(QUESTION_FIELD, body);
    try (var form = QuestionSubmitForm.bind(parameters)) {
      body.set(0, "changed");
      parameters.clear();
      assertEquals(Map.of(QUESTION_FIELD, "質問"), form.displayValues());
      assertThrows(
          UnsupportedOperationException.class,
          () -> form.displayValues().put(QUESTION_FIELD, "change"));
      assertThrows(UnsupportedOperationException.class, () -> form.getIssues().put("x", "change"));
      assertEquals("QuestionSubmitForm[REDACTED]", form.toString());
      assertFalse(form.displayValues().toString().contains(TOKEN));
      assertEquals(Set.of(QUESTION_FIELD), form.displayValues().keySet());
    }
  }

  @Test
  void qstForm007TerminalClosePreservesOtherOwners() {
    var first = QuestionSubmitForm.bind(input("質問"));
    var request = first.toRequest();
    var display = first.displayValues();
    first.close();
    first.close();
    var failure = assertThrows(IllegalStateException.class, first::toRequest);
    assertEquals("question submit form is closed", failure.getMessage());
    assertThrows(IllegalStateException.class, first::displayValues);
    assertEquals("質問", request.questionText());
    assertEquals(Map.of(QUESTION_FIELD, "質問"), display);
    assertEquals("QuestionSubmitForm[REDACTED]", first.toString());
    try (var other = QuestionSubmitForm.bind(input("other"))) {
      assertEquals("other", other.toRequest().questionText());
    }
    var invalid = QuestionSubmitForm.bind(input(""));
    invalid.close();
    assertThrows(IllegalStateException.class, invalid::toRequest);
  }

  @Test
  void qstForm008ConcurrentIndependentBodiesAndTokens() throws Exception {
    try (var executor = Executors.newFixedThreadPool(8)) {
      var results = new ArrayList<Future<byte[]>>();
      for (int i = 1; i <= 100; i++) {
        int index = i;
        results.add(
            executor.submit(
                () -> {
                  String body = "question-" + index;
                  String token = String.format(Locale.ROOT, "12345678-1234-4234-8234-%012d", index);
                  var parameters = input(body);
                  parameters.put(OPERATION_TOKEN_FIELD, List.of(token));
                  try (var form = QuestionSubmitForm.bind(parameters)) {
                    assertTrue(form.isValid());
                    assertEquals(body, form.displayValues().get(QUESTION_FIELD));
                    byte[] encoded = actual(form);
                    assertArrayEquals(golden(body, token), encoded);
                    return encoded;
                  }
                }));
      }
      for (int i = 1; i <= 100; i++) {
        String token = String.format(Locale.ROOT, "12345678-1234-4234-8234-%012d", i);
        assertArrayEquals(
            golden("question-" + i, token), results.get(i - 1).get(30, TimeUnit.SECONDS));
      }
    }
  }
}
