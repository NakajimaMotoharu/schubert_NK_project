package dev.codex.schubert.nk.batch.platform;

/** NK-OPS-001; OPS-009; UI251; SS341/343; PG-D-148; PT-OPS-STOP-002..016. */
public enum StopGateFailure {
  MALFORMED_STATE,
  NOT_STOPPED,
  COMMAND_FAILURE,
  TIMEOUT,
  INTERRUPTED
}
