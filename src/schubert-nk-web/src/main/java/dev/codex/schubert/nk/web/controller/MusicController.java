package dev.codex.schubert.nk.web.controller;

import dev.codex.schubert.nk.protocol.codec.FieldCodec;
import dev.codex.schubert.nk.protocol.codec.FieldEncodingException;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.*;
import dev.codex.schubert.nk.protocol.layout.media.*;
import dev.codex.schubert.nk.web.error.WebResultMapper;
import dev.codex.schubert.nk.web.messaging.*;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import dev.codex.schubert.nk.web.session.*;
import dev.codex.schubert.nk.web.view.*;
import jakarta.servlet.http.*;
import java.io.IOException;
import java.security.Principal;
import java.text.Normalizer;
import java.util.*;
import org.jspecify.annotations.*;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

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
