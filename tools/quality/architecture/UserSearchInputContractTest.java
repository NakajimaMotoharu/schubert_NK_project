package dev.codex.schubert.nk.web.form;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.protocol.layout.semantic.UserState;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.Test;

/** FUN009/UI225236/SS313332; USRFORM001..012; independent pure form, no controller fixture. */
public final class UserSearchInputContractTest {
  private static final String USERNAME_KEY = "username";
  private static final String ROLE_KEY = "role";
  private static final String STATE_KEY = "state";
  private static final String PAGE_KEY = "page";
  private static final String PUBLIC_VALUE = "PUBLIC";
  private static final String ADMIN_VALUE = "ADMIN";
  private static final String SUPPLEMENTARY_VALUE = "\uD800\uDC00";
  private static final String INVALID_MESSAGE = "入力項目を確認してください。";

  private static Map<String, List<String>> input(String name, String value) {
    return Map.of(name, List.of(value));
  }

  private static void invalid(String field, String value) {
    var form = UserSearchForm.bind(input(field, value));
    assertFalse(form.isValid());
    assertTrue(form.getIssues().containsKey(field));
    assertEquals(
        "invalid user search form",
        assertThrows(IllegalArgumentException.class, form::toRequest).getMessage());
  }

  @Test
  void usrform001DefaultsDoNotConferAuthentication() {
    var form = UserSearchForm.bind(Map.of());
    assertTrue(form.isValid());
    assertTrue(form.getIssues().isEmpty());
    assertEquals("", form.getUsername());
    assertEquals("", form.getRole());
    assertEquals("", form.getState());
    assertEquals(1, form.getPage());
    var dto = form.toRequest();
    assertEquals(Optional.empty(), dto.usernamePrefix());
    assertEquals(Optional.empty(), dto.role());
    assertEquals(Optional.empty(), dto.state());
    assertEquals(1, dto.page());
    assertEquals(50, dto.pageSize());
    assertEquals("UserSearchForm[REDACTED]", form.toString());
  }

  @Test
  void usrform002RoleAndStateLiteralsAreIndependentOptionalEnums() {
    String[] roles = {"", "USER", ADMIN_VALUE};
    UserRole[] roleValues = {null, UserRole.USER, UserRole.ADMIN};
    String[] states = {"", "ACTIVE", "DISABLED", "LOCKED"};
    UserState[] stateValues = {null, UserState.ACTIVE, UserState.DISABLED, UserState.LOCKED};
    for (int r = 0; r < roles.length; r++)
      for (int s = 0; s < states.length; s++) {
        var f =
            UserSearchForm.bind(Map.of(ROLE_KEY, List.of(roles[r]), STATE_KEY, List.of(states[s])));
        assertTrue(f.isValid());
        assertEquals(roles[r], f.getRole());
        assertEquals(states[s], f.getState());
        assertEquals(Optional.ofNullable(roleValues[r]), f.toRequest().role());
        assertEquals(Optional.ofNullable(stateValues[s]), f.toRequest().state());
      }
  }

  @Test
  void usrform003NormalizationPrecedesByteValidationAndOuterTrim() {
    var f = UserSearchForm.bind(input(USERNAME_KEY, "  e\u0301  "));
    assertTrue(f.isValid());
    assertEquals("é", f.getUsername());
    assertEquals(Optional.of("é"), f.toRequest().usernamePrefix());
    var bound = UserSearchForm.bind(input(USERNAME_KEY, "e\u0301".repeat(32)));
    assertTrue(bound.isValid());
    assertEquals("é".repeat(32), bound.getUsername());
    assertEquals(ADMIN_VALUE, UserSearchForm.bind(input(ROLE_KEY, "  ADMIN  ")).getRole());
  }

  @Test
  void usrform004Utf8BoundariesUseIndependentOneTwoAndFourByteWidths() {
    for (String value :
        List.of("x".repeat(63), "x".repeat(64), "é".repeat(32), SUPPLEMENTARY_VALUE.repeat(16))) {
      var f = UserSearchForm.bind(input(USERNAME_KEY, value));
      assertTrue(f.isValid());
      assertEquals(value, f.getUsername());
    }
    for (String value : List.of("x".repeat(65), "é".repeat(33), SUPPLEMENTARY_VALUE.repeat(17))) {
      var f = UserSearchForm.bind(input(USERNAME_KEY, value));
      assertFalse(f.isValid());
      assertEquals("UsernameはUTF-8で64 byte以内にしてください。", f.getIssues().get(USERNAME_KEY));
    }
  }

  @Test
  void usrform005PageClampAndUpperBoundHaveLiteralExpectations() {
    String[] values = {"", "0", "-0", "-1", "-2147483648", "1", "2", "999999", "000002"};
    int[] expected = {1, 1, 1, 1, 1, 1, 2, 999999, 2};
    for (int i = 0; i < values.length; i++) {
      var f = UserSearchForm.bind(input(PAGE_KEY, values[i]));
      assertTrue(f.isValid());
      assertEquals(expected[i], f.getPage());
      assertEquals(expected[i], f.toRequest().page());
      assertEquals(50, f.toRequest().pageSize());
    }
  }

