package dev.codex.schubert.nk.web.controller;

import dev.codex.schubert.nk.protocol.codec.FieldCodec;
import dev.codex.schubert.nk.protocol.codec.FieldEncodingException;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.media.MusicCategoryRecord;
import dev.codex.schubert.nk.protocol.layout.media.MusicCategoryRequestData;
import dev.codex.schubert.nk.protocol.layout.media.MusicCategoryResponseData;
import dev.codex.schubert.nk.protocol.layout.media.MusicSectionRecord;
import dev.codex.schubert.nk.protocol.layout.media.MusicSectionRequestData;
import dev.codex.schubert.nk.protocol.layout.media.MusicSectionResponseData;
import dev.codex.schubert.nk.web.error.WebResultMapper;
import dev.codex.schubert.nk.web.messaging.MusicWireClient;
import dev.codex.schubert.nk.web.messaging.ProtectedReadWireClient;
import dev.codex.schubert.nk.web.messaging.ProtectedReadWireException;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import dev.codex.schubert.nk.web.session.SessionStoreException;
import dev.codex.schubert.nk.web.view.MusicCategoryViewModel;
import dev.codex.schubert.nk.web.view.MusicSectionViewModel;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.security.Principal;
import java.text.Normalizer;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

/** SCR011/012/FUN007/AUT/TST/UI221..223,235/SS311..314,323,352/PG211/PT-SCR072..083. */
@Controller
@NullMarked
public final class MusicController {
  private final MusicWireClient client;
  private final ApiSessionInvalidHandler invalid;
  private final WebResultMapper mapper = new WebResultMapper();

  public MusicController(MusicWireClient client, ApiSessionInvalidHandler invalid) {
    this.client = Objects.requireNonNull(client, "client");
    this.invalid = Objects.requireNonNull(invalid, "invalid");
  }

  @GetMapping("/music")
  public @Nullable String categories(
      Principal principal, Model model, HttpServletRequest request, HttpServletResponse response)
      throws IOException {
    var actor = actor(principal, model, request, response);
    var result =
        exchange(
            new TypedPayloadValues(
                new LayoutId("MCTREQ01"), new MusicCategoryRequestData(), List.of()),
            actor,
            request,
            response);
    if (result.isEmpty()) return null;
    final MusicCategoryViewModel page;
    try {
      var p = result.orElseThrow();
      page =
          MusicCategoryViewModel.from(
              actor,
              (MusicCategoryResponseData) p.data(),
              p.records().stream().map(r -> (MusicCategoryRecord) r).toList());
    } catch (IllegalArgumentException failure) {
      response.sendError(503);
      return null;
    }
    model.addAttribute("page", page);
    return "music";
  }

  @GetMapping("/music/{category}")
  public @Nullable String sections(
      @PathVariable("category") String category,
      Principal principal,
      Model model,
      HttpServletRequest request,
      HttpServletResponse response)
      throws IOException {
    var actor = actor(principal, model, request, response);
    Objects.requireNonNull(category, "category");
    try {
      FieldCodec.encodeText(category, 64, true);
    } catch (FieldEncodingException failure) {
      response.sendError(400);
      return null;
    }
    String selected = Normalizer.normalize(category, Normalizer.Form.NFC);
    var result =
        exchange(
            new TypedPayloadValues(
                new LayoutId("MCSREQ01"), new MusicSectionRequestData(selected), List.of()),
            actor,
            request,
            response);
    if (result.isEmpty()) return null;
    var p = result.orElseThrow();
    if (p.records().isEmpty()) {
      response.sendError(404);
      return null;
    }
    final MusicSectionViewModel page;
    try {
      page =
          MusicSectionViewModel.from(
              actor,
              selected,
              (MusicSectionResponseData) p.data(),
              p.records().stream().map(r -> (MusicSectionRecord) r).toList());
    } catch (IllegalArgumentException failure) {
      response.sendError(503);
      return null;
    }
    model.addAttribute("page", page);
    return "music-sections";
  }

  private Optional<TypedPayloadValues> exchange(
      TypedPayloadValues input,
      SessionPrincipal actor,
      HttpServletRequest request,
      HttpServletResponse response)
      throws IOException {
    final ProtectedReadWireClient.Result result;
    try {
      result = client.exchange(input, actor.authenticationContext());
    } catch (ProtectedReadWireException failure) {
      response.sendError(503);
      return Optional.empty();
    }
    if (result.resultCode() == ResultCode.SESSION_INVALID) {
      invalid.handle(request, response);
      return Optional.empty();
    }
    int status = mapper.httpStatus(result.resultCode());
    if (status != 200) {
      response.sendError(status);
      return Optional.empty();
    }
    return result.payload();
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
