package dev.codex.schubert.nk.api.application.media;

import static dev.codex.schubert.nk.api.idempotency.CanonicalField.number;
import static dev.codex.schubert.nk.api.idempotency.CanonicalField.text;

import dev.codex.schubert.nk.api.idempotency.CanonicalField;
import dev.codex.schubert.nk.api.idempotency.CanonicalRequest;
import dev.codex.schubert.nk.api.persistence.MediaRepository;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.file.ContentDisposition;
import dev.codex.schubert.nk.protocol.file.MediaDescriptor;
import dev.codex.schubert.nk.protocol.file.MediaType;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.LayoutRegistry;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.layout.media.AnimationListRequestData;
import dev.codex.schubert.nk.protocol.layout.media.AudioDescriptorRequestData;
import dev.codex.schubert.nk.protocol.layout.media.MediaDescriptorData;
import dev.codex.schubert.nk.protocol.layout.media.MusicDescriptorRequestData;
import dev.codex.schubert.nk.protocol.layout.media.MusicSectionRequestData;
import dev.codex.schubert.nk.protocol.layout.media.MusicTrackRequestData;
import dev.codex.schubert.nk.protocol.layout.media.VideoDescriptorRequestData;
import java.sql.Connection;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import java.util.Optional;

/**
 * Decode once for request identity and stored query dispatch; not an authorization or file gate.
 * NK-MED-001/NK-MSG-002; FUN-005..007/MQ-006..010; UI235/241; SS323 §9.2/324/332; SSC-029;
 * PT-MED-033..036. Caller owns canonical fields, authentication, TX, Inbox and file/JMS.
 */
public final class MediaRequest {
  private enum Kind {
    AUDIO,
    MENU,
    ANIMATION,
    VIDEO,
    CATEGORIES,
    SECTIONS,
    TRACKS,
    MUSIC
  }

  private final Kind kind;
  private final CommonHeader header;
  private final TypedPayloadValues values;

  private MediaRequest(Kind kind, CommonHeader header, TypedPayloadValues values) {
    this.kind = kind;
    this.header = header;
    this.values = values;
  }

  public static MediaRequest decode(WireMessage<FixedPayload> request) {
    Objects.requireNonNull(request, "request");
    try {
      Kind kind =
          switch (request.header().layoutId().value()) {
            case "AUDREQ01" -> Kind.AUDIO;
            case "ANMREQ01" -> Kind.MENU;
            case "ANLREQ01" -> Kind.ANIMATION;
            case "VIDREQ01" -> Kind.VIDEO;
            case "MCTREQ01" -> Kind.CATEGORIES;
            case "MCSREQ01" -> Kind.SECTIONS;
            case "MTRREQ01" -> Kind.TRACKS;
            case "MEDREQ01" -> Kind.MUSIC;
            default -> throw new PermanentProtocolException("unsupported media request");
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
        return new MediaRequest(kind, request.header(), values);
      } finally {
        Arrays.fill(data, (byte) 0);
      }
    } catch (PermanentProtocolException | IllegalArgumentException failure) {
      throw new PermanentProtocolException("media request is invalid");
    }
  }

  public CommonHeader header() {
    return header;
  }

  public LayoutId responseLayoutId() {
    return new LayoutId(values.layoutId().value().replace("REQ", "RSP"));
  }

  /** SS324/333; PT-MED-050..053. Only these requests can have a definite missing asset. */
  public boolean descriptorRequest() {
    return kind == Kind.AUDIO || kind == Kind.VIDEO || kind == Kind.MUSIC;
  }

