package dev.codex.schubert.nk.protocol.layout.semantic;

/** Async job identifier. Trace: QWKREQ01, SS 323, PT-PRO-001-T04. */
public record AsyncJobId(long value) implements ProtocolId {
  public AsyncJobId {
    IdValue.validate(value);
  }
}
