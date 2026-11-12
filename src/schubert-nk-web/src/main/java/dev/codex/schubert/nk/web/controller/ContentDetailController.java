package dev.codex.schubert.nk.web.controller;

import dev.codex.schubert.nk.protocol.codec.FieldCodec;
import dev.codex.schubert.nk.protocol.codec.FieldEncodingException;
import dev.codex.schubert.nk.protocol.file.LargeResultDescriptor;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.media.MusicTrackRecord;
import dev.codex.schubert.nk.protocol.layout.media.MusicTrackRequestData;
import dev.codex.schubert.nk.protocol.layout.media.MusicTrackResponseData;
import dev.codex.schubert.nk.protocol.layout.media.VideoDescriptorRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioEntryRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.DeliveryMode;
import dev.codex.schubert.nk.protocol.layout.semantic.ScriptFileId;
import dev.codex.schubert.nk.web.error.WebResultMapper;
import dev.codex.schubert.nk.web.media.MediaDeliveryException;
import dev.codex.schubert.nk.web.media.MediaResponseDecoder;
import dev.codex.schubert.nk.web.messaging.MediaDescriptorWireClient;
import dev.codex.schubert.nk.web.messaging.MusicWireClient;
import dev.codex.schubert.nk.web.messaging.ProtectedReadWireException;
import dev.codex.schubert.nk.web.messaging.ScenarioWireClient;
import dev.codex.schubert.nk.web.messaging.ScenarioWireException;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import dev.codex.schubert.nk.web.session.SessionStoreException;
import dev.codex.schubert.nk.web.storage.FileIntegrityException;
import dev.codex.schubert.nk.web.storage.LargeResultReader;
import dev.codex.schubert.nk.web.view.AnimationWatchViewModel;
import dev.codex.schubert.nk.web.view.MusicTrackViewModel;
import dev.codex.schubert.nk.web.view.ScenarioDetailViewModel;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.security.Principal;
import java.text.Normalizer;
import java.util.List;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

/**
 * Bounded SCR007/010/013 read-only adapter using existing verified facades and held transfer
 * reader. FUN004/006/007/FIL/AUT/UI223234235237/SS313314333/PG-D365/PT-CONTENT001..010. No DTO,
 * context, physical path or descriptor is exposed in the HTML model. No ready claim.
 */
@Controller
@NullMarked
public final class ContentDetailController {
  private static final int HTTP_OK = 200;

  private final ScenarioWireClient scenarios;
  private final MediaDescriptorWireClient media;
  private final MusicWireClient music;
  private final LargeResultReader files;
  private final ApiSessionInvalidHandler invalid;
  private final WebResultMapper mapper = new WebResultMapper();

  public ContentDetailController(
      ScenarioWireClient scenarios,
      MediaDescriptorWireClient media,
      MusicWireClient music,
      LargeResultReader files,
      ApiSessionInvalidHandler invalid) {
    this.scenarios = Objects.requireNonNull(scenarios, "scenarios");
    this.media = Objects.requireNonNull(media, "media");
    this.music = Objects.requireNonNull(music, "music");
    this.files = Objects.requireNonNull(files, "files");
    this.invalid = Objects.requireNonNull(invalid, "invalid");
  }

  @GetMapping("/scenarios/{id:[0-9]{1,12}}")
  public @Nullable String scenario(
      @PathVariable("id") String id,
      Principal principal,
      Model model,
      HttpServletRequest request,
      HttpServletResponse response)
      throws IOException {
    var actor = actor(principal, model, request, response);
    Objects.requireNonNull(id, "id");
    final ScriptFileId selected;
    try {
      if (!id.matches("[0-9]{1,12}")) throw new IllegalArgumentException();
      selected = new ScriptFileId(Long.parseLong(id));
    } catch (IllegalArgumentException failure) {
      response.sendError(400);
      return null;
    }
    final ScenarioWireClient.Result result;
    try {
      result =
          scenarios.exchange(
              new TypedPayloadValues(
                  new LayoutId("SCNREQ01"), new ScenarioDetailRequestData(selected), List.of()),
              actor.authenticationContext());
    } catch (ScenarioWireException failure) {
      response.sendError(503);
      return null;
    }
    if (!success(result.resultCode(), request, response)) return null;
    try {
      var payload = result.payload().orElseThrow(IllegalArgumentException::new);
      var data = (ScenarioDetailResponseData) payload.data();
      if (!selected.equals(data.scriptFileId())) throw new IllegalArgumentException();
      final List<ScenarioEntryRecord> records;
      if (data.deliveryMode() == DeliveryMode.FILE) {
        var descriptor =
            new LargeResultDescriptor(
                data.fileId().orElseThrow(IllegalArgumentException::new),
                data.fileRelativePath().orElseThrow(IllegalArgumentException::new).wireValue(),
                data.fileByteLength(),
                data.fileSha256().orElseThrow(IllegalArgumentException::new).wireValue(),
                Math.toIntExact(data.fileRecordCount()));
        records = files.readScenario(descriptor);
      } else {
        records = payload.records().stream().map(r -> (ScenarioEntryRecord) r).toList();
      }
      model.addAttribute("page", ScenarioDetailViewModel.from(actor, data, records));
      return "scenario";
    } catch (FileIntegrityException | IllegalArgumentException failure) {
      SessionStoreException.preserveFatal(failure);
      response.sendError(503);
      return null;
    }
  }

