package dev.codex.schubert.nk.protocol.codec;

/** JMS body shape copied without a JMS dependency. Trace: NK-PRO-002, UI 231 §2/§5. */
public enum TransportBodyType {
  BYTES,
  TEXT,
  OBJECT,
  MAP
}
