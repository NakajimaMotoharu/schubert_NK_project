package dev.codex.schubert.nk.web.view;

import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.log.LogRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.time.ZoneOffset;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/**
 * SCR014/FUN008/AUT002/MON003/UI225,235/SS311,313,323,352/PG212/PT-WEB262..269. Verified-wire
 * display snapshot.
 */
@NullMarked
public final class LogSearchResultsViewModel {
  private final TopBarViewModel topBar;
  private final PageViewModel page;
  private final List<Row> rows;

  private LogSearchResultsViewModel(
      SessionPrincipal actor, PageViewModel page, List<LogRecord> records) {
    topBar = TopBarViewModel.from(actor);
    this.page = page;
    rows = List.copyOf(records.stream().map(Row::new).toList());
  }

  public static LogSearchResultsViewModel from(
      SessionPrincipal actor, PagedResponseData data, List<LogRecord> records) {
    Objects.requireNonNull(actor, "actor");
    if (actor.role() != UserRole.ADMIN)
      throw new IllegalArgumentException("log display requires administrator");
    var page = PageViewModel.from(data, 100);
    var copy = List.copyOf(records);
    long expected = page.isEmpty() ? 0 : page.getLastResult() - page.getFirstResult() + 1;
    if (copy.size() != expected)
      throw new IllegalArgumentException("inconsistent log record count");
    var ids = new HashSet<Long>();
    for (int i = 0; i < copy.size(); i++) {
      var current = copy.get(i);
      if (!ids.add(current.logId().value()))
        throw new IllegalArgumentException("duplicate log identity");
      if (i > 0) {
        var previous = copy.get(i - 1);
        int time = previous.occurredAt().compareTo(current.occurredAt());
        if (time < 0 || (time == 0 && previous.logId().value() <= current.logId().value()))
          throw new IllegalArgumentException("invalid log display order");
      }
    }
    return new LogSearchResultsViewModel(actor, page, copy);
  }

  public TopBarViewModel getTopBar() {
    return topBar;
  }

  public PageViewModel getPage() {
    return page;
  }

  public List<Row> getRows() {
    return rows;
  }

  @Override
  public String toString() {
    return "LogSearchResultsViewModel[REDACTED]";
  }

  public static final class Row {
    private final long id;
    private final String loggedAt;
    private final String logType;
    private final String level;
    private final String action;
    private final String message;
    private final String requestId;
    private final String messageId;
    private final String correlationId;
    private final String method;
    private final String path;
    private final String remoteAddr;
    private final String details;
    private final Optional<Integer> status;
    private final Optional<Integer> elapsedMs;

    private Row(LogRecord record) {
      id = record.logId().value();
      loggedAt = record.occurredAt().atOffset(ZoneOffset.UTC).toString();
      logType = record.logType().wireValue();
      level = record.level().wireValue();
      action = record.action().orElse("");
      message = record.message();
      requestId = record.httpRequestId().map(UUID::toString).orElse("");
      messageId = record.businessMessageId().map(UUID::toString).orElse("");
      correlationId = record.correlationId().map(UUID::toString).orElse("");
      method = record.httpMethod().orElse("");
      path = record.path().orElse("");
      status = record.httpStatus().map(v -> v.value());
      elapsedMs = record.elapsedMs().map(v -> v.value());
      remoteAddr = record.remoteAddress().orElse("");
      details = record.details().orElse("");
    }

    public long getId() {
      return id;
    }

    public String getLoggedAt() {
      return loggedAt;
    }

    public String getLogType() {
      return logType;
    }

    public String getLevel() {
      return level;
    }

    public String getAction() {
      return action;
    }

    public String getMessage() {
      return message;
    }

    public String getRequestId() {
      return requestId;
    }

    public String getMessageId() {
      return messageId;
    }

    public String getCorrelationId() {
      return correlationId;
    }

    public String getMethod() {
      return method;
    }

    public String getPath() {
      return path;
    }

    public Optional<Integer> getStatus() {
      return status;
    }

    public Optional<Integer> getElapsedMs() {
      return elapsedMs;
    }

    public String getRemoteAddr() {
      return remoteAddr;
    }

    public String getDetails() {
      return details;
    }

    @Override
    public String toString() {
      return "LogDisplayRow[REDACTED]";
    }
  }
}
