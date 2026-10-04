package dev.codex.schubert.nk.web.view;

import dev.codex.schubert.nk.protocol.layout.*;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionSummaryRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.form.QuestionSearchForm;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.nio.charset.StandardCharsets;
import java.time.*;
import java.time.format.DateTimeFormatter;
import java.util.*;
import org.jspecify.annotations.NullMarked;
import org.springframework.web.util.UriUtils;

/** SCR022/UI224236/SS313314323332; PG-D350368/PT-QRY-HTTP004,005,011,012/QDL-BIZ001,006. */
@NullMarked
public final class QuestionListViewModel {
  private static final DateTimeFormatter TIME =
      DateTimeFormatter.ofPattern("uuuu-MM-dd HH:mm:ss", Locale.ROOT)
          .withZone(ZoneOffset.ofHours(9));
  private final TopBarViewModel topBar;
  private final QuestionSearchForm filters;
  private final Optional<PageViewModel> page;
  private final List<Map<String, Object>> rows;

  private QuestionListViewModel(
      SessionPrincipal actor,
      QuestionSearchForm form,
      Optional<PageViewModel> page,
      List<QuestionSummaryRecord> records) {
    topBar = TopBarViewModel.from(actor);
    if (form.isAdmin() != (actor.role() == UserRole.ADMIN))
      throw new IllegalArgumentException("question display role mismatch");
    filters = form;
    this.page = page;
    rows = List.copyOf(records.stream().map(QuestionListViewModel::row).toList());
  }

  public static QuestionListViewModel success(
      SessionPrincipal actor,
      QuestionSearchForm form,
      PagedResponseData data,
      List<QuestionSummaryRecord> records) {
    Objects.requireNonNull(actor, "actor");
    Objects.requireNonNull(form, "form");
    if (!form.isValid()) throw new IllegalArgumentException("invalid successful question form");
    var page = PageViewModel.from(data, 50);
    if (page.getEffectivePage() != Math.min(form.getPage(), page.getTotalPages()))
      throw new IllegalArgumentException("question page does not match request");
    var copy = List.copyOf(records);
    long expected = page.isEmpty() ? 0 : page.getLastResult() - page.getFirstResult() + 1;
    if (copy.size() != expected)
      throw new IllegalArgumentException("inconsistent question record count");
    PayloadSemanticValidator.validate(
        new TypedPayloadValues(new LayoutId("QSSRSP01"), data, new ArrayList<PayloadRecord>(copy)));
    var ids = new HashSet<Long>();
    for (int i = 0; i < copy.size(); i++) {
      var current = copy.get(i);
      if (!ids.add(current.questionId().value()))
        throw new IllegalArgumentException("duplicate question identity");
      if ((actor.role() == UserRole.USER && !actor.username().equals(current.username()))
          || current.questionSummary().codePointCount(0, current.questionSummary().length()) > 100)
        throw new IllegalArgumentException("invalid question display scope");
      if (i > 0) {
        var previous = copy.get(i - 1);
        int order = previous.submittedAt().compareTo(current.submittedAt());
        if (order < 0
            || (order == 0 && previous.questionId().value() <= current.questionId().value()))
          throw new IllegalArgumentException("invalid question display order");
      }
    }
    return new QuestionListViewModel(actor, form, Optional.of(page), copy);
  }

  public static QuestionListViewModel invalid(SessionPrincipal actor, QuestionSearchForm form) {
    Objects.requireNonNull(actor, "actor");
    Objects.requireNonNull(form, "form");
    if (form.isValid()) throw new IllegalArgumentException("valid form used as invalid");
    return new QuestionListViewModel(actor, form, Optional.empty(), List.of());
  }

  private static Map<String, Object> row(QuestionSummaryRecord data) {
    return Map.copyOf(
        Map.ofEntries(
            Map.entry("id", data.questionId().value()),
            Map.entry("receiptId", data.receiptId()),
            Map.entry("username", data.username()),
            Map.entry("summary", data.questionSummary()),
            Map.entry("state", data.answerState().wireValue()),
            Map.entry("stateLabel", QuestionDetailViewModel.label(data.answerState())),
            Map.entry("submittedAt", TIME.format(data.submittedAt())),
            Map.entry("answeredAt", data.answeredAt().map(TIME::format).orElse("")),
            Map.entry("detailHref", "/questions/" + data.questionId().value()),
            Map.entry(
                "deleteHref", "/questions/" + data.questionId().value() + "#delete-confirm")));
  }

  private String link(int number) {
    var values = filters.getValues();
    return "/questions?keyword="
        + encode(Objects.requireNonNull(values.get("keyword")))
        + "&state="
        + encode(Objects.requireNonNull(values.get("state")))
        + "&from="
        + encode(Objects.requireNonNull(values.get("from")))
        + "&to="
        + encode(Objects.requireNonNull(values.get("to")))
        + (filters.isAdmin()
            ? "&username=" + encode(Objects.requireNonNull(values.get("username")))
            : "")
        + "&page="
        + number;
  }

  private static String encode(String value) {
    return UriUtils.encode(value, StandardCharsets.UTF_8);
  }

  public Optional<String> getPreviousHref() {
    return page.flatMap(
        value ->
            value.getPreviousPage().isPresent()
                ? Optional.of(link(value.getPreviousPage().getAsInt()))
                : Optional.empty());
  }

  public Optional<String> getNextHref() {
    return page.flatMap(
        value ->
            value.getNextPage().isPresent()
                ? Optional.of(link(value.getNextPage().getAsInt()))
                : Optional.empty());
  }

  public TopBarViewModel getTopBar() {
    return topBar;
  }

  public QuestionSearchForm getFilters() {
    return filters;
  }

  public Optional<PageViewModel> getPage() {
    return page;
  }

  public List<Map<String, Object>> getRows() {
    return rows;
  }

  @Override
  public String toString() {
    return "QuestionListViewModel[REDACTED]";
  }
}
