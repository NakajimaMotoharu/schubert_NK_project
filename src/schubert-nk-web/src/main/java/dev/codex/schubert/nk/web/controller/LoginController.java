package dev.codex.schubert.nk.web.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

/**
 * Anonymous Login display only; POST authentication belongs to the security chain. NK-WEB-002;
 * FUN-001/SYS-001/AUT-001; UI222/226/264; SS313/355; QA-045/UIC-005/SSC-074; PG219/PT-SCR105.
 */
@Controller
public final class LoginController {
  @GetMapping("/login")
  public String login() {
    return "login";
  }
}
