package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.security.SavedRequestTarget;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** Hand-written SSC038 JSON and explicit field oracles. NK-WEB-001/PT-WEB-009..015. */
class SessionAttributeCodecTest {
  static final SessionAttributeCodec CODEC = new SessionAttributeCodec();
  static final String TIME = "2026-09-08T00:00:00Z";
  static final String CONTEXT = "b".repeat(64);
  static final String CSRF = "c".repeat(64);
  static final Instant NOW = Instant.parse(TIME);
  static final String ANONYMOUS = "{\"formatVersion\":1,\"operationTokens\":[]}";

  @Test
  void web009AnonymousAndAuthenticatedGoldenJson() {
    for (boolean authenticated : List.of(false, true))
      for (UserRole role : UserRole.values())
        for (boolean csrf : List.of(false, true))
          for (boolean saved : List.of(false, true))
            for (int count : new int[] {0, 1, 10}) {
              var attributes =
                  attributes(
                      authenticated,
                      "reader",
                      role,
                      csrf ? CSRF : null,
                      saved ? "/logs?page=2" : null,
                      count);
              String expected =
                  json(
                      authenticated,
                      "reader",
                      role.name(),
                      csrf ? CSRF : null,
                      saved ? "/logs?page=2" : null,
                      count);
              assertArrayEquals(bytes(expected), CODEC.encode(attributes));
              var decoded = CODEC.decode(bytes(expected));
              check(
                  decoded,
                  authenticated,
                  "reader",
                  role,
                  csrf ? CSRF : null,
                  saved ? "/logs?page=2" : null,
                  count);
              assertEquals("SessionAttributes[REDACTED]", decoded.toString());
            }
  }

