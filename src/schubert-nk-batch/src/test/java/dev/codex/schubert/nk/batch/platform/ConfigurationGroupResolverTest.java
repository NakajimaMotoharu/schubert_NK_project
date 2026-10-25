package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collections;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeSet;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** OPS-009/UI251/SS343 6.12; PG-D-155; GID001..008; only synthetic opaque group fields persist. */
final class ConfigurationGroupResolverTest {
  private static final List<String> COMMAND = List.of("/usr/bin/getent", "group", "schubert");
  private static final byte[] RECORD = ascii("schubert:x:2000:member\n");

  @Test
  void canonicalByteBoundaries() throws Exception {
    for (String line : List.of("schubert::1:\n", "schubert:x:4294967295:member\n")) {
      var child = new Child(ascii(line));
      assertEquals(line.contains("4294967295") ? 4294967295L : 1, resolver(child).resolve());
      child.closedAndCleared();
    }
    byte[] largest = ascii("schubert::2000:" + "m".repeat(65520) + "\n");
    assertEquals(65536, largest.length);
    var child = new Child(largest);
    assertEquals(2000, resolver(child).resolve());
    child.closedAndCleared();
    byte[] opaque = ascii("schubert:x:2000:mm\n");
    opaque[9] = (byte) 0xff;
    opaque[opaque.length - 2] = (byte) 0x80;
    child = new Child(opaque);
    assertEquals(2000, resolver(child).resolve());
    child.closedAndCleared();
  }

  @Test
  void malformedAndNull() throws Exception {
    // BUG-154: retain sufficient length so the LF guard, not the size guard, rejects this input.
    byte[] noLf = ascii("schubert:x:2000:member");
    failure(() -> ConfigurationGroupResolver.parse(noLf, noLf.length));
    for (String line :
        List.of(
            "",
            "schubert::1:",
            "schubert::1:\r\n",
            "schubert::1:\n\n",
            "other::2000:\n",
            "Schubert::2000:\n",
            "schubert:2000:\n",
            "schubert::2000::\n",
            "schubert:::member\n",
            "schubert::0:\n",
            "schubert::01:\n",
            "schubert::-1:\n",
            "schubert::+1:\n",
            "schubert:: 1:\n",
            "schubert::1 :\n",
            "schubert::4294967296:\n",
            "schubert::9999999999:\n",
            "schubert::10000000000:\n",
            "schubert::a:\n")) {
      byte[] bytes = ascii(line);
      failure(() -> ConfigurationGroupResolver.parse(bytes, bytes.length));
    }
    for (int value : new int[] {0, 1, 9, 10, 13, 31, 127}) {
      byte[] bytes = RECORD.clone();
      bytes[9] = (byte) value;
      failure(() -> ConfigurationGroupResolver.parse(bytes, bytes.length));
    }
    for (int value : new int[] {'/', ':', ';', 128, 255}) {
      byte[] bytes = RECORD.clone();
      bytes[11] = (byte) value;
      failure(() -> ConfigurationGroupResolver.parse(bytes, bytes.length));
    }
    for (int size : new int[] {-1, 0, 12, RECORD.length + 1, 65537})
      failure(() -> ConfigurationGroupResolver.parse(RECORD, size));
    assertThrows(NullPointerException.class, () -> ConfigurationGroupResolver.parse(null, 13));
    assertThrows(NullPointerException.class, () -> new ConfigurationGroupResolver(null));
    byte[] longRecord = ascii("schubert::2000:" + "m".repeat(65521) + "\n");
    var child = new Child(longRecord);
    failure(() -> resolver(child).resolve());
    child.closedAndCleared();
  }

