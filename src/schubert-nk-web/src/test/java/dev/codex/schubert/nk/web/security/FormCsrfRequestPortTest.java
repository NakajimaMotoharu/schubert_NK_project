package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.lang.reflect.Proxy;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.NoSuchElementException;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Supplier;
import org.junit.jupiter.api.Test;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.security.web.csrf.DefaultCsrfToken;

/** AUT004/UI226/SS313314352/PT-WEB-CSRFPORT001..009; memory values only, no matching/auth. */
final class FormCsrfRequestPortTest {
  private static final String METHOD_PARAMETERS = "getParameterValues";
  private static final String CSRF = "_csrf";
  private static final String HEADER = "X-CSRF-TOKEN";
  private static final String VALUE = "A".repeat(64);
  private static final String READ_TOKEN_ERROR = "value resolution must not read token getters";
  private static final FormCsrfTokenRequestHandler HANDLER = new FormCsrfTokenRequestHandler();
  private static final CsrfToken TOKEN = new DefaultCsrfToken(HEADER, CSRF, VALUE);

  private static final class Fixture {
    String query;
    String[] submitted = {VALUE};
    String faultAt;
    Throwable fault;
    int parameterReads;
    final Map<String, Object> attributes = new LinkedHashMap<>();

    HttpServletRequest asRequest() {
      return (HttpServletRequest)
          Proxy.newProxyInstance(
              HttpServletRequest.class.getClassLoader(),
              new Class<?>[] {HttpServletRequest.class},
              (proxy, method, args) -> {
                if (method.getName().equals(faultAt)) throw fault;
                return switch (method.getName()) {
                  case "getQueryString" -> query;
                  case METHOD_PARAMETERS -> {
                    assertEquals(CSRF, args[0]);
                    parameterReads++;
                    yield submitted;
                  }
                  case "setAttribute" -> {
                    attributes.put((String) args[0], args[1]);
                    yield null;
                  }
                  case "getAttribute" -> attributes.get((String) args[0]);
                  case "toString" -> "memory csrf request";
                  case "hashCode" -> System.identityHashCode(proxy);
                  case "equals" -> proxy == args[0];
                  default ->
                      throw new AssertionError(
                          "unexpected csrf fixture request " + method.getName());
                };
              });
    }
  }

  private static HttpServletResponse response() {
    return (HttpServletResponse)
        Proxy.newProxyInstance(
            HttpServletResponse.class.getClassLoader(),
            new Class<?>[] {HttpServletResponse.class},
            (proxy, method, args) -> {
              if (method.getName().equals("toString")) return "memory csrf response";
              throw new AssertionError("response must not be mutated by attribute handler");
            });
  }

  @Test
  void lazyHandlingSetsOnlyTheTwoRequestAliases() {
    var f = new Fixture();
    var calls = new AtomicInteger();
    HANDLER.handle(
        f.asRequest(),
        response(),
        () -> {
          calls.incrementAndGet();
          return TOKEN;
        });
    assertEquals(0, calls.get());
    assertEquals(2, f.attributes.size());
    var stored = assertInstanceOf(CsrfToken.class, f.attributes.get(CSRF));
    assertSame(stored, f.attributes.get(CsrfToken.class.getName()));
    assertEquals(VALUE, stored.getToken());
    assertEquals(1, calls.get());
    assertEquals(CSRF, stored.getParameterName());
    assertEquals(HEADER, stored.getHeaderName());
  }

  @Test
  void nullApiBoundariesRejectBeforeDelegation() {
    var f = new Fixture();
    var request = f.asRequest();
    var response = response();
    Supplier<CsrfToken> supplier = () -> TOKEN;
    assertThrows(NullPointerException.class, () -> HANDLER.handle(null, response, supplier));
    assertThrows(NullPointerException.class, () -> HANDLER.handle(request, null, supplier));
    assertThrows(NullPointerException.class, () -> HANDLER.handle(request, response, null));
    assertThrows(NullPointerException.class, () -> HANDLER.resolveCsrfTokenValue(null, TOKEN));
    assertThrows(NullPointerException.class, () -> HANDLER.resolveCsrfTokenValue(request, null));
    assertEquals(Map.of(), f.attributes);
  }

  @Test
  void validSchemaReturnsSubmittedValueWithoutReadingToken() {
    CsrfToken unread =
        new CsrfToken() {
          private static final long serialVersionUID = 1L;

          @Override
          public String getHeaderName() {
            throw new AssertionError(READ_TOKEN_ERROR);
          }

          @Override
          public String getParameterName() {
            throw new AssertionError(READ_TOKEN_ERROR);
          }

          @Override
          public String getToken() {
            throw new AssertionError(READ_TOKEN_ERROR);
          }
        };
    for (String value : List.of(VALUE, "z".repeat(128), "aB0_-".repeat(20))) {
      var f = new Fixture();
      f.submitted = new String[] {value};
      assertEquals(value, HANDLER.resolveCsrfTokenValue(f.asRequest(), unread));
      assertEquals(1, f.parameterReads);
    }
  }

