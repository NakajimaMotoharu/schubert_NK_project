package dev.codex.schubert.nk.web.view;

import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadSemanticValidator;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDetailResponseData;
import dev.codex.schubert.nk.web.receipt.ReceiptReference;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/** SCR019 fresh API projection only; UI224/236; SS313/331§9.4; QA048; PG-D357/RCPT006E,F. */
@NullMarked
public final class QuestionAcceptedViewModel {
  private static final DateTimeFormatter TIME =
      DateTimeFormatter.ofPattern("uuuu-MM-dd HH:mm:ss", Locale.ROOT)
          .withZone(ZoneOffset.ofHours(9));
  private final TopBarViewModel topBar;
  private final Map<String, Object> values;

  private QuestionAcceptedViewModel(SessionPrincipal actor, QuestionDetailResponseData data) {
    topBar = TopBarViewModel.from(actor);
    String question = data.questionText();
    int count = Math.min(200, question.codePointCount(0, question.length()));
    values =
        Map.of(
            "receiptId", data.receiptId(),
            "submittedAt", TIME.format(data.submittedAt()),
            "question", question.substring(0, question.offsetByCodePoints(0, count)));
  }

  public static QuestionAcceptedViewModel from(
      SessionPrincipal actor, ReceiptReference reference, QuestionDetailResponseData data) {
    Objects.requireNonNull(actor, "actor");
    Objects.requireNonNull(reference, "reference");
    Objects.requireNonNull(data, "data");
    if (data.questionText().isEmpty())
      throw new IllegalArgumentException("question projection body is absent");
    if (reference.questionId() != data.questionId().value()
        || !reference.receiptId().equals(data.receiptId())
        || !reference
            .submittedAt()
            .truncatedTo(ChronoUnit.MILLIS)
            .equals(data.submittedAt().truncatedTo(ChronoUnit.MILLIS))
        || !actor.username().equals(data.username()))
      throw new IllegalArgumentException("invalid acceptance projection");
    PayloadSemanticValidator.validate(
        new TypedPayloadValues(new LayoutId("QSDRSP01"), data, List.of()));
    return new QuestionAcceptedViewModel(actor, data);
  }

  public TopBarViewModel getTopBar() {
    return topBar;
  }

  public Map<String, Object> getValues() {
    return values;
  }

  @Override
  public String toString() {
    return "QuestionAcceptedViewModel[REDACTED]";
  }
}