  @Test
  void ownedCommandAndExit() throws Exception {
    var child = new Child(RECORD);
    assertEquals(2000, resolver(child).resolve());
    assertEquals(List.of("getOutput", "getInput", "getError"), child.events.subList(0, 3));
    assertEquals(2, Collections.frequency(child.events, "read"));
    assertEquals(1, Collections.frequency(child.events, "wait"));
    assertEquals(1, Collections.frequency(child.events, "exit"));
    assertTrue(child.events.lastIndexOf("read") < child.events.indexOf("closeError"));
    assertEquals(
        List.of("closeError", "closeInput", "closeOutput", "alive"),
        child.events.subList(child.events.size() - 4, child.events.size()));
    assertEquals(65537, child.maximum);
    child.closedAndCleared();
    for (int exit : new int[] {-1, 1, 2, 3, 70}) {
      child = new Child(RECORD);
      child.exit = exit;
      Child failed = child;
      failure(() -> resolver(failed).resolve());
      // A failed command can already have produced bytes; all are drained/cleared, never parsed.
      child.closedAndCleared();
    }
    failure(
        () ->
            new ConfigurationGroupResolver(
                    command -> {
                      throw new IOException("synthetic private start");
                    })
                .resolve());
    assertThrows(
        NullPointerException.class,
        () -> new ConfigurationGroupResolver(command -> null).resolve());
  }

  @Test
  void timeoutInterruptAndTermination() throws Exception {
    for (String mode : List.of("timeout", "interrupt")) {
      var child = new Child(RECORD);
      child.mode = mode;
      child.alive = true;
      try {
        failure(() -> resolver(child).resolve());
        assertEquals(mode.equals("interrupt"), Thread.currentThread().isInterrupted());
        assertEquals(1, child.destroyed);
        assertEquals(0, child.forceDestroyed);
        child.closedAndCleared();
      } finally {
        Thread.interrupted();
      }
    }
    var child = new Child(RECORD);
    Thread.currentThread().interrupt();
    Child early = child;
    try {
      failure(() -> resolver(early).resolve());
      assertTrue(Thread.currentThread().isInterrupted());
      assertTrue(child.events.isEmpty());
    } finally {
      Thread.interrupted();
    }
    child = new Child(RECORD);
    child.interruptClose = true;
    Child late = child;
    try {
      failure(() -> resolver(late).resolve());
      assertTrue(Thread.currentThread().isInterrupted());
      child.closedAndCleared();
    } finally {
      Thread.interrupted();
    }
  }

