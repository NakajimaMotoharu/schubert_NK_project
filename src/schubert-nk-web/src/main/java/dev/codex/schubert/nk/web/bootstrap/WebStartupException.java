package dev.codex.schubert.nk.web.bootstrap;

/** Redacted fail-closed startup result; provider messages and credential material never escape. */
public final class WebStartupException extends IllegalStateException {
  private static final long serialVersionUID = 1L;

  public WebStartupException(String component) {
    super(component + " is unavailable");
  }
}
