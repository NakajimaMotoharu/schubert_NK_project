package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import java.beans.IntrospectionException;
import java.beans.Introspector;
import java.lang.reflect.InvocationTargetException;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.OptionalInt;
import java.util.Set;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import org.jsoup.Jsoup;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.thymeleaf.context.Context;
import org.thymeleaf.spring6.SpringTemplateEngine;
import org.thymeleaf.templateresolver.StringTemplateResolver;

/** PG192/SS313 section6.1/UI234 section2; independent literal pagination fixtures,015004. */
class PageViewModelTest {
  private record Fixture(long[] values, int previous, int next) {
    PagedResponseData data() {
      return new PagedResponseData(
          (int) values[0], (int) values[1], values[2], (int) values[3], values[4], values[5]);
    }
  }

  private static Fixture fixture(
      int page, int size, long total, int pages, long first, long last, int previous, int next) {
    return new Fixture(new long[] {page, size, total, pages, first, last}, previous, next);
  }

  private static List<Fixture> pages() {
    return List.of(
        fixture(1, 50, 101, 3, 1, 50, 0, 2),
        fixture(2, 50, 101, 3, 51, 100, 1, 3),
        fixture(3, 50, 101, 3, 101, 101, 2, 0),
        fixture(1, 100, 201, 3, 1, 100, 0, 2),
        fixture(2, 100, 201, 3, 101, 200, 1, 3),
        fixture(3, 100, 201, 3, 201, 201, 2, 0));
  }

  @Test
  @DisplayName("PT-WEB-174 empty and single page")
  void web174EmptyAndSinglePage() {
    for (int size : new int[] {50, 100}) {
      check(fixture(1, size, 0, 1, 0, 0, 0, 0));
      check(fixture(1, size, 1, 1, 1, 1, 0, 0));
      check(fixture(1, size, size, 1, 1, size, 0, 0));
    }
  }

  @Test
  @DisplayName("PT-WEB-175 first middle and last")
  void web175FirstMiddleAndLastPages() {
    pages().forEach(PageViewModelTest::check);
  }

  @Test
  @DisplayName("PT-WEB-176 maximum independent literals")
  void web176MaximumWireBounds() {
    check(fixture(999999, 50, 49999950, 999999, 49999901, 49999950, 999998, 0));
    check(fixture(999999, 100, 99999900, 999999, 99999801, 99999900, 999998, 0));
    check(fixture(1, 50, 49999950, 999999, 1, 50, 0, 2));
    check(fixture(1, 100, 99999900, 999999, 1, 100, 0, 2));
  }

  @Test
  @DisplayName("PT-WEB-177 inconsistent projections reject")
  void web177InvalidProjectionCombinations() {
    for (Fixture bad :
        List.of(
            fixture(1, 51, 1, 1, 1, 1, 0, 0), fixture(1, 50, 49999951, 999999, 1, 50, 0, 0),
            fixture(0, 50, 1, 1, 0, 0, 0, 0), fixture(2, 50, 1, 1, 1, 1, 0, 0),
            fixture(1, 50, 51, 1, 1, 50, 0, 0), fixture(1, 50, 1, 0, 1, 1, 0, 0),
            fixture(1, 50, 51, 2, 0, 50, 0, 0), fixture(1, 50, 51, 2, 1, 49, 0, 0),
            fixture(1, 50, 0, 1, 1, 0, 0, 0), fixture(1, 50, 0, 1, 0, 1, 0, 0))) {
      var failure =
          assertThrows(IllegalArgumentException.class, () -> PageViewModel.from(bad.data(), 50));
      assertEquals("invalid page projection", failure.getMessage());
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
    }
    assertThrows(
        IllegalArgumentException.class,
        () -> PageViewModel.from(fixture(1, 100, 99999901, 999999, 1, 100, 0, 0).data(), 100));
    assertThrows(
        IllegalArgumentException.class,
        () -> PageViewModel.from(fixture(1, 50, 1, 1, 1, 1, 0, 0).data(), 100));
    assertThrows(IllegalArgumentException.class, () -> new PagedResponseData(-1, 50, 0, 1, 0, 0));
    assertThrows(
        IllegalArgumentException.class, () -> new PagedResponseData(1000000, 50, 0, 1, 0, 0));
  }

  @Test
  @DisplayName("PT-WEB-178 null configuration and redaction")
  void web178NullConfigurationAndRedaction() {
    assertThrows(NullPointerException.class, () -> PageViewModel.from(null, 50));
    var input = fixture(1, 50, 0, 1, 0, 0, 0, 0).data();
    for (int invalid : new int[] {-1, 0, 1, 49, 51, 99, 101, 999, Integer.MAX_VALUE}) {
      var failure =
          assertThrows(IllegalArgumentException.class, () -> PageViewModel.from(input, invalid));
      assertEquals("unsupported page size", failure.getMessage());
    }
    assertEquals("PageViewModel[REDACTED]", PageViewModel.from(input, 50).toString());
  }

