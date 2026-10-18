package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.*;

import java.io.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** NK-OPS-001/OPS009/UI251/SS343/SSC308; QUERYOWN001..006; independent literal oracles. */
final class ProcessResourceScopeTest {
  @Test
  void queryown001LiteralTwentyFourFailurePriorityRows() throws Exception {
    // Rows: normal/IO/interruption/known-stop/runtime/error; columns: normal/stop/runtime/error.
    String[] winner = {"Ncre", "bbce", "bbce", "bbce", "bbbb", "bbbb"};
    // c/e in unknown columns select the cleanup instance, never a new normalized exception.
    for (boolean legacy : List.of(false, true)) {
      for (int row = 0; row < 6; row++) {
        for (int column = 0; column < 4; column++) {
          Throwable body = failure(row);
          Throwable cleanup = cleanup(column);
          Object owned = new Object();
          var calls = new ArrayList<String>();
          try {
            Throwable actual = null;
            try {
              if (legacy) {
                ProcessResourceScope.use(
                    () -> {
                      calls.add("release");
                      raiseUnchecked(cleanup);
                    },
                    () -> {
                      calls.add("body");
                      raise(body);
                    });
              } else
                ProcessResourceScope.acquire(
                    () -> {
                      calls.add("factory");
                      return owned;
                    },
                    resource -> {
                      assertSame(owned, resource);
                      calls.add("release");
                      raiseUnchecked(cleanup);
                    },
                    resource -> {
                      assertSame(owned, resource);
                      calls.add("body");
                      raise(body);
                    });
            } catch (IOException | InterruptedException | RuntimeException | Error observed) {
              actual = observed;
            }
            assertEquals(
                legacy ? List.of("body", "release") : List.of("factory", "body", "release"), calls);
            char expected = winner[row].charAt(column);
            if (expected == 'N') assertNull(actual);
            else {
              assertSame(expected == 'b' ? body : cleanup, actual);
              int secondary = row != 0 && column != 0 && expected == 'b' ? 1 : 0;
              assertEquals(secondary, actual.getSuppressed().length);
              if (secondary == 1) fixedSecondary(actual.getSuppressed()[0]);
            }
            assertEquals(row == 2 && column >= 2, Thread.currentThread().isInterrupted());
          } finally {
            Thread.interrupted();
          }
        }
      }
    }
  }

  @Test
  void queryown002FactoryAndNullBoundariesNeverReleaseUnownedResource() throws Exception {
    var calls = new AtomicInteger();
    for (Throwable factory :
        List.of(
            new IOException("private factory"),
            new IllegalStateException("private factory"),
            new AssertionError("private factory"))) {
      Throwable actual =
          assertThrows(
              Throwable.class,
              () ->
                  ProcessResourceScope.acquire(
                      () -> {
                        if (factory instanceof IOException io) throw io;
                        raiseUnchecked(factory);
                        return new Object();
                      },
                      resource -> calls.incrementAndGet(),
                      resource -> calls.incrementAndGet()));
      assertSame(factory, actual);
      assertEquals(0, actual.getSuppressed().length);
    }
    assertThrows(
        NullPointerException.class,
        () ->
            ProcessResourceScope.acquire(
                null, resource -> calls.incrementAndGet(), resource -> calls.incrementAndGet()));
    assertThrows(
        NullPointerException.class,
        () ->
            ProcessResourceScope.acquire(
                () -> {
                  calls.incrementAndGet();
                  return new Object();
                },
                null,
                resource -> calls.incrementAndGet()));
    assertThrows(
        NullPointerException.class,
        () ->
            ProcessResourceScope.acquire(
                () -> {
                  calls.incrementAndGet();
                  return new Object();
                },
                resource -> calls.incrementAndGet(),
                null));
    assertThrows(
        NullPointerException.class,
        () ->
            ProcessResourceScope.acquire(
                () -> null,
                resource -> calls.incrementAndGet(),
                resource -> calls.incrementAndGet()));
    assertEquals(0, calls.get());
  }

  @Test
  void queryown003SharedAndPreexistingExceptionsKeepIdentityWithoutSelfSuppression() {
    var same = new IllegalStateException("private existing");
    var original = new IOException("private secondary");
    same.addSuppressed(original);
    for (int count = 1; count <= 3; count++) {
      assertSame(
          same,
          assertThrows(
              IllegalStateException.class,
              () ->
                  ProcessResourceScope.acquire(
                      Object::new,
                      resource -> {
                        throw same;
                      },
                      resource -> {
                        throw same;
                      })));
      assertSame(original, same.getSuppressed()[0]);
      assertEquals(count + 1, same.getSuppressed().length);
      for (int i = 1; i <= count; i++) fixedSecondary(same.getSuppressed()[i]);
    }
  }

  @Test
  void queryown004ParallelScopesRetainDistinctOwnersAndReverseNestedRelease() throws Exception {
    var entered = new CountDownLatch(2);
    var leave = new CountDownLatch(1);
    List<FutureTask<List<String>>> tasks = new ArrayList<>();
    List<Thread> threads = new ArrayList<>();
    try {
      for (String identity : List.of("left", "right")) {
        var task =
            new FutureTask<List<String>>(
                () -> {
                  List<String> order = new ArrayList<>();
                  ProcessResourceScope.acquire(
                      () -> identity,
                      resource -> order.add(resource + " outer"),
                      outer ->
                          ProcessResourceScope.acquire(
                              () -> outer + " inner",
                              order::add,
                              inner -> {
                                assertEquals(identity + " inner", inner);
                                entered.countDown();
                                assertTrue(leave.await(5, TimeUnit.SECONDS));
                              }));
                  return order;
                });
        tasks.add(task);
        threads.add(Thread.startVirtualThread(task));
      }
      assertTrue(entered.await(5, TimeUnit.SECONDS));
      leave.countDown();
      assertEquals(List.of("left inner", "left outer"), tasks.get(0).get(5, TimeUnit.SECONDS));
      assertEquals(List.of("right inner", "right outer"), tasks.get(1).get(5, TimeUnit.SECONDS));
    } finally {
      leave.countDown();
      for (Thread thread : threads) {
        thread.interrupt();
        thread.join(5000);
        assertFalse(thread.isAlive());
      }
    }
  }

