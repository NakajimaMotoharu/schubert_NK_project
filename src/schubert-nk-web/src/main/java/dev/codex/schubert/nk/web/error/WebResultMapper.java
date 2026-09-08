package dev.codex.schubert.nk.web.error;

import dev.codex.schubert.nk.protocol.header.ResultCode;
import java.util.Objects;

/**
 * Generic classification only, not an HTTP writer. Controllers own field redisplay, conflict
 * refresh, Login redirects and mandatory API0102 invalidation. NK-WEB-001; FUN-001..013/TST;
 * UI221/232; SS313/351; SSC-048/PG-D-117/PT-WEB-158.
 */
public final class WebResultMapper {
  public int httpStatus(ResultCode code) {
    Objects.requireNonNull(code, "code");
    return switch (code) {
      case SUCCESS, IDEMPOTENT_SUCCESS -> 200;
      case VALIDATION_ERROR -> 400;
      case AUTHENTICATION_FAILED, SESSION_INVALID -> 401;
      case FORBIDDEN -> 403;
      case NOT_FOUND -> 404;
      case CONFLICT, NOT_CANCELLABLE -> 409;
      case LOCKED -> 429;
      case TEMPORARY_FAILURE, RESOURCE_LIMIT -> 503;
    };
  }
}
