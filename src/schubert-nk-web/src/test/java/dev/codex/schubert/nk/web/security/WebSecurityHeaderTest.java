package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;

/** NK-WEB-001/PT-WEB-091..094; UI222/226; SS313/342/352 §7.2; independent SS header oracle. */
class WebSecurityHeaderTest {
  private static final String LOGIN_PATH = "/login";
  private static final String ERROR_OPERATION = "ERROR";
  private static final String REDIRECT_OPERATION = "REDIRECT";
  private static final String STREAM_OPERATION = "STREAM";
  private static final String WRITER_OPERATION = "WRITER";
  private static final Map<String, String> EXPECTED =
      Map.of(
          "Content-Security-Policy",
              "default-src 'self'; style-src 'self'; img-src 'self' data:; media-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'self'; object-src 'none'",
          "Strict-Transport-Security", "max-age=31536000",
          "X-Content-Type-Options", "nosniff",
          "X-Frame-Options", "DENY",
          "Referrer-Policy", "same-origin",
          "Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=()",
          "Cache-Control", "no-store");

  @Test
  void web091EveryResponseGetsExactNonConflictingSecurityPolicy() throws Exception {
    var writer = new WebSecurityHeaderWriter();
    for (String method : List.of("GET", "HEAD", "POST")) {
      for (String path :
          List.of(
              LOGIN_PATH,
              "/",
              "/questions",
              "/notifications",
              "/admin/users",
              "/logs",
              "/error",
              "/music/media/item",
              "/static/styles.abc123.css")) {
        for (int status : new int[] {200, 206, 302, 400, 401, 403, 404, 409, 416, 429, 503}) {
          var request = new MockHttpServletRequest(method, path);
          var response = new MockHttpServletResponse();
          response.setStatus(status);
          response.getWriter().write("synthetic body");
          for (String name : EXPECTED.keySet()) {
            response.addHeader(name, "conflicting");
            response.addHeader(name, "duplicate");
          }
          writer.writeHeaders(request, response);
          writer.writeHeaders(request, response);
          exact(response);
          assertEquals(status, response.getStatus());
          assertEquals("synthetic body", response.getContentAsString());
          assertNull(request.getSession(false));
        }
      }
    }
  }

  @Test
  void web092RealHeaderFilterWritesBeforeEveryCommitAndAfterReset() throws Exception {
    var filter = new WebSecurityHeaderFilterFactory().create();
    for (String operation :
        List.of(
            "RETURN",
            ERROR_OPERATION,
            REDIRECT_OPERATION,
            "FLUSH",
            STREAM_OPERATION,
            WRITER_OPERATION,
            "RESET",
            "SERVLET",
            "IO")) {
      var request = new MockHttpServletRequest("GET", LOGIN_PATH);
      var commits = new AtomicInteger();
      var response =
          new MockHttpServletResponse() {
            @Override
            public jakarta.servlet.ServletOutputStream getOutputStream() {
              var delegate = super.getOutputStream();
              var owner = this;
              return new jakarta.servlet.ServletOutputStream() {
                @Override
                public boolean isReady() {
                  return delegate.isReady();
                }

                @Override
                public void setWriteListener(jakarta.servlet.WriteListener listener) {
                  delegate.setWriteListener(listener);
                }

                @Override
                public void write(int value) throws IOException {
                  delegate.write(value);
                }

                @Override
                public void close() throws IOException {
                  exact(owner);
                  commits.incrementAndGet();
                  delegate.close();
                }
              };
            }

            @Override
            public java.io.PrintWriter getWriter() throws java.io.UnsupportedEncodingException {
              var owner = this;
              return new java.io.PrintWriter(super.getWriter()) {
                @Override
                public void close() {
                  exact(owner);
                  commits.incrementAndGet();
                  super.close();
                }
              };
            }

            @Override
            public void setCommitted(boolean committed) {
              if (committed) {
                exact(this);
                commits.incrementAndGet();
              }
              super.setCommitted(committed);
            }
          };
      var run =
          (org.junit.jupiter.api.function.Executable)
              () ->
                  filter.doFilter(
                      request,
                      response,
                      (r, s) -> {
                        var http = (HttpServletResponse) s;
                        switch (operation) {
                          case ERROR_OPERATION -> http.sendError(403);
                          case REDIRECT_OPERATION -> http.sendRedirect(LOGIN_PATH);
                          case "FLUSH" -> http.flushBuffer();
                          case STREAM_OPERATION -> {
                            http.getOutputStream().write(65);
                            http.getOutputStream().close();
                          }
                          case WRITER_OPERATION -> {
                            http.getWriter().write("A");
                            http.getWriter().close();
                          }
                          case "RESET" -> {
                            http.setHeader("Cache-Control", "public");
                            http.reset();
                            http.flushBuffer();
                          }
                          case "SERVLET" -> throw new ServletException("synthetic failure");
                          case "IO" -> throw new IOException("synthetic failure");
                          default -> http.setStatus(206);
                        }
                      });
      if (operation.equals("SERVLET")) assertThrows(ServletException.class, run);
      else if (operation.equals("IO")) assertThrows(IOException.class, run);
      else assertDoesNotThrow(run);
      exact(response);
      if (Set.of(
              ERROR_OPERATION,
              REDIRECT_OPERATION,
              "FLUSH",
              STREAM_OPERATION,
              WRITER_OPERATION,
              "RESET")
          .contains(operation)) assertTrue(commits.get() > 0);
      if (operation.equals(ERROR_OPERATION)) assertEquals(403, response.getStatus());
      if (operation.equals(REDIRECT_OPERATION))
        assertEquals(LOGIN_PATH, response.getHeader("Location"));
      if (operation.equals(STREAM_OPERATION) || operation.equals(WRITER_OPERATION))
        assertEquals("A", response.getContentAsString());
      assertNull(request.getSession(false));
    }
  }