  @Test
  @DisplayName("PT-WEB-179 independent parallel projections")
  void web179IndependentParallelProjection()
      throws InterruptedException, ExecutionException, TimeoutException {
    var fixtures =
        List.of(fixture(1, 50, 0, 1, 0, 0, 0, 0), pages().get(1), pages().get(3), pages().get(5));
    var executor = Executors.newFixedThreadPool(8);
    try {
      var tasks = new ArrayList<java.util.concurrent.Future<?>>();
      for (int i = 0; i < 100; i++) {
        Fixture value = fixtures.get(i % 4);
        tasks.add(executor.submit(() -> check(value)));
      }
      for (var task : tasks) task.get(10, TimeUnit.SECONDS);
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
    }
  }

  @Test
  @DisplayName("PT-WEB-180 closed JavaBean contract")
  void web180JavaBeanDisplayContract()
      throws IntrospectionException, IllegalAccessException, InvocationTargetException {
    var model = PageViewModel.from(pages().get(1).data(), 50);
    Set<String> names = new HashSet<>();
    for (var property :
        Introspector.getBeanInfo(PageViewModel.class, Object.class).getPropertyDescriptors()) {
      assertTrue(names.add(property.getName()));
      assertNull(property.getWriteMethod());
      Object value = property.getReadMethod().invoke(model);
      assertNotNull(value);
      assertFalse(value instanceof PagedResponseData);
    }
    assertEquals(
        Set.of(
            "effectivePage",
            "pageSize",
            "totalCount",
            "totalPages",
            "firstResult",
            "lastResult",
            "previousPage",
            "nextPage",
            "empty",
            "paginated"),
        names);
  }

  @Test
  @DisplayName("PT-WEB-181 synthetic Thymeleaf DOM")
  void web181ThymeleafSyntheticDom() {
    var resolver = new StringTemplateResolver();
    resolver.setTemplateMode("HTML");
    resolver.setCacheable(false);
    var engine = new SpringTemplateEngine();
    engine.setTemplateResolver(resolver);
    String template =
        """
        <main><span id="page" th:text="${page.effectivePage}"></span>
        <span id="count" th:text="${page.totalCount}"></span>
        <span id="pages" th:text="${page.totalPages}"></span>
        <span id="first" th:text="${page.firstResult}"></span>
        <span id="last" th:text="${page.lastResult}"></span>
        <span id="empty" th:if="${page.empty}">該当するデータはありません</span>
        <nav id="pagination" th:if="${page.paginated}">
        <span id="previous" th:if="${page.previousPage.present}" th:text="${page.previousPage.asInt}"></span>
        <span id="next" th:if="${page.nextPage.present}" th:text="${page.nextPage.asInt}"></span>
        </nav></main>
        """;
    var fixtures = new ArrayList<>(pages());
    fixtures.add(fixture(1, 50, 0, 1, 0, 0, 0, 0));
    fixtures.add(fixture(1, 100, 1, 1, 1, 1, 0, 0));
    for (Fixture fixture : fixtures) {
      var page = PageViewModel.from(fixture.data(), (int) fixture.values[1]);
      var dom =
          Jsoup.parse(engine.process(template, new Context(Locale.ROOT, Map.of("page", page))));
      String[] ids = {"page", "count", "pages", "first", "last"};
      int[] indexes = {0, 2, 3, 4, 5};
      for (int i = 0; i < ids.length; i++)
        assertEquals(Long.toString(fixture.values[indexes[i]]), dom.select("#" + ids[i]).text());
      assertEquals(fixture.values[2] == 0 ? 1 : 0, dom.select("#empty").size());
      if (fixture.values[2] == 0) assertEquals("該当するデータはありません", dom.select("#empty").text());
      assertEquals(fixture.values[3] > 1 ? 1 : 0, dom.select("#pagination").size());
      assertEquals(
          fixture.previous == 0 ? "" : Integer.toString(fixture.previous),
          dom.select("#previous").text());
      assertEquals(
          fixture.next == 0 ? "" : Integer.toString(fixture.next), dom.select("#next").text());
    }
  }

  private static void check(Fixture fixture) {
    var value = PageViewModel.from(fixture.data(), (int) fixture.values[1]);
    assertEquals(fixture.values[0], value.getEffectivePage());
    assertEquals(fixture.values[1], value.getPageSize());
    assertEquals(fixture.values[2], value.getTotalCount());
    assertEquals(fixture.values[3], value.getTotalPages());
    assertEquals(fixture.values[4], value.getFirstResult());
    assertEquals(fixture.values[5], value.getLastResult());
    assertEquals(
        fixture.previous == 0 ? OptionalInt.empty() : OptionalInt.of(fixture.previous),
        value.getPreviousPage());
    assertEquals(
        fixture.next == 0 ? OptionalInt.empty() : OptionalInt.of(fixture.next),
        value.getNextPage());
    assertEquals(fixture.values[2] == 0, value.isEmpty());
    assertEquals(fixture.values[3] > 1, value.isPaginated());
  }
}
