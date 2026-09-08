package dev.codex.schubert.nk.web.error;

import dev.codex.schubert.nk.web.view.ErrorViewModel;
import dev.codex.schubert.nk.web.view.ErrorViewModel.Status;
import dev.codex.schubert.nk.web.view.TopBarViewModel;
import java.util.Optional;
import java.util.UUID;
import org.jspecify.annotations.Nullable;

/**
 * Servlet missing status is explicit; foreign diagnostics are never stringified. NK-WEB-001;
 * TST-001..005; UI222; SS313/351/352; SSC-047/PG-D-116/PT-WEB-148..157.
 */
public final class ProblemViewFactory {
  public ErrorViewModel create(
      @Nullable Object rawStatus, UUID requestId, Optional<TopBarViewModel> topBar) {
    Status status;
    if (rawStatus == null) status = Status.NOT_FOUND;
    else if (rawStatus instanceof Integer code)
      status =
          switch (code) {
            case 400 -> Status.BAD_REQUEST;
            case 401 -> Status.UNAUTHENTICATED;
            case 403 -> Status.FORBIDDEN;
            case 404 -> Status.NOT_FOUND;
            case 405 -> Status.METHOD_NOT_ALLOWED;
            case 409 -> Status.CONFLICT;
            case 416 -> Status.RANGE_INVALID;
            case 429 -> Status.RATE_LIMITED;
            case 503 -> Status.UNAVAILABLE;
            default -> Status.UNAVAILABLE;
          };
    else status = Status.UNAVAILABLE;
    return ErrorViewModel.of(status, requestId, topBar);
  }
}
