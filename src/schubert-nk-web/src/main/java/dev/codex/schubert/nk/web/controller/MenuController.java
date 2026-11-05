package dev.codex.schubert.nk.web.controller;

import dev.codex.schubert.nk.web.logging.WebRequestTrace;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import dev.codex.schubert.nk.web.session.SessionStoreException;
import dev.codex.schubert.nk.web.view.MenuViewModel;
import java.security.Principal;
import java.util.Objects;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

/**
 * GET only; URL security is enforced by WebSecurityFilterFactory. NK-WEB-001; FUN-002/AUT-001..003;
 * UI221/223/226; SS313; PG-D-115/PT-WEB-142..147.
 */
@Controller
public final class MenuController {
  @GetMapping("/")
  public String show(Principal principal, Model model) {
    Objects.requireNonNull(principal, "principal");
    Objects.requireNonNull(model, "model");
    if (!(principal instanceof SessionPrincipal closed)) throw new SessionStoreException();
    model.addAttribute("page", MenuViewModel.from(closed));
    WebRequestTrace
        .markMenuViewed(); // QA054/SSC336: terminal GET/200 gate, not a new business call.
    return "menu";
  }
}
