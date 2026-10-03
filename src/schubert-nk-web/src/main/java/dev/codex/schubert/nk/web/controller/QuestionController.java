package dev.codex.schubert.nk.web.controller;

import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.*;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.question.*;
import dev.codex.schubert.nk.protocol.layout.semantic.QuestionId;
import dev.codex.schubert.nk.web.error.WebResultMapper;
import dev.codex.schubert.nk.web.form.QuestionSearchForm;
import dev.codex.schubert.nk.web.messaging.*;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import dev.codex.schubert.nk.web.session.*;
import dev.codex.schubert.nk.web.view.*;
import jakarta.servlet.http.*;
import java.io.IOException;
import java.security.Principal;
import java.util.*;
import org.jspecify.annotations.*;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.*;

/** SCR022023 read only/UI224236/SS313314323332; PG-D350/PT-QRY-HTTP001..012. */
@Controller
@NullMarked
public final class QuestionController {
  private final QuestionWireClient client;
  private final ApiSessionInvalidHandler invalid;
  private final WebResultMapper mapper = new WebResultMapper();

  public QuestionController(QuestionWireClient client, ApiSessionInvalidHandler invalid) {
    this.client = Objects.requireNonNull(client, "client");
    this.invalid = Objects.requireNonNull(invalid, "invalid");
  }

  @GetMapping("/questions")
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
    var form = QuestionSearchForm.bind(parameters, actor.role());
    if (!form.isValid()) {
      response.setStatus(400);
      model.addAttribute("page", QuestionListViewModel.invalid(actor, form));
      return "questions/list";
    }
    final ProtectedReadWireClient.Result result;
    try {
      result =
          client.exchange(
              new TypedPayloadValues(new LayoutId("QSSREQ01"), form.toRequest(), List.of()),
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
    final QuestionListViewModel page;
    try {
      var payload = result.payload().orElseThrow();
      page =
          QuestionListViewModel.success(
              actor,
              form,
              (PagedResponseData) payload.data(),
              payload.records().stream().map(value -> (QuestionSummaryRecord) value).toList());
    } catch (IllegalArgumentException | ClassCastException | NoSuchElementException failure) {
      response.sendError(503);
      return null;
    }
    model.addAttribute("page", page);
    return "questions/list";
  }

  @GetMapping("/questions/{id:[0-9]{1,12}}")
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
    final QuestionId id;
    try {
      id = new QuestionId(Long.parseLong(target));
    } catch (IllegalArgumentException failure) {
      response.sendError(404);
      return null;
    }
    final ProtectedReadWireClient.Result result;
    try {
      result =
          client.exchange(
              new TypedPayloadValues(
                  new LayoutId("QSDREQ01"), new QuestionDetailRequestData(id), List.of()),
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
    final QuestionDetailViewModel page;
    try {
      page =
          QuestionDetailViewModel.from(
              actor, id, (QuestionDetailResponseData) result.payload().orElseThrow().data());
    } catch (IllegalArgumentException | ClassCastException | NoSuchElementException failure) {
      response.sendError(503);
      return null;
    }
    model.addAttribute("page", page);
    return "questions/detail";
  }
}
