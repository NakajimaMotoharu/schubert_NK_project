package dev.codex.schubert.nk.storage;

import java.io.IOException;
import java.lang.foreign.*;
import java.lang.invoke.MethodHandleProxies;
import java.util.Objects;
import java.util.Set;
import org.jspecify.annotations.NullMarked;

/**
 * Same-boot Linux CLOCK_MONOTONIC, explicitly shared across maintenance JVMs. No wall-clock,
 * process-local nanoTime origin or fallback. NK-OPS-001; OPS009/UI251/SS341§7.3/343;
 * SSC119/PT-OPS-COWNER001..004. The caller must separately bind boot/parent/epoch and ownership.
 */
@NullMarked
public final class LinuxMonotonicClock {
  /** Fixed clock_gettime ABI, never a caller-selected native symbol or clock. */
  public interface ReadCall {
    int call(int clock, MemorySegment result);
  }

  private final ReadCall read;

  public static LinuxMonotonicClock create() {
    return create(
        Objects.requireNonNull(System.getProperty("os.name")),
        Objects.requireNonNull(System.getProperty("os.arch")),
        Linker.nativeLinker().defaultLookup());
  }

  @SuppressWarnings("restricted")
  static LinuxMonotonicClock create(String os, String architecture, SymbolLookup symbols) {
    Objects.requireNonNull(os, "OS");
    Objects.requireNonNull(architecture, "architecture");
    Objects.requireNonNull(symbols, "native symbols");
    if (!os.equals("Linux") || !Set.of("amd64", "x86_64", "aarch64").contains(architecture))
      throw new IllegalStateException("shared monotonic clock unavailable");
    var address =
        symbols
            .find("clock_gettime")
            .orElseThrow(() -> new IllegalStateException("shared monotonic clock unavailable"));
    var read =
        MethodHandleProxies.asInterfaceInstance(
            ReadCall.class,
            Linker.nativeLinker()
                .downcallHandle(
                    address,
                    FunctionDescriptor.of(
                        ValueLayout.JAVA_INT, ValueLayout.JAVA_INT, ValueLayout.ADDRESS)));
    return new LinuxMonotonicClock(read);
  }

  LinuxMonotonicClock(ReadCall read) {
    this.read = Objects.requireNonNull(read, "monotonic read");
  }

  public long nowNanos() throws IOException {
    // Approved Linux 64-bit ABI: struct timespec { signed long seconds; signed long nanos; }.
    try (var arena = Arena.ofConfined()) {
      var value = arena.allocate(16, 8);
      if (read.call(1, value) != 0) throw unavailable();
      long seconds = value.get(ValueLayout.JAVA_LONG, 0);
      long nanos = value.get(ValueLayout.JAVA_LONG, 8);
      if (seconds < 0 || nanos < 0 || nanos >= 1_000_000_000L) throw unavailable();
      try {
        return Math.addExact(Math.multiplyExact(seconds, 1_000_000_000L), nanos);
      } catch (ArithmeticException overflow) {
        throw unavailable();
      }
    }
  }

  private static IOException unavailable() {
    return new IOException("shared monotonic clock unavailable");
  }
}
