package dev.codex.schubert.nk.web.controller;

import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionSubmitResponseData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionSummaryRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.QuestionId;
import dev.codex.schubert.nk.web.error.WebResultMapper;
import dev.codex.schubert.nk.web.form.QuestionDeleteForm;
import dev.codex.schubert.nk.web.form.QuestionSearchForm;
import dev.codex.schubert.nk.web.form.QuestionSubmitForm;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyException;
import dev.codex.schubert.nk.web.messaging.ProtectedReadWireClient;
import dev.codex.schubert.nk.web.messaging.ProtectedReadWireException;
import dev.codex.schubert.nk.web.messaging.QuestionWireClient;
import dev.codex.schubert.nk.web.receipt.ReceiptReference;
import dev.codex.schubert.nk.web.receipt.ReceiptReferenceException;
import dev.codex.schubert.nk.web.receipt.ReceiptReferenceRepository;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import dev.codex.schubert.nk.web.session.OperationTokenConflictException;
import dev.codex.schubert.nk.web.session.SessionOperationTokenLifecycle;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import dev.codex.schubert.nk.web.session.SessionStoreException;
import dev.codex.schubert.nk.web.session.WebSessionId;
import dev.codex.schubert.nk.web.view.QuestionAcceptedViewModel;
import dev.codex.schubert.nk.web.view.QuestionDetailViewModel;
import dev.codex.schubert.nk.web.view.QuestionListViewModel;
import dev.codex.schubert.nk.web.view.QuestionSubmitViewModel;
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

/** SCR018019022023/UI224236/SS313314323332; PG-D350357368/PT-QRY-HTTP/RCPT006/QDL-BIZ. */
@Controller
@NullMarked
public final class QuestionController {
  private static final int HTTP_OK = 200;

  private static final java.lang.String LITERAL_QSBREQ01 = "QSBREQ01";

  private static final java.lang.String LITERAL_PAGE = "page";

  private static final java.lang.String LITERAL_QDLREQ01 = "QDLREQ01";

  private final QuestionWireClient client;
  private final ApiSessionInvalidHandler invalid;
  private final WebResultMapper mapper = new WebResultMapper();
  private final Optional<ReceiptReferenceRepository> receipts;
  private final Optional<SessionOperationTokenLifecycle> tokens;
  private static final String RETRY = "処理結果を確認できません。同じ内容で再操作してください。";

  public QuestionController(QuestionWireClient client, ApiSessionInvalidHandler invalid) {
    this.client = Objects.requireNonNull(client, "client");
    this.invalid = Objects.requireNonNull(invalid, "invalid");
    receipts = Optional.empty();
    tokens = Optional.empty();
  }

  /** Caller supplies the real Web-role locator and the current session's short-TX lifecycle. */
  public QuestionController(
      QuestionWireClient client,
      ApiSessionInvalidHandler invalid,
      ReceiptReferenceRepository receipts,
      SessionOperationTokenLifecycle tokens) {
    this.client = Objects.requireNonNull(client, "client");
    this.invalid = Objects.requireNonNull(invalid, "invalid");
    this.receipts = Optional.of(Objects.requireNonNull(receipts, "receipts"));
    this.tokens = Optional.of(Objects.requireNonNull(tokens, "tokens"));
  }

  /** SCR018/QA049/RCPT006A: explicit form only; full pending capacity never creates a UUID. */
  @GetMapping("/questions/new")
  public @Nullable String newForm(
      Principal principal, Model model, HttpServletRequest request, HttpServletResponse response)
      throws IOException {
    var actor = actor(principal, model, request, response);
    if (tokens.isEmpty()) {
      response.sendError(503);
      return null;
    }
    try {
      var token = tokens.orElseThrow().issue(session(request), LITERAL_QSBREQ01);
      model.addAttribute(LITERAL_PAGE, QuestionSubmitViewModel.newForm(actor, token));
      return "questions/new";
    } catch (OperationTokenConflictException conflict) {
      JmsRequestReplyException.preserveFatal(conflict);
      response.sendError(409);
      return null;
    } catch (SessionStoreException failure) {
      JmsRequestReplyException.preserveFatal(failure);
      response.sendError(503);
      return null;
    }
  }

