package dev.codex.schubert.nk.web.view;

import dev.codex.schubert.nk.web.form.QuestionSubmitForm;
import dev.codex.schubert.nk.web.session.SessionOperationToken;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.util.Map;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/** SCR018 request-only display; UI224/236; SS313/314; QA049; PG-D357/RCPT006A..D,F. */
@NullMarked
public final class QuestionSubmitViewModel {
  private final TopBarViewModel topBar;
  private final Map<String, Object> values;
  private final Map<String, String> issues;
  private final String notice;

  private QuestionSubmitViewModel(
      SessionPrincipal actor,
      String question,
      String token,
      Map<String, String> issues,
      String notice) {
    topBar = TopBarViewModel.from(actor);
    values = Map.of("question", question, "operationToken", token);
    this.issues = Map.copyOf(issues);
    this.notice = Objects.requireNonNull(notice, "notice");
  }

  public static QuestionSubmitViewModel newForm(
      SessionPrincipal actor, SessionOperationToken token) {
    Objects.requireNonNull(token, "token");
    if (!token.purpose().equals("QSBREQ01"))
      throw new IllegalArgumentException("question form purpose is invalid");
    return new QuestionSubmitViewModel(actor, "", token.token().toString(), Map.of(), "");
  }

  public static QuestionSubmitViewModel redisplay(
      SessionPrincipal actor, QuestionSubmitForm form, String notice) {
    Objects.requireNonNull(form, "form");
    return new QuestionSubmitViewModel(
        actor,
        (String) Objects.requireNonNull(form.displayValues().get("question"), "question"),
        form.operationToken().toString(),
        form.getIssues(),
        notice);
  }

  public TopBarViewModel getTopBar() {
    return topBar;
  }

  public Map<String, Object> getValues() {
    return values;
  }

  public Map<String, String> getIssues() {
    return issues;
  }

  public String getNotice() {
    return notice;
  }

  @Override
  public String toString() {
    return "QuestionSubmitViewModel[REDACTED]";
  }
}
