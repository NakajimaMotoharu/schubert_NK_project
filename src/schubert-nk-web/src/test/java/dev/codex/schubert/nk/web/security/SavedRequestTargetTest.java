package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** Explicit URL bytes, no production normalization used for expected. PT-WEB-005..008. */
class SavedRequestTargetTest {
  private static final String GET_METHOD = "GET";

  @Test
  void web005SafeGetTargetsPreservePathAndQuery() {
    for (String value :
        List.of(
            "/",
            "/scenarios",
            "/file..txt",
            "/.../file",
            "/.hidden",
            "/logs?page=2",
            "/admin/users",
            "/audio/12?download=true",
            "/search?",
            "/search?q=日本語",
            "/search?q=%E6%97%A5%2F%2E%5C%23&next=https%3A%2F%2Fexample.test",
            "/search?q=a+b&x=%20",
            "/search?q=e\u0301",
            "/search?x=../&y=//external.test")) {
      var target = SavedRequestTarget.fromGet(GET_METHOD, value);
      assertEquals(value, target.location());
      assertEquals("SavedRequestTarget[REDACTED]", target.toString());
    }
  }

  @Test
  void web006ExternalMalformedAndStateChangingTargetsReject() {
    assertThrows(NullPointerException.class, () -> SavedRequestTarget.fromGet(null, "/"));
    assertThrows(NullPointerException.class, () -> SavedRequestTarget.fromGet(GET_METHOD, null));
    for (String method : List.of("POST", "PUT", "DELETE", "HEAD", "get", "")) invalid(method, "/");
    for (String value :
        List.of(
            "",
            "relative",
            "?q=x",
            "https://external.test/path",
            "javascript:alert(1)",
            "//external.test/path",
            "///path",
            "/path#fragment",
            "/path\\x",
            "/path\r\nLocation: https://example.test",
            "/path\u0000",
            "/path\u2028x",
            "/path\u2029x",
            "/a/../b",
            "/../logs",
            "/..",
            "/../../logs",
            "/.",
            "/./logs",
            "/a/..",
            "/a/.",
            "/a//b",
            "/a/./b",
            "/%2fexternal",
            "/%2Fexternal",
            "/%5cexternal",
            "/%2e%2e/path",
            "/path%",
            "/path?bad=%GG")) invalid(GET_METHOD, value);
  }

  @Test
  void web007Utf8LimitAndUnicodeBoundariesAreExact() {
    for (int length : new int[] {2047, 2048}) {
      String value = "/q?x=" + "a".repeat(length - 5);
      assertEquals(length, value.getBytes(StandardCharsets.UTF_8).length);
      assertEquals(value, SavedRequestTarget.fromGet(GET_METHOD, value).location());
    }
    String unicode = "/q?x=" + "あ".repeat(681);
    assertEquals(2048, unicode.getBytes(StandardCharsets.UTF_8).length);
    assertEquals(unicode, SavedRequestTarget.fromGet(GET_METHOD, unicode).location());
    invalid(GET_METHOD, "/" + "a".repeat(2048));
    invalid(GET_METHOD, unicode + "a");
    for (String value : List.of("/q?x=\ud800", "/q?x=\udc00", " /q", "/q ", "/q?x= "))
      invalid(GET_METHOD, value);
    String pair = "/q?x=\ud83d\ude00";
    assertEquals(pair, SavedRequestTarget.fromGet(GET_METHOD, pair).location());
  }

  @Test
  void web008ConcurrentTargetsRemainIndependent() throws Exception {
    try (var pool = Executors.newFixedThreadPool(10)) {
      var futures = new ArrayList<Future<Void>>();
      for (int i = 0; i < 100; i++) {
        final int n = i;
        futures.add(
            pool.submit(
                () -> {
                  String value = "/scenarios?q=日本語" + n + "&page=" + (n + 1);
                  var target = SavedRequestTarget.fromGet(GET_METHOD, value);
                  assertEquals(value, target.location());
                  assertFalse(target.toString().contains("日本語"));
                  assertEquals("SavedRequestTarget[REDACTED]", target.toString());
                  return null;
                }));
      }
      for (var future : futures) future.get(20, TimeUnit.SECONDS);
    }
  }

  static void invalid(String method, String value) {
    var error =
        assertThrows(
            IllegalArgumentException.class, () -> SavedRequestTarget.fromGet(method, value));
    assertEquals("saved GET target is invalid", error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }
}
