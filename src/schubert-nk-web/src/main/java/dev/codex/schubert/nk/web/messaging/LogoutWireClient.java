package dev.codex.schubert.nk.web.messaging;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import java.time.Clock;
import java.time.Duration;
import java.util.Set;
import java.util.UUID;
import java.util.function.Supplier;

/**
 * Fixed trusted facade, not an HTTP-selected capability or authorization grant.
 * NK-WEB001/AUT004/UI226,234/SS314,323,324; PG-D-342/PT-WEB-S3WIRE001..008.
 */
public final class LogoutWireClient {
  private final ProtectedReadWireClient client;

  public LogoutWireClient(
      JmsRequestReplyClient client,
      JmsRequestSender sender,
      Clock clock,
      Supplier<UUID> identifiers,
      Duration timeout) {
    this.client =
        new ProtectedReadWireClient(
            Set.of("LOGREQ01"), client, sender, clock, identifiers, timeout);
  }

  public ProtectedReadWireClient.Result exchange(
      TypedPayloadValues input, AuthenticationContext context) {
    return client.exchange(input, context);
  }
}
