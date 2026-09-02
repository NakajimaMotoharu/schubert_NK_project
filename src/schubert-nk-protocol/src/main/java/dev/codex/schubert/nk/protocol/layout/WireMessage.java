package dev.codex.schubert.nk.protocol.layout;

import dev.codex.schubert.nk.protocol.header.CommonHeader;
import java.util.Objects;

/** Header plus exact layout payload. Trace: NK-PRO-002, SS 322 §2. */
public record WireMessage<P extends LayoutPayload>(CommonHeader header, P payload) {
  public WireMessage {
    Objects.requireNonNull(header, "header");
    Objects.requireNonNull(payload, "payload");
    if (header.dataLength() != payload.dataLength()
        || header.recordLength() != payload.recordLength()
        || header.recordCount() != payload.recordCount()) {
      throw new LayoutValidationException("header lengths differ from payload lengths");
    }
  }
}
