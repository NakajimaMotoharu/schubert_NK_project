package dev.codex.schubert.nk.api.application.scenario;

import dev.codex.schubert.nk.api.idempotency.CanonicalField;
import dev.codex.schubert.nk.api.idempotency.CanonicalRequest;
import dev.codex.schubert.nk.api.persistence.ScenarioRepository;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.LayoutRegistry;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.layout.scenario.RouteListRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioFileListRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.SpeakerListRequestData;
import dev.codex.schubert.nk.protocol.layout.semantic.WireEnum;
import java.sql.Connection;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.OptionalLong;

/**
 * One validated Scenario request shared by HMAC construction and read-only query dispatch.
 * NK-SCN-001/NK-MSG-002; FUN-003..005/MQ-006..010; UI234/237/241; SS323 §9.1/324 §3/332 §4;
 * SSC-025/PT-SCN-009-Q01..Q04. Caller owns authentication, canonical cleanup, TX and file/JMS I/O.
 */
public final class ScenarioRequest {
  private enum Kind {
    GAMES,
    SPEAKERS,
    ROUTES,
    FILES,
    SEARCH,
    DETAIL
  }

  private final Kind kind;
  private final TypedPayloadValues values;
  private final CommonHeader header;

  private ScenarioRequest(Kind kind, TypedPayloadValues values, CommonHeader header) {
    this.kind = kind;
    this.values = values;
    this.header = header;
  }

  /**
   * Null is a caller contract error; unsupported/malformed wire is a bounded permanent rejection.
   */
  public static ScenarioRequest decode(WireMessage<FixedPayload> request) {
    Objects.requireNonNull(request, "request");
    try {
      Kind kind =
          switch (request.header().layoutId().value()) {
            case "GAMREQ01" -> Kind.GAMES;
            case "SPKREQ01" -> Kind.SPEAKERS;
            case "RTEREQ01" -> Kind.ROUTES;
            case "SCFREQ01" -> Kind.FILES;
            case "SRCREQ01" -> Kind.SEARCH;
            case "SCNREQ01" -> Kind.DETAIL;
            default -> throw new PermanentProtocolException("unsupported scenario request");
          };
      request
          .header()
          .validateAgainst(LayoutRegistry.standard().require(request.header().layoutId(), 1));
      byte[] data = request.payload().copyData();
      try {
        var values =
            PayloadTypeCatalog.decode(
                PayloadCodec.standard()
                    .decode(request.header().layoutId(), data, List.of(), false));
        return new ScenarioRequest(kind, values, request.header());
      } finally {
        Arrays.fill(data, (byte) 0);
      }
    } catch (PermanentProtocolException | IllegalArgumentException failure) {
      throw new PermanentProtocolException("scenario request is invalid");
    }
  }

  /** Validated immutable header; never log its context. SS324 §6.3, PT-SCN-009-S01..S05. */
  public CommonHeader header() {
    return header;
  }

  /** The six allowlisted request IDs all use the corresponding RSP01 suffix. */
  public LayoutId responseLayoutId() {
    return new LayoutId(values.layoutId().value().replace("REQ", "RSP"));
  }

  /** Present only for the detail request; binds response metadata/result reference to input. */
  public OptionalLong scriptFileId() {
    return kind == Kind.DETAIL
        ? OptionalLong.of(((ScenarioDetailRequestData) values.data()).scriptFileId().value())
        : OptionalLong.empty();
  }

  /** Actor must come from API verification; caller closes the returned secret-bearing fields. */
  public CanonicalRequest canonical(AuthenticatedActor actor) {
    Objects.requireNonNull(actor, "actor");
    List<CanonicalField> fields =
        switch (kind) {
          case GAMES -> List.of();
          case SPEAKERS ->
              List.of(
                  text(
                      "gameCode",
                      ((SpeakerListRequestData) values.data())
                          .gameCode()
                          .map(WireEnum::wireValue)));
          case ROUTES ->
              List.of(
                  text(
                      "gameCode",
                      Optional.of(((RouteListRequestData) values.data()).gameCode().wireValue())));
          case FILES -> {
            var data = (ScenarioFileListRequestData) values.data();
            yield List.of(
                text("gameCode", Optional.of(data.gameCode().wireValue())),
                number("prefix", data.prefix()));
          }
          case DETAIL ->
              List.of(
                  number(
                      "scriptFileId",
                      ((ScenarioDetailRequestData) values.data()).scriptFileId().value()));
          case SEARCH -> {
            var data = (ScenarioSearchRequestData) values.data();
            yield List.of(
                text("bodyKeyword", data.bodyKeyword()),
                text("gameCode", data.gameCode().map(WireEnum::wireValue)),
                text("speakerName", data.speakerName()),
                text("chapterTitle", data.chapterTitle()),
                text("entryType", data.entryType().map(WireEnum::wireValue)),
                text("voiceCondition", data.voiceCondition().map(WireEnum::wireValue)),
                number("page", data.page()),
                number("pageSize", data.pageSize()));
          }
        };
    return new CanonicalRequest(
        Long.toString(actor.userId()),
        values.layoutId().value(),
        "001",
        "REQUEST:" + values.layoutId().value(),
        fields);
  }

  /** Query only: does not touch authentication, commit, close, publish files or mutate Inbox. */
  public ScenarioQuerySnapshot query(
      ScenarioRepository repository, Connection connection, AuthenticatedActor actor) {
    Objects.requireNonNull(repository, "repository");
    Objects.requireNonNull(connection, "connection");
    Objects.requireNonNull(actor, "actor");
    return switch (kind) {
      case GAMES -> new ScenarioQuerySnapshot.Inline(repository.games(connection, actor));
      case SPEAKERS ->
          new ScenarioQuerySnapshot.Inline(
              repository.speakers(connection, actor, (SpeakerListRequestData) values.data()));
      case ROUTES ->
          new ScenarioQuerySnapshot.Inline(
              repository.routes(connection, actor, (RouteListRequestData) values.data()));
      case FILES ->
          new ScenarioQuerySnapshot.Inline(
              repository.files(connection, actor, (ScenarioFileListRequestData) values.data()));
      case SEARCH ->
          new ScenarioQuerySnapshot.Inline(
              repository.search(connection, actor, (ScenarioSearchRequestData) values.data()));
      case DETAIL ->
          new ScenarioQuerySnapshot.Detail(
              repository.detail(connection, actor, (ScenarioDetailRequestData) values.data()));
    };
  }

  private static CanonicalField text(String name, Optional<String> value) {
    if (value.isEmpty()) return new CanonicalField(name, "X1", null);
    return CanonicalField.text(name, value.orElseThrow());
  }

  private static CanonicalField number(String name, long value) {
    return CanonicalField.number(name, value);
  }

  @Override
  public String toString() {
    return "ScenarioRequest[REDACTED]";
  }
}
