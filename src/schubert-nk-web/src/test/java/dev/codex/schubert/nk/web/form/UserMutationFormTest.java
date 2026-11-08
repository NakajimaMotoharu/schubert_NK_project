package dev.codex.schubert.nk.web.form;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.PayloadValues;
import dev.codex.schubert.nk.protocol.layout.admin.PasswordResetRequestData;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.function.BooleanSupplier;
import java.util.function.Supplier;
import org.junit.jupiter.api.Test;

/** UI225236/SS313314 independent literal offsets; PG-D353/016069/CHANGE001..016. */
class UserMutationFormTest {
  private static final String STATUS_OPERATION = "STATUS";
  private static final String ROLE_OPERATION = "ROLE";
  private static final String PASSWORD_OPERATION = "PASSWORD";
  private static final String UNLOCK_OPERATION = "UNLOCK";
  private static final String EXPECTED_VERSION_FIELD = "expected_version";
  private static final String TRUE_TEXT = "true";
  private static final String OPERATION_TOKEN_FIELD = "operation_token";
  private static final String ENABLED_FIELD = "enabled";
  private static final String ROLE_FIELD = "role";
  private static final String USER_ROLE_TEXT = "USER";
  private static final String PASSWORD_FIELD = "password";
  private static final String PASSWORD_CONFIRMATION_FIELD = "password_confirmation";
  private static final String SYNTHETIC_TARGET_USERNAME = "target";
  private static final String TOKEN = "12345678-1234-4234-8234-123456789abc";
  private static final String PASSWORD = "TestPassword123!";
  private static final List<String> OPERATIONS =
      List.of(STATUS_OPERATION, ROLE_OPERATION, PASSWORD_OPERATION, UNLOCK_OPERATION);

  private record Form(
      Object owner,
      Runnable closer,
      BooleanSupplier valid,
      Supplier<Map<String, String>> issues,
      Supplier<Map<String, Object>> display,
      Supplier<PayloadData> request)
      implements AutoCloseable {
    @Override
    public void close() {
      closer.run();
    }
  }

  private static Form bind(
      String operation, long id, String username, Map<String, List<String>> p) {
    return switch (operation) {
      case STATUS_OPERATION -> {
        var f = UserStatusForm.bind(id, p);
        yield new Form(f, f::close, f::isValid, f::getIssues, f::displayValues, f::toRequest);
      }
      case ROLE_OPERATION -> {
        var f = UserRoleForm.bind(id, p);
        yield new Form(f, f::close, f::isValid, f::getIssues, f::displayValues, f::toRequest);
      }
      case PASSWORD_OPERATION -> {
        var f = PasswordResetForm.bind(id, username, p);
        yield new Form(f, f::close, f::isValid, f::getIssues, f::displayValues, f::toRequest);
      }
      case UNLOCK_OPERATION -> {
        var f = UserUnlockForm.bind(id, p);
        yield new Form(f, f::close, f::isValid, f::getIssues, f::displayValues, f::toRequest);
      }
      default -> throw new AssertionError("test operation");
    };
  }

  private static Map<String, List<String>> input(String operation, long id) {
    var p = new HashMap<String, List<String>>();
    p.put("operation", List.of(operation));
    p.put("id", List.of(Long.toString(id)));
    p.put(EXPECTED_VERSION_FIELD, List.of("7"));
    p.put("confirm", List.of(TRUE_TEXT));
    p.put(OPERATION_TOKEN_FIELD, List.of(TOKEN));
    switch (operation) {
      case STATUS_OPERATION -> p.put(ENABLED_FIELD, List.of(TRUE_TEXT));
      case ROLE_OPERATION -> p.put(ROLE_FIELD, List.of(USER_ROLE_TEXT));
      case PASSWORD_OPERATION -> {
        p.put(PASSWORD_FIELD, List.of(PASSWORD));
        p.put(PASSWORD_CONFIRMATION_FIELD, List.of(PASSWORD));
      }
      default -> {}
    }
    return p;
  }

