package dev.codex.schubert.nk.web.media;

import dev.codex.schubert.nk.protocol.codec.HeaderCodec;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.file.ContentDisposition;
import dev.codex.schubert.nk.protocol.file.MediaDescriptor;
import dev.codex.schubert.nk.protocol.file.MediaType;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.*;
import dev.codex.schubert.nk.protocol.layout.media.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import java.util.Optional;

/**
 * Media request/response binding after approved JMS/body/ACL/correlation validation. It does not
 * invent a response MAC or grant file access. NK-MED-001; MQ-004/020/FIL-006/007;
 * UI231/232/235/237; SS333 §8; SSC-030; PG-D-077; PT-MED-037..040. No I/O, auth cache or Web copy
 * of API HMAC keys.
 */
public final class MediaResponseDecoder {
  private MediaResponseDecoder() {}

  /** Validated projection only; error responses contain neither descriptor nor video metadata. */
  public static final class Result {
    private final ResultCode code;
    private final Optional<MediaDescriptor> descriptor;
    private final Optional<VideoDescriptorResponseData> video;

    private Result(
        ResultCode code,
        Optional<MediaDescriptor> descriptor,
        Optional<VideoDescriptorResponseData> video) {
      this.code = code;
      this.descriptor = descriptor;
      this.video = video;
    }

    public ResultCode resultCode() {
      return code;
    }

    public Optional<MediaDescriptor> descriptor() {
      return descriptor;
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
              header.authenticationContext().orElseThrow(IllegalArgumentException::new)));
      ResultCode code = header.resultCode().orElseThrow(IllegalArgumentException::new);
      byte[] data = Arrays.copyOfRange(body, 256, body.length);
      try {
        var payload = PayloadCodec.standard().decode(header.layoutId(), data, List.of(), code);
        if (!code.usesSuccessProfile()) return new Result(code, Optional.empty(), Optional.empty());
        var typed = PayloadTypeCatalog.decode(payload);
        // Both response records expose exactly the same named MEDIA1024 prefix fields.
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
      return switch (layout) {
        case "AUDREQ01" -> {
          var audio = (AudioDescriptorRequestData) typed.data();
          yield new Binding(
              MediaType.AUDIO,
              Long.toString(audio.audioId().value()),
              ContentDisposition.valueOf(audio.disposition().name()));
        }
        case "VIDREQ01" ->
            new Binding(
                MediaType.VIDEO,
                ((VideoDescriptorRequestData) typed.data()).videoId(),
                ContentDisposition.INLINE);
        default -> {
          var music = (MusicDescriptorRequestData) typed.data();
          yield new Binding(
              MediaType.MUSIC,
              music.trackId(),
              ContentDisposition.valueOf(music.disposition().name()));
        }
      };
    } finally {
      Arrays.fill(data, (byte) 0);
    }
  }

  private static boolean sameContext(AuthenticationContext first, AuthenticationContext second) {
    byte[] left = first.wireValue().getBytes(StandardCharsets.US_ASCII);
    byte[] right = second.wireValue().getBytes(StandardCharsets.US_ASCII);
    try {
      return MessageDigest.isEqual(left, right);
    } finally {
      Arrays.fill(left, (byte) 0);
      Arrays.fill(right, (byte) 0);
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
      this.id = id;
      this.disposition = disposition;
    }
  }
}
