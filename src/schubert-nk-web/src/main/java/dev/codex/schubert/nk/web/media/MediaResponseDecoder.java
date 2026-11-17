package dev.codex.schubert.nk.web.media;

import dev.codex.schubert.nk.protocol.codec.HeaderCodec;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.file.ContentDisposition;
import dev.codex.schubert.nk.protocol.file.MediaDescriptor;
import dev.codex.schubert.nk.protocol.file.MediaType;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutRegistry;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.layout.media.AudioDescriptorRequestData;
import dev.codex.schubert.nk.protocol.layout.media.MediaDescriptorData;
import dev.codex.schubert.nk.protocol.layout.media.MusicDescriptorRequestData;
import dev.codex.schubert.nk.protocol.layout.media.VideoDescriptorRequestData;
import dev.codex.schubert.nk.protocol.layout.media.VideoDescriptorResponseData;
import dev.codex.schubert.nk.web.messaging.ProtectedReadWireClient;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.text.Normalizer;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.Nullable;

/**
 * Media request/response binding after approved JMS/body/ACL/correlation validation. It does not
 * invent a response MAC or grant file access. NK-MED-001; MQ-004/020/FIL-006/007;
 * UI231/232/235/237; SS333 §8; SSC-030; PG-D-077; PT-MED-037..040. No I/O, auth cache or Web copy
 * of API HMAC keys.
 */
public final class MediaResponseDecoder {
  private static final int CONTEXT_BYTES = 64;
  private static final ContextOperations JDK_CONTEXT = new JdkContextOperations();

  private MediaResponseDecoder() {
    throw new AssertionError("static namespace");
  }

  /** Validated projection only; error responses contain neither descriptor nor video metadata. */
  public static final class Result {
    private final ResultCode code;
    private final Optional<MediaDescriptor> retainedDescriptor;
    private final Optional<VideoDescriptorResponseData> video;

    private Result(
        ResultCode code,
        Optional<MediaDescriptor> descriptor,
        Optional<VideoDescriptorResponseData> video) {
      this.code = code;
      this.retainedDescriptor = descriptor;
      this.video = video;
    }

    public ResultCode resultCode() {
      return code;
    }

    public Optional<MediaDescriptor> descriptor() {
      return retainedDescriptor;
    }

    public Optional<VideoDescriptorResponseData> videoMetadata() {
      return video;
    }

    @Override
    public String toString() {
      return "MediaResponse[REDACTED]";
    }
  }

  /** Decodes owned temporary bytes; caller's input remains unchanged and is never retained. */
  public static Result decode(WireMessage<FixedPayload> request, byte[] response)
      throws MediaDeliveryException {
    return decode(request, response, JDK_CONTEXT);
  }

  /** Closed trusted PT boundary; public/runtime callers always use the fixed JDK operations. */
  static Result decode(
      WireMessage<FixedPayload> request, byte[] response, ContextOperations contextOperations)
      throws MediaDeliveryException {
    Objects.requireNonNull(contextOperations, "context operations");
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    if (response.length < 256 || response.length > 2064) {
      throw new MediaDeliveryException(MediaDeliveryException.Reason.INVALID_DESCRIPTOR);
    }
    byte[] body = response.clone();
    try {
      Binding binding = binding(request);
      var header = HeaderCodec.standard().peek(body);
      require(
          header
              .layoutId()
              .value()
              .equals(request.header().layoutId().value().replace("REQ", "RSP")));
      header.validateAgainst(LayoutRegistry.standard().require(header.layoutId(), 1));
      require(header.totalLength() == body.length);
      require(header.correlationId().equals(request.header().messageId()));
      require(
          sameContext(
              request.header().authenticationContext().orElseThrow(IllegalArgumentException::new),
              header.authenticationContext().orElseThrow(IllegalArgumentException::new),
              contextOperations));
      ResultCode code = header.resultCode().orElseThrow(IllegalArgumentException::new);
      byte[] data = Arrays.copyOfRange(body, 256, body.length);
      try {
        var payload = PayloadCodec.standard().decode(header.layoutId(), data, List.of(), code);
        if (!code.usesSuccessProfile()) return new Result(code, Optional.empty(), Optional.empty());
        var typed = PayloadTypeCatalog.decode(payload);
        return project(binding, typed, code);
      } finally {
        Arrays.fill(data, (byte) 0);
      }
    } catch (PermanentProtocolException
        | IllegalArgumentException
        | IllegalStateException failure) {
      throw new MediaDeliveryException(MediaDeliveryException.Reason.INVALID_DESCRIPTOR);
    } finally {
      Arrays.fill(body, (byte) 0);
    }
  }