  private static void put(byte[] b, int offset, String v) {
    byte[] raw = v.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(raw, 0, b, offset, raw.length);
  }

  /** UI236 offset/length literals, independent of the production layout catalog/encoder. */
  private static byte[] golden(String op, long id, long version, String value, String token) {
    int size =
        switch (op) {
          case ROLE_OPERATION -> 68;
          case PASSWORD_OPERATION -> 324;
          default -> 60;
        };
    byte[] b = new byte[size];
    Arrays.fill(b, (byte) ' ');
    put(b, 0, String.format(Locale.ROOT, "%012d", id));
    int versionAt =
        switch (op) {
          case STATUS_OPERATION -> {
            b[12] = (byte) (value.equals(TRUE_TEXT) ? '1' : '0');
            yield 13;
          }
          case ROLE_OPERATION -> {
            put(b, 12, value);
            yield 17;
          }
          case PASSWORD_OPERATION -> {
            put(b, 12, value);
            yield 268;
          }
          default -> 12;
        };
    put(b, versionAt, String.format(Locale.ROOT, "%09d", version));
    put(b, versionAt + 9, token);
    return b;
  }

  private static byte[] wire(String operation, PayloadData data) {
    String layout =
        switch (operation) {
          case STATUS_OPERATION -> "USTREQ01";
          case ROLE_OPERATION -> "URLREQ01";
          case PASSWORD_OPERATION -> "UPWREQ01";
          default -> "ULKREQ01";
        };
    return PayloadCodec.standard()
        .encode(new PayloadValues(new LayoutId(layout), data.fields(), List.of()), false)
        .copyData();
  }

  private static void invalid(String op, String field, String value) throws Exception {
    var p = input(op, 1);
    p.put(field, List.of(value));
    try (var f = bind(op, 1, SYNTHETIC_TARGET_USERNAME, p)) {
      assertFalse(f.valid.getAsBoolean(), op + "/" + field);
      assertEquals("入力項目を確認してください。", f.issues.get().get(field));
      assertEquals(
          "invalid user mutation form",
          assertThrows(IllegalArgumentException.class, f.request::get).getMessage());
    }
  }

  private static void boundaries(String op, String value) throws Exception {
    for (long id : new long[] {1, 999999999999L})
      for (long version : new long[] {0, 999999999}) {
        var p = input(op, id);
        p.put(EXPECTED_VERSION_FIELD, List.of(Long.toString(version)));
        if (op.equals(STATUS_OPERATION)) p.put(ENABLED_FIELD, List.of(value));
        if (op.equals(ROLE_OPERATION)) p.put(ROLE_FIELD, List.of(value));
        try (var f = bind(op, id, SYNTHETIC_TARGET_USERNAME, p)) {
          assertTrue(f.valid.getAsBoolean());
          assertArrayEquals(golden(op, id, version, value, TOKEN), wire(op, f.request.get()));
          assertEquals(id, f.display.get().get("id"));
          assertEquals(version, f.display.get().get(EXPECTED_VERSION_FIELD));
        }
      }
  }

  @Test
  void change001StatusGolden() throws Exception {
    boundaries(STATUS_OPERATION, TRUE_TEXT);
    boundaries(STATUS_OPERATION, "false");
  }

  @Test
  void change002RoleGolden() throws Exception {
    boundaries(ROLE_OPERATION, USER_ROLE_TEXT);
    boundaries(ROLE_OPERATION, "ADMIN");
  }

  @Test
  void change003UnlockGolden() throws Exception {
    boundaries(UNLOCK_OPERATION, "");
  }

