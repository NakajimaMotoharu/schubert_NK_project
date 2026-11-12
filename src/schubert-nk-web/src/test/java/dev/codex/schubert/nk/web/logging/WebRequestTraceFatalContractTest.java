package dev.codex.schubert.nk.web.logging;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.sql.SQLException;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import org.springframework.mock.web.MockHttpServletRequest;

/** OPS-TRACE-FATAL001..005; BUG2714/SS312351352: only public Servlet attribute fault callbacks. */
@Timeout(value = 5, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class WebRequestTraceFatalContractTest {
  @Test
  void fatal001ReadCauseRetainsExactErrorIdentity() {
    var fatal = new AssertionError("PUBLIC read fatal");
    var request = new FaultRequest(false, new IllegalArgumentException("PUBLIC read", fatal));
    assertSame(fatal, assertThrows(AssertionError.class, () -> WebRequestTrace.existing(request)));
  }

  @Test
  void fatal002WriteSuppressedSqlNextRetainsIdentityAndGraph() {
    var fatal = new AssertionError("PUBLIC write fatal");
    var next = new SQLException("PUBLIC next", fatal);
    var sql = new SQLException("PUBLIC SQL");
    sql.setNextException(next);
    var failure = new IllegalStateException("PUBLIC write");
    failure.addSuppressed(sql);
    var request = new FaultRequest(true, failure);
    assertSame(
        fatal,
        assertThrows(
            AssertionError.class, () -> WebRequestTrace.ensure(request, () -> new UUID(0, 21))));
    assertEquals(1, failure.getSuppressed().length);
    assertSame(sql, failure.getSuppressed()[0]);
    assertSame(next, sql.getNextException());
    assertSame(fatal, next.getCause());
  }

  @Test
  void fatal003NonfatalCyclesKeepOnlyFixedMetadataCatalog() {
    for (boolean write : new boolean[] {false, true}) {
      var failure = new IllegalStateException("PUBLIC cycle");
      var alias = new IllegalArgumentException("PUBLIC alias", failure);
      failure.initCause(alias);
      failure.addSuppressed(alias);
      alias.addSuppressed(failure);
      var request = new FaultRequest(write, failure);
      var observed =
          assertThrows(
              IllegalStateException.class,
              () -> {
                if (write) WebRequestTrace.ensure(request, () -> new UUID(0, 22));
                else WebRequestTrace.existing(request);
              });
      assertEquals("request audit metadata is unavailable", observed.getMessage());
      assertNull(observed.getCause());
      assertEquals(0, observed.getSuppressed().length);
      assertSame(alias, failure.getCause());
      assertSame(failure, alias.getCause());
    }
  }

  @Test
  void fatal004DirectReadAndWriteErrorAreNeverNormalized() {
    for (boolean write : new boolean[] {false, true}) {
      var fatal = new AssertionError("PUBLIC direct");
      var request = new FaultRequest(write, fatal);
      assertSame(
          fatal,
          assertThrows(
              AssertionError.class,
              () -> {
                if (write) WebRequestTrace.ensure(request, () -> new UUID(0, 23));
                else WebRequestTrace.existing(request);
              }));
    }
  }

  @Test
  void fatal005FailedReadCanRecoverWithoutAFalseMarkerOrLeakedScope() {
    var fatal = new AssertionError("PUBLIC recover");
    var request = new FaultRequest(false, new IllegalStateException("PUBLIC read", fatal));
    assertSame(
        fatal,
        assertThrows(
            AssertionError.class, () -> WebRequestTrace.ensure(request, () -> new UUID(0, 17))));
    request.enabled = false;
    var trace = WebRequestTrace.ensure(request, () -> new UUID(1, 17));
    assertEquals(new UUID(0, 17), trace.requestId());
    assertEquals(new UUID(1, 17), trace.eventId());
    assertFalse(trace.menuViewCandidate());
    var scope = trace.enter();
    try {
      WebRequestTrace.markMenuViewed();
    } finally {
      scope.close();
      scope.close();
    }
    assertTrue(trace.menuViewCandidate());
    assertSame(trace, WebRequestTrace.existing(request).orElseThrow());
    assertTrue(trace.claimCompletion());
    assertFalse(trace.claimCompletion());
    var other = WebRequestTrace.ensure(new MockHttpServletRequest(), () -> new UUID(2, 17));
    WebRequestTrace.markMenuViewed();
    assertFalse(other.menuViewCandidate());
  }

  private static final class FaultRequest extends MockHttpServletRequest {
    private final boolean write;
    private final Throwable failure;
    private boolean enabled = true;

    private FaultRequest(boolean write, Throwable failure) {
      this.write = write;
      this.failure = failure;
    }

    @Override
    public Object getAttribute(String name) {
      if (!write && enabled && name.equals(WebRequestTrace.class.getName())) fail();
      return super.getAttribute(name);
    }

    @Override
    public void setAttribute(String name, Object value) {
      if (write && enabled && name.equals(WebRequestTrace.class.getName())) fail();
      super.setAttribute(name, value);
    }

    private void fail() {
      if (failure instanceof Error fatal) throw fatal;
      throw (RuntimeException) failure;
    }
  }
}