  /** Bind successful metadata to this decoded request; not a manifest/physical/auth gate. */
  public Optional<MediaDescriptor> descriptor(TypedPayloadValues response) {
    Objects.requireNonNull(response, "response");
    if (!response.layoutId().equals(responseLayoutId()))
      throw new IllegalArgumentException("media response layout mismatch");
    if (!descriptorRequest()) return Optional.empty();
    var data = MediaDescriptorData.from(response.data().fields());
    MediaType type;
    String id;
    ContentDisposition disposition;
    if (kind == Kind.AUDIO) {
      var request = (AudioDescriptorRequestData) values.data();
      type = MediaType.AUDIO;
      id = Long.toString(request.audioId().value());
      disposition = ContentDisposition.valueOf(request.disposition().name());
    } else if (kind == Kind.VIDEO) {
      type = MediaType.VIDEO;
      id = ((VideoDescriptorRequestData) values.data()).videoId();
      disposition = ContentDisposition.INLINE;
    } else {
      var request = (MusicDescriptorRequestData) values.data();
      type = MediaType.MUSIC;
      id = request.trackId();
      disposition = ContentDisposition.valueOf(request.disposition().name());
    }
    var descriptor =
        new MediaDescriptor(
            type,
            data.mediaLogicalId(),
            data.storageRelativePath().wireValue(),
            data.fileName(),
            data.fileByteLength(),
            data.sha256().wireValue(),
            data.mimeType().wireValue(),
            ContentDisposition.valueOf(data.contentDisposition().name()));
    if (!descriptor.logicalId().equals(id) || descriptor.disposition() != disposition)
      throw new IllegalArgumentException("media response request mismatch");
    return Optional.of(descriptor);
  }

  public CanonicalRequest canonical(AuthenticatedActor actor) {
    Objects.requireNonNull(actor, "actor");
    List<CanonicalField> fields =
        switch (kind) {
          case MENU, CATEGORIES -> List.of();
          case AUDIO -> {
            var data = (AudioDescriptorRequestData) values.data();
            yield List.of(
                number("audioId", data.audioId().value()),
                text("disposition", data.disposition().wireValue()));
          }
          case ANIMATION ->
              List.of(
                  text(
                      "category",
                      ((AnimationListRequestData) values.data()).category().wireValue()));
          case VIDEO ->
              List.of(text("videoId", ((VideoDescriptorRequestData) values.data()).videoId()));
          case SECTIONS ->
              List.of(text("category", ((MusicSectionRequestData) values.data()).category()));
          case TRACKS -> {
            var data = (MusicTrackRequestData) values.data();
            yield List.of(text("category", data.category()), text("section", data.section()));
          }
          case MUSIC -> {
            var data = (MusicDescriptorRequestData) values.data();
            yield List.of(
                text("trackId", data.trackId()),
                text("disposition", data.disposition().wireValue()));
          }
        };
    return new CanonicalRequest(
        Long.toString(actor.userId()),
        values.layoutId().value(),
        "001",
        "REQUEST:" + values.layoutId().value(),
        fields);
  }

  /** Descriptor absence only is empty. Query metadata is not physical/manifest verification. */
  public Optional<TypedPayloadValues> query(
      MediaRepository repository, Connection connection, AuthenticatedActor actor) {
    Objects.requireNonNull(repository, "repository");
    Objects.requireNonNull(connection, "connection");
    Objects.requireNonNull(actor, "actor");
    return switch (kind) {
      case AUDIO ->
          repository.audioMetadata(connection, actor, (AudioDescriptorRequestData) values.data());
      case MENU -> Optional.of(repository.animationMenu(connection, actor));
      case ANIMATION ->
          Optional.of(
              repository.animationList(
                  connection, actor, (AnimationListRequestData) values.data()));
      case VIDEO ->
          repository.videoMetadata(connection, actor, (VideoDescriptorRequestData) values.data());
      case CATEGORIES -> Optional.of(repository.musicCategories(connection, actor));
      case SECTIONS ->
          Optional.of(
              repository.musicSections(connection, actor, (MusicSectionRequestData) values.data()));
      case TRACKS ->
          Optional.of(
              repository.musicTracks(connection, actor, (MusicTrackRequestData) values.data()));
      case MUSIC ->
          repository.musicMetadata(connection, actor, (MusicDescriptorRequestData) values.data());
    };
  }

  @Override
  public String toString() {
    return "MediaRequest[REDACTED]";
  }
}