  /**
   * PG-D-343/PT-MED-HTTP010: the caller owns this exact request and private wire Result from its
   * exchange. Header/context/correlation/deadline/profile checks occurred in the trusted facade;
   * this is only request-bound descriptor projection, not a new authentication or file-access
   * grant.
   */
  public static Result decodeVerified(
      TypedPayloadValues request, ProtectedReadWireClient.Result response)
      throws MediaDeliveryException {
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    try {
      var bound = binding(request);
      var code = response.resultCode();
      if (!code.usesSuccessProfile()) return new Result(code, Optional.empty(), Optional.empty());
      var typed = response.payload().orElseThrow(IllegalArgumentException::new);
      require(typed.layoutId().value().equals(request.layoutId().value().replace("REQ", "RSP")));
      return project(bound, typed, code);
    } catch (IllegalArgumentException | IllegalStateException failure) {
      throw new MediaDeliveryException(MediaDeliveryException.Reason.INVALID_DESCRIPTOR);
    }
  }

  private static Result project(Binding binding, TypedPayloadValues typed, ResultCode code) {
    var media = MediaDescriptorData.from(typed.data().fields());
    var descriptor =
        new MediaDescriptor(
            binding.type,
            media.mediaLogicalId(),
            media.storageRelativePath().wireValue(),
            media.fileName(),
            media.fileByteLength(),
            media.sha256().wireValue(),
            media.mimeType().wireValue(),
            ContentDisposition.valueOf(media.contentDisposition().name()));
    require(descriptor.logicalId().equals(binding.id));
    require(descriptor.disposition() == binding.disposition);
    var video =
        typed.data() instanceof VideoDescriptorResponseData metadata
            ? Optional.of(metadata)
            : Optional.<VideoDescriptorResponseData>empty();
    return new Result(code, Optional.of(descriptor), video);
  }

  private static Binding binding(WireMessage<FixedPayload> request) {
    String layout = request.header().layoutId().value();
    require(layout.equals("AUDREQ01") || layout.equals("VIDREQ01") || layout.equals("MEDREQ01"));
    request
        .header()
        .validateAgainst(LayoutRegistry.standard().require(request.header().layoutId(), 1));
    byte[] data = request.payload().copyData();
    try {
      var typed =
          PayloadTypeCatalog.decode(
              PayloadCodec.standard().decode(request.header().layoutId(), data, List.of(), false));
      return binding(typed);
    } finally {
      Arrays.fill(data, (byte) 0);
    }
  }

  private static Binding binding(TypedPayloadValues typed) {
    require(typed.records().isEmpty());
    String layout = typed.layoutId().value();
    require(layout.equals("AUDREQ01") || layout.equals("VIDREQ01") || layout.equals("MEDREQ01"));
    if (layout.equals("AUDREQ01")) {
      require(typed.data() instanceof AudioDescriptorRequestData);
      var audio = (AudioDescriptorRequestData) typed.data();
      return new Binding(
          MediaType.AUDIO,
          Long.toString(audio.audioId().value()),
          ContentDisposition.valueOf(audio.disposition().name()));
    }
    if (layout.equals("VIDREQ01")) {
      require(typed.data() instanceof VideoDescriptorRequestData);
      return new Binding(
          MediaType.VIDEO,
          ((VideoDescriptorRequestData) typed.data()).videoId(),
          ContentDisposition.INLINE);
    }
    require(typed.data() instanceof MusicDescriptorRequestData);
    var music = (MusicDescriptorRequestData) typed.data();
    return new Binding(
        MediaType.MUSIC, music.trackId(), ContentDisposition.valueOf(music.disposition().name()));
  }

  private static boolean sameContext(
      AuthenticationContext first, AuthenticationContext second, ContextOperations operations) {
    byte[] left = contextBytes(first, operations);
    try {
      byte[] right = contextBytes(second, operations);
      try {
        return operations.same(left, right);
      } finally {
        Arrays.fill(right, (byte) 0);
      }
    } finally {
      Arrays.fill(left, (byte) 0);
    }
  }

  private static byte[] contextBytes(AuthenticationContext context, ContextOperations operations) {
    byte[] bytes = operations.encode(context);
    if (bytes == null) throw new IllegalStateException("invalid media context buffer");
    if (bytes.length != CONTEXT_BYTES) {
      Arrays.fill(bytes, (byte) 0);
      throw new IllegalStateException("invalid media context buffer");
    }
    return bytes;
  }

  /** Package-only fault port, never an HTTP/session/config-selected authorization capability. */
  interface ContextOperations {
    byte @Nullable [] encode(AuthenticationContext context);

    boolean same(byte[] first, byte[] second);
  }

  private static final class JdkContextOperations implements ContextOperations {
    @Override
    public byte[] encode(AuthenticationContext context) {
      return context.wireValue().getBytes(StandardCharsets.US_ASCII);
    }

    @Override
    public boolean same(byte[] first, byte[] second) {
      return MessageDigest.isEqual(first, second);
    }
  }

  private static void require(boolean valid) {
    if (!valid) throw new IllegalArgumentException("media response binding is invalid");
  }

  private static final class Binding {
    private final MediaType type;
    private final String id;
    private final ContentDisposition disposition;

    private Binding(MediaType type, String id, ContentDisposition disposition) {
      this.type = type;
      this.id = Normalizer.normalize(id, Normalizer.Form.NFC);
      this.disposition = disposition;
    }
  }
}
