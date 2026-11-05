package dev.codex.schubert.nk.web.logging;

import dev.codex.schubert.nk.protocol.layout.semantic.LogType;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/** Closed QA054/UI235/SS312351 projection kinds; no actor authorization or backend operation. */
@NullMarked
public enum WebHttpLogKind {
  REQUEST(LogType.REQUEST, "HTTP_REQUEST_COMPLETED", "HTTP request completed"),
  MENU_VIEWED(LogType.ACTION, "MENU_VIEWED", "Menu viewed");

  private final LogType retainedCategory;
  private final String retainedAction;
  private final String retainedMessage;

  WebHttpLogKind(LogType category, String action, String message) {
    this.retainedCategory = category;
    this.retainedAction = action;
    this.retainedMessage = message;
  }

  public LogType category() {
    return retainedCategory;
  }

  public String action() {
    return retainedAction;
  }

  public String message() {
    return retainedMessage;
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
