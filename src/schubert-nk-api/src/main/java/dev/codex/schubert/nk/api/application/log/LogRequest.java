package dev.codex.schubert.nk.api.application.log;

import static dev.codex.schubert.nk.api.idempotency.CanonicalField.number;

import dev.codex.schubert.nk.api.idempotency.CanonicalField;
import dev.codex.schubert.nk.api.idempotency.CanonicalRequest;
import dev.codex.schubert.nk.api.persistence.LogQueryRepository;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.LayoutRegistry;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.log.LogSearchRequestData;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.time.Instant;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import java.util.Optional;

/**
 * One strict decode for original HMAC fields and read-only Log search, not authorization.
 * NK-ADM-001/NK-MSG-002; FUN-008/MQ-006..010; UI235; SS323 §9.5/324/332;
 * SSC-037/PG-D-091/PT-ADM-061..063. Public arguments are nonnull; caller closes canonical buffers.
 */
public final class LogRequest {
  private final CommonHeader header;
  private final LogSearchRequestData data;

  private LogRequest(CommonHeader header, LogSearchRequestData data) {
    this.header = header;
    this.data = data;
  }

  public static LogRequest decode(WireMessage<FixedPayload> request) {
    Objects.requireNonNull(request, "request");
    byte[] data = request.payload().copyData();
    try {
      var header = request.header();
      require(header.layoutId().value().equals("LGSREQ01"));
      header.validateAgainst(LayoutRegistry.standard().require(header.layoutId(), 1));
      var values =
          PayloadTypeCatalog.decode(
              PayloadCodec.standard().decode(header.layoutId(), data, List.of(), false));
      return new LogRequest(header, (LogSearchRequestData) values.data());
    } catch (PermanentProtocolException | IllegalArgumentException failure) {
      throw new PermanentProtocolException("log request is invalid");
    } finally {
      Arrays.fill(data, (byte) 0);
    }
  }

  public CommonHeader header() {
    return header;
  }

  public LayoutId responseLayoutId() {
    return new LayoutId("LGSRSP01");
  }

  public CanonicalRequest canonical(AuthenticatedActor actor) {
    Objects.requireNonNull(actor, "actor");
    return new CanonicalRequest(
        Long.toString(actor.userId()),
        "LGSREQ01",
        "001",
        "REQUEST:LGSREQ01",
        List.of(
            optional("keyword", "X1", data.keyword()),
            optional("logType", "X1", data.logType().map(v -> v.wireValue())),
            optional("action", "X1", data.action()),
            optional("path", "X1", data.path()),
            optional("level", "X1", data.level().map(v -> v.wireValue())),
            optional("fromAt", "T1", data.fromAt().map(Instant::toString)),
            optional("toAt", "T1", data.toAt().map(Instant::toString)),
            number("page", data.page()),
            number("pageSize", data.pageSize())));
  }

  public TypedPayloadValues query(
      LogQueryRepository repository, Connection connection, AuthenticatedActor actor) {
    Objects.requireNonNull(repository, "repository");
    Objects.requireNonNull(connection, "connection");
    Objects.requireNonNull(actor, "actor");
    return repository.search(connection, actor, data);
  }

  /** Codec validates all independent counts/bytes; bind effective page to this original request. */
  public void validateResponse(TypedPayloadValues response) {
    Objects.requireNonNull(response, "response");
    require(response.layoutId().equals(responseLayoutId()));
    require(response.data() instanceof PagedResponseData);
    var page = (PagedResponseData) response.data();
    require(page.effectivePage() == Math.min(data.page(), page.totalPages()));
    PayloadCodec.standard().encode(PayloadTypeCatalog.encode(response), ResultCode.SUCCESS);
  }

  private static CanonicalField optional(String name, String type, Optional<String> value) {
    return new CanonicalField(
        name, type, value.isPresent() ? value.get().getBytes(StandardCharsets.UTF_8) : null);
  }

  private static void require(boolean valid) {
    if (!valid) throw new IllegalArgumentException("log query identity is inconsistent");
  }

  @Override
  public String toString() {
    return "LogRequest[REDACTED]";
  }
}