  @Test
  void missingMultipleNullAndMalformedValuesReturnNull() {
    for (String[] values :
        Arrays.asList(null, new String[0], new String[] {null}, new String[] {VALUE, VALUE})) {
      var f = new Fixture();
      f.submitted = values;
      assertNull(HANDLER.resolveCsrfTokenValue(f.asRequest(), TOKEN));
    }
    for (String value :
        List.of(
            "",
            "a".repeat(63),
            "a".repeat(129),
            " " + VALUE,
            VALUE + "+",
            VALUE + "/",
            VALUE + "é",
            VALUE + "\n")) {
      var f = new Fixture();
      f.submitted = new String[] {value};
      assertNull(HANDLER.resolveCsrfTokenValue(f.asRequest(), TOKEN));
    }
  }

  @Test
  void queryCsrfAndInvalidEscapesRejectBeforeBodyRead() {
    for (String key : List.of(CSRF, "%5fcsrf", "%5Fcsrf", "%5fc%73rf", "%", "%GG")) {
      var f = new Fixture();
      f.query = "unrelated=1&" + key + "=public";
      assertNull(HANDLER.resolveCsrfTokenValue(f.asRequest(), TOKEN));
      assertEquals(0, f.parameterReads);
    }
  }

  @Test
  void absentEmptyAndDifferentCaseQueryNamesKeepBodyValue() {
    for (String query :
        Arrays.asList(null, "", "unrelated=1&empty", "_CSRF=public", "q=%26&%61=public")) {
      var f = new Fixture();
      f.query = query;
      assertEquals(VALUE, HANDLER.resolveCsrfTokenValue(f.asRequest(), TOKEN));
      assertEquals(1, f.parameterReads);
    }
  }

  @Test
  void deferredNullAndFailureAreNotMadeIntoValidValues() {
    var missing = new Fixture();
    HANDLER.handle(missing.asRequest(), response(), () -> null);
    var absent = assertInstanceOf(CsrfToken.class, missing.attributes.get(CSRF));
    assertEquals(
        "csrfTokenSupplier returned null delegate",
        assertThrows(IllegalStateException.class, absent::getToken).getMessage());
    var failure = new IllegalStateException("synthetic supplier fault");
    var broken = new Fixture();
    HANDLER.handle(
        broken.asRequest(),
        response(),
        () -> {
          throw failure;
        });
    var delegated = assertInstanceOf(CsrfToken.class, broken.attributes.get(CSRF));
    assertSame(failure, assertThrows(IllegalStateException.class, delegated::getToken));
  }

  @Test
  void bodyArgumentFaultIsNullButOutsideQueryAndFatalPropagate() {
    var body = new Fixture();
    body.faultAt = METHOD_PARAMETERS;
    body.fault = new IllegalArgumentException("synthetic body fault");
    assertNull(HANDLER.resolveCsrfTokenValue(body.asRequest(), TOKEN));
    var queryFailure = new IllegalArgumentException("synthetic query fault");
    var query = new Fixture();
    query.faultAt = "getQueryString";
    query.fault = queryFailure;
    assertSame(
        queryFailure,
        assertThrows(
            IllegalArgumentException.class,
            () -> HANDLER.resolveCsrfTokenValue(query.asRequest(), TOKEN)));
    var fatal = new AssertionError("synthetic fatal");
    var broken = new Fixture();
    broken.faultAt = METHOD_PARAMETERS;
    broken.fault = fatal;
    assertSame(
        fatal,
        assertThrows(
            AssertionError.class, () -> HANDLER.resolveCsrfTokenValue(broken.asRequest(), TOKEN)));
    var stateFailure = new NoSuchElementException("synthetic enumeration fault");
    var other = new Fixture();
    other.faultAt = METHOD_PARAMETERS;
    other.fault = stateFailure;
    assertSame(
        stateFailure,
        assertThrows(
            NoSuchElementException.class,
            () -> HANDLER.resolveCsrfTokenValue(other.asRequest(), TOKEN)));
  }

  @Test
  void sharedHandlerKeepsParallelRequestAttributesSeparate() throws Exception {
    try (var workers = Executors.newFixedThreadPool(2)) {
      var pending = new ArrayList<Future<String>>();
      for (int i = 0; i < 8; i++) {
        String value = "A".repeat(64 + i);
        pending.add(
            workers.submit(
                () -> {
                  var f = new Fixture();
                  f.submitted = new String[] {value};
                  var request = f.asRequest();
                  HANDLER.handle(
                      request, response(), () -> new DefaultCsrfToken(HEADER, CSRF, value));
                  assertEquals(2, f.attributes.size());
                  assertSame(f.attributes.get(CSRF), f.attributes.get(CsrfToken.class.getName()));
                  assertEquals(
                      value, assertInstanceOf(CsrfToken.class, f.attributes.get(CSRF)).getToken());
                  return HANDLER.resolveCsrfTokenValue(request, TOKEN);
                }));
      }
      for (int i = 0; i < 8; i++)
        assertEquals("A".repeat(64 + i), pending.get(i).get(10, TimeUnit.SECONDS));
    }
  }
}
