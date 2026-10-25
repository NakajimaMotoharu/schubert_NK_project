package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;

/** SS342343354/SSC234; PT-OPS-CLOSE743001..004. Literal order, never OS authority. */
class FixedNativeCoverageTerminalTest {
  static final String INV = "1234567890abcdef1234567890abcdef";

  @Test
  void close743001SameOwnerTerminalReturnPrecedesOneClosingAndEachIndependentExport()
      throws Exception {
    var calls = new ArrayList<String>();
    var profile =
        FixedNativeCoverageProfile.parseTerminal(
                FixedNativeCoverageProfile.TerminalRole.BOOTSTRAP,
                INV,
                List.of(
                    "-javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=output=none,append=false,dumponexit=false,sessionid=BOOTSTRAP-1234567890abcdef1234567890abcdef-ordinary"))
            .orElseThrow();
    var agent =
        new FixedNativeCoverageCheckpoint.Agent() {
          public String version() {
            return "0.8.15.202606040825";
          }

          public String session() {
            return "BOOTSTRAP-1234567890abcdef1234567890abcdef-ordinary";
          }

          public byte[] executionDataWithoutReset() {
            calls.add("snapshot");
            return new byte[] {1, (byte) 0xc0, (byte) 0xc0, 0x10, 7};
          }
        };
    var checkpoint =
        new FixedNativeCoverageCheckpoint(profile, agent, (name, bytes) -> calls.add(name));
    var terminal = new FixedNativeCoverageTerminal(() -> Optional.of(checkpoint));
    assertTrue(terminal.terminal());
    calls.add("entry-return");
    assertTrue(terminal.closing());
    assertEquals(
        List.of(
            "snapshot", INV + ".terminal.exec", "entry-return", "snapshot", INV + ".closing.exec"),
        calls);
    assertThrows(IOException.class, terminal::terminal);
    assertThrows(IOException.class, terminal::closing);
    assertEquals(5, calls.size());
  }

  @Test
  void close743002NoAgentIsExplicitlyInactiveWithoutNativeIo() throws Exception {
    var terminal = new FixedNativeCoverageTerminal(Optional::empty);
    assertFalse(terminal.terminal());
    assertFalse(terminal.closing());
    for (var role : FixedNativeCoverageProfile.TerminalRole.values()) {
      var nativeDefault = new FixedNativeCoverageTerminal(role, null);
      assertFalse(nativeDefault.terminal());
      assertFalse(nativeDefault.closing());
    }
  }

  @Test
  void close743003BeforeTerminalFailureMissingAndRepeatedAttemptsNeverFallback() {
    assertThrows(
        IllegalArgumentException.class,
        () -> new FixedNativeCoverageTerminal((FixedNativeCoverageTerminal.Factory) null));
    assertThrows(IllegalArgumentException.class, () -> new FixedNativeCoverageTerminal(null, null));
    var early = new FixedNativeCoverageTerminal(Optional::empty);
    assertThrows(IOException.class, early::closing);
    assertThrows(IOException.class, early::closing);
    for (FixedNativeCoverageTerminal.Factory factory :
        List.<FixedNativeCoverageTerminal.Factory>of(
            () -> null,
            () -> {
              throw new IOException("PRIVATE");
            })) {
      var terminal = new FixedNativeCoverageTerminal(factory);
      assertThrows(IOException.class, terminal::terminal);
      assertThrows(IOException.class, terminal::terminal);
      assertThrows(IOException.class, terminal::closing);
    }
  }

  @Test
  void close743004ForeignThreadCannotConsumeOwnersAttempts() throws Exception {
    var terminal = new FixedNativeCoverageTerminal(Optional::empty);
    var failure = new AtomicReference<Throwable>();
    var foreign =
        new Thread(
            () -> {
              try {
                terminal.terminal();
              } catch (Throwable value) {
                failure.set(value);
              }
            });
    foreign.start();
    foreign.join(5000);
    assertFalse(foreign.isAlive());
    assertInstanceOf(IOException.class, failure.get());
    assertFalse(terminal.terminal());
    failure.set(null);
    var second =
        new Thread(
            () -> {
              try {
                terminal.closing();
              } catch (Throwable value) {
                failure.set(value);
              }
            });
    second.start();
    second.join(5000);
    assertFalse(second.isAlive());
    assertInstanceOf(IOException.class, failure.get());
    assertFalse(terminal.closing());
  }

  @Test
  void close743005CheckpointMustHaveNormallyCompletedTerminalAndCannotRetryClosing()
      throws Exception {
    var profile =
        FixedNativeCoverageProfile.parseTerminal(
                FixedNativeCoverageProfile.TerminalRole.BOOTSTRAP,
                INV,
                List.of(
                    "-javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=output=none,append=false,dumponexit=false,sessionid=BOOTSTRAP-1234567890abcdef1234567890abcdef-ordinary"))
            .orElseThrow();
    var agent =
        new FixedNativeCoverageCheckpoint.Agent() {
          public String version() {
            return "0.8.15.202606040825";
          }

          public String session() {
            return "BOOTSTRAP-1234567890abcdef1234567890abcdef-ordinary";
          }

          public byte[] executionDataWithoutReset() {
            return new byte[] {1, (byte) 0xc0, (byte) 0xc0, 0x10, 7};
          }
        };
    var writes = new ArrayList<String>();
    var early = new FixedNativeCoverageCheckpoint(profile, agent, (n, b) -> writes.add(n));
    assertThrows(
        IOException.class, () -> early.capture(FixedNativeCoverageCheckpoint.Point.CLOSING));
    early.capture(FixedNativeCoverageCheckpoint.Point.TERMINAL);
    assertThrows(
        IOException.class, () -> early.capture(FixedNativeCoverageCheckpoint.Point.CLOSING));
    assertEquals(List.of(INV + ".terminal.exec"), writes);
    var partial =
        new FixedNativeCoverageCheckpoint(
            profile,
            agent,
            (n, b) -> {
              throw new IOException("PRIVATE");
            });
    assertThrows(
        IOException.class, () -> partial.capture(FixedNativeCoverageCheckpoint.Point.TERMINAL));
    assertThrows(
        IOException.class, () -> partial.capture(FixedNativeCoverageCheckpoint.Point.CLOSING));
    var ordinary =
        FixedNativeCoverageProfile.parse(
                dev.codex.schubert.nk.storage.ServiceConfigFiles.Service.API,
                FixedNativeCoverageProfile.Phase.ORDINARY,
                INV,
                List.of(
                    "-javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=output=none,append=false,dumponexit=false,sessionid=API-1234567890abcdef1234567890abcdef-ordinary"))
            .orElseThrow();
    var foreignRole =
        new FixedNativeCoverageCheckpoint(ordinary, agent, (n, b) -> fail("no write"));
    assertThrows(
        IllegalArgumentException.class,
        () -> foreignRole.capture(FixedNativeCoverageCheckpoint.Point.CLOSING));
  }
}
