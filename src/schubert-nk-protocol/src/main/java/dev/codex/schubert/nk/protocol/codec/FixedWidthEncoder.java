package dev.codex.schubert.nk.protocol.codec;

import dev.codex.schubert.nk.protocol.layout.LayoutDefinition;
import dev.codex.schubert.nk.protocol.layout.LayoutPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutRegistry;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import java.util.List;
import java.util.Objects;

/** Exact-size fixed-width encoder. Trace: NK-PRO-002, SS 322 §4. */
public final class FixedWidthEncoder {
  private final LayoutRegistry registry;
  private final HeaderCodec headerCodec;

  public FixedWidthEncoder(LayoutRegistry registry) {
    this.registry = Objects.requireNonNull(registry, "registry");
    headerCodec = new HeaderCodec(registry);
  }

  public static FixedWidthEncoder standard() {
    return new FixedWidthEncoder(LayoutRegistry.standard());
  }

  public byte[] encode(WireMessage<? extends LayoutPayload> message) {
    Objects.requireNonNull(message, "message");
    try {
      LayoutDefinition definition =
          registry.require(message.header().layoutId(), message.header().layoutVersion());
      message.header().validateAgainst(definition);
      LayoutPayload payload = message.payload();
      byte[] header = headerCodec.encode(message.header());
      byte[] data = payload.copyData();
      List<byte[]> records = payload.copyRecords();
      int expectedLength = definition.totalLengthFor(records.size());
      byte[] body = new byte[expectedLength];
      int offset = 0;
      offset = copy(body, offset, header);
      offset = copy(body, offset, data);
      for (byte[] record : records) {
        offset = copy(body, offset, record);
      }
      return body;
    } catch (IllegalArgumentException exception) {
      throw new MessageEncodingException("message could not be encoded", exception);
    }
  }

  private static int copy(byte[] target, int offset, byte[] value) {
    System.arraycopy(value, 0, target, offset, value.length);
    return offset + value.length;
  }
}
