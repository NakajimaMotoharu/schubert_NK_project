package dev.codex.schubert.nk.api.application.question;

import static dev.codex.schubert.nk.api.idempotency.CanonicalField.number;

import dev.codex.schubert.nk.api.idempotency.CanonicalField;
import dev.codex.schubert.nk.api.idempotency.CanonicalRequest;
import dev.codex.schubert.nk.api.persistence.QuestionQueryRepository;
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
import dev.codex.schubert.nk.protocol.layout.question.NotificationDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionSearchRequestData;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.time.Instant;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;

/**
 * Strict four-query decode and original-field HMAC, not a current authorization grant.
 * NK-QRY-001/NK-NTF-001; QST005..010/NTF001..012/MQ006..010; UI224236241;
 * SS323/324/332/SSC157/PG-D-330; PT-QRY009..012/NTF009. Caller closes canonical buffers.
 */
public final class QuestionQueryRequest {
  private final CommonHeader header;
  private final TypedPayloadValues values;

  private QuestionQueryRequest(CommonHeader header, TypedPayloadValues values) {
    this.header = header;
    this.values = values;
  }

  public static QuestionQueryRequest decode(WireMessage<FixedPayload> request) {
    Objects.requireNonNull(request, "request");
    byte[] bytes = request.payload().copyData();
    try {
      var header = request.header();
      require(
          Set.of("QSSREQ01", "QSDREQ01", "NTSREQ01", "NTDREQ01")
              .contains(header.layoutId().value()));
      header.validateAgainst(LayoutRegistry.standard().require(header.layoutId(), 1));
      return new QuestionQueryRequest(
          header,
          PayloadTypeCatalog.decode(
              PayloadCodec.standard().decode(header.layoutId(), bytes, List.of(), false)));
    } catch (PermanentProtocolException | IllegalArgumentException failure) {
      throw new PermanentProtocolException("question query request is invalid");
    } finally {
      Arrays.fill(bytes, (byte) 0);
    }
  }

  public CommonHeader header() {
    return header;
  }

  public boolean questionScope() {
    return header.layoutId().value().startsWith("QS");
  }

  public boolean detailRequest() {
    return values.data() instanceof QuestionDetailRequestData
        || values.data() instanceof NotificationDetailRequestData;
  }

  public boolean usernameSpecified() {
    return values.data() instanceof QuestionSearchRequestData data && data.username().isPresent();
  }

  public LayoutId responseLayoutId() {
    return new LayoutId(header.layoutId().value().substring(0, 3) + "RSP01");
  }

  public CanonicalRequest canonical(AuthenticatedActor actor) {
    Objects.requireNonNull(actor, "actor");
    List<CanonicalField> fields;
    if (detailRequest()) {
      fields =
          questionScope()
              ? List.of(
                  number(
                      "questionId",
                      ((QuestionDetailRequestData) values.data()).questionId().value()))
              : List.of(
                  number(
                      "notificationId",
                      ((NotificationDetailRequestData) values.data()).notificationId().value()));
    } else if (questionScope()) {
      var d = (QuestionSearchRequestData) values.data();
      fields =
          List.of(
              optional("keyword", "X1", d.keyword()),
              optional("username", "X1", d.username()),
              optional("answerState", "X1", d.answerState().map(v -> v.wireValue())),
              optional("submittedFrom", "T1", d.submittedFrom().map(Instant::toString)),
              optional("submittedTo", "T1", d.submittedTo().map(Instant::toString)),
              number("page", d.page()),
              number("pageSize", d.pageSize()));
    } else {
      var d = (NotificationSearchRequestData) values.data();
      fields =
          List.of(
              optional("notificationType", "X1", d.notificationType().map(v -> v.wireValue())),
              optional("submittedFrom", "T1", d.submittedFrom().map(Instant::toString)),
              optional("submittedTo", "T1", d.submittedTo().map(Instant::toString)),
              number("page", d.page()),
              number("pageSize", d.pageSize()));
    }
    return new CanonicalRequest(
        Long.toString(actor.userId()),
        header.layoutId().value(),
        "001",
        "REQUEST:" + header.layoutId().value(),
        fields);
  }

  public Optional<TypedPayloadValues> query(
      QuestionQueryRepository repository, Connection connection, AuthenticatedActor actor) {
    Objects.requireNonNull(repository, "repository");
    Objects.requireNonNull(connection, "connection");
    Objects.requireNonNull(actor, "actor");
    if (questionScope())
      return detailRequest()
          ? repository.questionDetail(connection, actor, (QuestionDetailRequestData) values.data())
          : Optional.of(
              repository.questionSearch(
                  connection, actor, (QuestionSearchRequestData) values.data()));
    return detailRequest()
        ? repository.notificationDetail(
            connection, actor, (NotificationDetailRequestData) values.data())
        : Optional.of(
            repository.notificationSearch(
                connection, actor, (NotificationSearchRequestData) values.data()));
  }

  /** Codec validates bytes/semantic invariants; additionally bind original detail ID/page. */
  public void validateResponse(TypedPayloadValues response) {
    Objects.requireNonNull(response, "response");
    require(response.layoutId().equals(responseLayoutId()));
    if (detailRequest()) {
      if (questionScope()) {
        require(response.data() instanceof QuestionDetailResponseData);
        require(
            ((QuestionDetailResponseData) response.data())
                .questionId()
                .equals(((QuestionDetailRequestData) values.data()).questionId()));
      } else {
        require(response.data() instanceof NotificationDetailResponseData);
        require(
            ((NotificationDetailResponseData) response.data())
                .notificationId()
                .equals(((NotificationDetailRequestData) values.data()).notificationId()));
      }
    } else {
      validatePage(
          response,
          questionScope()
              ? ((QuestionSearchRequestData) values.data()).page()
              : ((NotificationSearchRequestData) values.data()).page());
    }
    PayloadCodec.standard().encode(PayloadTypeCatalog.encode(response), ResultCode.SUCCESS);
  }

  private static void validatePage(TypedPayloadValues response, int requested) {
    require(response.data() instanceof PagedResponseData);
    var page = (PagedResponseData) response.data();
    require(page.effectivePage() == Math.min(requested, page.totalPages()));
  }

  private static CanonicalField optional(String name, String type, Optional<String> value) {
    if (value.isEmpty()) return new CanonicalField(name, type, null);
    byte[] owned = value.orElseThrow().getBytes(StandardCharsets.UTF_8);
    try {
      return new CanonicalField(name, type, owned);
    } finally {
      Arrays.fill(owned, (byte) 0);
    }
  }

  private static void require(boolean valid) {
    if (!valid) throw new IllegalArgumentException("query identity is inconsistent");
  }

  @Override
  public String toString() {
    return "QuestionQueryRequest[REDACTED]";
  }
}
