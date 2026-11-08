package dev.codex.schubert.nk.web.form;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadValues;
import dev.codex.schubert.nk.protocol.layout.admin.UserCreateRequestData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** UI225/236 independent literals/372-byte oracle; PG-D345/016055/PT-USER-CREATE001..008. */
class UserCreateFormTest {
  private static final String USERNAME_FIELD = "username";
  private static final String SYNTHETIC_USERNAME = "user1";
  private static final String PASSWORD_FIELD = "password";
  private static final String PASSWORD_CONFIRMATION_FIELD = "password_confirmation";
  private static final String ROLE_FIELD = "role";
  private static final String USER_ROLE_TEXT = "USER";
  private static final String ENABLED_FIELD = "enabled";
  private static final String TOKEN = "12345678-1234-4234-8234-123456789abc";
  private static final String PASSWORD = "TestPassword123!";

  private static Map<String, List<String>> input() {
    return new HashMap<>(
        Map.of(
            USERNAME_FIELD,
            List.of(SYNTHETIC_USERNAME),
            PASSWORD_FIELD,
            List.of(PASSWORD),
            PASSWORD_CONFIRMATION_FIELD,
            List.of(PASSWORD),
            ROLE_FIELD,
            List.of(USER_ROLE_TEXT),
            ENABLED_FIELD,
            List.of("true"),
            "operation_token",
            List.of(TOKEN)));
  }

  private static void put(byte[] bytes, int offset, String value) {
    byte[] encoded = value.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(encoded, 0, bytes, offset, encoded.length);
  }

  private static byte[] golden(
      String username, String password, String role, boolean enabled, String token) {
    byte[] result = new byte[372];
    Arrays.fill(result, (byte) ' ');
    put(result, 0, username);
    put(result, 64, password);
    put(result, 320, role);
    result[325] = (byte) (enabled ? '1' : '0');
    put(result, 326, token);
    return result;
  }

  private static byte[] encode(UserCreateRequestData request) {
    return PayloadCodec.standard()
        .encode(new PayloadValues(new LayoutId("UCRREQ01"), request.fields(), List.of()), false)
        .copyData();
  }

  private static void invalid(String field, String value) {
    var parameters = input();
    parameters.put(field, List.of(value));
    try (var form = UserCreateForm.bind(parameters)) {
      assertFalse(form.isValid(), field);
      assertTrue(form.getIssues().containsKey(field), field);
      var failure = assertThrows(IllegalArgumentException.class, form::toRequest);
      assertEquals("invalid user create form", failure.getMessage());
      assertEquals("UserCreateForm[REDACTED]", form.toString());
    }
  }

  @Test
  void create001IndependentWireAndClosedRoleEnabledValues() {
    for (String role : List.of(USER_ROLE_TEXT, "ADMIN"))
      for (boolean enabled : List.of(true, false)) {
        var values = input();
        values.put(ROLE_FIELD, List.of(role));
        values.put(ENABLED_FIELD, List.of(Boolean.toString(enabled)));
        try (var form = UserCreateForm.bind(values)) {
          assertTrue(form.isValid());
          var request = form.toRequest();
          assertEquals(UserRole.valueOf(role), request.role());
          assertEquals(enabled, request.enabled());
          assertEquals(UUID.fromString(TOKEN), request.operationToken());
          assertArrayEquals(
              golden(SYNTHETIC_USERNAME, PASSWORD, role, enabled, TOKEN), encode(request));
        }
      }
  }

