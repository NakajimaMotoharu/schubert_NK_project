package dev.codex.schubert.nk.web.messaging;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import java.time.Clock;
import java.time.Duration;
import java.util.Set;
import java.util.UUID;
import java.util.function.Supplier;

/**
 * ANM/ANL only; no descriptor/update capability.
 * NK-WEB001/NK-MED001/FUN006/MQ/AUT/UI232,235/SS311,312,321,323/PG206/PT-WEB238..245.
 */
public final class AnimationWireClient {
  private final ProtectedReadWireClient client;

  public AnimationWireClient(
      JmsRequestReplyClient client,
      JmsRequestSender sender,
      Clock clock,
      Supplier<UUID> identifiers,
      Duration timeout) {
    this.client =
        new ProtectedReadWireClient(
            Set.of("ANMREQ01", "ANLREQ01"), client, sender, clock, identifiers, timeout);
  }

  public ProtectedReadWireClient.Result exchange(
      TypedPayloadValues input, AuthenticationContext context) {
    return client.exchange(input, context);
  }
}
