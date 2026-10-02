package dev.codex.schubert.nk.api.persistence;

import dev.codex.schubert.nk.protocol.header.ResultCode;
import java.util.Objects;

/**
 * Fixed query classification; no SQL/body/provider diagnosis. NK-QRY/NTF-001; SS332; PT-QRY003/005.
 */
public final class QuestionQueryException extends RuntimeException {
  private static final long serialVersionUID = 1L;
  private final ResultCode code;

  QuestionQueryException(ResultCode code) {
    super("question query is unavailable");
    this.code = Objects.requireNonNull(code, "code");
  }

  public ResultCode resultCode() {
    return code;
  }
}
