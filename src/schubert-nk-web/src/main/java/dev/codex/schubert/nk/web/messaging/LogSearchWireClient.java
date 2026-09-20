package dev.codex.schubert.nk.web.messaging;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import java.time.Clock;
import java.time.Duration;
import java.util.Set;
import java.util.UUID;
import java.util.function.Supplier;

/** LGS only; NK-WEB001/NK-ADM001/FUN008/AUT/MQ/UI232,235/SS311,312,321,323/PG213/PT-WEB270..277. */
public final class LogSearchWireClient {
  private final ProtectedReadWireClient client;

  public LogSearchWireClient(
      JmsRequestReplyClient client,
      JmsRequestSender sender,
      Clock clock,
      Supplier<UUID> identifiers,
      Duration timeout) {
    this.client =
        new ProtectedReadWireClient(
            Set.of("LGSREQ01"), client, sender, clock, identifiers, timeout);
  }

  public ProtectedReadWireClient.Result exchange(
      TypedPayloadValues input, AuthenticationContext context) {
    return client.exchange(input, context);
  }
}
