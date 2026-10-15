package dev.codex.schubert.nk.api.messaging.outbound;

import jakarta.jms.JMSException;
import org.apache.activemq.artemis.api.core.ActiveMQDuplicateIdException;

/** Independent standard Throwable graphs; PT-OPS-CAUSE3404-001; BUG1299/YKT1065. */
public final class OutboxCauseGraphCanary {
  private OutboxCauseGraphCanary() {}

  public static void main(String[] args) {
    Throwable input = graph(args[0]);
    System.out.println("ENTER " + args[0]);
    System.out.flush();
    boolean actual = OutboxJmsSender.isDuplicateConfirmation(input);
    System.out.println("RESULT " + actual);
  }

  private static Throwable graph(String name) {
    RuntimeException a = new RuntimeException("synthetic a");
    RuntimeException b = new RuntimeException("synthetic b");
    JMSException jms = new JMSException("synthetic jms");
    ActiveMQDuplicateIdException duplicate =
        new ActiveMQDuplicateIdException("synthetic duplicate");
    return switch (name) {
      case "acyclic" -> new RuntimeException("synthetic wrapper", b);
      case "direct" -> duplicate;
      case "cause-cycle" -> {
        a.initCause(b);
        b.initCause(a);
        yield a;
      }
      case "mixed-cycle" -> {
        jms.setLinkedException(b);
        b.initCause(jms);
        yield jms;
      }
      case "alternate-edge" -> {
        jms.setLinkedException(b);
        jms.initCause(duplicate);
        yield jms;
      }
      case "reachable-through-cycle" -> {
        jms.setLinkedException(b);
        jms.initCause(duplicate);
        b.initCause(jms);
        yield jms;
      }
      case "suppressed-only" -> {
        a.addSuppressed(duplicate);
        yield a;
      }
      case "message-only" -> new RuntimeException("AMQ229035 duplicate id synthetic");
      default -> throw new IllegalArgumentException("unknown synthetic case");
    };
  }
}
