package dev.codex.schubert.nk.web.view;

import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import java.util.Objects;
import java.util.OptionalInt;
import org.jspecify.annotations.NullMarked;

/**
 * Closed display numbers only; NK-WEB-001/FUN003/008/009/QST005/NTF; UI234/235/236; SS313
 * section6.1; PG192/PT-WEB-174..181.
 */
@NullMarked
public final class PageViewModel {
  private final int effectivePage;
  private final int pageSize;
  private final long totalCount;
  private final int totalPages;
  private final long firstResult;
  private final long lastResult;

  private PageViewModel(PagedResponseData data) {
    effectivePage = data.effectivePage();
    pageSize = data.pageSize();
    totalCount = data.totalCount();
    totalPages = data.totalPages();
    firstResult = data.firstResult();
    lastResult = data.lastResult();
  }

  /** Caller supplies the interface's fixed size; never repairs an inconsistent response. */
  public static PageViewModel from(PagedResponseData data, int expectedPageSize) {
    Objects.requireNonNull(data, "page data");
    if (expectedPageSize != 50 && expectedPageSize != 100)
      throw new IllegalArgumentException("unsupported page size");
    long total = data.totalCount();
    long pages = Math.max(1, (total + expectedPageSize - 1) / expectedPageSize);
    long first = total == 0 ? 0 : (data.effectivePage() - 1L) * expectedPageSize + 1;
    long last = Math.min((long) data.effectivePage() * expectedPageSize, total);
    if (data.pageSize() != expectedPageSize
        || total > 999999L * expectedPageSize
        || data.effectivePage() < 1
        || data.effectivePage() > pages
        || data.totalPages() != pages
        || data.firstResult() != first
        || data.lastResult() != last) throw new IllegalArgumentException("invalid page projection");
    return new PageViewModel(data);
  }

  public int getEffectivePage() {
    return effectivePage;
  }

  public int getPageSize() {
    return pageSize;
  }

  public long getTotalCount() {
    return totalCount;
  }

  public int getTotalPages() {
    return totalPages;
  }

  public long getFirstResult() {
    return firstResult;
  }

  public long getLastResult() {
    return lastResult;
  }

  public boolean isEmpty() {
    return totalCount == 0;
  }

  public boolean isPaginated() {
    return totalPages > 1;
  }

  public OptionalInt getPreviousPage() {
    return effectivePage > 1 ? OptionalInt.of(effectivePage - 1) : OptionalInt.empty();
  }

  public OptionalInt getNextPage() {
    return effectivePage < totalPages ? OptionalInt.of(effectivePage + 1) : OptionalInt.empty();
  }

  @Override
  public String toString() {
    return "PageViewModel[REDACTED]";
  }
}
