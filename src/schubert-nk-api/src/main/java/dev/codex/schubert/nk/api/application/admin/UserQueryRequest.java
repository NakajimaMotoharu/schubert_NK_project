package dev.codex.schubert.nk.api.application.admin;

import static dev.codex.schubert.nk.api.idempotency.CanonicalField.number;
import static dev.codex.schubert.nk.api.idempotency.CanonicalField.text;

import dev.codex.schubert.nk.api.idempotency.CanonicalField;
import dev.codex.schubert.nk.api.idempotency.CanonicalRequest;
import dev.codex.schubert.nk.api.persistence.UserQueryRepository;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.*;
import dev.codex.schubert.nk.protocol.layout.admin.*;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import java.sql.Connection;
import java.time.Instant;
import java.util.*;

/**
 * Strict User query values shared by HMAC and read-only query, not an authorization grant.
 * NK-ADM-001/NK-MSG-002; FUN-009/MQ-006..010; UI236/241; SS323 §9.4/324/332;
 * SSC-035/PG-D-088/PT-ADM-040..043. Caller closes each independent canonical buffer.
 */
public final class UserQueryRequest {
  private final CommonHeader header;
  private final TypedPayloadValues values;

  private UserQueryRequest(CommonHeader header, TypedPayloadValues values) {
    this.header = header;
    this.values = values;
  }

  public static UserQueryRequest decode(WireMessage<FixedPayload> request) {
    Objects.requireNonNull(request, "request");
    byte[] data = request.payload().copyData();
    try {
      var header = request.header();
      require(
          header.layoutId().value().equals("USRREQ01")
              || header.layoutId().value().equals("UDTREQ01"));
      header.validateAgainst(LayoutRegistry.standard().require(header.layoutId(), 1));
      var values =
          PayloadTypeCatalog.decode(
              PayloadCodec.standard().decode(header.layoutId(), data, List.of(), false));
      return new UserQueryRequest(header, values);
    } catch (PermanentProtocolException | IllegalArgumentException failure) {
      throw new PermanentProtocolException("user query request is invalid");
    } finally {
      Arrays.fill(data, (byte) 0);
    }
  }

  public CommonHeader header() {
    return header;
  }

  public boolean detailRequest() {
    return header.layoutId().value().equals("UDTREQ01");
  }

  public LayoutId responseLayoutId() {
    return new LayoutId(detailRequest() ? "UDTRSP01" : "USRRSP01");
  }

  public CanonicalRequest canonical(AuthenticatedActor actor) {
    Objects.requireNonNull(actor, "actor");
    List<CanonicalField> fields;
    if (detailRequest())
      fields = List.of(number("userId", ((UserDetailRequestData) values.data()).userId().value()));
    else {
      var data = (UserSearchRequestData) values.data();
      fields =
          List.of(
              optionalText("usernamePrefix", data.usernamePrefix()),
              optionalText("role", data.role().map(v -> v.wireValue())),
              optionalText("state", data.state().map(v -> v.wireValue())),
              number("page", data.page()),
              number("pageSize", data.pageSize()));
    }
    return new CanonicalRequest(
        Long.toString(actor.userId()),
        header.layoutId().value(),
        "001",
        "REQUEST:" + header.layoutId().value(),
        fields);
  }

  public Optional<TypedPayloadValues> query(
      UserQueryRepository repository,
      Connection connection,
      AuthenticatedActor actor,
      Instant now) {
    Objects.requireNonNull(repository, "repository");
    Objects.requireNonNull(connection, "connection");
    Objects.requireNonNull(actor, "actor");
    Objects.requireNonNull(now, "now");
    return detailRequest()
        ? repository.detail(connection, actor, (UserDetailRequestData) values.data(), now)
        : Optional.of(
            repository.search(connection, actor, (UserSearchRequestData) values.data(), now));
  }

  /** Codec owns all wire/page/count invariants; add only request-dependent target/page binding. */
  public void validateResponse(TypedPayloadValues response) {
    Objects.requireNonNull(response, "response");
    require(response.layoutId().equals(responseLayoutId()));
    if (detailRequest()) {
      require(response.data() instanceof UserDetailResponseData);
      require(
          ((UserDetailResponseData) response.data())
              .userId()
              .equals(((UserDetailRequestData) values.data()).userId()));
    } else {
      require(response.data() instanceof PagedResponseData);
      var page = (PagedResponseData) response.data();
      require(
          page.effectivePage()
              == Math.min(((UserSearchRequestData) values.data()).page(), page.totalPages()));
    }
    PayloadCodec.standard().encode(PayloadTypeCatalog.encode(response), ResultCode.SUCCESS);
  }

  private static CanonicalField optionalText(String name, Optional<String> value) {
    return value.isPresent() ? text(name, value.get()) : new CanonicalField(name, "X1", null);
  }

  private static void require(boolean valid) {
    if (!valid) throw new IllegalArgumentException("user query identity is inconsistent");
  }

  @Override
  public String toString() {
    return "UserQueryRequest[REDACTED]";
  }
}
