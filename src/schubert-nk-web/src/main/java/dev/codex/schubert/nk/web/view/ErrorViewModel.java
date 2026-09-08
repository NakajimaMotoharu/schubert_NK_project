package dev.codex.schubert.nk.web.view;

import java.util.Objects;
import java.util.Optional;
import java.util.UUID;

/**
 * Closed error display, no Throwable/request/session objects. NK-WEB-001; TST-001..005; UI222;
 * SS313/352; SSC-047/PG-D-116/PT-WEB-148..157.
 */
public final class ErrorViewModel {
  public enum Status {
    BAD_REQUEST(400, "入力内容を確認してください。"),
    UNAUTHENTICATED(401, "再度ログインしてください。"),
    FORBIDDEN(403, "この操作を実行する権限がありません。"),
    NOT_FOUND(404, "対象が見つかりません。"),
    METHOD_NOT_ALLOWED(405, "この操作方法は利用できません。"),
    CONFLICT(409, "状態が更新されたため操作できません。再表示してください。"),
    RANGE_INVALID(416, "指定された範囲を取得できません。"),
    RATE_LIMITED(429, "しばらく待ってから再操作してください。"),
    UNAVAILABLE(503, "現在処理できません。しばらくしてから再操作してください。");

    private final int code;
    private final String message;

    Status(int code, String message) {
      this.code = code;
      this.message = message;
    }
  }

  private final Status status;
  private final UUID requestId;
  private final Optional<TopBarViewModel> topBar;

  private ErrorViewModel(Status status, UUID requestId, Optional<TopBarViewModel> topBar) {
    this.status = status;
    this.requestId = requestId;
    this.topBar = topBar;
  }

  public static ErrorViewModel of(Status status, UUID requestId, Optional<TopBarViewModel> topBar) {
    return new ErrorViewModel(
        Objects.requireNonNull(status, "status"),
        Objects.requireNonNull(requestId, "requestId"),
        Objects.requireNonNull(topBar, "topBar"));
  }

  public int getStatus() {
    return status.code;
  }

  public String getMessage() {
    return status.message;
  }

  public String getRequestId() {
    return requestId.toString();
  }

  public Optional<TopBarViewModel> getTopBar() {
    return topBar;
  }

  @Override
  public String toString() {
    return "ErrorViewModel[REDACTED]";
  }
}