  /** SCR018/QA048049/RCPT006B..D: no transaction spans API/JMS; no automatic new token. */
  @PostMapping("/questions/new")
  public @Nullable String submit(
      @RequestParam MultiValueMap<String, String> parameters,
      Principal principal,
      Model model,
      HttpServletRequest request,
      HttpServletResponse response)
      throws IOException {
    var actor = actor(principal, model, request, response);
    Objects.requireNonNull(parameters, "parameters");
    // Both dependencies are absent in the legacy read-only constructor and required together
    // in the full constructor. Do not add an impossible partial-pair coverage branch.
    if (tokens.isEmpty()) {
      response.sendError(503);
      return null;
    }
    // bind constructs a non-null final form; close only wipes its invariant non-null char[].
    // Use explicit ownership rather than generated nullable-resource/suppression branches.
    // All normal, known-failure and unknown-failure exits still erase the form body.
    final var form = QuestionSubmitForm.bind(parameters);
    try {
      if (!form.isValid()) return redisplay(actor, model, response, form, 400, "");
      final WebSessionId session;
      try {
        session = session(request);
        tokens.orElseThrow().require(session, LITERAL_QSBREQ01, form.operationToken());
      } catch (OperationTokenConflictException conflict) {
        JmsRequestReplyException.preserveFatal(conflict);
        response.sendError(409);
        return null;
      } catch (SessionStoreException failure) {
        JmsRequestReplyException.preserveFatal(failure);
        return redisplay(actor, model, response, form, 503, RETRY);
      }
      final ProtectedReadWireClient.Result result;
      try {
        result =
            client.exchange(
                new TypedPayloadValues(new LayoutId(LITERAL_QSBREQ01), form.toRequest(), List.of()),
                actor.authenticationContext());
      } catch (ProtectedReadWireException failure) {
        return redisplay(actor, model, response, form, 503, RETRY);
      }
      if (result.resultCode() == ResultCode.SESSION_INVALID) {
        invalid.handle(request, response);
        return null;
      }
      int status = mapper.httpStatus(result.resultCode());
      if (status != HTTP_OK) {
        if (status == 400 || status == 503)
          return redisplay(
              actor, model, response, form, status, status == 400 ? "入力項目を確認してください。" : RETRY);
        response.sendError(status);
        return null;
      }
      try {
        var data = (QuestionSubmitResponseData) result.payload().orElseThrow().data();
        // The wire facade has validated layout/context/correlation and the genuine typed reply.
        // Completion is retention metadata only; API owner/HMAC/stored-result checks stay in API.
        var reference =
            new ReceiptReference(data.receiptId(), data.questionId().value(), data.submittedAt());
        tokens
            .orElseThrow()
            .completeVerified(
                session, LITERAL_QSBREQ01, form.operationToken(), result.resultCode());
        receipts.orElseThrow().register(reference);
        // Closed view resolution is intentional. Match the security handlers' fixed relative
        // redirect, and never encode a session identifier or accept a caller-selected URL.
        response.setHeader("Location", "/questions/accepted/" + reference.receiptId());
        response.setStatus(302);
        return null;
      } catch (OperationTokenConflictException conflict) {
        JmsRequestReplyException.preserveFatal(conflict);
        response.sendError(409);
        return null;
      } catch (SessionStoreException | ReceiptReferenceException failure) {
        JmsRequestReplyException.preserveFatal(failure);
        return redisplay(actor, model, response, form, 503, RETRY);
      }
    } finally {
      form.close();
    }
  }