  @Test
  void stdioFailureMatrix() throws Exception {
    // PG174/SSC063/BUG195/YKT154: private IO scope keeps the existing Future oracle.
    for (String scope : List.of("closeOutput", "closeInput", "closeError", "destroy"))
      for (String primary :
          List.of("runtime", "read", "timeout", "interrupt", "exit", "oversize", "success"))
        for (Throwable unknown :
            List.of(
                new IllegalStateException("synthetic compound"),
                new NullPointerException("synthetic compound"),
                new AssertionError("synthetic compound"))) {
          var child = new Child(primary.equals("oversize") ? new byte[65537] : RECORD);
          child.alive = true;
          int[] injected = {0};
          child.compound =
              name -> {
                if (name.equals(scope)) {
                  injected[0]++;
                  throwUnknown(unknown);
                }
                if (name.equals("wait") && primary.equals("runtime")) throwUnknown(unknown);
              };
          if (primary.equals("exit")) child.exit = 2;
          if (primary.equals("timeout") || primary.equals("interrupt")) child.mode = primary;
          if (primary.equals("read")) child.readBehavior = "exception";
          try {
            Throwable actual = assertThrows(unknown.getClass(), () -> resolver(child).resolve());
            assertSame(unknown, actual);
            assertEquals(primary.equals("runtime") ? 1 : 0, actual.getSuppressed().length);
            if (primary.equals("runtime")) {
              var fixed = assertInstanceOf(IOException.class, actual.getSuppressed()[0]);
              assertEquals("configuration group lookup failed", fixed.getMessage());
              assertNull(fixed.getCause());
              assertEquals(0, fixed.getSuppressed().length);
            }
            assertEquals(1, injected[0]);
            assertEquals(1, child.destroyed);
            assertEquals(0, child.forceDestroyed);
            assertTrue(child.events.contains("wait"));
            assertEquals(primary.equals("interrupt"), Thread.currentThread().isInterrupted());
            child.closedAndCleared();
            assertArrayEquals(primary.equals("oversize") ? new byte[65537] : RECORD, child.record);
          } finally {
            Thread.interrupted();
          }
        }
    for (String getter : List.of("getOutput", "getInput", "getError")) {
      var child = new Child(RECORD);
      child.getFailure = getter;
      child.alive = true;
      assertSame(
          child.runtime,
          assertThrows(IllegalStateException.class, () -> resolver(child).resolve()));
      assertEquals(getter.equals("getOutput") ? 0 : 1, child.outputClosed);
      assertEquals(getter.equals("getError") ? 1 : 0, child.inputClosed);
      assertEquals(0, child.errorClosed);
      assertEquals(1, child.destroyed);
    }
    for (String missing : List.of("getOutput", "getInput", "getError")) {
      var child = new Child(RECORD);
      child.nullGetter = missing;
      assertThrows(NullPointerException.class, () -> resolver(child).resolve());
      assertEquals(missing.equals("getOutput") ? 0 : 1, child.outputClosed);
      assertEquals(missing.equals("getInput") ? 0 : 1, child.inputClosed);
      assertEquals(missing.equals("getError") ? 0 : 1, child.errorClosed);
    }
    for (String close : List.of("closeOutput", "closeInput", "closeError", "all"))
      for (String primary :
          List.of("success", "exit", "timeout", "interrupt", "read", "oversize")) {
        var child = new Child(primary.equals("oversize") ? new byte[65537] : RECORD);
        child.closeFailure = close;
        if (primary.equals("exit")) child.exit = 2;
        if (primary.equals("timeout") || primary.equals("interrupt")) {
          child.mode = primary;
          child.alive = true;
        }
        if (primary.equals("read")) child.readBehavior = "exception";
        try {
          failure(() -> resolver(child).resolve());
          child.closedAndCleared();
        } finally {
          Thread.interrupted();
        }
      }
    for (String point : List.of("wait", "exit", "closeOutput")) {
      var child = new Child(RECORD);
      child.runtimeAt = point;
      assertSame(
          child.runtime,
          assertThrows(IllegalStateException.class, () -> resolver(child).resolve()));
      child.closedAndCleared();
    }
    var programming = new Child(RECORD);
    programming.runtimeAt = "read";
    var rejected = assertThrows(IllegalStateException.class, () -> resolver(programming).resolve());
    assertEquals("configuration group reader failed", rejected.getMessage());
    assertNull(rejected.getCause());
    assertEquals(0, rejected.getSuppressed().length);
    programming.closedAndCleared();
    var fatal = new Child(RECORD);
    fatal.readBehavior = "error";
    assertSame(fatal.fatal, assertThrows(AssertionError.class, () -> resolver(fatal).resolve()));
    fatal.closedAndCleared();
  }

  @Test
  void sourceBufferAndNoLeak() throws Exception {
    for (String mode : List.of("zero", "negative", "overflow", "exception")) {
      var child = new Child(RECORD);
      child.readBehavior = mode;
      failure(() -> resolver(child).resolve());
      child.closedAndCleared();
    }
    for (int chunk : new int[] {1, 7, 13, 65536}) {
      var child = new Child(RECORD);
      child.chunk = chunk;
      assertEquals(2000, resolver(child).resolve());
      child.closedAndCleared();
    }
    var child = new Child(ascii("schubert:synthetic-opaque:2000:synthetic-member\n"));
    child.closeFailure = "all";
    failure(() -> resolver(child).resolve());
    child.closedAndCleared();
  }

  @Test
  void concurrentLookup() throws Exception {
    var children = new ConcurrentLinkedQueue<Child>();
    var counter = new AtomicInteger();
    var resolver =
        new ConfigurationGroupResolver(
            command -> {
              assertEquals(COMMAND, command);
              var child = new Child(ascii("schubert:x:" + counter.incrementAndGet() + ":\n"));
              children.add(child);
              return child;
            });
    try (var executor = Executors.newFixedThreadPool(8)) {
      var futures = new ArrayList<Future<Long>>();
      for (int i = 0; i < 64; i++) futures.add(executor.submit(resolver::resolve));
      var actual = new TreeSet<Long>();
      for (var future : futures) actual.add(future.get(5, TimeUnit.SECONDS));
      var expected = new TreeSet<Long>();
      for (long i = 1; i <= 64; i++) expected.add(i);
      assertEquals(expected, actual);
      assertEquals(64, children.size());
      children.forEach(Child::closedAndCleared);
    }
  }

