package dev.codex.schubert.nk.web.controller;

import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationId;
import dev.codex.schubert.nk.web.error.WebResultMapper;
import dev.codex.schubert.nk.web.form.CancelForm;
import dev.codex.schubert.nk.web.form.NotificationSearchForm;
import dev.codex.schubert.nk.web.messaging.NotificationWireClient;
import dev.codex.schubert.nk.web.messaging.ProtectedReadWireClient;
import dev.codex.schubert.nk.web.messaging.ProtectedReadWireException;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import dev.codex.schubert.nk.web.session.OperationTokenConflictException;
import dev.codex.schubert.nk.web.session.SessionOperationTokenLifecycle;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import dev.codex.schubert.nk.web.session.SessionStoreException;
import dev.codex.schubert.nk.web.session.WebSessionId;
import dev.codex.schubert.nk.web.view.NotificationDetailViewModel;
import dev.codex.schubert.nk.web.view.NotificationListViewModel;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.security.Principal;
import java.util.List;
import java.util.Map;
import java.util.NoSuchElementException;
import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

/** SCR020021/UI224236/SS313314; PG-D347368/PT-NTF-HTTP,NTC-BIZ; API context owns scope. */
@Controller
@NullMarked
public final class NotificationController {
  private static final int HTTP_OK = 200;

  private static final java.lang.String LITERAL_NTCREQ01 = "NTCREQ01";

  private final NotificationWireClient client;
  private final ApiSessionInvalidHandler invalid;
  private final WebResultMapper mapper = new WebResultMapper();
  private final Optional<SessionOperationTokenLifecycle> tokens;
  private static final String RETRY = "処理結果を確認できません。同じ内容で再操作してください。";

  public NotificationController(NotificationWireClient client, ApiSessionInvalidHandler invalid) {
    this.client = Objects.requireNonNull(client, "client");
    this.invalid = Objects.requireNonNull(invalid, "invalid");
    tokens = Optional.empty();
  }

  /** Full SCR021 shares the exact current-row lifecycle used by the security chain. */
  public NotificationController(
      NotificationWireClient client,
      ApiSessionInvalidHandler invalid,
      SessionOperationTokenLifecycle tokens) {
    this.client = Objects.requireNonNull(client, "client");
    this.invalid = Objects.requireNonNull(invalid, "invalid");
    this.tokens = Optional.of(Objects.requireNonNull(tokens, "tokens"));
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
    if (status != HTTP_OK) {
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

  /** SCR021: fresh current owner/state precedes issuance for the one visible RECEIVED form. */
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
    return showDetail(id, actor, model, request, response, Optional.empty(), 200, "");
  }

  private @Nullable String showDetail(
      NotificationId id,
      SessionPrincipal actor,
      Model model,
      HttpServletRequest request,
      HttpServletResponse response,
      Optional<CancelForm> redisplay,
      int status,
      String notice)
      throws IOException {
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
    int readStatus = mapper.httpStatus(result.resultCode());
    if (readStatus != HTTP_OK) {
      response.sendError(readStatus);
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
    model.addAttribute("notice", notice);
    if (tokens.isPresent() && "RECEIVED".equals(page.getValues().get("state"))) {
      if (redisplay.isPresent()) {
        var form = redisplay.orElseThrow();
        model.addAttribute(
            "action", Map.of("fields", form.displayValues(), "issues", form.getIssues()));
      } else {
        try {
          var token = tokens.orElseThrow().issue(session(request), LITERAL_NTCREQ01);
          model.addAttribute(
              "action",
              Map.of(
                  "fields",
                  Map.of(
                      "operation",
                      "CANCEL",
                      "id",
                      id.value(),
                      "operation_token",
                      token.token().toString(),
                      "confirm",
                      false),
                  "issues",
                  Map.of()));
        } catch (OperationTokenConflictException conflict) {
          response.sendError(409);
          return null;
        } catch (SessionStoreException failure) {
          response.sendError(503);
          return null;
        }
      }
    }
    response.setStatus(status);
    return "notifications/detail";
  }

  /** No pre-update detail fetch: API owns the current state, owner and replay/HMAC checks. */
  @PostMapping("/notifications/{id:[0-9]{1,12}}")
  public @Nullable String cancel(
      @PathVariable("id") String target,
      @RequestParam MultiValueMap<String, String> parameters,
      Principal principal,
      Model model,
      HttpServletRequest request,
      HttpServletResponse response)
      throws IOException {
    Objects.requireNonNull(target, "target");
    Objects.requireNonNull(parameters, "parameters");
    Objects.requireNonNull(model, "model");
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    if (!(Objects.requireNonNull(principal, "principal") instanceof SessionPrincipal actor))
      throw new SessionStoreException();
    if (tokens.isEmpty()) {
      response.sendError(503);
      return null;
    }
    final NotificationId id;
    try {
      id = new NotificationId(Long.parseLong(target));
    } catch (IllegalArgumentException malformed) {
      response.sendError(404);
      return null;
    }
    var form = CancelForm.bind(id.value(), parameters);
    if (!form.isValid())
      return showDetail(
          id, actor, model, request, response, Optional.of(form), 400, "入力項目を確認してください。");
    var input = form.toRequest();
    final WebSessionId session;
    try {
      session = session(request);
      tokens.orElseThrow().require(session, LITERAL_NTCREQ01, input.operationToken());
    } catch (OperationTokenConflictException conflict) {
      response.sendError(409);
      return null;
    } catch (SessionStoreException failure) {
      return showDetail(id, actor, model, request, response, Optional.of(form), 503, RETRY);
    }
    final ProtectedReadWireClient.Result result;
    try {
      result =
          client.exchange(
              new TypedPayloadValues(new LayoutId(LITERAL_NTCREQ01), input, List.of()),
              actor.authenticationContext());
    } catch (ProtectedReadWireException failure) {
      return showDetail(id, actor, model, request, response, Optional.of(form), 503, RETRY);
    }
    if (result.resultCode() == ResultCode.SESSION_INVALID) {
      invalid.handle(request, response);
      return null;
    }
    int status = mapper.httpStatus(result.resultCode());
    if (status != HTTP_OK) {
      if (status == 400 || status == 409 || status == 503)
        return showDetail(
            id,
            actor,
            model,
            request,
            response,
            Optional.of(form),
            status,
            result.resultCode() == ResultCode.NOT_CANCELLABLE ? "現在の状態では取り消せません。" : RETRY);
      response.sendError(status);
      return null;
    }
    // Protected facade has validated layout, context, correlation, success body and filler.
    try {
      tokens
          .orElseThrow()
          .completeVerified(session, LITERAL_NTCREQ01, input.operationToken(), result.resultCode());
    } catch (OperationTokenConflictException conflict) {
      response.sendError(409);
      return null;
    } catch (SessionStoreException failure) {
      return showDetail(id, actor, model, request, response, Optional.of(form), 503, RETRY);
    }
    response.setHeader("Location", "/notifications/" + id.value());
    response.setStatus(302);
    return null;
  }

  private static WebSessionId session(HttpServletRequest request) {
    var current = request.getSession(false);
    if (current == null) throw new OperationTokenConflictException();
    try {
      return WebSessionId.parse(current.getId());
    } catch (IllegalArgumentException malformed) {
      throw new OperationTokenConflictException();
    }
  }
}
