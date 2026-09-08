package dev.codex.schubert.nk.web.security;

import java.util.List;
import org.springframework.security.web.header.HeaderWriterFilter;

/**
 * Commit-aware Spring filter; final server/dispatch registration is a separate gate. NK-WEB-001;
 * SYS-006/FUN-001/AUT-004; UI222/226; SS313/342/352; PG-D-106/PT-WEB-091..094.
 */
public final class WebSecurityHeaderFilterFactory {
  public HeaderWriterFilter create() {
    return new HeaderWriterFilter(List.of(new WebSecurityHeaderWriter()));
  }
}