  @Test
  void web010PrincipalTokenAndCollectionInvariantsFailFast() {
    var context = AuthenticationContext.of(CONTEXT);
    var tokens = tokens(1);
    for (Executable call :
        List.<Executable>of(
            () -> CODEC.encode(null),
            () -> CODEC.decode(null),
            () -> new SessionPrincipal(null, UserRole.USER, context, NOW),
            () -> new SessionPrincipal("u", null, context, NOW),
            () -> new SessionPrincipal("u", UserRole.USER, null, NOW),
            () -> new SessionPrincipal("u", UserRole.USER, context, null),
            () -> new SessionOperationToken(null, new UUID(0, 1), NOW),
            () -> new SessionOperationToken("QSBREQ01", null, NOW),
            () -> new SessionOperationToken("QSBREQ01", new UUID(0, 1), null),
            () -> new SessionAttributes(null, Optional.empty(), Optional.empty(), List.of()),
            () -> new SessionAttributes(Optional.empty(), null, Optional.empty(), List.of()),
            () -> new SessionAttributes(Optional.empty(), Optional.empty(), null, List.of()),
            () -> new SessionAttributes(Optional.empty(), Optional.empty(), Optional.empty(), null),
            () ->
                new SessionAttributes(
                    Optional.empty(),
                    Optional.empty(),
                    Optional.empty(),
                    Arrays.asList((SessionOperationToken) null))))
      assertThrows(NullPointerException.class, call);
    for (String name :
        List.of("", "a".repeat(65), "é".repeat(33), "u ", "u\n", "u\u0000", "u\ud800"))
      assertThrows(
          IllegalArgumentException.class,
          () -> new SessionPrincipal(name, UserRole.USER, context, NOW));
    assertEquals(
        "é".repeat(32),
        new SessionPrincipal("e\u0301".repeat(32), UserRole.USER, context, NOW).username());
    for (String csrf :
        List.of("x".repeat(63), "x".repeat(129), "%".repeat(64), "x".repeat(63) + " "))
      assertThrows(
          IllegalArgumentException.class,
          () -> attributes(false, "u", UserRole.USER, csrf, null, 0));
    assertThrows(
        IllegalArgumentException.class,
        () -> new SessionOperationToken("USRREQ01", new UUID(0, 1), NOW));
    assertThrows(
        IllegalArgumentException.class,
        () -> attributes(false, "u", UserRole.USER, null, null, 11));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new SessionAttributes(
                Optional.empty(),
                Optional.empty(),
                Optional.empty(),
                List.of(
                    tokens.getFirst(),
                    new SessionOperationToken("QDLREQ01", new UUID(0, 1), NOW))));
    var caller = new ArrayList<>(tokens);
    var attributes =
        new SessionAttributes(Optional.empty(), Optional.empty(), Optional.empty(), caller);
    caller.clear();
    assertEquals(1, attributes.operationTokens().size());
    assertThrows(UnsupportedOperationException.class, () -> attributes.operationTokens().clear());
    assertEquals(
        "SessionPrincipal[REDACTED]",
        new SessionPrincipal("u", UserRole.USER, context, NOW).toString());
    assertEquals("SessionOperationToken[REDACTED]", tokens.getFirst().toString());
  }

  @Test
  void web011UnknownDuplicateNullAndTypesNeverDeserialize() {
    for (String text :
        List.of(
            "{}",
            "{\"formatVersion\":1}",
            "{\"operationTokens\":[]}",
            "[]",
            "null",
            "1",
            "true",
            "\"text\"",
            "{\"formatVersion\":1,\"formatVersion\":1,\"operationTokens\":[]}",
            ANONYMOUS.replace("[]", "null"),
            ANONYMOUS.replace("[]", "{}"),
            ANONYMOUS.replace("[]", "[[]]"),
            ANONYMOUS.replace("[]", "[{\"purpose\":\"QSBREQ01\"}]"),
            ANONYMOUS.replace("[]", "[{\"purpose\":\"QSBREQ01\",\"purpose\":\"QSBREQ01\"}]"),
            ANONYMOUS.replace("[]", "[{\"class\":\"arbitrary.type\"}]"))) invalid(text);
    // QA049 permits integer v2; legacy v1 malformed/unknown versions still reject.
    for (String version : List.of("0", "3", "1.0", "1e0", "\"1\"", "null", "true", "[]"))
      invalid(ANONYMOUS.replace(":1,", ":" + version + ","));
    for (String key :
        List.of("password", "class", "requestBody", "lastAccessedAt", "rawSessionId", "unknown"))
      invalid(ANONYMOUS.replace("}", ",\"" + key + "\":\"private-marker\"}"));
    for (String key :
        List.of(
            "username", "role", "authenticationContext", "loginAt", "csrfToken", "savedRequest"))
      for (String value : List.of("null", "1", "true", "[]", "{}"))
        invalid(ANONYMOUS.replace("}", ",\"" + key + "\":" + value + "}"));
    for (String key : List.of("username", "role", "authenticationContext", "loginAt"))
      invalid("{\"formatVersion\":1,\"operationTokens\":[],\"" + key + "\":\"partial\"}");
    String full = json(true, "reader", "USER", CSRF, "/logs", 1);
    for (String key :
        List.of(
            "username",
            "role",
            "authenticationContext",
            "loginAt",
            "csrfToken",
            "savedRequest",
            "operationTokens"))
      invalid(full.substring(0, full.length() - 1) + ",\"" + key + "\":null}");
    for (String field : List.of("purpose", "token", "issuedAt")) {
      String item = tokenJson(1);
      int start = item.indexOf("\"" + field + "\":");
      String duplicate = item.substring(0, item.length() - 1) + ",\"" + field + "\":\"duplicate\"}";
      invalid(ANONYMOUS.replace("[]", "[" + duplicate + "]"));
      assertTrue(start >= 0);
    }
  }

  @Test
  void web012MalformedUtf8AndBoundedDocumentsRejectSafely() {
    for (byte[] input :
        List.of(
            new byte[0],
            new byte[] {(byte) 0xc3, 0x28},
            new byte[] {(byte) 0xff},
            bytes("\ufeff" + ANONYMOUS),
            new byte[16385])) invalid(input);
    for (String text :
        List.of(
            " ",
            "{",
            ANONYMOUS + "{}",
            ANONYMOUS + " false",
            ANONYMOUS + " private-marker",
            "/*private-marker*/" + ANONYMOUS,
            "{formatVersion:1,operationTokens:[]}",
            "{\"formatVersion\":1,\"operationTokens\":[],}",
            "{\"formatVersion\":1,\"operationTokens\":["
                + "[".repeat(100)
                + "0"
                + "]".repeat(100)
                + "]}")) invalid(text);
    String maximum = ANONYMOUS + " ".repeat(16384 - bytes(ANONYMOUS).length);
    byte[] input = bytes(maximum);
    byte[] copy = input.clone();
    assertEquals(16384, input.length);
    assertTrue(CODEC.decode(input).principal().isEmpty());
    assertArrayEquals(copy, input);
    invalid(maximum + " ");
  }

  @Test
  void web013UnicodeSavedTargetsAndTokenPurposesPreserveMeaning() {
    String username = "\u00e9".repeat(32);
    String csrf = "_".repeat(128);
    String target = "/q?x=" + "\u3042".repeat(681);
    var value = attributes(true, username, UserRole.ADMIN, csrf, target, 10);
    String expected = json(true, username, "ADMIN", csrf, target, 10);
    byte[] actual = CODEC.encode(value);
    assertArrayEquals(bytes(expected), actual);
    assertTrue(actual.length < 16384);
    check(CODEC.decode(bytes(expected)), true, username, UserRole.ADMIN, csrf, target, 10);
    for (String purpose :
        List.of(
            "UCRREQ01",
            "USTREQ01",
            "URLREQ01",
            "UPWREQ01",
            "ULKREQ01",
            "QSBREQ01",
            "NTCREQ01",
            "QDLREQ01")) {
      String text = json(false, "u", "USER", null, null, 1).replace("QSBREQ01", purpose);
      assertEquals(purpose, CODEC.decode(bytes(text)).operationTokens().getFirst().purpose());
      var single =
          new SessionAttributes(
              Optional.empty(),
              Optional.empty(),
              Optional.empty(),
              List.of(new SessionOperationToken(purpose, new UUID(0, 1), NOW)));
      assertArrayEquals(bytes(text), CODEC.encode(single));
    }
    for (String name : List.of("a\"b", "a\\b", "日本語"))
      assertArrayEquals(
          bytes(json(true, name, "USER", null, null, 0)),
          CODEC.encode(attributes(true, name, UserRole.USER, null, null, 0)));
    var duplicate =
        ANONYMOUS.replace(
            "[]", "[" + tokenJson(1) + "," + tokenJson(1).replace("QSBREQ01", "QDLREQ01") + "]");
    invalid(duplicate);
    String eleven =
        ANONYMOUS.replace(
            "[]",
            "["
                + String.join(
                    ",",
                    java.util.stream.IntStream.rangeClosed(1, 11)
                        .mapToObj(SessionAttributeCodecTest::tokenJson)
                        .toList())
                + "]");
    invalid(eleven);
  }

  @Test
  void web014IndependentDecodeAcceptsOrderButRejectsInvalidValues() {
    String reverse =
        " { \"operationTokens\": [], \"savedRequest\": \"/logs\", \"csrfToken\": "
            + quote(CSRF)
            + ", \"loginAt\": "
            + quote(TIME)
            + ", \"authenticationContext\": "
            + quote(CONTEXT)
            + ", \"role\": \"ADMIN\", \"username\": \"reader\", \"formatVersion\": 1 } ";
    check(CODEC.decode(bytes(reverse)), true, "reader", UserRole.ADMIN, CSRF, "/logs", 0);
    String full = json(true, "reader", "USER", CSRF, "/logs", 1);
    for (String bad :
        List.of(
            "private-marker",
            "2026-02-30T00:00:00Z",
            "+1000000001-01-01T00:00:00Z",
            "2026-09-08T00:00:00.000Z",
            "2026-09-08T09:00:00+09:00")) {
      invalid(full.replace("\"loginAt\":" + quote(TIME), "\"loginAt\":" + quote(bad)));
      invalid(full.replace("\"issuedAt\":" + quote(TIME), "\"issuedAt\":" + quote(bad)));
    }
    for (String bad : List.of("not-a-uuid", "1-1-1-1-1", "00000000-0000-0000-0000-00000000000A"))
      invalid(full.replace("00000000-0000-0000-0000-000000000001", bad));
    for (String bad : List.of("SUPERUSER", "user", ""))
      invalid(full.replace("\"USER\"", quote(bad)));
    for (String bad : List.of("b".repeat(63), "B".repeat(64), "g".repeat(64)))
      invalid(full.replace(CONTEXT, bad));
    invalid(full.replace("/logs", "https://external.test/"));
    for (String path : List.of("/../logs", "/..", "/../../logs", "/./logs"))
      invalid(full.replace("/logs", path));
    invalid(full.replace("QSBREQ01", "LGSREQ01"));
    invalid(full.replace(CSRF, "c".repeat(63)));
    invalid(full.replace("reader", "a".repeat(65)));
    // Historical login time is valid data, not a current-authentication/expiry decision here.
    String historical = full.replace(TIME, "1800-01-01T00:00:00Z");
    assertEquals(
        Instant.parse("1800-01-01T00:00:00Z"),
        CODEC.decode(bytes(historical)).principal().orElseThrow().loginAt());
  }

  @Test
  void web015ConcurrentAttributesHaveNoCrossSessionState() throws Exception {
    try (var pool = Executors.newFixedThreadPool(10)) {
      var futures = new ArrayList<Future<Void>>();
      for (int i = 0; i < 100; i++) {
        final int n = i;
        futures.add(
            pool.submit(
                () -> {
                  String name = "reader" + n;
                  String target = "/logs?q=\u65e5\u672c\u8a9e" + n;
                  String expected = json(true, name, "ADMIN", CSRF, target, n % 11);
                  check(
                      CODEC.decode(bytes(expected)),
                      true,
                      name,
                      UserRole.ADMIN,
                      CSRF,
                      target,
                      n % 11);
                  assertArrayEquals(
                      bytes(expected),
                      CODEC.encode(attributes(true, name, UserRole.ADMIN, CSRF, target, n % 11)));
                  return null;
                }));
      }
      for (var future : futures) future.get(20, TimeUnit.SECONDS);
    }
  }

  static SessionAttributes attributes(
      boolean authenticated, String name, UserRole role, String csrf, String saved, int count) {
    return new SessionAttributes(
        authenticated
            ? Optional.of(new SessionPrincipal(name, role, AuthenticationContext.of(CONTEXT), NOW))
            : Optional.empty(),
        Optional.ofNullable(csrf),
        Optional.ofNullable(saved).map(value -> SavedRequestTarget.fromGet("GET", value)),
        tokens(count));
  }

  static List<SessionOperationToken> tokens(int count) {
    return java.util.stream.IntStream.rangeClosed(1, count)
        .mapToObj(n -> new SessionOperationToken("QSBREQ01", new UUID(0, n), NOW))
        .toList();
  }

  static String quote(String text) {
    return "\"" + text.replace("\\", "\\\\").replace("\"", "\\\"") + "\"";
  }

  static String tokenJson(int n) {
    return "{\"purpose\":\"QSBREQ01\",\"token\":\"00000000-0000-0000-0000-"
        + String.format(Locale.ROOT, "%012x", n)
        + "\",\"issuedAt\":"
        + quote(TIME)
        + "}";
  }

  static String json(
      boolean authenticated, String name, String role, String csrf, String saved, int count) {
    // QA049 current-write oracle is v2; ANONYMOUS/reverse legacy decode fixtures remain v1.
    var s = new StringBuilder("{\"formatVersion\":2");
    if (authenticated)
      s.append(",\"username\":")
          .append(quote(name))
          .append(",\"role\":")
          .append(quote(role))
          .append(",\"authenticationContext\":")
          .append(quote(CONTEXT))
          .append(",\"loginAt\":")
          .append(quote(TIME));
    if (csrf != null) s.append(",\"csrfToken\":").append(quote(csrf));
    if (saved != null) s.append(",\"savedRequest\":").append(quote(saved));
    s.append(",\"operationTokens\":[");
    for (int i = 1; i <= count; i++) {
      if (i > 1) s.append(',');
      s.append(tokenJson(i));
    }
    return s.append("]}").toString();
  }

  static void check(
      SessionAttributes actual,
      boolean authenticated,
      String name,
      UserRole role,
      String csrf,
      String saved,
      int count) {
    assertEquals(authenticated, actual.principal().isPresent());
    if (authenticated) {
      var p = actual.principal().orElseThrow();
      assertEquals(name, p.username());
      assertEquals(role, p.role());
      assertEquals(CONTEXT, p.authenticationContext().wireValue());
      assertEquals(NOW, p.loginAt());
    }
    assertEquals(Optional.ofNullable(csrf), actual.csrfToken());
    assertEquals(
        Optional.ofNullable(saved), actual.savedRequest().map(SavedRequestTarget::location));
    assertEquals(count, actual.operationTokens().size());
    for (int i = 0; i < count; i++) {
      var token = actual.operationTokens().get(i);
      assertEquals("QSBREQ01", token.purpose());
      assertEquals(new UUID(0, i + 1), token.token());
      assertEquals(NOW, token.issuedAt());
    }
  }

  static byte[] bytes(String text) {
    return text.getBytes(StandardCharsets.UTF_8);
  }

  static void invalid(String text) {
    invalid(bytes(text));
  }

  static void invalid(byte[] data) {
    var error = assertThrows(SessionAttributeException.class, () -> CODEC.decode(data));
    assertEquals("session attributes are invalid", error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }
}
