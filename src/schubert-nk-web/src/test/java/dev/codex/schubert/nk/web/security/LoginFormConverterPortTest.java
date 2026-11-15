package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import jakarta.servlet.http.HttpServletRequest;
import java.lang.reflect.Proxy;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Enumeration;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.NoSuchElementException;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;

/** FUN001/AUT/UI226/SS313314352/PT-WEB-FORMPORT001..013; untrusted input only, no auth manager. */
@Timeout(value = 30, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class LoginFormConverterPortTest {
  private static final String FIXTURE_FAULT = "synthetic fixture fault";
  private static final String FORM_GET_METHOD = "getMethod";
  private static final String FORM_GET_PARAMETER_VALUES = "getParameterValues";
  private static final String USERNAME = "username";
  private static final String PASSWORD = "password";
  private static final String READER = "public-reader";
  private static final String PUBLIC_PASSWORD = "public-fixture";
  private static final String FORM_TYPE = "application/x-www-form-urlencoded";
  private static final String UTF8 = "UTF-8";
  private static final String LOGIN_PATH = "/login";
  private static final String METHOD_POST = "POST";
  private static final String FORWARDED_PROTO = "X-Forwarded-Proto";
  private static final String FORWARDED_FOR = "X-Forwarded-For";
  private static final String CLIENT = "192.0.2.9";
  private static final String FIXED_ERROR = "login form is invalid";
  private static final LoginFormAuthenticationConverter CONVERTER =
      new LoginFormAuthenticationConverter(new CaddyClientAddressResolver());

  private enum Names {
    NORMAL,
    NULL_ENUM,
    NULL_ELEMENT,
    UNKNOWN,
    THROW
  }

  private static final class Fixture {
    String httpMethod = METHOD_POST;
    String uri = LOGIN_PATH;
    String encoding = UTF8;
    String contentType = FORM_TYPE;
    String query;
    String peer = "127.0.0.1";
    Names names = Names.NORMAL;
    String faultAt;
    Throwable fault;
    final Map<String, String[]> parameters = new LinkedHashMap<>();
    final Map<String, List<String>> headers = new LinkedHashMap<>();

    Fixture() {
      parameters.put(USERNAME, new String[] {READER});
      parameters.put(PASSWORD, new String[] {PUBLIC_PASSWORD});
      headers.put(FORWARDED_PROTO, List.of("https"));
      headers.put(FORWARDED_FOR, List.of(CLIENT));
    }

    private Enumeration<String> parameterNames() {
      return switch (names) {
        case NORMAL -> Collections.enumeration(parameters.keySet());
        case NULL_ENUM -> null;
        case NULL_ELEMENT -> Collections.enumeration(Arrays.asList((String) null));
        case UNKNOWN -> Collections.enumeration(List.of("unexpected"));
        case THROW ->
            new Enumeration<>() {
              @Override
              public boolean hasMoreElements() {
                return true;
              }

              @Override
              public String nextElement() {
                throw new NoSuchElementException(FIXTURE_FAULT);
              }
            };
      };
    }

    HttpServletRequest asRequest() {
      return (HttpServletRequest)
          Proxy.newProxyInstance(
              HttpServletRequest.class.getClassLoader(),
              new Class<?>[] {HttpServletRequest.class},
              (proxy, method, args) -> {
                if (method.getName().equals(faultAt)) throw fault;
                return switch (method.getName()) {
                  case FORM_GET_METHOD -> httpMethod;
                  case "getRequestURI" -> uri;
                  case "getCharacterEncoding" -> encoding;
                  case "getContentType" -> contentType;
                  case "getQueryString" -> query;
                  case "getParameterNames" -> parameterNames();
                  case FORM_GET_PARAMETER_VALUES -> parameters.get((String) args[0]);
                  case "getRemoteAddr" -> peer;
                  case "getHeaders" ->
                      Collections.enumeration(headers.getOrDefault((String) args[0], List.of()));
                  case "toString" -> "memory servlet fixture";
                  case "hashCode" -> System.identityHashCode(proxy);
                  case "equals" -> proxy == args[0];
                  default ->
                      throw new AssertionError("unexpected fixture method " + method.getName());
                };
              });
    }
  }

  private static void rejected(Fixture f) {
    var error =
        assertThrows(LoginFormRejectedException.class, () -> CONVERTER.convert(f.asRequest()));
    assertEquals(FIXED_ERROR, error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }

  private static void untrusted(Authentication value, String username, String password) {
    var token = assertInstanceOf(UsernamePasswordAuthenticationToken.class, value);
    assertFalse(token.isAuthenticated());
    assertTrue(token.getAuthorities().isEmpty());
    assertEquals(username, token.getPrincipal());
    assertEquals(CLIENT, assertInstanceOf(LoginClientAddress.class, token.getDetails()).value());
    char[] chars = assertInstanceOf(char[].class, token.getCredentials());
    try {
      assertArrayEquals(password.toCharArray(), chars);
    } finally {
      Arrays.fill(chars, '\0');
      token.eraseCredentials();
    }
    assertNull(token.getCredentials());
    assertArrayEquals(new char[chars.length], chars);
  }

  @Test
  void validDefaultFormRemainsUnauthenticated() {
    var f = new Fixture();
    f.parameters.put("_csrf", new String[] {"public-placeholder"});
    untrusted(CONVERTER.convert(f.asRequest()), READER, PUBLIC_PASSWORD);
  }

  @Test
  void explicitUtf8AndLiteralCharactersArePreserved() {
    for (String type : List.of(FORM_TYPE, FORM_TYPE + ";charset=UTF-8")) {
      var f = new Fixture();
      f.contentType = type;
      f.encoding = "utf-8";
      f.parameters.put(USERNAME, new String[] {" e\u0301 "});
      f.parameters.put(PASSWORD, new String[] {"e\u0301"});
      untrusted(CONVERTER.convert(f.asRequest()), " e\u0301 ", "e\u0301");
    }
  }

  @Test
  void methodPathAndEncodingRejectBeforeCredentials() {
    for (String method : List.of("GET", "PUT", "post")) {
      var f = new Fixture();
      f.httpMethod = method;
      rejected(f);
    }
    var wrong = new Fixture();
    wrong.uri = "/elsewhere";
    rejected(wrong);
    for (String encoding : Arrays.asList(null, "ISO-8859-1")) {
      var f = new Fixture();
      f.encoding = encoding;
      rejected(f);
    }
  }

  @Test
  void missingMalformedAndIncompatibleMediaTypesReject() {
    for (String type :
        Arrays.asList(
            null,
            "",
            "bad",
            "application/json",
            "text/x-www-form-urlencoded",
            "application/*",
            FORM_TYPE + ";charset=ISO-8859-1",
            FORM_TYPE + ";charset=NO_SUCH_CHARSET")) {
      var f = new Fixture();
      f.contentType = type;
      rejected(f);
    }
  }

  @Test
  void queryFormNamesAndMalformedEscapesReject() {
    for (String key :
        List.of(
            USERNAME, "USERNAME", "%75sername", PASSWORD, "PaSsWoRd", "_csrf", "%5fcsrf", "%GG")) {
      var f = new Fixture();
      f.query = "q=other&" + key + "=public";
      rejected(f);
    }
  }

  @Test
  void absentEmptyAndNonFormQueryAreAllowedStructurally() {
    for (String query : Arrays.asList(null, "", "unused=1&empty", "q=%26&%61=1")) {
      var f = new Fixture();
      f.query = query;
      untrusted(CONVERTER.convert(f.asRequest()), READER, PUBLIC_PASSWORD);
    }
  }

  @Test
  void nullUnknownAndBrokenParameterNamesReject() {
    for (Names names : List.of(Names.NULL_ENUM, Names.NULL_ELEMENT, Names.UNKNOWN, Names.THROW)) {
      var f = new Fixture();
      f.names = names;
      rejected(f);
    }
  }

  @Test
  void usernameNullMissingEmptyAndMultiplicityReject() {
    for (String[] values :
        Arrays.asList(
            null,
            new String[0],
            new String[] {null},
            new String[] {""},
            new String[] {"one", "two"})) {
      var f = new Fixture();
      f.parameters.put(USERNAME, values);
      rejected(f);
    }
  }

  @Test
  void passwordNullMissingEmptyAndMultiplicityReject() {
    for (String[] values :
        Arrays.asList(
            null,
            new String[0],
            new String[] {null},
            new String[] {""},
            new String[] {"one", "two"})) {
      var f = new Fixture();
      f.parameters.put(PASSWORD, values);
      rejected(f);
    }
  }

  @Test
  void numericProxyRejectionStaysDistinct() {
    var peer = new Fixture();
    peer.peer = "192.0.2.10";
    var proto = new Fixture();
    proto.headers.put(FORWARDED_PROTO, List.of("http"));
    var forwarded = new Fixture();
    forwarded.headers.put("Forwarded", List.of("public"));
    var absent = new Fixture();
    absent.headers.remove(FORWARDED_FOR);
    for (var f : List.of(peer, proto, forwarded, absent)) {
      var e =
          assertThrows(CaddyRequestRejectedException.class, () -> CONVERTER.convert(f.asRequest()));
      assertEquals("request proxy is invalid", e.getMessage());
      assertNull(e.getCause());
    }
  }

  @Test
  void fixtureFaultsAreRedactedButFatalIsNotHidden() {
    for (var failure :
        List.of(
            new IllegalArgumentException(FIXTURE_FAULT),
            new IllegalStateException(FIXTURE_FAULT),
            new NoSuchElementException(FIXTURE_FAULT))) {
      var f = new Fixture();
      f.faultAt = FORM_GET_PARAMETER_VALUES;
      f.fault = failure;
      rejected(f);
    }
    var fatal = new AssertionError("synthetic fatal");
    var f = new Fixture();
    f.faultAt = FORM_GET_METHOD;
    f.fault = fatal;
    assertSame(fatal, assertThrows(AssertionError.class, () -> CONVERTER.convert(f.asRequest())));
  }

  @Test
  void nullApiBoundariesReject() {
    assertThrows(NullPointerException.class, () -> new LoginFormAuthenticationConverter(null));
    assertThrows(NullPointerException.class, () -> CONVERTER.convert(null));
  }

  @Test
  void sharedConverterKeepsParallelInputsSeparate() throws Exception {
    var workers = Executors.newFixedThreadPool(2);
    try {
      var pending = new ArrayList<Future<Authentication>>();
      for (int i = 0; i < 8; i++) {
        String name = READER + i;
        pending.add(
            workers.submit(
                () -> {
                  var f = new Fixture();
                  f.parameters.put(USERNAME, new String[] {name});
                  return CONVERTER.convert(f.asRequest());
                }));
      }
      for (int i = 0; i < 8; i++)
        untrusted(pending.get(i).get(10, TimeUnit.SECONDS), READER + i, PUBLIC_PASSWORD);
    } finally {
      workers.shutdownNow();
      assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));
    }
  }

  @Test
  void formfatal014EveryDeclaredClassificationPreservesCauseAndSuppressedFatalIdentity() {
    for (int kind = 0; kind < 3; kind++) {
      for (String site : List.of(FORM_GET_METHOD, FORM_GET_PARAMETER_VALUES)) {
        for (boolean cause : new boolean[] {true, false}) {
          AssertionError fatal = new AssertionError(FIXTURE_FAULT);
          RuntimeException wrapper = classifiedFormFailure(kind, cause ? fatal : null);
          if (!cause) wrapper.addSuppressed(fatal);
          Fixture f = new Fixture();
          f.faultAt = site;
          f.fault = wrapper;
          assertSame(
              fatal, assertThrows(AssertionError.class, () -> CONVERTER.convert(f.asRequest())));
          assertEquals(0, fatal.getSuppressed().length);
        }
      }
    }
  }

  @Test
  void formfatal015NonfatalCyclesAreFiniteRedactedAndUnknownRuntimeKeepsIdentity() {
    for (int kind = 0; kind < 3; kind++) {
      RuntimeException first = new RuntimeException(FIXTURE_FAULT);
      RuntimeException second = new RuntimeException(FIXTURE_FAULT);
      first.initCause(second);
      second.initCause(first);
      RuntimeException shared = new RuntimeException(FIXTURE_FAULT);
      first.addSuppressed(shared);
      RuntimeException wrapper = classifiedFormFailure(kind, first);
      wrapper.addSuppressed(shared);
      Fixture f = new Fixture();
      f.faultAt = FORM_GET_PARAMETER_VALUES;
      f.fault = wrapper;
      rejected(f);
      assertSame(second, first.getCause());
      assertSame(first, second.getCause());
    }
    Fixture f = new Fixture();
    UnsupportedOperationException unknown = new UnsupportedOperationException(FIXTURE_FAULT);
    f.faultAt = FORM_GET_METHOD;
    f.fault = unknown;
    assertSame(
        unknown,
        assertThrows(UnsupportedOperationException.class, () -> CONVERTER.convert(f.asRequest())));
  }

  private static RuntimeException classifiedFormFailure(int kind, Throwable cause) {
    return switch (kind) {
      case 0 -> new IllegalArgumentException(FIXTURE_FAULT, cause);
      case 1 -> new IllegalStateException(FIXTURE_FAULT, cause);
      case 2 -> new NoSuchElementException(FIXTURE_FAULT, cause);
      default -> throw new AssertionError("unknown form exception fixture");
    };
  }
}
