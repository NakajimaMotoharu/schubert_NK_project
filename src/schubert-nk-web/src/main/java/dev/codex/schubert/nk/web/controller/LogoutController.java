package dev.codex.schubert.nk.web.controller;

import dev.codex.schubert.nk.web.security.LocalLogoutHandler;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.Objects;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.PostMapping;

/** POST only, existing CSRF/authentication chain; UI226/SS313314/PG-D363/RERUN007. */
@Controller
public final class LogoutController {
  private final LocalLogoutHandler handler;

  public LogoutController(LocalLogoutHandler handler) {
    this.handler = Objects.requireNonNull(handler, "Logout handler");
  }

  @PostMapping("/logout")
  public void logout(HttpServletRequest request, HttpServletResponse response) throws IOException {
    handler.handle(request, response);
  }
}
