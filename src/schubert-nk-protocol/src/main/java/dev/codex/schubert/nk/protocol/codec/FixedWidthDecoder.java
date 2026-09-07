package dev.codex.schubert.nk.protocol.codec;

import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutDefinition;
import dev.codex.schubert.nk.protocol.layout.LayoutRegistry;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import org.jspecify.annotations.Nullable;

/** Byte-slice fixed-width decoder. Trace: NK-PRO-002, SS 322 §5. */
public final class FixedWidthDecoder {
  private final LayoutRegistry registry;
  private final HeaderCodec headerCodec;

  public FixedWidthDecoder(LayoutRegistry registry) {
    this.registry = Objects.requireNonNull(registry, "registry");
    headerCodec = new HeaderCodec(registry);
  }

  public static FixedWidthDecoder standard() {
    return new FixedWidthDecoder(LayoutRegistry.standard());
  }

  public WireMessage<FixedPayload> decode(
      byte @Nullable [] body, TransportMetadata metadata, ExpectedRoute route) {
    Objects.requireNonNull(metadata, "metadata");
    Objects.requireNonNull(route, "route");
    if (body == null) {
      throw new PermanentProtocolException("message body is null");
    }
    if (body.length < LayoutDefinition.HEADER_LENGTH) {
      throw new PermanentProtocolException("message body is shorter than the common header");
    }
    int routeMaximum =
        BrokerTopology.requireAddress(route.destinationAddress()).maximumBodyLength();
    if (body.length > routeMaximum) {
      throw new PermanentProtocolException("message body exceeds the route maximum length");
    }
    CommonHeader header = headerCodec.peek(body);
    ProtocolValidator.validateTransport(header, metadata, route);
    if (body.length != header.totalLength()) {
      throw new PermanentProtocolException("actual body length differs from the wire header");
    }
    LayoutDefinition definition = registry.require(header.layoutId(), header.layoutVersion());
    int offset = LayoutDefinition.HEADER_LENGTH;
    byte[] data = Arrays.copyOfRange(body, offset, offset + definition.dataLength());
    offset += definition.dataLength();
    List<byte[]> records = new ArrayList<>(header.recordCount());
    for (int index = 0; index < header.recordCount(); index++) {
      records.add(Arrays.copyOfRange(body, offset, offset + definition.recordLength()));
      offset += definition.recordLength();
    }
    return new WireMessage<>(header, new FixedPayload(data, definition.recordLength(), records));
  }
}
