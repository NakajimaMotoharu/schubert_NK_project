package dev.codex.schubert.nk.web.controller;

import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.*;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationId;
import dev.codex.schubert.nk.web.error.WebResultMapper;
import dev.codex.schubert.nk.web.form.NotificationSearchForm;
import dev.codex.schubert.nk.web.messaging.*;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import dev.codex.schubert.nk.web.session.*;
import dev.codex.schubert.nk.web.view.NotificationDetailViewModel;
import dev.codex.schubert.nk.web.view.NotificationListViewModel;
import jakarta.servlet.http.*;
import java.io.IOException;
import java.security.Principal;
import java.util.*;
import org.jspecify.annotations.*;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.*;

/** SCR020/UI224,236/SS313,314; PG-D347/PT-NTF-HTTP001..010; owner is API context only. */
@Controller
@NullMarked
public final class NotificationController {
  private final NotificationWireClient client;
  private final ApiSessionInvalidHandler invalid;
  private final WebResultMapper mapper = new WebResultMapper();

  public NotificationController(NotificationWireClient client, ApiSessionInvalidHandler invalid) {
    this.client = Objects.requireNonNull(client, "client");
    this.invalid = Objects.requireNonNull(invalid, "invalid");
  }

  @GetMapping("/notifications")
  public @Nullable String list(
      @RequestParam MultiValueMap<String, String> parameters,
      Principal principal,
      Model model,
      HttpServletRequest request,
      HttpServletResponse response)
      throws IOException {
    Objects.requireNonNull(parameters, "parameters");
    Objects.requireNonNull(model, "model");
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    if (!(Objects.requireNonNull(principal, "principal") instanceof SessionPrincipal actor))
      throw new SessionStoreException();
    var form = NotificationSearchForm.bind(parameters);
    if (!form.isValid()) {
      response.setStatus(400);
      model.addAttribute("page", NotificationListViewModel.invalid(actor, form));
      return "notifications/list";
    }
    final ProtectedReadWireClient.Result result;
    try {
      result =
          client.exchange(
              new TypedPayloadValues(new LayoutId("NTSREQ01"), form.toRequest(), List.of()),
              actor.authenticationContext());
    } catch (ProtectedReadWireException failure) {
      response.sendError(503);
      return null;
    }
    if (result.resultCode() == ResultCode.SESSION_INVALID) {
      invalid.handle(request, response);
      return null;
    }
    int status = mapper.httpStatus(result.resultCode());
    if (status != 200) {
      response.sendError(status);
      return null;
    }
    final NotificationListViewModel page;
    try {
      var payload = result.payload().orElseThrow();
      page =
          NotificationListViewModel.success(
              actor,
              form,
              (PagedResponseData) payload.data(),
              payload.records().stream().map(value -> (NotificationRecord) value).toList());
    } catch (IllegalArgumentException | ClassCastException | NoSuchElementException failure) {
      response.sendError(503);
      return null;
    }
    model.addAttribute("page", page);
    return "notifications/list";
  }

  /** SCR021 reference only; cancellation/token lifecycle remains QA049, not fullReady. */
  @GetMapping("/notifications/{id:[0-9]{1,12}}")
  public @Nullable String detail(
      @PathVariable("id") String target,
      Principal principal,
      Model model,
      HttpServletRequest request,
      HttpServletResponse response)
      throws IOException {
    Objects.requireNonNull(target, "target");
    Objects.requireNonNull(model, "model");
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    if (!(Objects.requireNonNull(principal, "principal") instanceof SessionPrincipal actor))
      throw new SessionStoreException();
    final NotificationId id;
    try {
      id = new NotificationId(Long.parseLong(target));
    } catch (IllegalArgumentException invalidId) {
      response.sendError(404);
      return null;
    }
    final ProtectedReadWireClient.Result result;
    try {
      result =
          client.exchange(
              new TypedPayloadValues(
                  new LayoutId("NTDREQ01"), new NotificationDetailRequestData(id), List.of()),
              actor.authenticationContext());
    } catch (ProtectedReadWireException failure) {
      response.sendError(503);
      return null;
    }
    if (result.resultCode() == ResultCode.SESSION_INVALID) {
      invalid.handle(request, response);
      return null;
    }
    int status = mapper.httpStatus(result.resultCode());
    if (status != 200) {
      response.sendError(status);
      return null;
    }
    final NotificationDetailViewModel page;
    try {
      page =
          NotificationDetailViewModel.from(
              actor, id, (NotificationDetailResponseData) result.payload().orElseThrow().data());
    } catch (IllegalArgumentException | ClassCastException | NoSuchElementException failure) {
      response.sendError(503);
      return null;
    }
    model.addAttribute("page", page);
    return "notifications/detail";
  }
}
