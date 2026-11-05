package dev.codex.schubert.nk.web.logging;

import dev.codex.schubert.nk.protocol.layout.semantic.LogType;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/** Closed QA054/UI235/SS312351 projection kinds; no actor authorization or backend operation. */
@NullMarked
public enum WebHttpLogKind {
  REQUEST(LogType.REQUEST, "HTTP_REQUEST_COMPLETED", "HTTP request completed"),
  MENU_VIEWED(LogType.ACTION, "MENU_VIEWED", "Menu viewed");

  private final LogType category;
  private final String action;
  private final String message;

  WebHttpLogKind(LogType category, String action, String message) {
    this.category = category;
    this.action = action;
    this.message = message;
  }

  public LogType category() {
    return category;
  }

  public String action() {
    return action;
  }

  public String message() {
    return message;
  }

  /** Only an actual successful menu model and terminal metadata establish this observation. */
  public boolean eligible(boolean marked, String method, int status, String route, boolean actor) {
    Objects.requireNonNull(method, "method");
    Objects.requireNonNull(route, "route");
    return this == MENU_VIEWED
        && marked
        && method.equals("GET")
        && status == 200
        && route.equals("/")
        && actor;
  }
}
