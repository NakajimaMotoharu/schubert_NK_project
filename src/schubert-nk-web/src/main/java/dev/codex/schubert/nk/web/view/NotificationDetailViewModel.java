package dev.codex.schubert.nk.web.view;

import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadSemanticValidator;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.question.NotificationDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationErrorCode;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationId;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationState;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.time.Instant;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * SCR021 reference/UI224236/SS313314323332; PG-D349/PT-NTF-DETAIL001..008. No raw result/session
 * retention.
 */
@NullMarked
public final class NotificationDetailViewModel {
  private static final DateTimeFormatter RETAINED_TIME =
      DateTimeFormatter.ofPattern("uuuu-MM-dd HH:mm:ss", Locale.ROOT)
          .withZone(ZoneOffset.ofHours(9));
  private static final Map<NotificationState, String> STATE_LABELS =
      Map.of(
          NotificationState.RECEIVED, "受付中",
          NotificationState.PROCESSING, "処理中",
          NotificationState.COMPLETED, "処理完了",
          NotificationState.ERROR, "エラー",
          NotificationState.CANCELLED, "取消済み");
  private final TopBarViewModel topBar;
  private final Map<String, Object> values;

  private NotificationDetailViewModel(SessionPrincipal actor, NotificationDetailResponseData data) {
    topBar = TopBarViewModel.from(actor);
    String label = Objects.requireNonNull(STATE_LABELS.get(data.internalState()), "state label");
    boolean answer = data.internalState() == NotificationState.COMPLETED && !data.questionDeleted();
    values =
        Map.copyOf(
            Map.ofEntries(
                Map.entry("id", data.notificationId().value()),
                Map.entry("receiptId", data.receiptId()),
                Map.entry("state", data.internalState().wireValue()),
                Map.entry("stateLabel", label),
                Map.entry("submittedAt", time(data.submittedAt())),
                Map.entry(
                    "startedAt",
                    data.processingStartedAt().map(NotificationDetailViewModel::time).orElse("")),
                Map.entry(
                    "completedAt",
                    data.processingCompletedAt().map(NotificationDetailViewModel::time).orElse("")),
                Map.entry(
                    "errorAt", data.errorAt().map(NotificationDetailViewModel::time).orElse("")),
                Map.entry(
                    "cancelledAt",
                    data.cancelledAt().map(NotificationDetailViewModel::time).orElse("")),
                Map.entry("deleted", data.questionDeleted()),
                Map.entry("question", data.questionText().orElse("")),
                Map.entry("answerAvailable", answer),
                Map.entry("answer", data.answerText().orElse("")),
                Map.entry(
                    "errorCode", data.errorCode().map(NotificationErrorCode::wireValue).orElse("")),
                Map.entry("userFacingError", data.userFacingError().orElse("")),
                Map.entry(
                    "questionHref",
                    answer ? "/questions/" + data.questionId().orElseThrow().value() : "")));
  }

  public static NotificationDetailViewModel from(
      SessionPrincipal actor, NotificationId requested, NotificationDetailResponseData data) {
    Objects.requireNonNull(actor, "actor");
    Objects.requireNonNull(requested, "requested");
    Objects.requireNonNull(data, "data");
    if (!requested.equals(data.notificationId()))
      throw new IllegalArgumentException("invalid notification detail projection");
    PayloadSemanticValidator.validate(
        new TypedPayloadValues(new LayoutId("NTDRSP01"), data, List.of()));
    return new NotificationDetailViewModel(actor, data);
  }

  private static String time(Instant at) {
    return RETAINED_TIME.format(at);
  }

  public TopBarViewModel getTopBar() {
    return topBar;
  }

  public Map<String, Object> getValues() {
    return values;
  }

  @Override
  public String toString() {
    return "NotificationDetailViewModel[REDACTED]";
  }
}
