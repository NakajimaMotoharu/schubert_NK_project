package dev.codex.schubert.nk.api.dispatch;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.messaging.inbound.SyncRequestProcessor;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import java.io.IOException;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

/**
 * Fixed SS323 31-request registration, before any consumer exposure. Not process readiness.
 * NK-MSG-001/AUT-001; MQ003/006/AUT002; UI231232; SS311312323342; SSC149; PT-JMS-DISPATCH-026-A..F.
 * Internal events and response layouts cannot register here.
 */
public final class ApiSyncRequestDispatcher implements SyncRequestProcessor {
  private static final Set<String> REQUIRED =
      Set.of(
          "LGNREQ01",
          "LOGREQ01",
          "GAMREQ01",
          "SPKREQ01",
          "SRCREQ01",
          "RTEREQ01",
          "SCFREQ01",
          "SCNREQ01",
          "AUDREQ01",
          "ANMREQ01",
          "ANLREQ01",
          "VIDREQ01",
          "MCTREQ01",
          "MCSREQ01",
          "MTRREQ01",
          "MEDREQ01",
          "LGSREQ01",
          "USRREQ01",
          "UDTREQ01",
          "UCRREQ01",
          "USTREQ01",
          "URLREQ01",
          "UPWREQ01",
          "ULKREQ01",
          "QSBREQ01",
          "NTSREQ01",
          "NTDREQ01",
          "NTCREQ01",
          "QSSREQ01",
          "QSDREQ01",
          "QDLREQ01");
  private final Map<String, SyncRequestProcessor> processors;

  public ApiSyncRequestDispatcher(Map<String, SyncRequestProcessor> processors) throws IOException {
    var copy = Map.copyOf(Objects.requireNonNull(processors, "request processors"));
    if (!copy.keySet().equals(REQUIRED))
      throw new IOException("mandatory API registration unavailable");
    this.processors = copy;
  }

  @Override
  public byte[] process(WireMessage<FixedPayload> request) {
    Objects.requireNonNull(request, "request");
    var processor = processors.get(request.header().layoutId().value());
    if (processor == null) throw new TemporaryInfrastructureException();
    return Objects.requireNonNull(processor.process(request), "encoded response");
  }
}
