package dev.codex.schubert.nk.web.controller;

import dev.codex.schubert.nk.protocol.file.ContentDisposition;
import dev.codex.schubert.nk.protocol.file.MediaDescriptor;
import dev.codex.schubert.nk.protocol.file.MediaType;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.media.AudioDescriptorRequestData;
import dev.codex.schubert.nk.protocol.layout.media.MusicDescriptorRequestData;
import dev.codex.schubert.nk.protocol.layout.media.VideoDescriptorRequestData;
import dev.codex.schubert.nk.protocol.layout.semantic.AudioId;
import dev.codex.schubert.nk.web.error.WebResultMapper;
import dev.codex.schubert.nk.web.logging.WebMediaAudit;
import dev.codex.schubert.nk.web.logging.WebMediaAudit.Failure;
import dev.codex.schubert.nk.web.media.MediaDeliveryException;
import dev.codex.schubert.nk.web.media.MediaRangeService;
import dev.codex.schubert.nk.web.media.MediaResponseDecoder;
import dev.codex.schubert.nk.web.messaging.MediaDescriptorWireClient;
import dev.codex.schubert.nk.web.messaging.ProtectedReadWireException;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import dev.codex.schubert.nk.web.security.WebRequestContext;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import dev.codex.schubert.nk.web.session.SessionStoreException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.FilterOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.security.Principal;
import java.text.Normalizer;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

/** Fixed SS313/333 media routes, fresh API authentication on GET and HEAD; PG-D-343/PT-MED-HTTP. */
@Controller
@NullMarked
public final class MediaController {
  private static final int HTTP_OK = 200;

  private final MediaDescriptorWireClient client;
  private final ApiSessionInvalidHandler invalid;
  private final MediaRangeService service;
  private final WebMediaAudit audit;
  private final WebResultMapper mapper = new WebResultMapper();

  public MediaController(
      MediaDescriptorWireClient client,
      ApiSessionInvalidHandler invalid,
      MediaRangeService service,
      WebMediaAudit audit) {
    this.client = Objects.requireNonNull(client, "client");
    this.invalid = Objects.requireNonNull(invalid, "invalid");
    this.service = Objects.requireNonNull(service, "service");
    this.audit = Objects.requireNonNull(audit, "audit");
  }

  @GetMapping("/audio/{id}")
  public void audio(
      @PathVariable("id") String id,
      Principal principal,
      HttpServletRequest request,
      HttpServletResponse response)
      throws IOException {
    deliver(MediaType.AUDIO, id, ContentDisposition.INLINE, principal, request, response);
  }

  @GetMapping("/audio/{id}/download")
  public void audioDownload(
      @PathVariable("id") String id,
      Principal principal,
      HttpServletRequest request,
      HttpServletResponse response)
      throws IOException {
    deliver(MediaType.AUDIO, id, ContentDisposition.ATTACHMENT, principal, request, response);
  }

  @GetMapping("/animation/media/{id}")
  public void video(
      @PathVariable("id") String id,
      Principal principal,
      HttpServletRequest request,
      HttpServletResponse response)
      throws IOException {
    deliver(MediaType.VIDEO, id, ContentDisposition.INLINE, principal, request, response);
  }

  @GetMapping("/music/media/{id}")
  public void music(
      @PathVariable("id") String id,
      Principal principal,
      HttpServletRequest request,
      HttpServletResponse response)
      throws IOException {
    deliver(MediaType.MUSIC, id, ContentDisposition.INLINE, principal, request, response);
  }

  @GetMapping("/music/download/{id}")
  public void musicDownload(
      @PathVariable("id") String id,
      Principal principal,
      HttpServletRequest request,
      HttpServletResponse response)
      throws IOException {
    deliver(MediaType.MUSIC, id, ContentDisposition.ATTACHMENT, principal, request, response);
  }

