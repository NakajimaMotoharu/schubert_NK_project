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
 * NK-WEB001/FUN009,010/NTF/UI224,236/SS313,323,324; PG-D-342/PT-WEB-S3WIRE001..008.
 */
public final class NotificationWireClient {
  private final ProtectedReadWireClient client;

  public NotificationWireClient(
      JmsRequestReplyClient client,
      JmsRequestSender sender,
      Clock clock,
      Supplier<UUID> identifiers,
      Duration timeout) {
    this.client =
        new ProtectedReadWireClient(
            Set.of("NTSREQ01", "NTDREQ01", "NTCREQ01"),
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
