package dev.codex.schubert.nk.web.controller;

import dev.codex.schubert.nk.web.error.ProblemViewFactory;
import dev.codex.schubert.nk.web.security.WebDisplayContext;
import dev.codex.schubert.nk.web.security.WebRequestContext;
import jakarta.servlet.RequestDispatcher;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.util.Objects;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.RequestMapping;

/**
 * Fixed common error view; never reads error Throwable/message/URI or session. NK-WEB-001/SCR-090;
 * TST/MON; UI221/222/226; SS313/314/351/352; SSC-047/PG-D-116/PT-WEB-148..157.
 */
@Controller
public final class ErrorController {
  private final ProblemViewFactory factory;

  public ErrorController(ProblemViewFactory factory) {
    this.factory = Objects.requireNonNull(factory, "factory");
  }

  @RequestMapping("/error")
  public String error(HttpServletRequest request, HttpServletResponse response, Model model) {
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    Objects.requireNonNull(model, "model");
    Object status = request.getAttribute(RequestDispatcher.ERROR_STATUS_CODE);
    if (request.getDispatcherType() != jakarta.servlet.DispatcherType.ERROR
        && !"GET".equals(request.getMethod())
        && !"HEAD".equals(request.getMethod())) {
      status = 405;
      response.setHeader("Allow", "GET, HEAD");
    }
    var page =
        factory.create(
            status,
            WebRequestContext.require(request).requestId(),
            WebDisplayContext.existing(request).map(WebDisplayContext::topBar));
    response.setStatus(page.getStatus());
    model.addAttribute("page", page);
    return "error/error";
  }
}
