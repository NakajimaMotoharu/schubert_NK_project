package dev.codex.schubert.nk.web.messaging;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import java.time.Clock;
import java.time.Duration;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.function.Supplier;

/**
 * Existing six-request facade; public result/error contract preserved by PG206.
 * NK-WEB001/NK-SCN001/FUN003..005/MQ/AUT/UI232,234/SS311,312,321,323,352;
 * PG191,206/PT-WEB166..173,238..245. Original dev-web untracked files are not modified.
 */
public final class ScenarioWireClient {
  private final ProtectedReadWireClient client;

  public ScenarioWireClient(
      JmsRequestReplyClient client,
      JmsRequestSender sender,
      Clock clock,
      Supplier<UUID> identifiers,
      Duration timeout) {
    this.client =
        new ProtectedReadWireClient(
            Set.of("GAMREQ01", "SPKREQ01", "SRCREQ01", "RTEREQ01", "SCFREQ01", "SCNREQ01"),
            client,
            sender,
            clock,
            identifiers,
            timeout);
  }

  public Result exchange(TypedPayloadValues input, AuthenticationContext context) {
    try {
      return new Result(client.exchange(input, context));
    } catch (ProtectedReadWireException failure) {
      throw new ScenarioWireException(
          ScenarioWireException.Reason.valueOf(failure.reason().name()));
    }
  }

  public static final class Result {
    private final ProtectedReadWireClient.Result retainedResult;

    private Result(ProtectedReadWireClient.Result result) {
      this.retainedResult = result;
    }

    public ResultCode resultCode() {
      return retainedResult.resultCode();
    }

    public Optional<TypedPayloadValues> payload() {
      return retainedResult.payload();
    }

    @Override
    public String toString() {
      return "ScenarioResponse[REDACTED]";
    }
  }
}
