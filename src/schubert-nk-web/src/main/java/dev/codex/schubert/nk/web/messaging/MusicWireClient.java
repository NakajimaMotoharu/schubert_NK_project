package dev.codex.schubert.nk.web.messaging;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import java.time.Clock;
import java.time.Duration;
import java.util.Set;
import java.util.UUID;
import java.util.function.Supplier;

/**
 * MCT/MCS/MTR only;
 * NK-WEB001/NK-MED001/FUN007/AUT/MQ/UI232,235/SS311,312,321,323/PG210/PT-WEB254..261.
 */
public final class MusicWireClient {
  private final ProtectedReadWireClient client;

  public MusicWireClient(
      JmsRequestReplyClient client,
      JmsRequestSender sender,
      Clock clock,
      Supplier<UUID> identifiers,
      Duration timeout) {
    this.client =
        new ProtectedReadWireClient(
            Set.of("MCTREQ01", "MCSREQ01", "MTRREQ01"),
            client,
            sender,
            clock,
            identifiers,
            timeout);
  }

  public ProtectedReadWireClient.Result exchange(
      TypedPayloadValues input, AuthenticationContext context) {
    return client.exchange(input, context);
  }
}
