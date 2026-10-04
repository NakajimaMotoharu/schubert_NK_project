package dev.codex.schubert.nk.web.view;

import dev.codex.schubert.nk.web.form.UserCreateForm;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/** Closed SCR016 display; no password, context or arbitrary DTO. UI225236/SSC177/PG-D366/081. */
@NullMarked
public final class UserCreateViewModel {
  private final Map<String, Object> values;

  private UserCreateViewModel(
      SessionPrincipal actor,
      Map<String, Object> fields,
      Map<String, String> issues,
      UUID token,
      String message) {
    values =
        Map.of(
            "topBar",
            TopBarViewModel.from(Objects.requireNonNull(actor, "actor")),
            "fields",
            Map.copyOf(fields),
            "issues",
            Map.copyOf(issues),
            "token",
            Objects.requireNonNull(token, "token").toString(),
            "message",
            Objects.requireNonNull(message, "message"));
  }

  public static UserCreateViewModel newForm(SessionPrincipal actor, UUID token) {
    return new UserCreateViewModel(
        actor, Map.of("username", "", "role", "USER", "enabled", true), Map.of(), token, "");
  }

  public static UserCreateViewModel redisplay(
      SessionPrincipal actor, UserCreateForm form, UUID token, String message, boolean conflict) {
    Objects.requireNonNull(form, "form");
    var issues = new HashMap<>(form.getIssues());
    if (conflict) issues.put("username", "Username又は操作の整合性を確認してください。");
    return new UserCreateViewModel(actor, form.displayValues(), issues, token, message);
  }

  public Map<String, Object> getValues() {
    return values;
  }

  @Override
  public String toString() {
    return "UserCreateViewModel[REDACTED]";
  }
}