  @GetMapping("/animation/opening")
  public @Nullable String opening(
      Principal principal, Model model, HttpServletRequest request, HttpServletResponse response)
      throws IOException {
    return watch("opening", principal, model, request, response);
  }

  @GetMapping("/animation/videos/{id}")
  public @Nullable String watch(
      @PathVariable("id") String id,
      Principal principal,
      Model model,
      HttpServletRequest request,
      HttpServletResponse response)
      throws IOException {
    var actor = actor(principal, model, request, response);
    Objects.requireNonNull(id, "id");
    String selected = Normalizer.normalize(id, Normalizer.Form.NFC);
    var input =
        new TypedPayloadValues(
            new LayoutId("VIDREQ01"), new VideoDescriptorRequestData(selected), List.of());
    try {
      var result = media.exchange(input, actor.authenticationContext());
      if (!success(result.resultCode(), request, response)) return null;
      var data = MediaResponseDecoder.decodeVerified(input, result).videoMetadata().orElseThrow();
      model.addAttribute("page", AnimationWatchViewModel.from(actor, data));
      return "animation-watch";
    } catch (ProtectedReadWireException failure) {
      response.sendError(
          failure.reason() == ProtectedReadWireException.Reason.INVALID_INPUT ? 400 : 503);
      return null;
    } catch (MediaDeliveryException | IllegalArgumentException failure) {
      SessionStoreException.preserveFatal(failure);
      response.sendError(503);
      return null;
    }
  }

  @GetMapping("/music/{category}/{section}")
  public @Nullable String tracks(
      @PathVariable("category") String category,
      @PathVariable("section") String section,
      Principal principal,
      Model model,
      HttpServletRequest request,
      HttpServletResponse response)
      throws IOException {
    var actor = actor(principal, model, request, response);
    Objects.requireNonNull(category, "category");
    Objects.requireNonNull(section, "section");
    try {
      FieldCodec.encodeText(category, 64, true);
      FieldCodec.encodeText(section, 128, true);
    } catch (FieldEncodingException failure) {
      response.sendError(400);
      return null;
    }
    category = Normalizer.normalize(category, Normalizer.Form.NFC);
    section = Normalizer.normalize(section, Normalizer.Form.NFC);
    try {
      var result =
          music.exchange(
              new TypedPayloadValues(
                  new LayoutId("MTRREQ01"),
                  new MusicTrackRequestData(category, section),
                  List.of()),
              actor.authenticationContext());
      if (!success(result.resultCode(), request, response)) return null;
      var payload = result.payload().orElseThrow(IllegalArgumentException::new);
      if (payload.records().isEmpty()) {
        response.sendError(404);
        return null;
      }
      model.addAttribute(
          "page",
          MusicTrackViewModel.from(
              actor,
              category,
              section,
              (MusicTrackResponseData) payload.data(),
              payload.records().stream().map(r -> (MusicTrackRecord) r).toList()));
      return "music-list";
    } catch (ProtectedReadWireException | IllegalArgumentException failure) {
      SessionStoreException.preserveFatal(failure);
      response.sendError(503);
      return null;
    }
  }

  private boolean success(
      ResultCode result, HttpServletRequest request, HttpServletResponse response)
      throws IOException {
    if (result == ResultCode.SESSION_INVALID) {
      invalid.handle(request, response);
      return false;
    }
    int status = mapper.httpStatus(result);
    if (status != HTTP_OK) {
      response.sendError(status);
      return false;
    }
    return true;
  }

  private static SessionPrincipal actor(
      Principal principal, Model model, HttpServletRequest request, HttpServletResponse response) {
    Objects.requireNonNull(principal, "principal");
    Objects.requireNonNull(model, "model");
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    if (!(principal instanceof SessionPrincipal actor)) throw new SessionStoreException();
    return actor;
  }
}
