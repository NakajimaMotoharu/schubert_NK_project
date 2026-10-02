package dev.codex.schubert.nk.web.controller;

import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.admin.UserRecord;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.error.WebResultMapper;
import dev.codex.schubert.nk.web.form.UserSearchForm;
import dev.codex.schubert.nk.web.messaging.ProtectedReadWireClient;
import dev.codex.schubert.nk.web.messaging.ProtectedReadWireException;
import dev.codex.schubert.nk.web.messaging.UserAdministrationWireClient;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import dev.codex.schubert.nk.web.session.SessionStoreException;
import dev.codex.schubert.nk.web.view.UserListViewModel;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.security.Principal;
import java.util.*;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

/**
 * Fixed SCR015, not full User mutation assembly. FUN009/AUT002/UI225,236/SS313,314;
 * PG-D344/PT-USER-HTTP001..010.
 */
@Controller
@NullMarked
public final class UserAdminController {
  private final UserAdministrationWireClient client;
  private final ApiSessionInvalidHandler invalid;
  private final WebResultMapper mapper = new WebResultMapper();

  public UserAdminController(
      UserAdministrationWireClient client, ApiSessionInvalidHandler invalid) {
    this.client = Objects.requireNonNull(client, "client");
    this.invalid = Objects.requireNonNull(invalid, "invalid");
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
      model.addAttribute("page", UserListViewModel.invalid(actor, form));
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
    if (status != 200) {
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
    model.addAttribute("page", page);
    return "admin/user-list";
  }
}
