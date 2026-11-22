package dev.codex.schubert.nk.web.form;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadValues;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.protocol.layout.semantic.UserState;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import org.junit.jupiter.api.Test;

/** USER-SEARCH001..008; UI225236/SS313323332; independent96byte/Unicode/page vectors. */
final class UserSearchFormContractTest {
  private static final String USERNAME = "username";
  private static final String ROLE = "role";
  private static final String STATE = "state";
  private static final String PAGE = "page";
  private static final String INVALID = "入力項目を確認してください。";
  private static final String BYTE_LIMIT = "UsernameはUTF-8で64 byte以内にしてください。";
  private static final String UNKNOWN_VALUE = "UNKNOWN";
  private static final List<String> FIELDS = List.of(USERNAME, ROLE, STATE, PAGE);

  private static UserSearchForm bind(String field, String value) {
    return UserSearchForm.bind(Map.of(field, List.of(value)));
  }

  private static byte[] wire(UserSearchForm form) {
    return PayloadCodec.standard()
        .encode(
            new PayloadValues(new LayoutId("USRREQ01"), form.toRequest().fields(), List.of()),
            false)
        .copyData();
  }

  private static void put(byte[] target, int at, String value) {
    byte[] source = value.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(source, 0, target, at, source.length);
  }

  private static void assertInvalid(UserSearchForm form, String field, String message) {
    assertFalse(form.isValid());
    assertEquals(message, form.getIssues().get(field));
    assertEquals(
        "invalid user search form",
        assertThrows(IllegalArgumentException.class, form::toRequest).getMessage());
  }

  @Test
  void search001MissingAndEmptyUseExplicitOptionalAndNinetySixByteGolden() {
    for (var parameters :
        List.of(
            Map.<String, List<String>>of(),
            Map.of(
                USERNAME, List.of(""), ROLE, List.of(""), STATE, List.of(""), PAGE, List.of("")))) {
      var form = UserSearchForm.bind(parameters);
      assertTrue(form.isValid());
      assertEquals("", form.getUsername());
      assertEquals("", form.getRole());
      assertEquals("", form.getState());
      assertEquals(1, form.getPage());
      assertEquals(Optional.empty(), form.toRequest().usernamePrefix());
      assertEquals(Optional.empty(), form.toRequest().role());
      assertEquals(Optional.empty(), form.toRequest().state());
      assertEquals(50, form.toRequest().pageSize());
      byte[] expected = new byte[96];
      Arrays.fill(expected, (byte) ' ');
      put(expected, 77, "000001");
      put(expected, 83, "050");
      assertArrayEquals(expected, wire(form));
      assertEquals("UserSearchForm[REDACTED]", form.toString());
    }
  }

  @Test
  void search002NfcTrimAndUtf8BoundariesUseIndependentCanonicalStrings() {
    var form = bind(USERNAME, "  " + "e\u0301".repeat(32) + "  ");
    assertTrue(form.isValid());
    assertEquals("é".repeat(32), form.getUsername());
    assertEquals(Optional.of("é".repeat(32)), form.toRequest().usernamePrefix());
    for (String value : List.of("x".repeat(64), "é".repeat(32), "😀".repeat(16), "?_%+&/")) {
      var valid = bind(USERNAME, value);
      assertTrue(valid.isValid());
      assertEquals(value, valid.getUsername());
    }
    for (String value : List.of("x".repeat(65), "é".repeat(33), "😀".repeat(17))) {
      var rejected = bind(USERNAME, value);
      assertInvalid(rejected, USERNAME, BYTE_LIMIT);
      assertEquals(value, rejected.getUsername());
    }
  }

  @Test
  void search003ClosedEnumsAndPopulatedWireUseLiteralFieldsOffsetsAndValues() {
    var roles = Map.of("USER", UserRole.USER, "ADMIN", UserRole.ADMIN);
    var states =
        Map.of(
            "ACTIVE", UserState.ACTIVE, "DISABLED", UserState.DISABLED, "LOCKED", UserState.LOCKED);
    for (var entry : roles.entrySet())
      assertEquals(Optional.of(entry.getValue()), bind(ROLE, entry.getKey()).toRequest().role());
    for (var entry : states.entrySet())
      assertEquals(Optional.of(entry.getValue()), bind(STATE, entry.getKey()).toRequest().state());
    for (String value : List.of("user", UNKNOWN_VALUE, "ADMINISTRATOR"))
      assertInvalid(bind(ROLE, value), ROLE, INVALID);
    for (String value : List.of("active", UNKNOWN_VALUE, "ENABLED"))
      assertInvalid(bind(STATE, value), STATE, INVALID);
    var form =
        UserSearchForm.bind(
            Map.of(
                USERNAME,
                List.of(" prefixé "),
                ROLE,
                List.of("ADMIN"),
                STATE,
                List.of("LOCKED"),
                PAGE,
                List.of("2")));
    byte[] expected = new byte[96];
    Arrays.fill(expected, (byte) ' ');
    put(expected, 0, "prefixé");
    put(expected, 64, "ADMIN");
    put(expected, 69, "LOCKED");
    put(expected, 77, "000002");
    put(expected, 83, "050");
    assertArrayEquals(expected, wire(form));
    assertEquals(2, form.toRequest().page());
  }