  @Test
  void nativeFactory() throws Exception {
    // BUG-155: reduce the isolated child's pipe capacity, without altering the host/group.
    var producer =
        new ProcessBuilder(
                "/usr/bin/python3",
                "-c",
                "import os,fcntl; fcntl.fcntl(1,fcntl.F_SETPIPE_SZ,4096); "
                    + "os.write(1,b'schubert::2000:'+b'm'*65520+b'\\n')")
            .redirectError(ProcessBuilder.Redirect.DISCARD)
            .start();
    assertEquals(2000, new ConfigurationGroupResolver(command -> producer).resolve());
    assertFalse(producer.isAlive());
    for (String body :
        List.of(
            "os.write(1,b'schubert::2000:'+b'm'*65521+b'\\n')",
            "os.write(1,b'schubert::2000:'+b'm'*65520+b'\\n'); sys.exit(3)",
            "os.write(1,b'schubert:x:'); time.sleep(60)")) {
      var rejected = producer(body);
      failure(() -> new ConfigurationGroupResolver(command -> rejected).resolve());
      assertTrue(rejected.waitFor(5, TimeUnit.SECONDS));
      assertFalse(rejected.isAlive());
    }
    var interrupted = producer("os.write(1,b'schubert:x:'); time.sleep(60)");
    var admitted = new CountDownLatch(1);
    var outcome = new AtomicReference<Throwable>();
    var worker =
        new Thread(
            () -> {
              try {
                failure(
                    () ->
                        new ConfigurationGroupResolver(
                                command -> {
                                  admitted.countDown();
                                  return interrupted;
                                })
                            .resolve());
                assertTrue(Thread.currentThread().isInterrupted());
              } catch (Throwable failure) {
                outcome.set(failure);
              }
            });
    worker.start();
    assertTrue(admitted.await(5, TimeUnit.SECONDS));
    worker.interrupt();
    assertTrue(worker.join(java.time.Duration.ofSeconds(10)));
    assertNull(outcome.get());
    assertTrue(interrupted.waitFor(5, TimeUnit.SECONDS));
    assertFalse(interrupted.isAlive());
    var builder = ConfigurationGroupResolver.NativeProcess.builder(COMMAND);
    assertEquals(COMMAND, builder.command());
    assertEquals(
        Map.of("PATH", "/usr/bin:/bin", "LANG", "C", "LC_ALL", "C"), builder.environment());
    assertEquals(ProcessBuilder.Redirect.DISCARD, builder.redirectError());
    // This PG/PT host intentionally has no deployed schubert group (getent exit2, 2026-09-12).
    // Not a claim that a root-deployed production lookup has succeeded.
    failure(() -> new ConfigurationGroupResolver().resolve());
  }

  private static Process producer(String body) throws IOException {
    return new ProcessBuilder(
            "/usr/bin/python3",
            "-c",
            "import os,fcntl,time,sys; fcntl.fcntl(1,fcntl.F_SETPIPE_SZ,4096); " + body)
        .redirectError(ProcessBuilder.Redirect.DISCARD)
        .start();
  }

  private static byte[] ascii(String text) {
    return text.getBytes(StandardCharsets.US_ASCII);
  }

  private static ConfigurationGroupResolver resolver(Child child) {
    return new ConfigurationGroupResolver(
        command -> {
          assertEquals(COMMAND, command);
          return child;
        });
  }