  @Test
  void usrform006MalformedUpperAndOverflowPageNeverBecomeARequest() {
    for (String value :
        List.of("+1", "1.0", PUBLIC_VALUE, "1000000", "2147483647", "2147483648", "-2147483649")) {
      var f = UserSearchForm.bind(input(PAGE_KEY, value));
      assertFalse(f.isValid());
      assertEquals(1, f.getPage());
      assertEquals(INVALID_MESSAGE, f.getIssues().get(PAGE_KEY));
      assertThrows(IllegalArgumentException.class, f::toRequest);
    }
  }

  @Test
  void usrform007UnknownAndNonSingleFieldsHaveExplicitIssueKeys() {
    var unknown =
        UserSearchForm.bind(
            Map.of("owner", List.of(PUBLIC_VALUE), USERNAME_KEY, List.of(PUBLIC_VALUE)));
    assertFalse(unknown.isValid());
    assertEquals(INVALID_MESSAGE, unknown.getIssues().get("form"));
    assertEquals(PUBLIC_VALUE, unknown.getUsername());
    for (String name : List.of(USERNAME_KEY, ROLE_KEY, STATE_KEY, PAGE_KEY))
      for (List<String> values : List.of(List.<String>of(), List.of(PUBLIC_VALUE, PUBLIC_VALUE))) {
        var f = UserSearchForm.bind(Map.of(name, values));
        assertFalse(f.isValid());
        assertEquals(INVALID_MESSAGE, f.getIssues().get(name));
      }
  }

  @Test
  void usrform008ControlAndSurrogateRejectionIsNotUnicodeRejection() {
    for (String value : List.of("\u0000", "\u007f", "\u0085", "\uD800", "\uDC00"))
      for (String name : List.of(USERNAME_KEY, ROLE_KEY, STATE_KEY, PAGE_KEY)) invalid(name, value);
    for (String value : List.of("é", "\uE000", SUPPLEMENTARY_VALUE)) {
      var f = UserSearchForm.bind(input(USERNAME_KEY, value));
      assertTrue(f.isValid());
      assertEquals(value, f.getUsername());
    }
  }

  @Test
  void usrform009UnknownEnumsAreFieldFailuresWithoutGrant() {
    for (String value : List.of("user", "ROOT", "DISABLED")) invalid(ROLE_KEY, value);
    for (String value : List.of("active", "REMOVED", ADMIN_VALUE)) invalid(STATE_KEY, value);
  }

  @Test
  void usrform010NullAtEveryCollectionBoundaryIsRejected() {
    assertThrows(NullPointerException.class, () -> UserSearchForm.bind(null));
    var key = new HashMap<String, List<String>>();
    key.put(null, List.of(PUBLIC_VALUE));
    assertThrows(NullPointerException.class, () -> UserSearchForm.bind(key));
    var list = new HashMap<String, List<String>>();
    list.put(USERNAME_KEY, null);
    assertThrows(NullPointerException.class, () -> UserSearchForm.bind(list));
    var elements = new ArrayList<String>();
    elements.add(null);
    assertThrows(
        NullPointerException.class, () -> UserSearchForm.bind(Map.of(USERNAME_KEY, elements)));
  }

  @Test
  void usrform011CallerMutationCannotAlterTheCapturedRequest() {
    var values = new ArrayList<>(List.of(PUBLIC_VALUE));
    var input = new HashMap<String, List<String>>();
    input.put(USERNAME_KEY, values);
    var f = UserSearchForm.bind(input);
    values.set(0, "CHANGED");
    input.clear();
    assertEquals(PUBLIC_VALUE, f.getUsername());
    assertEquals(Optional.of(PUBLIC_VALUE), f.toRequest().usernamePrefix());
    assertThrows(
        UnsupportedOperationException.class, () -> f.getIssues().put(USERNAME_KEY, PUBLIC_VALUE));
    var bad = UserSearchForm.bind(input(ROLE_KEY, "BAD"));
    assertThrows(UnsupportedOperationException.class, () -> bad.getIssues().clear());
    assertFalse(bad.isValid());
    assertTrue(f.isValid());
  }

  @Test
  void usrform012InvalidConversionAndDiagnosticsStayValueFree() {
    var f = UserSearchForm.bind(input(ROLE_KEY, "PUBLIC_UNRECOGNIZED"));
    assertEquals("UserSearchForm[REDACTED]", f.toString());
    var ex = assertThrows(IllegalArgumentException.class, f::toRequest);
    assertEquals("invalid user search form", ex.getMessage());
    assertNull(ex.getCause());
    assertEquals(0, ex.getSuppressed().length);
    var next = UserSearchForm.bind(input(USERNAME_KEY, "OTHER"));
    assertTrue(next.isValid());
    assertEquals(Optional.of("OTHER"), next.toRequest().usernamePrefix());
    assertEquals(50, next.toRequest().pageSize());
    assertFalse(f.isValid());
  }
}