  @Test
  void change004PasswordGoldenAndNoSecretProjection() throws Exception {
    boundaries(PASSWORD_OPERATION, PASSWORD);
    try (var f =
        bind(PASSWORD_OPERATION, 1, SYNTHETIC_TARGET_USERNAME, input(PASSWORD_OPERATION, 1))) {
      assertEquals(Map.of("id", 1L, EXPECTED_VERSION_FIELD, 7L), f.display.get());
      assertEquals(PASSWORD, ((PasswordResetRequestData) f.request.get()).newPassword());
    }
  }

  @Test
  void change005OperationAndUnknownFieldRejection() throws Exception {
    for (String op : OPERATIONS) {
      for (String value : List.of("", "status", "UNKNOWN", " " + op, op + " "))
        invalid(op, "operation", value);
      for (String other : OPERATIONS) if (!other.equals(op)) invalid(op, "operation", other);
      for (String field :
          List.of(
              "owner",
              "username",
              "authenticationContext",
              ENABLED_FIELD,
              ROLE_FIELD,
              PASSWORD_FIELD,
              PASSWORD_CONFIRMATION_FIELD)) {
        var p = input(op, 1);
        if (p.containsKey(field)) continue;
        p.put(field, List.of("synthetic-secret-canary"));
        try (var f = bind(op, 1, SYNTHETIC_TARGET_USERNAME, p)) {
          assertFalse(f.valid.getAsBoolean());
          assertTrue(f.issues.get().containsKey("form"));
        }
      }
    }
    assertThrows(
        IllegalArgumentException.class,
        () -> UserMutationInput.bind("OTHER", 1, "", input(UNLOCK_OPERATION, 1)));
    assertThrows(
        NullPointerException.class,
        () -> UserMutationInput.bind(null, 1, "", input(UNLOCK_OPERATION, 1)));
  }

  @Test
  void change006PathAndHiddenIdentifier() throws Exception {
    for (String op : OPERATIONS) {
      for (long id : new long[] {0, -1, 1000000000000L, Long.MAX_VALUE})
        assertThrows(
            IllegalArgumentException.class,
            () -> bind(op, id, SYNTHETIC_TARGET_USERNAME, input(op, 1)));
      for (String id :
          List.of("", "0", "2", "-1", "+1", "１", "1.0", "1 ", "1000000000000", "9".repeat(30)))
        invalid(op, "id", id);
      var p = input(op, 1);
      p.put("id", List.of("000000000001"));
      try (var f = bind(op, 1, SYNTHETIC_TARGET_USERNAME, p)) {
        assertTrue(f.valid.getAsBoolean());
        assertEquals(1L, f.display.get().get("id"));
      }
    }
  }

  @Test
  void change007VersionSyntax() throws Exception {
    for (String op : OPERATIONS)
      for (String version : List.of("", "-1", "+1", "1000000000", "１", "1e1", "1 ", "9".repeat(30)))
        invalid(op, EXPECTED_VERSION_FIELD, version);
  }

  @Test
  void change008ConfirmAndTokenSyntax() throws Exception {
    for (String op : OPERATIONS) {
      for (String confirm : List.of("", "false", "on", "TRUE", "true "))
        invalid(op, "confirm", confirm);
      for (String token :
          List.of(
              "",
              TOKEN.toUpperCase(Locale.ROOT),
              "1-1-1-1-1",
              " " + TOKEN,
              TOKEN + " ",
              "g" + TOKEN.substring(1))) invalid(op, OPERATION_TOKEN_FIELD, token);
      for (String token :
          List.of("00000000-0000-0000-0000-000000000000", "ffffffff-ffff-ffff-ffff-ffffffffffff")) {
        var p = input(op, 1);
        p.put(OPERATION_TOKEN_FIELD, List.of(token));
        String value =
            switch (op) {
              case STATUS_OPERATION -> TRUE_TEXT;
              case ROLE_OPERATION -> USER_ROLE_TEXT;
              case PASSWORD_OPERATION -> PASSWORD;
              default -> "";
            };
        try (var f = bind(op, 1, SYNTHETIC_TARGET_USERNAME, p)) {
          assertTrue(f.valid.getAsBoolean());
          assertArrayEquals(golden(op, 1, 7, value, token), wire(op, f.request.get()));
        }
      }
    }
  }

