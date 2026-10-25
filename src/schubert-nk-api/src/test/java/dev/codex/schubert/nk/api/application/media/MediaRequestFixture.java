package dev.codex.schubert.nk.api.application.media;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

/** UI235 literal request DATA; used only by Media PT and never to generate response expected. */
public final class MediaRequestFixture {
  private MediaRequestFixture() {}

  public static WireMessage<FixedPayload> message(String layout, byte[] data) {
    UUID id = UUID.randomUUID();
    var header =
        new CommonHeader(
            "SCHBNK01",
            1,
            new LayoutId(layout),
            1,
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            id,
            id,
            Instant.parse("2026-09-08T00:00:00Z"),
            Optional.of(AuthenticationContext.of("b".repeat(64))),
            256,
            data.length,
            0,
            0,
            256 + data.length,
            Optional.empty());
    return new WireMessage<>(header, new FixedPayload(data, 0, List.of()));
  }

  public static byte[] data(String layout) {
    return switch (layout) {
      case "ANMREQ01", "MCTREQ01" -> new byte[0];
      case "AUDREQ01" -> field(16, 0, "000000000700A");
      case "ANLREQ01" -> field(16, 0, "MAIN");
      case "VIDREQ01" -> field(64, 0, "opening");
      case "MCSREQ01" -> field(64, 0, "BGM");
      case "MTRREQ01" -> {
        byte[] result = field(192, 0, "BGM");
        put(result, 64, "ゲーム");
        yield result;
      }
      case "MEDREQ01" -> {
        byte[] result = field(72, 0, "music-0");
        put(result, 64, "A");
        yield result;
      }
      default -> throw new AssertionError("unsupported test layout");
    };
  }

  public static byte[] field(int length, int offset, String value) {
    byte[] bytes = new byte[length];
    Arrays.fill(bytes, (byte) 32);
    put(bytes, offset, value);
    return bytes;
  }

  public static void put(byte[] bytes, int offset, String value) {
    byte[] valueBytes = value.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(valueBytes, 0, bytes, offset, valueBytes.length);
  }
}
