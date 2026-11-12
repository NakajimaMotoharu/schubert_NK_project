package dev.codex.schubert.nk.web.controller;

import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.admin.UserDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.admin.UserDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.admin.UserMutationResponseData;
import dev.codex.schubert.nk.protocol.layout.admin.UserRecord;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.error.WebResultMapper;
import dev.codex.schubert.nk.web.form.PasswordResetForm;
import dev.codex.schubert.nk.web.form.UserChangeForm;
import dev.codex.schubert.nk.web.form.UserCreateForm;
import dev.codex.schubert.nk.web.form.UserRoleForm;
import dev.codex.schubert.nk.web.form.UserSearchForm;
import dev.codex.schubert.nk.web.form.UserStatusForm;
import dev.codex.schubert.nk.web.form.UserUnlockForm;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyException;
import dev.codex.schubert.nk.web.messaging.ProtectedReadWireClient;
import dev.codex.schubert.nk.web.messaging.ProtectedReadWireException;
import dev.codex.schubert.nk.web.messaging.UserAdministrationWireClient;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import dev.codex.schubert.nk.web.session.OperationTokenConflictException;
import dev.codex.schubert.nk.web.session.SessionOperationTokenLifecycle;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import dev.codex.schubert.nk.web.session.SessionStoreException;
import dev.codex.schubert.nk.web.session.WebSessionId;
import dev.codex.schubert.nk.web.view.UserCreateViewModel;
import dev.codex.schubert.nk.web.view.UserDetailViewModel;
import dev.codex.schubert.nk.web.view.UserListViewModel;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.security.Principal;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.NoSuchElementException;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

/**
 * Closed SCR015..017, same-core retained-token User operations and fresh API truth.
 * FUN009/AUT002/UI225236/SS313314/SSC177; PG-D366/367/PT-USER-HTTP/DETAIL/BIZ.
 */
@Controller
@NullMarked
public final class UserAdminController {
  private static final String LOCKED_STATE = "LOCKED";
  private static final int HTTP_OK = 200;

  private static final java.lang.String LITERAL_PASSWORD = "PASSWORD";

  private static final java.lang.String LITERAL_UCRREQ01 = "UCRREQ01";

  private static final java.lang.String LITERAL_PAGE = "page";

  private final UserAdministrationWireClient client;
  private final ApiSessionInvalidHandler invalid;
  private final WebResultMapper mapper = new WebResultMapper();
  private final Optional<SessionOperationTokenLifecycle> tokens;
  private static final Map<String, String> PURPOSES =
      Map.of(
          "STATUS",
          "USTREQ01",
          "ROLE",
          "URLREQ01",
          LITERAL_PASSWORD,
          "UPWREQ01",
          "UNLOCK",
          "ULKREQ01");
  private static final String RETRY = "処理結果を確認できません。同じ内容で再操作してください。";

  public UserAdminController(
      UserAdministrationWireClient client, ApiSessionInvalidHandler invalid) {
    this.client = Objects.requireNonNull(client, "client");
    this.invalid = Objects.requireNonNull(invalid, "invalid");
    tokens = Optional.empty();
  }

  /** SSC177/PG-D366: caller must supply the same current core used by Spring Session. */
  public UserAdminController(
      UserAdministrationWireClient client,
      ApiSessionInvalidHandler invalid,
      SessionOperationTokenLifecycle tokens) {
    this.client = Objects.requireNonNull(client, "client");
    this.invalid = Objects.requireNonNull(invalid, "invalid");
    this.tokens = Optional.of(Objects.requireNonNull(tokens, "tokens"));
  }