  private void deliver(
      MediaType type,
      String id,
      ContentDisposition disposition,
      Principal principal,
      HttpServletRequest request,
      HttpServletResponse response)
      throws IOException {
    Objects.requireNonNull(id, "id");
    Objects.requireNonNull(principal, "principal");
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    if (!(principal instanceof SessionPrincipal actor)) throw new SessionStoreException();
    // BUG-548/YKT-392: use the same NFC logical ID across URL input, wire and Range binding.
    id = Normalizer.normalize(id, Normalizer.Form.NFC);
    final TypedPayloadValues input;
    String logicalId = id;
    try {
      var mode =
          dev.codex.schubert.nk.protocol.layout.semantic.ContentDisposition.valueOf(
              disposition.name());
      if (type == MediaType.AUDIO) {
        if (!id.matches("[0-9]{1,12}")) throw new IllegalArgumentException();
        var audio = new AudioId(Long.parseLong(id));
        logicalId = Long.toString(audio.value());
        input =
            new TypedPayloadValues(
                new LayoutId("AUDREQ01"), new AudioDescriptorRequestData(audio, mode), List.of());
      } else if (type == MediaType.VIDEO) {
        input =
            new TypedPayloadValues(
                new LayoutId("VIDREQ01"), new VideoDescriptorRequestData(id), List.of());
      } else {
        input =
            new TypedPayloadValues(
                new LayoutId("MEDREQ01"), new MusicDescriptorRequestData(id, mode), List.of());
      }
    } catch (IllegalArgumentException failure) {
      response.sendError(400);
      return;
    }
    final MediaDescriptor descriptor;
    try {
      var wire = client.exchange(input, actor.authenticationContext());
      if (wire.resultCode() == ResultCode.SESSION_INVALID) {
        invalid.handle(request, response);
        return;
      }
      int status = mapper.httpStatus(wire.resultCode());
      if (status != HTTP_OK) {
        response.sendError(status);
        return;
      }
      descriptor = MediaResponseDecoder.decodeVerified(input, wire).descriptor().orElseThrow();
    } catch (ProtectedReadWireException failure) {
      response.sendError(
          failure.reason() == ProtectedReadWireException.Reason.INVALID_INPUT ? 400 : 503);
      return;
    } catch (MediaDeliveryException failure) {
      response.sendError(503);
      return;
    }
    var requestId = WebRequestContext.require(request).requestId();
    var output = new ServletResponse(response);
    try {
      service.deliver(
          type,
          logicalId,
          disposition,
          Optional.ofNullable(request.getHeader("Range")),
          request.getMethod().equals("HEAD"),
          descriptor,
          output);
    } catch (MediaDeliveryException failure) {
      Failure reason =
          failure.reason() == MediaDeliveryException.Reason.BUSY
              ? Failure.BUSY
              : output.clientAbort ? Failure.CLIENT_ABORT : Failure.IO;
      if (response.isCommitted()) {
        audit.record(requestId, actor, descriptor, response.getStatus(), output.bytes, reason);
        throw new IOException("media response interrupted");
      }
      failure
          .retryAfterSeconds()
          .ifPresent(seconds -> response.setHeader("Retry-After", Integer.toString(seconds)));
      response.sendError(503);
      audit.record(requestId, actor, descriptor, 503, output.bytes, reason);
      return;
    }
    audit.record(requestId, actor, descriptor, response.getStatus(), output.bytes, Failure.NONE);
  }

  private static final class ServletResponse implements MediaRangeService.Response {
    private final HttpServletResponse response;
    private long bytes;
    private boolean clientAbort;

    private ServletResponse(HttpServletResponse response) {
      this.response = response;
    }

    @Override
    public void begin(int status, Map<String, String> headers) {
      response.setStatus(status);
      headers.forEach(response::setHeader);
    }

    @Override
    public OutputStream body() throws IOException {
      return new FilterOutputStream(response.getOutputStream()) {
        @Override
        public void write(byte[] value, int offset, int length) throws IOException {
          try {
            out.write(value, offset, length);
            bytes += length;
          } catch (IOException failure) {
            clientAbort = true;
            throw failure;
          }
        }
      };
    }
  }
}
