package dev.codex.schubert.nk.web.controller;

import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.media.AnimationListRequestData;
import dev.codex.schubert.nk.protocol.layout.media.AnimationListResponseData;
import dev.codex.schubert.nk.protocol.layout.media.AnimationMenuRequestData;
import dev.codex.schubert.nk.protocol.layout.media.AnimationMenuResponseData;
import dev.codex.schubert.nk.protocol.layout.media.AnimationRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.AnimationListCategory;
import dev.codex.schubert.nk.web.error.WebResultMapper;
import dev.codex.schubert.nk.web.messaging.AnimationWireClient;
import dev.codex.schubert.nk.web.messaging.ProtectedReadWireClient;
import dev.codex.schubert.nk.web.messaging.ProtectedReadWireException;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import dev.codex.schubert.nk.web.session.SessionStoreException;
import dev.codex.schubert.nk.web.view.AnimationListViewModel;
import dev.codex.schubert.nk.web.view.AnimationMenuViewModel;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.security.Principal;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

/**
 * SCR008/009/FUN006/AUT/TST/UI221..223,235/SS311..314,323,352/PG207/PT-SCR054..065. Null endpoint
 * return means response was handled, never a successful empty model.
 */
@Controller
@NullMarked
public final class AnimationController {
  private final AnimationWireClient client;
  private final ApiSessionInvalidHandler invalid;
  private final WebResultMapper mapper = new WebResultMapper();

  public AnimationController(AnimationWireClient client, ApiSessionInvalidHandler invalid) {
    this.client = Objects.requireNonNull(client, "client");
    this.invalid = Objects.requireNonNull(invalid, "invalid");
  }

  @GetMapping("/animation")
  public @Nullable String menu(
      Principal principal, Model model, HttpServletRequest request, HttpServletResponse response)
      throws IOException {
    var actor = actor(principal, model, request, response);
    var result =
        exchange(
            new TypedPayloadValues(
                new LayoutId("ANMREQ01"), new AnimationMenuRequestData(), List.of()),
            actor,
            request,
            response);
    if (result.isEmpty()) return null;
    // BUG222: the private wire Result guarantees the same menu sum invariant as this projection.
    // Malformed sums are rejected by PayloadSemanticValidator and mapped to 503 in exchange.
    var page =
        AnimationMenuViewModel.from(actor, (AnimationMenuResponseData) result.orElseThrow().data());
    model.addAttribute("page", page);
    return "animation";
  }

  @GetMapping("/animation/main")
  public @Nullable String main(
      Principal principal, Model model, HttpServletRequest request, HttpServletResponse response)
      throws IOException {
    return list(AnimationListCategory.MAIN, principal, model, request, response);
  }

  @GetMapping("/animation/ova")
  public @Nullable String ova(
      Principal principal, Model model, HttpServletRequest request, HttpServletResponse response)
      throws IOException {
    return list(AnimationListCategory.OVA, principal, model, request, response);
  }

  private @Nullable String list(
      AnimationListCategory category,
      Principal principal,
      Model model,
      HttpServletRequest request,
      HttpServletResponse response)
      throws IOException {
    var actor = actor(principal, model, request, response);
    var result =
        exchange(
            new TypedPayloadValues(
                new LayoutId("ANLREQ01"), new AnimationListRequestData(category), List.of()),
            actor,
            request,
            response);
    if (result.isEmpty()) return null;
    final AnimationListViewModel page;
    try {
      var payload = result.orElseThrow();
      page =
          AnimationListViewModel.from(
              actor,
              category,
              (AnimationListResponseData) payload.data(),
              payload.records().stream().map(record -> (AnimationRecord) record).toList());
    } catch (IllegalArgumentException failure) {
      response.sendError(503);
      return null;
    }
    model.addAttribute("page", page);
    return "animation-list";
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