  @Test
  void change009ClosedRoleAndBoolean() throws Exception {
    for (String flag : List.of("", "TRUE", "1", "0", "false "))
      invalid(STATUS_OPERATION, ENABLED_FIELD, flag);
    for (String role : List.of("", "user", "OTHER", "ADMIN "))
      invalid(ROLE_OPERATION, ROLE_FIELD, role);
  }

  @Test
  void change010PasswordNfcCodepointByteBoundaries() throws Exception {
    for (String value :
        List.of(
            "p".repeat(12),
            "p".repeat(128),
            "é".repeat(128),
            "😀".repeat(64),
            "😀".repeat(12),
            " password123",
            "é".repeat(12),
            "x\ue000".repeat(6))) {
      var p = input(PASSWORD_OPERATION, 1);
      p.put(PASSWORD_FIELD, List.of(value.equals("é".repeat(12)) ? "e\u0301".repeat(12) : value));
      p.put(PASSWORD_CONFIRMATION_FIELD, List.of(value));
      try (var f = bind(PASSWORD_OPERATION, 1, SYNTHETIC_TARGET_USERNAME, p)) {
        assertTrue(f.valid.getAsBoolean());
        assertArrayEquals(
            golden(PASSWORD_OPERATION, 1, 7, value, TOKEN),
            wire(PASSWORD_OPERATION, f.request.get()));
      }
    }
  }