  /** SCR019/QA048/RCPT006E,F: locator is not proof; each GET verifies fresh current API state. */
  @GetMapping("/questions/accepted/{receiptId}")
  public @Nullable String accepted(
      @PathVariable("receiptId") String target,
      Principal principal,
      Model model,
      HttpServletRequest request,
      HttpServletResponse response)
      throws IOException {
    var actor = actor(principal, model, request, response);
    Objects.requireNonNull(target, "receiptId");
    if (receipts.isEmpty()) {
      response.sendError(503);
      return null;
    }
    try {
      ReceiptReference.requireReceiptId(target);
    } catch (IllegalArgumentException malformed) {
      response.sendError(404);
      return null;
    }
    final Optional<ReceiptReference> found;
    try {
      found = receipts.orElseThrow().find(target);
    } catch (ReceiptReferenceException failure) {
      JmsRequestReplyException.preserveFatal(failure);
      response.sendError(503);
      return null;
    }
    if (found.isEmpty()) {
      response.sendError(404);
      return null;
    }
    var reference = found.orElseThrow(); // find has committed/closed before the API exchange.
    final ProtectedReadWireClient.Result result;
    try {
      result =
          client.exchange(
              new TypedPayloadValues(
                  new LayoutId("QSDREQ01"),
                  new QuestionDetailRequestData(new QuestionId(reference.questionId())),
                  List.of()),
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
    final QuestionAcceptedViewModel page;
    try {
      page =
          QuestionAcceptedViewModel.from(
              actor, reference, (QuestionDetailResponseData) result.payload().orElseThrow().data());
    } catch (IllegalArgumentException | ClassCastException | NoSuchElementException failure) {
      response.sendError(503);
      return null;
    }
    model.addAttribute(LITERAL_PAGE, page);
    return "questions/accepted";
  }

  private static SessionPrincipal actor(
      Principal principal, Model model, HttpServletRequest request, HttpServletResponse response) {
    Objects.requireNonNull(model, "model");
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    if (!(Objects.requireNonNull(principal, "principal") instanceof SessionPrincipal actor))
      throw new SessionStoreException();
    return actor;
  }

  private static WebSessionId session(HttpServletRequest request) {
    var session = request.getSession(false);
    if (session == null) throw new OperationTokenConflictException();
    try {
      return WebSessionId.parse(session.getId());
    } catch (IllegalArgumentException malformed) {
      JmsRequestReplyException.preserveFatal(malformed);
      throw new OperationTokenConflictException();
    }
  }

  private static String redisplay(
      SessionPrincipal actor,
      Model model,
      HttpServletResponse response,
      QuestionSubmitForm form,
      int status,
      String notice) {
    response.setStatus(status);
    model.addAttribute(LITERAL_PAGE, QuestionSubmitViewModel.redisplay(actor, form, notice));
    return "questions/new";
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
      model.addAttribute(LITERAL_PAGE, QuestionListViewModel.invalid(actor, form));
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
    if (status != HTTP_OK) {
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
    model.addAttribute(LITERAL_PAGE, page);
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
    return showDetail(id, actor, model, request, response, Optional.empty(), 200, "");
  }

  private @Nullable String showDetail(
      QuestionId id,
      SessionPrincipal actor,
      Model model,
      HttpServletRequest request,
      HttpServletResponse response,
      Optional<QuestionDeleteForm> redisplay,
      int status,
      String notice)
      throws IOException {
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
    int readStatus = mapper.httpStatus(result.resultCode());
    if (readStatus != HTTP_OK) {
      response.sendError(readStatus);
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
    model.addAttribute(LITERAL_PAGE, page);
    model.addAttribute("notice", notice);
    if (tokens.isPresent()) {
      if (redisplay.isPresent()) {
        var form = redisplay.orElseThrow();
        model.addAttribute(
            "action", Map.of("fields", form.displayValues(), "issues", form.getIssues()));
      } else {
        try {
          var token = tokens.orElseThrow().issue(session(request), LITERAL_QDLREQ01);
          model.addAttribute(
              "action",
              Map.of(
                  "fields",
                  Map.of(
                      "operation",
                      "DELETE",
                      "id",
                      id.value(),
                      "operation_token",
                      token.token().toString(),
                      "confirm",
                      false),
                  "issues",
                  Map.of()));
        } catch (OperationTokenConflictException conflict) {
          JmsRequestReplyException.preserveFatal(conflict);
          response.sendError(409);
          return null;
        } catch (SessionStoreException failure) {
          JmsRequestReplyException.preserveFatal(failure);
          response.sendError(503);
          return null;
        }
      }
    }
    response.setStatus(status);
    return "questions/detail";
  }

  /** Existing detail confirmation handles list selection too; API owns target/owner/HMAC. */
  @PostMapping("/questions/{id:[0-9]{1,12}}")
  public @Nullable String delete(
      @PathVariable("id") String target,
      @RequestParam MultiValueMap<String, String> parameters,
      Principal principal,
      Model model,
      HttpServletRequest request,
      HttpServletResponse response)
      throws IOException {
    var actor = actor(principal, model, request, response);
    Objects.requireNonNull(target, "target");
    Objects.requireNonNull(parameters, "parameters");
    if (tokens.isEmpty()) {
      response.sendError(503);
      return null;
    }
    final QuestionId id;
    try {
      id = new QuestionId(Long.parseLong(target));
    } catch (IllegalArgumentException malformed) {
      response.sendError(404);
      return null;
    }
    var form = QuestionDeleteForm.bind(id.value(), parameters);
    if (!form.isValid())
      return showDetail(
          id, actor, model, request, response, Optional.of(form), 400, "入力項目を確認してください。");
    var input = form.toRequest();
    final WebSessionId session;
    try {
      session = session(request);
      tokens.orElseThrow().require(session, LITERAL_QDLREQ01, input.operationToken());
    } catch (OperationTokenConflictException conflict) {
      JmsRequestReplyException.preserveFatal(conflict);
      response.sendError(409);
      return null;
    } catch (SessionStoreException failure) {
      JmsRequestReplyException.preserveFatal(failure);
      return showDetail(id, actor, model, request, response, Optional.of(form), 503, RETRY);
    }
    final ProtectedReadWireClient.Result result;
    try {
      result =
          client.exchange(
              new TypedPayloadValues(new LayoutId(LITERAL_QDLREQ01), input, List.of()),
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
        return showDetail(id, actor, model, request, response, Optional.of(form), status, RETRY);
      response.sendError(status);
      return null;
    }
    // Do not prefetch IF030 here: a deleted question still permits owner-bound QDL replay0200.
    try {
      tokens
          .orElseThrow()
          .completeVerified(session, LITERAL_QDLREQ01, input.operationToken(), result.resultCode());
    } catch (OperationTokenConflictException conflict) {
      JmsRequestReplyException.preserveFatal(conflict);
      response.sendError(409);
      return null;
    } catch (SessionStoreException failure) {
      JmsRequestReplyException.preserveFatal(failure);
      return showDetail(id, actor, model, request, response, Optional.of(form), 503, RETRY);
    }
    response.setHeader("Location", "/questions");
    response.setStatus(302);
    return null;
  }
}
