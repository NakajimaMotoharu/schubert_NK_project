package dev.codex.schubert.nk.web.view;

import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.log.LogRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.form.LogSearchForm;
import dev.codex.schubert.nk.web.form.LogSearchForm.Code;
import dev.codex.schubert.nk.web.form.LogSearchForm.Field;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.OptionalInt;
import org.jspecify.annotations.NullMarked;
import org.springframework.web.util.UriUtils;

/** SCR014/FUN008/AUT002/MON003/UI222,225,235/SS313,352/PG215/PT-WEB286..293. */
@NullMarked
public final class LogSearchViewModel {
  private final TopBarViewModel topBar;
  private final Filters filters;
  private final List<FieldError> errors;
  private final Optional<LogSearchResultsViewModel> results;
  private final Optional<String> previousHref;
  private final Optional<String> nextHref;

  private LogSearchViewModel(
      SessionPrincipal actor, LogSearchForm form, Optional<LogSearchResultsViewModel> results) {
    Objects.requireNonNull(actor, "actor");
    if (actor.role() != UserRole.ADMIN)
      throw new IllegalArgumentException("log display requires administrator");
    topBar = TopBarViewModel.from(actor);
    filters = new Filters(form);
    errors =
        List.copyOf(
            Arrays.stream(Field.values())
                .filter(field -> form.getIssues().containsKey(field))
                .map(
                    field ->
                        new FieldError(field, Objects.requireNonNull(form.getIssues().get(field))))
                .toList());
    this.results = results;
    previousHref = results.flatMap(value -> pageLink(value.getPage().getPreviousPage()));
    nextHref = results.flatMap(value -> pageLink(value.getPage().getNextPage()));
  }

  public static LogSearchViewModel success(
      SessionPrincipal actor, LogSearchForm form, PagedResponseData data, List<LogRecord> records) {
    Objects.requireNonNull(form, "form");
    if (!form.isValid()) throw new IllegalArgumentException("invalid successful log form");
    var result = LogSearchResultsViewModel.from(actor, data, records);
    if (result.getPage().getEffectivePage()
        != Math.min(form.getPage(), result.getPage().getTotalPages()))
      throw new IllegalArgumentException("log response page does not match request");
    return new LogSearchViewModel(actor, form, Optional.of(result));
  }

  public static LogSearchViewModel invalid(SessionPrincipal actor, LogSearchForm form) {
    Objects.requireNonNull(form, "form");
    if (form.isValid()) throw new IllegalArgumentException("valid form used as invalid");
    return new LogSearchViewModel(actor, form, Optional.empty());
  }

  private Optional<String> pageLink(OptionalInt page) {
    if (page.isEmpty()) return Optional.empty();
    return Optional.of(
        "/logs?q="
            + encode(filters.q)
            + "&log_type="
            + encode(filters.logType)
            + "&action="
            + encode(filters.action)
            + "&path="
            + encode(filters.path)
            + "&level="
            + encode(filters.level)
            + "&from="
            + encode(filters.from)
            + "&to="
            + encode(filters.to)
            + "&page="
            + page.getAsInt());
  }

  private static String encode(String value) {
    return UriUtils.encode(value, StandardCharsets.UTF_8);
  }

  public TopBarViewModel getTopBar() {
    return topBar;
  }

  public Filters getFilters() {
    return filters;
  }

  public List<FieldError> getErrors() {
    return errors;
  }

  public Optional<LogSearchResultsViewModel> getResults() {
    return results;
  }

  public Optional<String> getPreviousHref() {
    return previousHref;
  }

  public Optional<String> getNextHref() {
    return nextHref;
  }

  @Override
  public String toString() {
    return "LogSearchViewModel[REDACTED]";
  }

  public static final class Filters {
    private final String q;
    private final String logType;
    private final String action;
    private final String path;
    private final String level;
    private final String from;
    private final String to;

    private Filters(LogSearchForm form) {
      var values = form.getValues();
      q = Objects.requireNonNull(values.get(Field.Q));
      logType = Objects.requireNonNull(values.get(Field.LOG_TYPE));
      action = Objects.requireNonNull(values.get(Field.ACTION));
      path = Objects.requireNonNull(values.get(Field.PATH));
      level = Objects.requireNonNull(values.get(Field.LEVEL));
      from = Objects.requireNonNull(values.get(Field.FROM));
      to = Objects.requireNonNull(values.get(Field.TO));
    }

    public String getQ() {
      return q;
    }

    public String getLogType() {
      return logType;
    }

    public String getAction() {
      return action;
    }

    public String getPath() {
      return path;
    }

    public String getLevel() {
      return level;
    }

    public String getFrom() {
      return from;
    }

    public String getTo() {
      return to;
    }

    @Override
    public String toString() {
      return "LogFilters[REDACTED]";
    }
  }

  public static final class FieldError {
    private static final Map<Field, String> NAMES =
        Map.of(
            Field.FORM,
            "form",
            Field.Q,
            "q",
            Field.LOG_TYPE,
            "log_type",
            Field.ACTION,
            "action",
            Field.PATH,
            "path",
            Field.LEVEL,
            "level",
            Field.FROM,
            "from",
            Field.TO,
            "to",
            Field.PAGE,
            "page");
    private static final Map<Code, String> MESSAGES =
        Map.of(
            Code.BINDING, "入力項目を確認してください。",
            Code.CHARACTERS, "使用できない文字が含まれています。",
            Code.VALUE, "入力値を確認してください。",
            Code.RANGE, "From/Toは順序を確認し、31日以内にしてください。");
    private static final Map<Field, String> LENGTHS =
        Map.of(
            Field.Q, "メッセージはUTF-8で256 byte以内にしてください。",
            Field.ACTION, "アクションはUTF-8で64 byte以内にしてください。",
            Field.PATH, "パスはUTF-8で256 byte以内にしてください。");
    private final String name;
    private final String message;

    private FieldError(Field field, Code code) {
      name = Objects.requireNonNull(NAMES.get(field));
      message =
          Objects.requireNonNull(code == Code.LENGTH ? LENGTHS.get(field) : MESSAGES.get(code));
    }

    public String getName() {
      return name;
    }

    public String getMessage() {
      return message;
    }

    @Override
    public String toString() {
      return "LogFieldError[REDACTED]";
    }
  }
}