  private static void failure(Executable operation) {
    var failure = assertThrows(IOException.class, operation);
    assertEquals("configuration group lookup failed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static void throwUnknown(Throwable failure) {
    if (failure instanceof RuntimeException runtime) throw runtime;
    throw (Error) failure;
  }

  private static final class Child extends Process {
    final byte[] record;
    final List<String> events = Collections.synchronizedList(new ArrayList<>());
    final Set<byte[]> observed = Collections.newSetFromMap(new IdentityHashMap<>());
    final IllegalStateException runtime = new IllegalStateException("synthetic runtime failure");
    final AssertionError fatal = new AssertionError("synthetic fatal reader");
    String mode = "success";
    String closeFailure = "";
    String readBehavior = "normal";
    String getFailure = "";
    String nullGetter = "";
    String runtimeAt = "";
    int exit;
    int position;
    int maximum;
    int destroyed;
    int forceDestroyed;
    int outputClosed;
    int inputClosed;
    int errorClosed;
    int chunk = Integer.MAX_VALUE;
    boolean alive;
    boolean interruptClose;
    java.util.function.Consumer<String> compound = name -> {};

    Child(byte[] record) {
      this.record = record.clone();
    }

    void event(String name) {
      events.add(name);
      compound.accept(name);
      if (runtimeAt.equals(name) || getFailure.equals(name)) throw runtime;
    }

    void closeEvent(String name) throws IOException {
      event(name);
      if (interruptClose && name.equals("closeOutput")) Thread.currentThread().interrupt();
      if (closeFailure.equals(name) || closeFailure.equals("all"))
        throw new IOException("synthetic opaque close diagnostic");
    }

    @Override
    public InputStream getInputStream() {
      event("getOutput");
      if (nullGetter.equals("getOutput")) return null;
      return new InputStream() {
        @Override
        public int read() {
          throw new AssertionError("bounded bulk only");
        }

        @Override
        public int read(byte[] target, int offset, int length) throws IOException {
          event("read");
          observed.add(target);
          maximum = Math.max(maximum, target.length);
          assertEquals(65537, target.length);
          if (readBehavior.equals("error")) throw fatal;
          if (readBehavior.equals("zero")) return 0;
          if (readBehavior.equals("negative")) return -2;
          if (readBehavior.equals("overflow")) return length + 1;
          if (readBehavior.equals("exception")) {
            target[offset] = 99;
            throw new IOException("synthetic opaque read diagnostic");
          }
          if (position == record.length) return -1;
          int count = Math.min(Math.min(record.length - position, length), chunk);
          System.arraycopy(record, position, target, offset, count);
          position += count;
          return count;
        }

        @Override
        public void close() throws IOException {
          outputClosed++;
          closeEvent("closeOutput");
        }
      };
    }

    @Override
    public OutputStream getOutputStream() {
      event("getInput");
      if (nullGetter.equals("getInput")) return null;
      return new OutputStream() {
        @Override
        public void write(int value) {
          throw new AssertionError("no stdin data");
        }

        @Override
        public void close() throws IOException {
          inputClosed++;
          closeEvent("closeInput");
        }
      };
    }

    @Override
    public InputStream getErrorStream() {
      event("getError");
      if (nullGetter.equals("getError")) return null;
      return new InputStream() {
        @Override
        public int read() {
          throw new AssertionError("stderr discarded");
        }

        @Override
        public void close() throws IOException {
          errorClosed++;
          closeEvent("closeError");
        }
      };
    }

    @Override
    public boolean waitFor(long time, TimeUnit unit) throws InterruptedException {
      event("wait");
      assertEquals(5, time);
      assertEquals(TimeUnit.SECONDS, unit);
      if (mode.equals("interrupt")) throw new InterruptedException("synthetic wait diagnostic");
      return !mode.equals("timeout");
    }

    @Override
    public int waitFor() {
      throw new AssertionError("no unbounded wait");
    }

    @Override
    public int exitValue() {
      event("exit");
      return exit;
    }

    @Override
    public boolean isAlive() {
      event("alive");
      return alive;
    }

    @Override
    public void destroy() {
      destroyed++;
      alive = false;
      event("destroy");
    }

    @Override
    public Process destroyForcibly() {
      forceDestroyed++;
      throw new AssertionError("no force kill");
    }

    void closedAndCleared() {
      assertEquals(1, outputClosed);
      assertEquals(1, inputClosed);
      assertEquals(1, errorClosed);
      for (byte[] bytes : observed) assertArrayEquals(new byte[65537], bytes);
    }
  }
}
