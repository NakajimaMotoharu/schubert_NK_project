package dev.codex.schubert.nk.web.view;

import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.util.Objects;

/**
 * Display strings only; no retained authentication object. NK-WEB-001; FUN-002/AUT-001..003;
 * UI222/223/226; SS313; PG-D-115/PT-WEB-142..147.
 */
public final class TopBarViewModel {
  private final String username;
  private final String role;

  private TopBarViewModel(SessionPrincipal principal) {
    username = principal.username();
    role = principal.role().wireValue();
  }

  public static TopBarViewModel from(SessionPrincipal principal) {
    return new TopBarViewModel(Objects.requireNonNull(principal, "principal"));
  }

  public String getBrand() {
    return "schubert NK";
  }

  public String getUsername() {
    return username;
  }

  public String getRole() {
    return role;
  }

  @Override
  public String toString() {
    return "TopBarViewModel[REDACTED]";
  }
}