  @Test
  void create002NfcCodePointAndByteBoundariesWithoutPasswordTrimming() {
    for (String password :
        List.of(
            "p".repeat(12),
            "p".repeat(128),
            "é".repeat(128),
            "😀".repeat(64),
            "😀".repeat(12),
            " password123",
            "é".repeat(12))) {
      var values = input();
      values.put(USERNAME_FIELD, List.of("  USER._-01  "));
      values.put(
          PASSWORD_FIELD,
          List.of(password.equals("é".repeat(12)) ? "e\u0301".repeat(12) : password));
      values.put(PASSWORD_CONFIRMATION_FIELD, List.of(password));
      try (var form = UserCreateForm.bind(values)) {
        assertTrue(form.isValid());
        assertEquals("USER._-01", form.displayValues().get(USERNAME_FIELD));
        assertEquals(password, form.toRequest().initialPassword());
        assertArrayEquals(
            golden("USER._-01", password, USER_ROLE_TEXT, true, TOKEN), encode(form.toRequest()));
      }
    }
    for (String username : List.of("a", "a".repeat(64), ".", "-", "_", "A09._-")) {
      var values = input();
      values.put(USERNAME_FIELD, List.of(username));
      try (var form = UserCreateForm.bind(values)) {
        assertTrue(form.isValid());
        assertEquals(username, form.toRequest().username());
      }
    }
  }

  @Test
  void create003RequiredClosedBindingAndNullContracts() {
    for (String field : input().keySet()) {
      var missing = input();
      missing.remove(field);
      try (var form = UserCreateForm.bind(missing)) {
        assertFalse(form.isValid());
        assertTrue(form.getIssues().containsKey(field));
        assertThrows(IllegalArgumentException.class, form::toRequest);
      }
      for (List<String> list : List.of(List.<String>of(), List.of("first", "second"))) {
        var values = input();
        values.put(field, list);
        try (var form = UserCreateForm.bind(values)) {
          assertFalse(form.isValid());
          assertTrue(form.getIssues().containsKey(field));
        }
      }
    }
    for (String field : List.of("unexpected", "_csrf")) {
      var values = input();
      values.put(field, List.of("synthetic-csrf-canary"));
      try (var form = UserCreateForm.bind(values)) {
        assertEquals(field.equals("_csrf"), form.isValid());
        assertFalse(form.displayValues().toString().contains("synthetic-csrf-canary"));
      }
      values.put(field, List.of());
      try (var form = UserCreateForm.bind(values)) {
        assertFalse(form.isValid());
        assertTrue(form.getIssues().containsKey("form"));
      }
      values.put(field, List.of("a", "b"));
      try (var form = UserCreateForm.bind(values)) {
        assertFalse(form.isValid());
      }
    }
    assertThrows(NullPointerException.class, () -> UserCreateForm.bind(null));
    for (String field : input().keySet()) {
      var values = input();
      values.put(field, null);
      assertThrows(NullPointerException.class, () -> UserCreateForm.bind(values));
      values.put(field, Arrays.asList((String) null));
      assertThrows(NullPointerException.class, () -> UserCreateForm.bind(values));
    }
    var values = input();
    values.put(null, List.of("x"));
    assertThrows(NullPointerException.class, () -> UserCreateForm.bind(values));
  }

  @Test
  void create004UsernamePasswordAndUnicodeRejections() {
    for (String username :
        List.of(
            "",
            " ",
            "a".repeat(65),
            "user:name",
            "user/name",
            "é",
            "user name",
            "user\u0000name",
            "user\ud800name",
            "user\udfffname")) invalid(USERNAME_FIELD, username);
    for (String password :
        List.of(
            "",
            "p".repeat(11),
            "p".repeat(129),
            "é".repeat(128) + "x",
            "😀".repeat(65),
            "password123 ",
            "password123\n",
            "password123\u007f",
            "password123\u0085",
            "password123\ud800",
            "password123\udfff")) invalid(PASSWORD_FIELD, password);
    var values = input();
    values.put(USERNAME_FIELD, List.of("TestPassword123"));
    values.put(PASSWORD_FIELD, List.of("testpassword123"));
    values.put(PASSWORD_CONFIRMATION_FIELD, List.of("testpassword123"));
    try (var form = UserCreateForm.bind(values)) {
      assertFalse(form.isValid());
      assertTrue(form.getIssues().containsKey(PASSWORD_FIELD));
    }
  }

