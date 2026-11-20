package dev.codex.schubert.nk.web.error;

import dev.codex.schubert.nk.protocol.header.ResultCode;
import java.util.Map;
import java.util.Objects;

/**
 * Generic classification only, not an HTTP writer. Controllers own field redisplay, conflict
 * refresh, Login redirects and mandatory API0102 invalidation. NK-WEB-001; FUN-001..013/TST;
 * UI221/232; SS313/351; SSC-048/PG-D-117/PT-WEB-158.
 */
public final class WebResultMapper {
  private static final Map<ResultCode, Integer> HTTP_STATUS =
      Map.ofEntries(
          Map.entry(ResultCode.SUCCESS, 200),
          Map.entry(ResultCode.VALIDATION_ERROR, 400),
          Map.entry(ResultCode.AUTHENTICATION_FAILED, 401),
          Map.entry(ResultCode.SESSION_INVALID, 401),
          Map.entry(ResultCode.FORBIDDEN, 403),
          Map.entry(ResultCode.NOT_FOUND, 404),
          Map.entry(ResultCode.CONFLICT, 409),
          Map.entry(ResultCode.LOCKED, 429),
          Map.entry(ResultCode.NOT_CANCELLABLE, 409),
          Map.entry(ResultCode.IDEMPOTENT_SUCCESS, 200),
          Map.entry(ResultCode.TEMPORARY_FAILURE, 503),
          Map.entry(ResultCode.RESOURCE_LIMIT, 503));

  public int httpStatus(ResultCode code) {
    ResultCode approved = Objects.requireNonNull(code, "code");
    return Objects.requireNonNull(HTTP_STATUS.get(approved), "unmapped result code");
  }
}