  @Test
  void web093NullAndResponseFaultContractsDoNotHideFailures() {
    var writer = new WebSecurityHeaderWriter();
    var request =
        new MockHttpServletRequest() {
          @Override
          public String getRequestURI() {
            throw new AssertionError("request must not be read");
          }
        };
    writer.writeHeaders(request, new MockHttpServletResponse());
    assertThrows(
        NullPointerException.class, () -> writer.writeHeaders(null, new MockHttpServletResponse()));
    assertThrows(NullPointerException.class, () -> writer.writeHeaders(request, null));
    for (String header : EXPECTED.keySet()) {
      var fault = new IllegalStateException("synthetic servlet fault");
      var response =
          new MockHttpServletResponse() {
            @Override
            public void setHeader(String name, String value) {
              if (name.equals(header)) throw fault;
              super.setHeader(name, value);
            }
          };
      assertSame(
          fault,
          assertThrows(IllegalStateException.class, () -> writer.writeHeaders(request, response)));
      assertEquals(0, response.getContentAsByteArray().length);
      assertFalse(response.isCommitted());
    }
  }

  @Test
  void web094ConcurrentResponsesHaveNoSharedMutableState() throws Exception {
    var writer = new WebSecurityHeaderWriter();
    var filter = new WebSecurityHeaderFilterFactory().create();
    var pool = Executors.newFixedThreadPool(8);
    try {
      var jobs = new ArrayList<Callable<Void>>();
      for (int i = 0; i < 100; i++) {
        String body = "response-" + i;
        jobs.add(
            () -> {
              var request = new MockHttpServletRequest("GET", "/search");
              var response = new MockHttpServletResponse();
              writer.writeHeaders(request, response);
              filter.doFilter(request, response, (r, s) -> s.getWriter().write(body));
              exact(response);
              assertEquals(body, response.getContentAsString());
              assertEquals(200, response.getStatus());
              assertNull(request.getSession(false));
              return null;
            });
      }
      synchronized (writer) {
        for (var future : pool.invokeAll(jobs, 10, TimeUnit.SECONDS))
          future.get(10, TimeUnit.SECONDS);
      }
    } finally {
      pool.shutdownNow();
      assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));
    }
  }

  private static void exact(MockHttpServletResponse response) {
    EXPECTED.forEach(
        (name, value) ->
            assertEquals(List.of(value), List.copyOf(response.getHeaders(name)), name));
  }
}