  @Test
  void create005ConfirmationEnumFlagAndCanonicalToken() {
    invalid(PASSWORD_CONFIRMATION_FIELD, "OtherPassword123!");
    for (String role : List.of("", "user", "UNKNOWN", " USER")) invalid(ROLE_FIELD, role);
    for (String enabled : List.of("", "TRUE", "1", "0", "false ")) invalid(ENABLED_FIELD, enabled);
    for (String token :
        List.of(
            "",
            TOKEN.toUpperCase(Locale.ROOT),
            "1-1-1-1-1",
            "invalid",
            TOKEN + " ",
            TOKEN.replace('a', 'g'))) invalid("operation_token", token);
  }

  @Test
  void create006ImmutableProjectionAndSecretLifetime() {
    var values = input();
    var passwords = new ArrayList<>(List.of(PASSWORD));
    values.put(PASSWORD_FIELD, passwords);
    try (var form = UserCreateForm.bind(values)) {
      passwords.set(0, "ChangedPassword123!");
      values.clear();
      assertEquals(PASSWORD, form.toRequest().initialPassword());
      assertEquals(
          Map.of(
              USERNAME_FIELD, SYNTHETIC_USERNAME, ROLE_FIELD, USER_ROLE_TEXT, ENABLED_FIELD, true),
          form.displayValues());
      assertThrows(UnsupportedOperationException.class, () -> form.displayValues().clear());
      assertThrows(
          UnsupportedOperationException.class, () -> form.getIssues().put("secret", PASSWORD));
      assertEquals("UserCreateForm[REDACTED]", form.toString());
      assertFalse(form.displayValues().toString().contains(PASSWORD));
      assertFalse(form.displayValues().toString().contains(TOKEN));
      assertFalse(form.getIssues().toString().contains(PASSWORD));
      assertEquals("UserCreateRequestData[REDACTED]", form.toRequest().toString());
      assertDoesNotThrow(form::close);
      assertDoesNotThrow(form::close);
      var failure = assertThrows(IllegalStateException.class, form::toRequest);
      assertEquals("user create form is closed", failure.getMessage());
      assertEquals(SYNTHETIC_USERNAME, form.displayValues().get(USERNAME_FIELD));
    }
  }

  @Test
  void create007OneHundredConcurrentIndependentRequests() throws Exception {
    var executor = Executors.newFixedThreadPool(8);
    try {
      var results = new ArrayList<Future<Void>>();
      for (int i = 1; i <= 100; i++) {
        int n = i;
        results.add(
            executor.submit(
                () -> {
                  String name = "user" + n;
                  String password = "SyntheticPassword-" + n;
                  String token = String.format(Locale.ROOT, "12345678-1234-4234-8234-%012x", n);
                  var values = input();
                  values.put(USERNAME_FIELD, List.of(name));
                  values.put(PASSWORD_FIELD, List.of(password));
                  values.put(PASSWORD_CONFIRMATION_FIELD, List.of(password));
                  values.put("operation_token", List.of(token));
                  try (var form = UserCreateForm.bind(values)) {
                    assertTrue(form.isValid());
                    assertArrayEquals(
                        golden(name, password, USER_ROLE_TEXT, true, token),
                        encode(form.toRequest()));
                    assertFalse(form.displayValues().toString().contains(password));
                  }
                  return null;
                }));
      }
      for (var result : results) assertNull(result.get(10, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
    }
  }

  @Test
  void create008InvalidSecretsRemainAbsentAndClosedInvalidCannotSend() {
    var values = input();
    values.put(PASSWORD_CONFIRMATION_FIELD, List.of("SecretCanaryDifferent123!"));
    try (var form = UserCreateForm.bind(values)) {
      assertEquals(Map.of(PASSWORD_CONFIRMATION_FIELD, "入力項目を確認してください。"), form.getIssues());
      assertEquals(
          Map.of(
              USERNAME_FIELD, SYNTHETIC_USERNAME, ROLE_FIELD, USER_ROLE_TEXT, ENABLED_FIELD, true),
          form.displayValues());
      assertFalse(form.toString().contains("SecretCanary"));
      assertThrows(IllegalArgumentException.class, form::toRequest);
      assertDoesNotThrow(form::close);
      assertThrows(IllegalStateException.class, form::toRequest);
    }
  }
}