  @GetMapping("/admin/users/new")
  public @Nullable String newForm(
      Principal principal, Model model, HttpServletRequest request, HttpServletResponse response)
      throws IOException {
    var actor = administrator(principal, model, request, response);
    if (actor == null || !assembled(response)) return null;
    try {
      var token = tokens.orElseThrow().issue(session(request), LITERAL_UCRREQ01);
      model.addAttribute(LITERAL_PAGE, UserCreateViewModel.newForm(actor, token.token()));
      return "admin/user-new";
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

  @PostMapping("/admin/users/new")
  public @Nullable String create(
      @RequestParam MultiValueMap<String, String> parameters,
      Principal principal,
      Model model,
      HttpServletRequest request,
      HttpServletResponse response)
      throws IOException {
    var actor = administrator(principal, model, request, response);
    Objects.requireNonNull(parameters, "parameters");
    if (actor == null || !assembled(response)) return null;
    var token = retained(parameters, LITERAL_UCRREQ01, request, response);
    if (token == null) return null;
    final var form = UserCreateForm.bind(parameters);
    try {
      if (!form.isValid())
        return showCreate(actor, form, token, model, response, 400, "入力項目を確認してください。");
      final ProtectedReadWireClient.Result result;
      try {
        result =
            client.exchange(
                new TypedPayloadValues(new LayoutId(LITERAL_UCRREQ01), form.toRequest(), List.of()),
                actor.authenticationContext());
      } catch (ProtectedReadWireException failure) {
        return showCreate(actor, form, token, model, response, 503, RETRY);
      }
      if (result.resultCode() == ResultCode.SESSION_INVALID) {
        invalid.handle(request, response);
        return null;
      }
      int status = mapper.httpStatus(result.resultCode());
      if (status != HTTP_OK) {
        if (status == 400 || status == 409 || status == 503)
          return showCreate(
              actor,
              form,
              token,
              model,
              response,
              status,
              status == 503 ? RETRY : "Username又は操作の整合性を確認してください。");
        response.sendError(status);
        return null;
      }
      try {
        var data = (UserMutationResponseData) result.payload().orElseThrow().data();
        if (data.updatedVersion() != 0) throw new IllegalArgumentException();
        tokens
            .orElseThrow()
            .completeVerified(session(request), LITERAL_UCRREQ01, token, result.resultCode());
        response.setHeader("Location", "/admin/users/" + data.userId().value());
        response.setStatus(302);
        return null;
      } catch (OperationTokenConflictException conflict) {
        JmsRequestReplyException.preserveFatal(conflict);
        response.sendError(409);
        return null;
      } catch (SessionStoreException failure) {
        JmsRequestReplyException.preserveFatal(failure);
        return showCreate(actor, form, token, model, response, 503, RETRY);
      } catch (IllegalArgumentException | ClassCastException | NoSuchElementException failure) {
        JmsRequestReplyException.preserveFatal(failure);
        response.sendError(503);
        return null;
      }
    } finally {
      form.close();
    }
  }

  @PostMapping("/admin/users/{id:[0-9]{1,12}}")
  public @Nullable String change(
      @PathVariable("id") long id,
      @RequestParam MultiValueMap<String, String> parameters,
      Principal principal,
      Model model,
      HttpServletRequest request,
      HttpServletResponse response)
      throws IOException {
    var actor = administrator(principal, model, request, response);
    Objects.requireNonNull(parameters, "parameters");
    if (actor == null || !assembled(response)) return null;
    var operations = parameters.get("operation");
    if (operations == null || operations.size() != 1 || id < 1 || id > 999999999999L) {
      response.sendError(400);
      return null;
    }
    String operation = Objects.requireNonNull(operations.getFirst(), "operation");
    if (!PURPOSES.containsKey(operation)) {
      response.sendError(400);
      return null;
    }
    String purpose = Objects.requireNonNull(PURPOSES.get(operation));
    var token = retained(parameters, purpose, request, response);
    if (token == null) return null;
    @Nullable UserDetailViewModel before = null;
    String username = "";
    if (operation.equals(LITERAL_PASSWORD)) {
      before = lookup(id, actor, request, response);
      if (before == null) return null;
      username = (String) Objects.requireNonNull(before.getValues().get("username"));
    }
    final UserChangeForm form =
        switch (operation) {
          case "STATUS" -> UserStatusForm.bind(id, parameters);
          case "ROLE" -> UserRoleForm.bind(id, parameters);
          case LITERAL_PASSWORD -> PasswordResetForm.bind(id, username, parameters);
          default -> UserUnlockForm.bind(id, parameters);
        };
    try {
      if (!form.isValid())
        return showChange(
            id, actor, operation, form, token, model, request, response, 400, "入力項目を確認してください。");
      final ProtectedReadWireClient.Result result;
      try {
        result =
            client.exchange(
                new TypedPayloadValues(new LayoutId(purpose), form.toRequest(), List.of()),
                actor.authenticationContext());
      } catch (ProtectedReadWireException failure) {
        return showChange(id, actor, operation, form, token, model, request, response, 503, RETRY);
      }
      if (result.resultCode() == ResultCode.SESSION_INVALID) {
        invalid.handle(request, response);
        return null;
      }
      int status = mapper.httpStatus(result.resultCode());
      if (status != HTTP_OK) {
        if (status == 400 || status == 409 || status == 503)
          return showChange(
              id,
              actor,
              operation,
              form,
              token,
              model,
              request,
              response,
              status,
              status == 503 ? RETRY : "最新情報を確認し、必要なら明示的にフォームを取得し直してください。");
        response.sendError(status);
        return null;
      }
      try {
        var data = (UserMutationResponseData) result.payload().orElseThrow().data();
        long version =
            ((Number) Objects.requireNonNull(form.displayValues().get("expected_version")))
                .longValue();
        boolean noChangeUnlock =
            operation.equals("UNLOCK")
                && result.resultCode() == ResultCode.IDEMPOTENT_SUCCESS
                && data.updatedVersion() == version;
        if (data.userId().value() != id
            || (!noChangeUnlock && data.updatedVersion() != version + 1))
          throw new IllegalArgumentException();
        tokens
            .orElseThrow()
            .completeVerified(session(request), purpose, token, result.resultCode());
        if (before != null && Boolean.TRUE.equals(before.getValues().get("self"))) {
          invalid.handleVerifiedSelfReset(request, response);
          return null;
        }
        response.setHeader("Location", "/admin/users/" + id);
        response.setStatus(302);
        return null;
      } catch (OperationTokenConflictException conflict) {
        JmsRequestReplyException.preserveFatal(conflict);
        response.sendError(409);
        return null;
      } catch (SessionStoreException failure) {
        JmsRequestReplyException.preserveFatal(failure);
        return showChange(id, actor, operation, form, token, model, request, response, 503, RETRY);
      } catch (IllegalArgumentException | ClassCastException | NoSuchElementException failure) {
        JmsRequestReplyException.preserveFatal(failure);
        response.sendError(503);
        return null;
      }
    } finally {
      form.close();
    }
  }

  /** SSC177: issue precisely the forms displayed, atomically, after fresh API detail. */
  @GetMapping("/admin/users/{id:[0-9]{1,12}}")
  public @Nullable String detail(
      @PathVariable("id") long id,
      Principal principal,
      Model model,
      HttpServletRequest request,
      HttpServletResponse response)
      throws IOException {
    var actor = administrator(principal, model, request, response);
    if (actor == null) return null;
    var page = lookup(id, actor, request, response);
    if (page == null) return null;
    if (tokens.isPresent()) {
      var operations = new ArrayList<String>();
      if (!Boolean.TRUE.equals(page.getValues().get("self"))) {
        operations.add("STATUS");
        operations.add("ROLE");
      }
      operations.add(LITERAL_PASSWORD);
      if (LOCKED_STATE.equals(page.getValues().get("state"))) operations.add("UNLOCK");
      try {
        var issued =
            tokens
                .orElseThrow()
                .issueForForms(
                    session(request),
                    operations.stream()
                        .map(value -> Objects.requireNonNull(PURPOSES.get(value)))
                        .toList());
        var forms = new ArrayList<Map<String, Object>>();
        for (int index = 0; index < operations.size(); index++) {
          var fields = new HashMap<String, Object>();
          fields.put("id", id);
          fields.put("expected_version", Objects.requireNonNull(page.getValues().get("version")));
          fields.put("enabled", "DISABLED".equals(page.getValues().get("state")));
          fields.put("role", Objects.requireNonNull(page.getValues().get("role")));
          forms.add(
              displayForm(operations.get(index), fields, Map.of(), issued.get(index).token()));
        }
        model.addAttribute("forms", List.copyOf(forms));
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
    model.addAttribute(LITERAL_PAGE, page);
    model.addAttribute("message", "");
    return "admin/user-detail";
  }

  private static @Nullable SessionPrincipal administrator(
      Principal principal, Model model, HttpServletRequest request, HttpServletResponse response)
      throws IOException {
    Objects.requireNonNull(model, "model");
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    if (!(Objects.requireNonNull(principal, "principal") instanceof SessionPrincipal actor))
      throw new SessionStoreException();
    if (actor.role() != UserRole.ADMIN) {
      response.sendError(403);
      return null;
    }
    return actor;
  }

  private boolean assembled(HttpServletResponse response) throws IOException {
    if (tokens.isPresent()) return true;
    response.sendError(503);
    return false;
  }

  private static WebSessionId session(HttpServletRequest request) {
    var current = request.getSession(false);
    if (current == null) throw new OperationTokenConflictException();
    try {
      return WebSessionId.parse(current.getId());
    } catch (IllegalArgumentException failure) {
      JmsRequestReplyException.preserveFatal(failure);
      throw new OperationTokenConflictException();
    }
  }

  private @Nullable UUID retained(
      MultiValueMap<String, String> parameters,
      String purpose,
      HttpServletRequest request,
      HttpServletResponse response)
      throws IOException {
    var values = parameters.get("operation_token");
    if (values == null || values.size() != 1) {
      response.sendError(400);
      return null;
    }
    String text = Objects.requireNonNull(values.getFirst(), "operation token");
    if (!text.matches("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")) {
      response.sendError(400);
      return null;
    }
    var token = UUID.fromString(text);
    try {
      tokens.orElseThrow().require(session(request), purpose, token);
      return token;
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

  private static String showCreate(
      SessionPrincipal actor,
      UserCreateForm form,
      UUID token,
      Model model,
      HttpServletResponse response,
      int status,
      String message) {
    response.setStatus(status);
    model.addAttribute(
        LITERAL_PAGE, UserCreateViewModel.redisplay(actor, form, token, message, status == 409));
    return "admin/user-new";
  }

  private @Nullable String showChange(
      long id,
      SessionPrincipal actor,
      String operation,
      UserChangeForm form,
      UUID token,
      Model model,
      HttpServletRequest request,
      HttpServletResponse response,
      int status,
      String message)
      throws IOException {
    var page = lookup(id, actor, request, response);
    if (page == null) return null;
    response.setStatus(status);
    model.addAttribute(LITERAL_PAGE, page);
    model.addAttribute("message", message);
    model.addAttribute(
        "forms", List.of(displayForm(operation, form.displayValues(), form.getIssues(), token)));
    return "admin/user-detail";
  }

  private static Map<String, Object> displayForm(
      String operation, Map<String, Object> fields, Map<String, String> issues, UUID token) {
    return Map.of(
        "operation",
        operation,
        "fields",
        Map.copyOf(fields),
        "issues",
        Map.copyOf(issues),
        "token",
        token.toString());
  }

  private @Nullable UserDetailViewModel lookup(
      long id, SessionPrincipal actor, HttpServletRequest request, HttpServletResponse response)
      throws IOException {
    final UserId target;
    try {
      target = new UserId(id);
    } catch (IllegalArgumentException failure) {
      response.sendError(404);
      return null;
    }
    final ProtectedReadWireClient.Result result;
    try {
      result =
          client.exchange(
              new TypedPayloadValues(
                  new LayoutId("UDTREQ01"), new UserDetailRequestData(target), List.of()),
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
    final UserDetailViewModel page;
    try {
      page =
          UserDetailViewModel.from(
              actor, target, (UserDetailResponseData) result.payload().orElseThrow().data());
    } catch (IllegalArgumentException | ClassCastException | NoSuchElementException failure) {
      response.sendError(503);
      return null;
    }
    return page;
  }

  @GetMapping("/admin/users")
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
    if (actor.role() != UserRole.ADMIN) {
      response.sendError(403);
      return null;
    }
    var form = UserSearchForm.bind(parameters);
    if (!form.isValid()) {
      response.setStatus(400);
      model.addAttribute(LITERAL_PAGE, UserListViewModel.invalid(actor, form));
      return "admin/user-list";
    }
    final ProtectedReadWireClient.Result result;
    try {
      result =
          client.exchange(
              new TypedPayloadValues(new LayoutId("USRREQ01"), form.toRequest(), List.of()),
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
    final UserListViewModel page;
    try {
      var payload = result.payload().orElseThrow();
      page =
          UserListViewModel.success(
              actor,
              form,
              (PagedResponseData) payload.data(),
              payload.records().stream().map(value -> (UserRecord) value).toList());
    } catch (IllegalArgumentException | ClassCastException | NoSuchElementException failure) {
      response.sendError(503);
      return null;
    }
    model.addAttribute(LITERAL_PAGE, page);
    return "admin/user-list";
  }
}
