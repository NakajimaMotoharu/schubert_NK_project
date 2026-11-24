package dev.codex.schubert.nk.web.view;

import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadSemanticValidator;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.AnswerState;
import dev.codex.schubert.nk.protocol.layout.semantic.QuestionId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/** SCR023/UI224236/SS313314323332; PG-D350368/PT-QRY-HTTP006,011/QDL-BIZ001,009. */
@NullMarked
public final class QuestionDetailViewModel {
  private static final DateTimeFormatter TIME =
      DateTimeFormatter.ofPattern("uuuu-MM-dd HH:mm:ss", Locale.ROOT)
          .withZone(ZoneOffset.ofHours(9));
  private static final Map<AnswerState, String> STATE_LABELS =
      Map.of(
          AnswerState.ANSWERED, "回答済み",
          AnswerState.UNANSWERED, "未回答",
          AnswerState.ERROR, "エラー");
  private final TopBarViewModel topBar;
  private final Map<String, Object> values;

  private QuestionDetailViewModel(SessionPrincipal actor, QuestionDetailResponseData data) {
    topBar = TopBarViewModel.from(actor);
    values =
        Map.copyOf(
            Map.ofEntries(
                Map.entry("id", data.questionId().value()),
                Map.entry("receiptId", data.receiptId()),
                Map.entry("admin", actor.role() == UserRole.ADMIN),
                Map.entry("username", data.username()),
                Map.entry("state", data.answerState().wireValue()),
                Map.entry("stateLabel", label(data.answerState())),
                Map.entry("submittedAt", TIME.format(data.submittedAt())),
                Map.entry("answeredAt", data.answeredAt().map(TIME::format).orElse("")),
                Map.entry("question", data.questionText()),
                Map.entry(
                    "summary",
                    data.questionText()
                        .substring(
                            0,
                            data.questionText()
                                .offsetByCodePoints(
                                    0,
                                    Math.min(
                                        100,
                                        data.questionText()
                                            .codePointCount(0, data.questionText().length()))))),
                Map.entry("answer", data.answerText().orElse("")),
                Map.entry("answerAvailable", data.answerState() == AnswerState.ANSWERED)));
  }

  public static QuestionDetailViewModel from(
      SessionPrincipal actor, QuestionId target, QuestionDetailResponseData data) {
    Objects.requireNonNull(actor, "actor");
    Objects.requireNonNull(target, "target");
    Objects.requireNonNull(data, "data");
    // UI236 QSDRSP01 active-question M field; semantic relationships alone do not check X presence.
    if (data.questionText().isEmpty())
      throw new IllegalArgumentException("question projection body is absent");
    if (!target.equals(data.questionId())
        || (actor.role() == UserRole.USER && !actor.username().equals(data.username())))
      throw new IllegalArgumentException("invalid question detail projection");
    PayloadSemanticValidator.validate(
        new TypedPayloadValues(new LayoutId("QSDRSP01"), data, List.of()));
    return new QuestionDetailViewModel(actor, data);
  }

  static String label(AnswerState state) {
    return Objects.requireNonNull(STATE_LABELS.get(state), "unsupported answer state");
  }

  public TopBarViewModel getTopBar() {
    return topBar;
  }

  public Map<String, Object> getValues() {
    return values;
  }

  @Override
  public String toString() {
    return "QuestionDetailViewModel[REDACTED]";
  }
}
