package dev.codex.schubert.characterization;

import static org.junit.jupiter.api.Assertions.*;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import java.lang.reflect.Proxy;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

/** SS355 L01: independent Current operation order/DOM projection, no fixture reset in driver. */
final class SharedLogProjectionDriverTest {
  @Test
  void sameCurrentPathsAndLiteralProjection() throws Exception {
    List<String> operations = new ArrayList<>();
    Page page = page(operations);
    Map<String, Object> actual =
        CurrentCharacterizationTest.captureLogProjection(
            page,
            "https://example.test",
            () -> {
              operations.add("query");
              return new CurrentCharacterizationTest.LogProjectionRows(
                  List.of("", "login_success", "menu", "", "search", "", "log_search", ""),
                  List.of(
                      "REQUEST",
                      "SECURITY",
                      "ACTION",
                      "REQUEST",
                      "ACTION",
                      "REQUEST",
                      "ACTION",
                      "REQUEST"));
            });
    assertEquals(
        List.of(
            "https://example.test/search?q=%E6%84%9B",
            "https://example.test/logs?log_type=ACTION&page=1",
            "query",
            "article.log-row",
            "article.log-row details.log-details"),
        operations);
    assertEquals(
        Map.of(
            "databaseActions",
            List.of("", "login_success", "menu", "", "search", "", "log_search", ""),
            "databaseTypes",
            List.of(
                "REQUEST",
                "SECURITY",
                "ACTION",
                "REQUEST",
                "ACTION",
                "REQUEST",
                "ACTION",
                "REQUEST"),
            "displayedRows",
            2,
            "pageSize",
            100,
            "sort",
            "logged_at desc,id desc",
            "detailsElements",
            2),
        actual);
  }

  @Test
  void emptyOrFailedQueryCannotBecomePass() {
    List<String> operations = new ArrayList<>();
    assertThrows(
        AssertionError.class,
        () ->
            CurrentCharacterizationTest.captureLogProjection(
                page(operations),
                "https://example.test",
                () -> new CurrentCharacterizationTest.LogProjectionRows(List.of(), List.of())));
    assertEquals(2, operations.size());
    var expected = new java.io.IOException("query failure");
    assertSame(
        expected,
        assertThrows(
            java.io.IOException.class,
            () ->
                CurrentCharacterizationTest.captureLogProjection(
                    page(new ArrayList<>()),
                    "https://example.test",
                    () -> {
                      throw expected;
                    })));
  }

  private static Page page(List<String> operations) {
    return (Page)
        Proxy.newProxyInstance(
            Page.class.getClassLoader(),
            new Class<?>[] {Page.class},
            (p, method, args) -> {
              if (method.getName().equals("navigate")) {
                operations.add((String) args[0]);
                return null;
              }
              if (method.getName().equals("locator")) {
                operations.add((String) args[0]);
                return Proxy.newProxyInstance(
                    Locator.class.getClassLoader(),
                    new Class<?>[] {Locator.class},
                    (l, called, ignored) -> {
                      if (called.getName().equals("count")) return 2;
                      throw new AssertionError("unexpected locator operation");
                    });
              }
              throw new AssertionError("unexpected page operation");
            });
  }
}