  @Test
  void change011PasswordInvalidAndTrustedUsername() throws Exception {
    for (String value :
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
            "password123\udfff")) invalid(PASSWORD_OPERATION, PASSWORD_FIELD, value);
    invalid(PASSWORD_OPERATION, PASSWORD_CONFIRMATION_FIELD, "OtherPassword123!");
    var p = input(PASSWORD_OPERATION, 1);
    p.put(PASSWORD_FIELD, List.of("testpassword123"));
    p.put(PASSWORD_CONFIRMATION_FIELD, List.of("testpassword123"));
    try (var f = bind(PASSWORD_OPERATION, 1, " TestPassword123 ", p)) {
      assertFalse(f.valid.getAsBoolean());
      assertTrue(f.issues.get().containsKey(PASSWORD_FIELD));
    }
    p.put(PASSWORD_FIELD, List.of("é".repeat(12)));
    p.put(PASSWORD_CONFIRMATION_FIELD, List.of("é".repeat(12)));
    try (var f = bind(PASSWORD_OPERATION, 1, "e\u0301".repeat(12), p)) {
      assertFalse(f.valid.getAsBoolean());
      assertTrue(f.issues.get().containsKey(PASSWORD_FIELD));
    }
    assertThrows(
        IllegalArgumentException.class,
        () -> PasswordResetForm.bind(1, " ", input(PASSWORD_OPERATION, 1)));
    assertThrows(
        NullPointerException.class,
        () -> PasswordResetForm.bind(1, null, input(PASSWORD_OPERATION, 1)));
    try (var f = PasswordResetForm.bind(1, "現行利用者", input(PASSWORD_OPERATION, 1))) {
      assertTrue(f.isValid());
    }
  }

  @Test
  void change012NullMissingAndDuplicates() throws Exception {
    for (String op : OPERATIONS) {
      assertThrows(NullPointerException.class, () -> bind(op, 1, SYNTHETIC_TARGET_USERNAME, null));
      var nullableKey = input(op, 1);
      nullableKey.put(null, List.of("x"));
      assertThrows(
          NullPointerException.class, () -> bind(op, 1, SYNTHETIC_TARGET_USERNAME, nullableKey));
      for (String field : input(op, 1).keySet()) {
        var missing = input(op, 1);
        missing.remove(field);
        try (var f = bind(op, 1, SYNTHETIC_TARGET_USERNAME, missing)) {
          assertFalse(f.valid.getAsBoolean());
          assertTrue(f.issues.get().containsKey(field));
        }
        for (List<String> list : List.of(List.<String>of(), List.of("a", "b"))) {
          var p = input(op, 1);
          p.put(field, list);
          try (var f = bind(op, 1, SYNTHETIC_TARGET_USERNAME, p)) {
            assertFalse(f.valid.getAsBoolean());
            assertTrue(f.issues.get().containsKey(field));
            assertTrue(f.issues.get().containsKey("form"));
          }
        }
        var p = input(op, 1);
        p.put(field, null);
        assertThrows(NullPointerException.class, () -> bind(op, 1, SYNTHETIC_TARGET_USERNAME, p));
        p.put(field, Arrays.asList((String) null));
        assertThrows(NullPointerException.class, () -> bind(op, 1, SYNTHETIC_TARGET_USERNAME, p));
      }
      for (String extra : List.of("_csrf", "unknown")) {
        var p = input(op, 1);
        p.put(extra, List.of("synthetic-csrf-canary"));
        try (var f = bind(op, 1, SYNTHETIC_TARGET_USERNAME, p)) {
          assertEquals(extra.equals("_csrf"), f.valid.getAsBoolean());
        }
        for (List<String> list : List.of(List.<String>of(), List.of("a", "b"))) {
          p.put(extra, list);
          try (var f = bind(op, 1, SYNTHETIC_TARGET_USERNAME, p)) {
            assertFalse(f.valid.getAsBoolean());
            assertTrue(f.issues.get().containsKey("form"));
          }
        }
      }
    }
  }

  @Test
  void change013ImmutableSnapshotAndRedaction() throws Exception {
    for (String op : OPERATIONS) {
      var p = input(op, 1);
      var id = new ArrayList<>(List.of("1"));
      p.put("id", id);
      try (var f = bind(op, 1, SYNTHETIC_TARGET_USERNAME, p)) {
        id.set(0, "2");
        p.clear();
        assertTrue(f.valid.getAsBoolean());
        assertEquals(1L, f.display.get().get("id"));
        assertThrows(UnsupportedOperationException.class, () -> f.display.get().put("id", 2L));
        assertThrows(UnsupportedOperationException.class, () -> f.issues.get().put("id", "x"));
        assertEquals(f.owner.getClass().getSimpleName() + "[REDACTED]", f.owner.toString());
        assertFalse(f.display.get().toString().contains(TOKEN));
        assertFalse(f.display.get().toString().contains(PASSWORD));
      }
    }
    try (var raw = UserMutationInput.bind(UNLOCK_OPERATION, 1, "", input(UNLOCK_OPERATION, 1))) {
      assertEquals("UserMutationInput[REDACTED]", raw.toString());
    }
  }

  @Test
  void change014TerminalCloseAndSeparateDto() throws Exception {
    for (String op : OPERATIONS) {
      var p = input(op, 1);
      var f = bind(op, 1, SYNTHETIC_TARGET_USERNAME, p);
      try (var other = bind(op, 1, SYNTHETIC_TARGET_USERNAME, p)) {
        var request = f.request.get();
        var original = wire(op, request);
        f.close();
        f.close();
        assertTrue(f.valid.getAsBoolean());
        assertTrue(f.issues.get().isEmpty());
        assertEquals(
            "user mutation form is closed",
            assertThrows(IllegalStateException.class, f.request::get).getMessage());
        assertThrows(IllegalStateException.class, f.display::get);
        assertArrayEquals(original, wire(op, request));
        assertArrayEquals(original, wire(op, other.request.get()));
      } finally {
        f.close();
      }
      var invalid = input(op, 1);
      invalid.put("confirm", List.of("false"));
      try (var invalidForm = bind(op, 1, SYNTHETIC_TARGET_USERNAME, invalid)) {
        assertThrows(IllegalArgumentException.class, invalidForm.request::get);
        assertFalse(invalidForm.display.get().containsKey(PASSWORD_FIELD));
      }
    }
    var raw =
        UserMutationInput.bind(
            PASSWORD_OPERATION, 1, SYNTHETIC_TARGET_USERNAME, input(PASSWORD_OPERATION, 1));
    try {
      assertEquals(PASSWORD, raw.password());
      raw.close();
      assertThrows(IllegalStateException.class, raw::password);
    } finally {
      raw.close();
    }
    try (var invalidRaw =
        UserMutationInput.bind(PASSWORD_OPERATION, 1, SYNTHETIC_TARGET_USERNAME, Map.of())) {
      assertThrows(IllegalArgumentException.class, invalidRaw::password);
    }
  }

  @Test
  void change015OneHundredIndependentParallelOperations() throws Exception {
    var executor = Executors.newFixedThreadPool(8);
    try {
      var tasks = new ArrayList<Callable<Void>>();
      for (int i = 1; i <= 100; i++) {
        final int index = i;
        tasks.add(
            () -> {
              String op = OPERATIONS.get(index % 4);
              String token = String.format(Locale.ROOT, "12345678-1234-4234-8234-%012d", index);
              var p = input(op, index);
              p.put(OPERATION_TOKEN_FIELD, List.of(token));
              p.put(EXPECTED_VERSION_FIELD, List.of(Integer.toString(index)));
              String value =
                  switch (op) {
                    case STATUS_OPERATION -> TRUE_TEXT;
                    case ROLE_OPERATION -> USER_ROLE_TEXT;
                    case PASSWORD_OPERATION -> PASSWORD;
                    default -> "";
                  };
              try (var f = bind(op, index, SYNTHETIC_TARGET_USERNAME, p)) {
                assertTrue(f.valid.getAsBoolean());
                assertArrayEquals(
                    golden(op, index, index, value, token), wire(op, f.request.get()));
              }
              return null;
            });
      }
      for (var future : executor.invokeAll(tasks, 30, TimeUnit.SECONDS))
        future.get(30, TimeUnit.SECONDS);
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
    }
  }

  @Test
  void change016InputCannotGrantApiAuthority() throws Exception {
    // Existing UserCommand/Mutation SQL suites assert self/last ADMIN/version/revocation outcomes.
    // Here the form is only a typed wire boundary, never an authentication/authorization provider.
    for (String op : OPERATIONS) {
      var p = input(op, 1);
      p.put(EXPECTED_VERSION_FIELD, List.of("0"));
      try (var f = bind(op, 1, SYNTHETIC_TARGET_USERNAME, p)) {
        assertTrue(f.valid.getAsBoolean());
        var names = new HashSet<>(Set.of("User ID", "Expected version", "Operation token"));
        switch (op) {
          case STATUS_OPERATION -> names.add("Enabled");
          case ROLE_OPERATION -> names.add("New role");
          case PASSWORD_OPERATION -> names.add("New Password");
          default -> {}
        }
        assertEquals(names, f.request.get().fields().names());
        var display = new HashMap<String, Object>(Map.of("id", 1L, EXPECTED_VERSION_FIELD, 0L));
        if (op.equals(STATUS_OPERATION)) display.put(ENABLED_FIELD, true);
        if (op.equals(ROLE_OPERATION)) display.put(ROLE_FIELD, USER_ROLE_TEXT);
        assertEquals(display, f.display.get());
      }
      p.put("role_context", List.of("ADMIN"));
      try (var f = bind(op, 1, SYNTHETIC_TARGET_USERNAME, p)) {
        assertFalse(f.valid.getAsBoolean());
        assertThrows(IllegalArgumentException.class, f.request::get);
      }
    }
  }
}
