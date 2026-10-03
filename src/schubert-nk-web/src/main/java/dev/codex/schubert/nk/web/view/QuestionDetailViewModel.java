package dev.codex.schubert.nk.web.view;

import dev.codex.schubert.nk.protocol.layout.*;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.*;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.time.*;
import java.time.format.DateTimeFormatter;
import java.util.*;
import org.jspecify.annotations.NullMarked;

/** SCR023 reference/UI224236/SS313314323332; PG-D350/PT-QRY-HTTP006,011. */
@NullMarked
public final class QuestionDetailViewModel {
  private static final DateTimeFormatter TIME =
      DateTimeFormatter.ofPattern("uuuu-MM-dd HH:mm:ss", Locale.ROOT)
          .withZone(ZoneOffset.ofHours(9));
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
                Map.entry("answer", data.answerText().orElse("")),
                Map.entry("answerAvailable", data.answerState() == AnswerState.ANSWERED)));
  }

  public static QuestionDetailViewModel from(
      SessionPrincipal actor, QuestionId target, QuestionDetailResponseData data) {
    Objects.requireNonNull(actor, "actor");
    Objects.requireNonNull(target, "target");
    Objects.requireNonNull(data, "data");
    if (!target.equals(data.questionId())
        || (actor.role() == UserRole.USER && !actor.username().equals(data.username())))
      throw new IllegalArgumentException("invalid question detail projection");
    PayloadSemanticValidator.validate(
        new TypedPayloadValues(new LayoutId("QSDRSP01"), data, List.of()));
    return new QuestionDetailViewModel(actor, data);
  }

  static String label(AnswerState state) {
    return switch (state) {
      case ANSWERED -> "回答済み";
      case UNANSWERED -> "未回答";
      case ERROR -> "エラー";
    };
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
