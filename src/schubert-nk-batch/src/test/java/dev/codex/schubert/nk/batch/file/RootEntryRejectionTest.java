package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.batch.platform.RootContextNoIoFixture;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** PT-ROOTGUARD-001..003: literal negative results and zero native effects, not startup grants. */
final class RootEntryRejectionTest {
  private static final List<RootStartupContext.Service> NON_SERVICE =
      List.of(
          RootStartupContext.Service.MORNING,
          RootStartupContext.Service.CLEANUP,
          RootStartupContext.Service.EXPIRY);

  @Test
  void guard001SetprivRejectsEveryNonServiceRoleBeforeAnyIo() {
    for (var role : NON_SERVICE) {
      var fixture = new RootContextNoIoFixture();
      var work = new AtomicInteger();
      var failure =
          assertThrows(
              StorageIoException.class,
              () ->
                  RootServiceExecutableAdmission.withSetpriv(
                      fixture.context(),
                      RootServiceProofTest.self(role),
                      path -> work.incrementAndGet()));
      unavailable(failure);
      assertEquals(0, fixture.calls());
      assertEquals(0, work.get());
    }
  }

  @Test
  void guard002ObserveRejectsEveryNonServiceRoleBeforeAnyIo() throws Exception {
    var issued = RootServiceProofTest.issued();
    for (var role : NON_SERVICE) {
      var fixture = new RootContextNoIoFixture();
      unavailable(
          assertThrows(
              StorageIoException.class,
              () ->
                  RootStartupPending.observe(
                      fixture.context(), RootServiceProofTest.self(role), issued)));
      assertEquals(0, fixture.calls());
    }
  }

  @Test
  void guard003AllNativeEntryNullContractsPrecedeIoAndCallbacks() throws Exception {
    var fixture = new RootContextNoIoFixture();
    var root = fixture.context();
    var self = RootServiceProofTest.self(RootStartupContext.Service.API);
    var issued = RootServiceProofTest.issued();
    var owner =
        MaintenanceOwnerFrame.consume(StartupLaunchRecordTest.bytes(StartupLaunchFilesTest.OWNER));
    var work = new AtomicInteger();
    RootServiceExecutableAdmission.Work action = path -> work.incrementAndGet();
    for (int index = 0; index < 3; index++) {
      int absent = index;
      assertThrows(
          NullPointerException.class,
          () ->
              RootServiceExecutableAdmission.withSetpriv(
                  absent == 0 ? null : root,
                  absent == 1 ? null : self,
                  absent == 2 ? null : action));
      assertThrows(
          NullPointerException.class,
          () ->
              RootStartupPending.observe(
                  absent == 0 ? null : root,
                  absent == 1 ? null : self,
                  absent == 2 ? null : issued));
    }
    var security = RootServiceExecutableAdmissionTest.security(new byte[0]);
    RootServiceExecutableAdmission.Capability caps = path -> work.incrementAndGet();
    for (int index = 0; index < 4; index++) {
      int absent = index;
      assertThrows(
          NullPointerException.class,
          () ->
              RootStartupPending.awaitLaunch(
                  absent == 0 ? null : root, absent == 1 ? null : self,
                  absent == 2 ? null : issued, absent == 3 ? null : owner));
      assertThrows(
          NullPointerException.class,
          () ->
              RootServiceExecutableAdmission.admit(
                  absent == 0 ? null : RootServiceExecutableAdmissionTest.HELD,
                      absent == 1 ? null : "a".repeat(64),
                  absent == 2 ? null : security, absent == 3 ? null : caps));
    }
    assertEquals(0, fixture.calls());
    assertEquals(0, work.get());
  }

  private static void unavailable(StorageIoException failure) {
    assertEquals(StorageIoException.Reason.UNAVAILABLE, failure.reason());
    assertEquals("transfer storage operation failed", failure.getMessage());
    assertNull(failure.getCause());
  }

  /** PT-ROOTGUARD-004 / SSC308: primitive319 is outside Integer's mandated cache. */
  @Test
  void guard004RootDescriptorPreallocatesAndPreservesPrimitiveFailureOwnership() throws Exception {
    var calls = new RootCalls();
    int actual =
        dev.codex.schubert.nk.storage.ResourceScope.acquire(
            () -> new RootServiceExecutableAdmission.RootDescriptor(calls),
            RootServiceExecutableAdmission.RootDescriptor::close,
            owned -> owned.descriptor);
    assertEquals(319, actual);
    assertEquals(1, calls.opens);
    assertEquals(1, calls.closes);
    assertEquals(319, calls.closedDescriptor);
    var bad = new RootCalls();
    bad.value = -1;
    unavailable(
        assertThrows(
            StorageIoException.class,
            () -> new RootServiceExecutableAdmission.RootDescriptor(bad)));
    assertEquals(1, bad.opens);
    assertEquals(0, bad.closes);
    var failed = new RootCalls();
    var failure = new StorageIoException(StorageIoException.Reason.MISSING);
    failed.failure = failure;
    assertSame(
        failure,
        assertThrows(
            StorageIoException.class,
            () -> new RootServiceExecutableAdmission.RootDescriptor(failed)));
    assertEquals(1, failed.opens);
    assertEquals(0, failed.closes);
    assertThrows(
        NullPointerException.class, () -> new RootServiceExecutableAdmission.RootDescriptor(null));
  }

  private static final class RootCalls implements dev.codex.schubert.nk.storage.DirectoryCalls {
    private int value = 319;
    private int opens;
    private int closes;
    private int closedDescriptor = -1;
    private @org.jspecify.annotations.Nullable StorageIoException failure;

    @Override
    public int openRoot() throws StorageIoException {
      opens++;
      if (failure != null) throw failure;
      return value;
    }

    @Override
    public void close(int descriptor) {
      closes++;
      closedDescriptor = descriptor;
    }

    @Override
    public int openDirectory(int parent, String name) {
      throw new AssertionError("unexpected traversal");
    }

    @Override
    public int openEntry(int parent, String name) {
      throw new AssertionError("unexpected entry");
    }

    @Override
    public int createFile(int parent, String name) {
      throw new AssertionError("unexpected create");
    }

    @Override
    public void createDirectory(int parent, String name) {
      throw new AssertionError("unexpected create");
    }

    @Override
    public void publish(int parent, String part, String ready) {
      throw new AssertionError("unexpected publish");
    }

    @Override
    public void unlink(int parent, String name) {
      throw new AssertionError("unexpected unlink");
    }

    @Override
    public void sync(int parent) {
      throw new AssertionError("unexpected sync");
    }
  }
}
