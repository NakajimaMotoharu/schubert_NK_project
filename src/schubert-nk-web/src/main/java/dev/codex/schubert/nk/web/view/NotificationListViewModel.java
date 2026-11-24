package dev.codex.schubert.nk.web.view;

import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationState;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationType;
import dev.codex.schubert.nk.web.form.NotificationSearchForm;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.nio.charset.StandardCharsets;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;
import org.springframework.web.util.UriUtils;

/** SCR020 display only/UI224,236/SS313,332; PG-D347/PT-NTF-HTTP001..010. */
@NullMarked
public final class NotificationListViewModel {
  private static final DateTimeFormatter TIME =
      DateTimeFormatter.ofPattern("uuuu-MM-dd HH:mm:ss", Locale.ROOT)
          .withZone(ZoneOffset.ofHours(9));
  private static final Map<NotificationState, NotificationType> DISPLAY_TYPES =
      Map.of(
          NotificationState.RECEIVED, NotificationType.ACCEPTED,
          NotificationState.PROCESSING, NotificationType.ACCEPTED,
          NotificationState.CANCELLED, NotificationType.ACCEPTED,
          NotificationState.COMPLETED, NotificationType.COMPLETED,
          NotificationState.ERROR, NotificationType.ERROR);
  private static final Map<NotificationType, String> TYPE_LABELS =
      Map.of(
          NotificationType.ACCEPTED, "受付通知",
          NotificationType.COMPLETED, "処理済通知",
          NotificationType.ERROR, "エラー通知");
  private final TopBarViewModel topBar;
  private final NotificationSearchForm filters;
  private final Optional<PageViewModel> page;
  private final List<Map<String, Object>> rows;

  private NotificationListViewModel(
      SessionPrincipal actor,
      NotificationSearchForm form,
      Optional<PageViewModel> page,
      List<NotificationRecord> records) {
    topBar = TopBarViewModel.from(Objects.requireNonNull(actor, "actor"));
    filters = form;
    this.page = page;
    rows = List.copyOf(records.stream().map(NotificationListViewModel::row).toList());
  }

  public static NotificationListViewModel success(
      SessionPrincipal actor,
      NotificationSearchForm form,
      PagedResponseData data,
      List<NotificationRecord> records) {
    Objects.requireNonNull(form, "form");
    if (!form.isValid()) throw new IllegalArgumentException("invalid successful notification form");
    var page = PageViewModel.from(data, 50);
    if (page.getEffectivePage() != Math.min(form.getPage(), page.getTotalPages()))
      throw new IllegalArgumentException("notification page does not match request");
    var copy = List.copyOf(records);
    long expected = page.isEmpty() ? 0 : page.getLastResult() - page.getFirstResult() + 1;
    if (copy.size() != expected)
      throw new IllegalArgumentException("inconsistent notification record count");
    var ids = new HashSet<Long>();
    for (int i = 0; i < copy.size(); i++) {
      var current = copy.get(i);
      if (!ids.add(current.notificationId().value()))
        throw new IllegalArgumentException("duplicate notification identity");
      NotificationType type = DISPLAY_TYPES.get(current.internalState());
      if (current.notificationType() != type
          || current.questionSummary().codePointCount(0, current.questionSummary().length()) > 100
          || (current.questionDeleted() && !current.questionSummary().equals("削除済み")))
        throw new IllegalArgumentException("invalid notification display state");
      if (i > 0) {
        var previous = copy.get(i - 1);
        int order = previous.lastUpdatedAt().compareTo(current.lastUpdatedAt());
        if (order < 0
            || (order == 0
                && previous.notificationId().value() <= current.notificationId().value()))
          throw new IllegalArgumentException("invalid notification display order");
      }
    }
    return new NotificationListViewModel(actor, form, Optional.of(page), copy);
  }

  public static NotificationListViewModel invalid(
      SessionPrincipal actor, NotificationSearchForm form) {
    Objects.requireNonNull(form, "form");
    if (form.isValid()) throw new IllegalArgumentException("valid form used as invalid");
    return new NotificationListViewModel(actor, form, Optional.empty(), List.of());
  }

  private static Map<String, Object> row(NotificationRecord value) {
    String type = Objects.requireNonNull(TYPE_LABELS.get(value.notificationType()), "type label");
    return Map.copyOf(
        Map.ofEntries(
            Map.entry("id", value.notificationId().value()),
            Map.entry("receiptId", value.receiptId()),
            Map.entry("type", type),
            Map.entry("state", value.internalState().wireValue()),
            Map.entry("submittedAt", TIME.format(value.submittedAt())),
            Map.entry("lastUpdatedAt", TIME.format(value.lastUpdatedAt())),
            Map.entry("summary", value.questionSummary()),
            Map.entry("deleted", value.questionDeleted()),
            Map.entry("detailHref", "/notifications/" + value.notificationId().value())));
  }

  private String link(int number) {
    var values = filters.getValues();
    return "/notifications?type="
        + encode(Objects.requireNonNull(values.get("type")))
        + "&from="
        + encode(Objects.requireNonNull(values.get("from")))
        + "&to="
        + encode(Objects.requireNonNull(values.get("to")))
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

  public NotificationSearchForm getFilters() {
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
    return "NotificationListViewModel[REDACTED]";
  }
}
