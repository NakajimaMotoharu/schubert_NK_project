package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.InputStream;
import java.io.OutputStream;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;

/** PT-OPS-INBOX-OWNER001..006: independent process port, no child or service is started. */
final class InspectorChildOwnerTest {
  @AfterEach
  void clearOwnInterrupt() {
    Thread.interrupted();
  }

  @Test
  void deadChildNeedsNoTerminationRequest() throws Exception {
    var child = new Child(false, true, false);
    InspectorDeploymentTest.finishOwnedChild(child);
    assertEquals(0, child.destroyCalls);
    assertEquals(0, child.waitCalls);
  }

  @Test
  void liveChildRequiresOneTermAndFiniteConfirmedWait() throws Exception {
    var child = new Child(true, true, false);
    InspectorDeploymentTest.finishOwnedChild(child);
    assertEquals(1, child.destroyCalls);
    assertEquals(1, child.waitCalls);
    assertFalse(Thread.currentThread().isInterrupted());
  }

  @Test
  void unconfirmedTerminationIsAnAssertionFailure() {
    var child = new Child(true, false, false);
    var failure =
        assertThrows(AssertionError.class, () -> InspectorDeploymentTest.finishOwnedChild(child));
    assertTrue(failure.getMessage().startsWith("owned tool termination unconfirmed"));
    assertEquals(1, child.destroyCalls);
    assertEquals(1, child.waitCalls);
  }

  @Test
  void callerInterruptIsPreservedAfterActualWait() throws Exception {
    var child = new Child(true, true, false);
    Thread.currentThread().interrupt();
    InspectorDeploymentTest.finishOwnedChild(child);
    assertTrue(Thread.currentThread().isInterrupted());
    assertEquals(1, child.destroyCalls);
    assertEquals(1, child.waitCalls);
  }

  @Test
  void newInterruptRemainsUnconfirmedAndRestoresNotification() {
    var child = new Child(true, false, true);
    assertThrows(InterruptedException.class, () -> InspectorDeploymentTest.finishOwnedChild(child));
    assertTrue(Thread.currentThread().isInterrupted());
    assertEquals(1, child.destroyCalls);
    assertEquals(1, child.waitCalls);
  }

  @Test
  void failedTermPreservesCallerInterruptAndDoesNotClaimJoin() {
    var child = new Child(true, true, false);
    var failure = new IllegalStateException("synthetic termination failure");
    child.termFailure = failure;
    Thread.currentThread().interrupt();
    assertSame(
        failure,
        assertThrows(
            IllegalStateException.class, () -> InspectorDeploymentTest.finishOwnedChild(child)));
    assertTrue(Thread.currentThread().isInterrupted());
    assertEquals(1, child.destroyCalls);
    assertEquals(0, child.waitCalls);
  }

  private static final class Child extends Process {
    private final boolean alive;
    private final boolean terminationConfirmed;
    private final boolean interruptWait;
    private int destroyCalls;
    private int waitCalls;
    private RuntimeException termFailure;

    private Child(boolean alive, boolean terminationConfirmed, boolean interruptWait) {
      this.alive = alive;
      this.terminationConfirmed = terminationConfirmed;
      this.interruptWait = interruptWait;
    }

    @Override
    public boolean isAlive() {
      return alive;
    }

    @Override
    public void destroy() {
      destroyCalls++;
      if (termFailure != null) throw termFailure;
    }

    @Override
    public boolean waitFor(long timeout, TimeUnit unit) throws InterruptedException {
      waitCalls++;
      assertEquals(10, timeout);
      assertEquals(TimeUnit.SECONDS, unit);
      assertFalse(Thread.currentThread().isInterrupted());
      if (interruptWait) throw new InterruptedException("synthetic interrupt");
      return terminationConfirmed;
    }

    @Override
    public int waitFor() {
      throw new AssertionError("unbounded wait forbidden");
    }

    @Override
    public int exitValue() {
      throw new AssertionError("exit status does not establish termination here");
    }

    @Override
    public OutputStream getOutputStream() {
      throw new AssertionError("process stream not part of termination contract");
    }

    @Override
    public InputStream getInputStream() {
      throw new AssertionError("process stream not part of termination contract");
    }

    @Override
    public InputStream getErrorStream() {
      throw new AssertionError("process stream not part of termination contract");
    }
  }
}
