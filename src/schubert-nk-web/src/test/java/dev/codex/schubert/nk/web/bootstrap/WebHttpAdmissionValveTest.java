package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.time.Duration;
import java.util.concurrent.atomic.AtomicInteger;
import org.apache.catalina.connector.Connector;
import org.apache.catalina.connector.Request;
import org.apache.catalina.connector.Response;
import org.apache.catalina.valves.ValveBase;
import org.junit.jupiter.api.Test;

/** Independent missing/duplicate/fatal terminal ownership, NATIVE-STOP004. */
final class WebHttpAdmissionValveTest {
  @Test
  void terminalOnlyCompletionAndMalformedOrDuplicateCallbacks() throws Exception {
    var gate = new WebHttpAdmission();
    var valve = new WebHttpAdmissionValve(gate);
    var coyote = new org.apache.coyote.Request();
    var request = new Request(new Connector(), coyote);
    var response = new Response(new org.apache.coyote.Response());
    assertThrows(NullPointerException.class, () -> new WebHttpAdmissionValve(null));
    assertThrows(NullPointerException.class, () -> valve.invoke(null, response));
    assertThrows(NullPointerException.class, () -> valve.invoke(request, null));
    assertFalse(valve.getRequestAttributesEnabled());
    valve.setRequestAttributesEnabled(false);
    assertThrows(IllegalArgumentException.class, () -> valve.setRequestAttributesEnabled(true));
    valve.log(null, response, 0);
    valve.log(request, null, 0);
    valve.log(request, response, 0);
    valve.invoke(request, response);
    assertEquals(503, response.getStatus());
    assertEquals("no-store", response.getHeader("Cache-Control"));
    var calls = new AtomicInteger();
    valve.setNext(
        new ValveBase(true) {
          @Override
          public void invoke(Request req, Response res) {
            calls.incrementAndGet();
          }
        });
    gate.admit();
    valve.invoke(request, response);
    valve.invoke(request, response);
    assertEquals(2, calls.get());
    assertThrows(IOException.class, () -> gate.drain(Duration.ZERO));
    valve.log(request, null, 0);
    assertThrows(IOException.class, () -> gate.drain(Duration.ZERO));
    valve.log(request, response, 0);
    valve.log(request, response, 0);
    gate.drain(Duration.ZERO);
    request.setAttribute(WebHttpAdmissionValve.class.getName() + ".lease", "invalid");
    assertThrows(jakarta.servlet.ServletException.class, () -> valve.invoke(request, response));
    valve.log(request, response, 0);
    gate.drain(Duration.ZERO);
  }

  @Test
  void fatalInvocationStillRequiresRealTerminalAndMissingNextNeverCompletes() throws Exception {
    var gate = new WebHttpAdmission();
    var valve = new WebHttpAdmissionValve(gate);
    var request = new Request(new Connector(), new org.apache.coyote.Request());
    var response = new Response(new org.apache.coyote.Response());
    gate.admit();
    assertThrows(NullPointerException.class, () -> valve.invoke(request, response));
    var fatal = new LinkageError("synthetic fatal");
    valve.setNext(
        new ValveBase(true) {
          @Override
          public void invoke(Request req, Response res) {
            throw fatal;
          }
        });
    assertSame(fatal, assertThrows(LinkageError.class, () -> valve.invoke(request, response)));
    assertThrows(IOException.class, () -> gate.drain(Duration.ZERO));
    valve.log(request, response, 0);
    gate.drain(Duration.ZERO);
  }
}
