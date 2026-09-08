package dev.codex.schubert.nk.api.error;

import dev.codex.schubert.nk.protocol.header.ResultCode;

/** Admission limit, not a retry that deletes accepted work. SS311 §8/351; PT-SCN-008-C01/C03. */
public final class CapacityExceededException extends RuntimeException {
  private static final long serialVersionUID = 1L;

  public CapacityExceededException() {
    super("resource capacity limit exceeded");
  }

  public ResultCode resultCode() {
    return ResultCode.RESOURCE_LIMIT;
  }
}
