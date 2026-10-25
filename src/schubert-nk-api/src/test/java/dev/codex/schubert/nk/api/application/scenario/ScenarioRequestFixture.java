package dev.codex.schubert.nk.api.application.scenario;

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

/** Hand-built UI234 request DATA, no production encoder/oracle. Shared only by PT-SCN-009 tests. */
public final class ScenarioRequestFixture {
  private ScenarioRequestFixture() {}

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

  public static byte[] spaces(int length) {
    byte[] data = new byte[length];
    Arrays.fill(data, (byte) 32);
    return data;
  }

  public static void put(byte[] data, int offset, String value) {
    byte[] bytes = value.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(bytes, 0, data, offset, bytes.length);
  }

  public static byte[] search() {
    byte[] data = spaces(672);
    put(data, 663, "000001100");
    return data;
  }
}