  @Test
  void queryown005SystemctlDefersNullButOwnsEveryPriorGetter() {
    for (int index = 0; index < 3; index++) {
      for (boolean missing : List.of(false, true)) {
        var child = new Child(index, missing);
        Throwable actual =
            assertThrows(
                Throwable.class,
                () -> new SystemctlStateSource(command -> child).read(ApplicationUnit.API));
        if (missing) assertInstanceOf(NullPointerException.class, actual);
        else assertSame(child.fault, actual);
        assertEquals(missing ? 3 : index + 1, child.getters);
        assertEquals(1, child.destroyed);
        assertEquals(0, child.waits);
        for (int i = 0; i < 3; i++)
          assertEquals((missing ? i != index : i < index) ? 1 : 0, child.closes[i]);
      }
    }
  }

  @Test
  void queryown006InspectorRejectsEachMissingGetterBeforeNextInBothModes() {
    for (boolean streaming : List.of(false, true)) {
      for (int index = 0; index < 3; index++) {
        for (boolean missing : List.of(false, true)) {
          var child = new Child(index, missing);
          var reader = new InspectorUnitProbe.NativeReader(command -> child);
          Throwable actual =
              assertThrows(
                  Throwable.class,
                  () -> {
                    if (streaming)
                      reader.executeStreaming(
                          List.of("fixed fixture"), 8, TimeUnit.SECONDS.toNanos(5));
                    else reader.execute(List.of("fixed fixture"), 8);
                  });
          if (missing) assertInstanceOf(NullPointerException.class, actual);
          else assertSame(child.fault, actual);
          assertEquals(index + 1, child.getters);
          assertEquals(1, child.destroyed);
          assertEquals(0, child.waits);
          for (int i = 0; i < 3; i++) assertEquals(i < index ? 1 : 0, child.closes[i]);
        }
      }
      var reader = new InspectorUnitProbe.NativeReader(command -> null);
      assertThrows(
          NullPointerException.class,
          () -> {
            if (streaming)
              reader.executeStreaming(List.of("fixed fixture"), 8, TimeUnit.SECONDS.toNanos(5));
            else reader.execute(List.of("fixed fixture"), 8);
          });
    }
  }

  private static Throwable failure(int index) {
    return switch (index) {
      case 0 -> null;
      case 1 -> new IOException("private body");
      case 2 -> new InterruptedException("private body");
      case 3 -> new StopGateException(StopGateFailure.TIMEOUT);
      case 4 -> new IllegalStateException("private body");
      case 5 -> new AssertionError("private body");
      default -> throw new AssertionError(index);
    };
  }

  private static Throwable cleanup(int index) {
    return switch (index) {
      case 0 -> null;
      case 1 -> new StopGateException(StopGateFailure.COMMAND_FAILURE);
      case 2 -> new IllegalArgumentException("private cleanup");
      case 3 -> new AssertionError("private cleanup");
      default -> throw new AssertionError(index);
    };
  }

  private static void raise(Throwable failure) throws IOException, InterruptedException {
    if (failure instanceof IOException io) throw io;
    if (failure instanceof InterruptedException interruption) throw interruption;
    raiseUnchecked(failure);
  }

  private static void raiseUnchecked(Throwable failure) {
    if (failure instanceof RuntimeException runtime) throw runtime;
    if (failure instanceof Error error) throw error;
  }

  private static void fixedSecondary(Throwable failure) {
    var fixed = assertInstanceOf(StopGateException.class, failure);
    assertEquals(StopGateFailure.COMMAND_FAILURE, fixed.reason());
    assertEquals("application stop check failed", fixed.getMessage());
    assertNull(fixed.getCause());
    assertEquals(0, fixed.getSuppressed().length);
  }

  private static final class Child extends Process {
    final int failing;
    final boolean missing;
    final int[] closes = new int[3];
    final IllegalStateException fault = new IllegalStateException("private getter");
    int getters, destroyed, waits;

    Child(int failing, boolean missing) {
      this.failing = failing;
      this.missing = missing;
    }

    private boolean absent(int index) {
      getters++;
      if (index != failing) return false;
      if (!missing) throw fault;
      return true;
    }

    @Override
    public InputStream getInputStream() {
      if (absent(0)) return null;
      return new ByteArrayInputStream(new byte[0]) {
        @Override
        public void close() {
          closes[0]++;
        }
      };
    }

    @Override
    public OutputStream getOutputStream() {
      if (absent(1)) return null;
      return new ByteArrayOutputStream() {
        @Override
        public void close() {
          closes[1]++;
        }
      };
    }

    @Override
    public InputStream getErrorStream() {
      if (absent(2)) return null;
      return new ByteArrayInputStream(new byte[0]) {
        @Override
        public void close() {
          closes[2]++;
        }
      };
    }

    @Override
    public boolean isAlive() {
      return destroyed == 0;
    }

    @Override
    public void destroy() {
      destroyed++;
    }

    @Override
    public int waitFor() {
      throw new AssertionError("no unbounded wait");
    }

    @Override
    public boolean waitFor(long timeout, TimeUnit unit) {
      waits++;
      throw new AssertionError("no wait after getter failure");
    }

    @Override
    public int exitValue() {
      throw new AssertionError("no exit read after getter failure");
    }
  }
}