  @Test
  void search004PageSignedIntBoundariesAndUnknownSyntaxAreNotSilentlyRepaired() {
    var valid =
        Map.of("0", 1, "-1", 1, "-2147483648", 1, "1", 1, "999999", 999999, "0002", 2, " 2 ", 2);
    for (var entry : valid.entrySet()) {
      var form = bind(PAGE, entry.getKey());
      assertTrue(form.isValid());
      assertEquals(entry.getValue().intValue(), form.getPage());
      assertEquals(entry.getValue().intValue(), form.toRequest().page());
    }
    for (String page :
        List.of(
            "1000000",
            "2147483647",
            "2147483648",
            "-2147483649",
            "+1",
            "１",
            "1.0",
            "1e1",
            "-",
            "9".repeat(40))) assertInvalid(bind(PAGE, page), PAGE, INVALID);
  }

  @Test
  void search005UnknownFieldsMissingValuesAndAllNullBoundariesStayDistinct() {
    for (String field : List.of("unexpected", "_csrf"))
      assertInvalid(bind(field, "x"), "form", INVALID);
    for (String field : FIELDS) {
      for (List<String> values : List.of(List.<String>of(), List.of("first", "second")))
        assertInvalid(UserSearchForm.bind(Map.of(field, values)), field, INVALID);
      var nullable = new HashMap<String, List<String>>();
      nullable.put(field, null);
      assertThrows(NullPointerException.class, () -> UserSearchForm.bind(nullable));
      nullable.put(field, Arrays.asList((String) null));
      assertThrows(NullPointerException.class, () -> UserSearchForm.bind(nullable));
    }
    var nullKey = new HashMap<String, List<String>>();
    nullKey.put(null, List.of("x"));
    assertThrows(NullPointerException.class, () -> UserSearchForm.bind(nullKey));
    assertThrows(NullPointerException.class, () -> UserSearchForm.bind(null));
  }

  @Test
  void search006ControlsAreRejectedBeforeTrimAndSupplementaryCharactersRemainValid() {
    for (String field : FIELDS)
      for (String value :
          List.of(
              "\tvalue", "value\n", "value\r", "\u0000", "\u007f", "\u0085", "\ud800", "\udfff"))
        assertInvalid(bind(field, value), field, INVALID);
    var supplementary = bind(USERNAME, "😀");
    assertTrue(supplementary.isValid());
    assertEquals("😀", supplementary.getUsername());
    assertEquals(Optional.of("😀"), supplementary.toRequest().usernamePrefix());
  }

  @Test
  void search007DefensiveSnapshotsAndInvalidRedisplayAreImmutableAndRedacted() {
    var names = new ArrayList<>(List.of(" PUBLIC_QUERY "));
    var caller = new HashMap<String, List<String>>();
    caller.put(USERNAME, names);
    var form = UserSearchForm.bind(caller);
    names.set(0, "CHANGED");
    caller.clear();
    assertEquals("PUBLIC_QUERY", form.getUsername());
    assertEquals(Optional.of("PUBLIC_QUERY"), form.toRequest().usernamePrefix());
    assertThrows(UnsupportedOperationException.class, () -> form.getIssues().put(USERNAME, "x"));
    var rejected = bind(ROLE, UNKNOWN_VALUE);
    assertEquals(UNKNOWN_VALUE, rejected.getRole());
    assertInvalid(rejected, ROLE, INVALID);
    assertThrows(UnsupportedOperationException.class, () -> rejected.getIssues().clear());
    assertEquals("UserSearchForm[REDACTED]", rejected.toString());
    assertFalse(form.toString().contains("PUBLIC_QUERY"));
  }

  @Test
  void search008IndependentParallelBindingsNeverShareMutableFields()
      throws InterruptedException, ExecutionException, TimeoutException {
    var executor = Executors.newFixedThreadPool(4);
    try {
      var results = new ArrayList<Future<?>>();
      for (int index = 1; index <= 16; index++) {
        final int number = index;
        results.add(
            executor.submit(
                () -> {
                  String username = "public-" + number;
                  var form =
                      UserSearchForm.bind(
                          Map.of(
                              USERNAME,
                              List.of(username),
                              PAGE,
                              List.of(Integer.toString(number))));
                  assertTrue(form.isValid());
                  assertEquals(username, form.getUsername());
                  assertEquals(number, form.getPage());
                  assertEquals(Optional.of(username), form.toRequest().usernamePrefix());
                  assertTrue(form.getIssues().isEmpty());
                }));
      }
      for (var result : results) result.get(5, TimeUnit.SECONDS);
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
    }
  }
}
