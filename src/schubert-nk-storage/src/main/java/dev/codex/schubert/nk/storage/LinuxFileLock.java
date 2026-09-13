package dev.codex.schubert.nk.storage;

import java.io.IOException;
import java.lang.foreign.*;
import java.lang.invoke.MethodHandleProxies;
import java.nio.file.Path;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import org.jspecify.annotations.NullMarked;

/**
 * Scoped local Linux flock on an already admitted, retained regular inode. NK-OPS-001; OPS-009;
 * UI251; SS311/341/343; SSC-049/PG-D-146; PT-OPS-FLOCK-001..008. File adapters only. The caller
 * owns root/type/UID/ACL/stable-namespace admission and must keep the borrowed procfs capability
 * alive throughout this call. Never return a live path/channel/descriptor from the operation.
 */
@NullMarked
public final class LinuxFileLock {
  private static final StructLayout STATE = Linker.Option.captureStateLayout();
  private static final long ERRNO =
      STATE.byteOffset(MemoryLayout.PathElement.groupElement("errno"));
  private final OpenCall open;
  private final LockCall flock;
  private final CloseCall close;

  /** JDK checked MethodHandle adapter signature; callers never choose the native symbol. */
  public interface OpenCall {
    int call(MemorySegment state, MemorySegment path, int flags, int mode);
  }

  public interface LockCall {
    int call(MemorySegment state, int descriptor, int flags);
  }

  public interface CloseCall {
    int call(MemorySegment state, int descriptor);
  }

  @FunctionalInterface
  public interface Operation<T> {
    T execute() throws IOException;
  }

  public static LinuxFileLock create() {
    return create(
        Objects.requireNonNull(System.getProperty("os.name"), "os.name"),
        Objects.requireNonNull(System.getProperty("os.arch"), "os.arch"),
        Linker.nativeLinker().defaultLookup());
  }

  static LinuxFileLock create(String os, String architecture, SymbolLookup symbols) {
    Objects.requireNonNull(os, "os");
    Objects.requireNonNull(architecture, "architecture");
    Objects.requireNonNull(symbols, "symbols");
    if (!os.equals("Linux") || !Set.of("amd64", "x86_64", "aarch64").contains(architecture))
      throw new IllegalStateException("native file locking is unavailable");
    return new LinuxFileLock(
        bind(
            symbols,
            "open",
            OpenCall.class,
            FunctionDescriptor.of(
                ValueLayout.JAVA_INT,
                ValueLayout.ADDRESS,
                ValueLayout.JAVA_INT,
                ValueLayout.JAVA_INT),
            Linker.Option.captureCallState("errno"),
            Linker.Option.firstVariadicArg(2)),
        bind(
            symbols,
            "flock",
            LockCall.class,
            FunctionDescriptor.of(ValueLayout.JAVA_INT, ValueLayout.JAVA_INT, ValueLayout.JAVA_INT),
            Linker.Option.captureCallState("errno")),
        bind(
            symbols,
            "close",
            CloseCall.class,
            FunctionDescriptor.of(ValueLayout.JAVA_INT, ValueLayout.JAVA_INT),
            Linker.Option.captureCallState("errno")));
  }

  LinuxFileLock(OpenCall open, LockCall flock, CloseCall close) {
    this.open = Objects.requireNonNull(open, "open");
    this.flock = Objects.requireNonNull(flock, "flock");
    this.close = Objects.requireNonNull(close, "close");
  }

  /**
   * Empty means EWOULDBLOCK, with no operation executed. Every other native/IO/close failure throws
   * a fixed diagnostic. Runtime programming failures escape after closing the owned FD. No file is
   * created, truncated, unlinked or repaired.
   */
  public <T> Optional<T> tryExclusive(Path heldFile, Operation<T> operation)
      throws StorageIoException {
    Objects.requireNonNull(operation, "operation");
    String path = heldPath(heldFile);
    try (Arena arena = Arena.ofConfined()) {
      return acquire(arena, path, operation);
    } catch (IOException failure) {
      // Drop every source cause/suppressed diagnostic; close failure also prevents success.
      throw unavailable();
    }
  }

  // BUG-140/YKT-110: one return from the Arena owner; this helper only borrows its lifetime.
  private <T> Optional<T> acquire(Arena arena, String path, Operation<T> operation)
      throws IOException {
    MemorySegment state = arena.allocate(STATE);
    // Intentional follow of the caller's retained kernel FD, never a replaceable raw pathname.
    int descriptor = open.call(state, arena.allocateFrom(path), 0x80000, 0);
    if (descriptor < 0) throw unavailable();
    var owned = new OwnedDescriptor(descriptor, close);
    return ResourceScope.use(
        owned::close,
        () -> {
          int result = flock.call(state, owned.descriptor, 2 | 4);
          if (result != 0) {
            if (result == -1 && state.get(ValueLayout.JAVA_INT, ERRNO) == 11)
              return Optional.empty();
            throw unavailable();
          }
          return Optional.of(operation.execute());
        });
  }

  private static String heldPath(Path held) {
    Objects.requireNonNull(held, "held file");
    String path = held.toString();
    if (!path.matches("/proc/self/fd/(0|[1-9][0-9]{0,9})"))
      throw new IllegalArgumentException("invalid held file capability");
    try {
      Integer.parseInt(path.substring(14));
    } catch (NumberFormatException failure) {
      throw new IllegalArgumentException("invalid held file capability");
    }
    return path;
  }

  // PG-D-146: the one native binding boundary for this capability. Owner NK-OPS-001 PG.
  // Re-review at PG gate/JDK or ABI change. No null/coverage/native-access check is suppressed.
  @SuppressWarnings("restricted")
  private static <T> T bind(
      SymbolLookup symbols,
      String name,
      Class<T> type,
      FunctionDescriptor signature,
      Linker.Option... options) {
    var symbol =
        symbols
            .find(name)
            .orElseThrow(() -> new IllegalStateException("native file locking is unavailable"));
    return MethodHandleProxies.asInterfaceInstance(
        type, Linker.nativeLinker().downcallHandle(symbol, signature, options));
  }

  private static StorageIoException unavailable() {
    return new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
  }

  private static final class OwnedDescriptor implements AutoCloseable {
    private final int descriptor;
    private final CloseCall close;

    private OwnedDescriptor(int descriptor, CloseCall close) {
      this.descriptor = descriptor;
      this.close = close;
    }

    @Override
    public void close() throws StorageIoException {
      try (Arena arena = Arena.ofConfined()) {
        // A single lexical close consumes ownership even if the OS reports failure; never retry.
        if (close.call(arena.allocate(STATE), descriptor) != 0) throw unavailable();
      }
    }
  }
}
