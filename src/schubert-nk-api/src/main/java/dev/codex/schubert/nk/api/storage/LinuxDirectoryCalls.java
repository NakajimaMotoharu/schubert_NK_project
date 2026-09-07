package dev.codex.schubert.nk.api.storage;

import java.lang.foreign.Arena;
import java.lang.foreign.FunctionDescriptor;
import java.lang.foreign.Linker;
import java.lang.foreign.MemoryLayout;
import java.lang.foreign.MemorySegment;
import java.lang.foreign.StructLayout;
import java.lang.foreign.SymbolLookup;
import java.lang.foreign.ValueLayout;
import java.lang.invoke.MethodHandleProxies;
import java.util.Objects;
import java.util.Set;

/**
 * Linux libc port using public Java25 FFM, never reflection/internal APIs or fallback rename.
 * NK-SCN-001; RD FIL-001..009; UI237; SS333 §7.3/342; SSC-019; PT-SCN-008-F01/F03. Package-private:
 * only owned capabilities may expose filesystem operations to services.
 */
final class LinuxDirectoryCalls implements DirectoryCalls {
  // Linux x86-64/AArch64 ABI constants, not portable POSIX guesses. See PG-D-055.
  private static final int AT_FDCWD = -100;
  private static final int DIRECTORY_FLAGS = 0x10000 | 0x20000 | 0x80000;
  private static final int ENTRY_FLAGS = 0x200000 | 0x20000 | 0x80000;
  private static final StructLayout STATE = Linker.Option.captureStateLayout();
  private static final long ERRNO_OFFSET =
      STATE.byteOffset(MemoryLayout.PathElement.groupElement("errno"));
  private final OpenCall open;
  private final MkdirCall mkdir;
  private final RenameCall rename;
  private final UnlinkCall unlink;
  private final FdCall sync;
  private final FdCall close;

  // Public SAM signatures allow the JDK's checked MethodHandle adapter, avoiding broad Throwable
  // catches. This enclosing class remains package-private. No user-supplied native symbol is used.
  public interface OpenCall {
    int call(MemorySegment state, int directory, MemorySegment name, int flags, int mode);
  }

  public interface MkdirCall {
    int call(MemorySegment state, int directory, MemorySegment name, int mode);
  }

  public interface RenameCall {
    int call(
        MemorySegment state,
        int source,
        MemorySegment part,
        int target,
        MemorySegment ready,
        int flags);
  }

  public interface UnlinkCall {
    int call(MemorySegment state, int directory, MemorySegment name, int flags);
  }

  public interface FdCall {
    int call(MemorySegment state, int directory);
  }

  static LinuxDirectoryCalls create() {
    return create(
        Objects.requireNonNull(System.getProperty("os.name"), "os.name"),
        Objects.requireNonNull(System.getProperty("os.arch"), "os.arch"),
        Linker.nativeLinker().defaultLookup());
  }

  static LinuxDirectoryCalls create(String os, String architecture, SymbolLookup symbols) {
    Objects.requireNonNull(os, "os");
    Objects.requireNonNull(architecture, "architecture");
    Objects.requireNonNull(symbols, "symbols");
    if (!os.equals("Linux") || !Set.of("amd64", "x86_64", "aarch64").contains(architecture)) {
      throw new IllegalStateException("native storage is unavailable");
    }
    return new LinuxDirectoryCalls(symbols);
  }

  private LinuxDirectoryCalls(SymbolLookup symbols) {
    open =
        bind(
            symbols,
            "openat",
            OpenCall.class,
            FunctionDescriptor.of(
                ValueLayout.JAVA_INT,
                ValueLayout.JAVA_INT,
                ValueLayout.ADDRESS,
                ValueLayout.JAVA_INT,
                ValueLayout.JAVA_INT),
            Linker.Option.captureCallState("errno"),
            Linker.Option.firstVariadicArg(3));
    mkdir =
        bind(
            symbols,
            "mkdirat",
            MkdirCall.class,
            FunctionDescriptor.of(
                ValueLayout.JAVA_INT,
                ValueLayout.JAVA_INT,
                ValueLayout.ADDRESS,
                ValueLayout.JAVA_INT),
            Linker.Option.captureCallState("errno"));
    rename =
        bind(
            symbols,
            "renameat2",
            RenameCall.class,
            FunctionDescriptor.of(
                ValueLayout.JAVA_INT,
                ValueLayout.JAVA_INT,
                ValueLayout.ADDRESS,
                ValueLayout.JAVA_INT,
                ValueLayout.ADDRESS,
                ValueLayout.JAVA_INT),
            Linker.Option.captureCallState("errno"));
    unlink =
        bind(
            symbols,
            "unlinkat",
            UnlinkCall.class,
            FunctionDescriptor.of(
                ValueLayout.JAVA_INT,
                ValueLayout.JAVA_INT,
                ValueLayout.ADDRESS,
                ValueLayout.JAVA_INT),
            Linker.Option.captureCallState("errno"));
    sync =
        bind(
            symbols,
            "fsync",
            FdCall.class,
            FunctionDescriptor.of(ValueLayout.JAVA_INT, ValueLayout.JAVA_INT),
            Linker.Option.captureCallState("errno"));
    close =
        bind(
            symbols,
            "close",
            FdCall.class,
            FunctionDescriptor.of(ValueLayout.JAVA_INT, ValueLayout.JAVA_INT),
            Linker.Option.captureCallState("errno"));
  }

  // PG-D-055/SSC-019: this single audited native boundary intentionally invokes restricted FFM.
  // Owner: NK-SCN-001 PG. Re-review at PG gate and every JDK/ABI change; F01/F03 exercise libc.
  // No other compiler warning, native-access check, null analysis or coverage is suppressed.
  @SuppressWarnings("restricted")
  private static <T> T bind(
      SymbolLookup symbols,
      String name,
      Class<T> type,
      FunctionDescriptor signature,
      Linker.Option... options) {
    MemorySegment symbol =
        symbols
            .find(name)
            .orElseThrow(() -> new IllegalStateException("native storage is unavailable"));
    return MethodHandleProxies.asInterfaceInstance(
        type, Linker.nativeLinker().downcallHandle(symbol, signature, options));
  }

  @Override
  public int openRoot() throws StorageIoException {
    return open(AT_FDCWD, "/", DIRECTORY_FLAGS);
  }

  @Override
  public int openDirectory(int parent, String name) throws StorageIoException {
    return open(parent, segment(name), DIRECTORY_FLAGS);
  }

  @Override
  public int openEntry(int parent, String name) throws StorageIoException {
    return open(parent, segment(name), ENTRY_FLAGS);
  }

  private int open(int parent, String name, int flags) throws StorageIoException {
    try (Arena arena = Arena.ofConfined()) {
      MemorySegment state = arena.allocate(STATE);
      return check(open.call(state, parent, arena.allocateFrom(name), flags, 0), state);
    }
  }

  @Override
  public void createDirectory(int parent, String name) throws StorageIoException {
    segment(name);
    try (Arena arena = Arena.ofConfined()) {
      MemorySegment state = arena.allocate(STATE);
      check(mkdir.call(state, parent, arena.allocateFrom(name), 0750), state);
    }
  }

  @Override
  public void publish(int directory, String part, String ready) throws StorageIoException {
    segment(part);
    segment(ready);
    try (Arena arena = Arena.ofConfined()) {
      MemorySegment state = arena.allocate(STATE);
      check(
          rename.call(
              state, directory, arena.allocateFrom(part), directory, arena.allocateFrom(ready), 1),
          state);
    }
  }

  @Override
  public void unlink(int directory, String name) throws StorageIoException {
    segment(name);
    try (Arena arena = Arena.ofConfined()) {
      MemorySegment state = arena.allocate(STATE);
      check(unlink.call(state, directory, arena.allocateFrom(name), 0), state);
    }
  }

  @Override
  public void sync(int directory) throws StorageIoException {
    call(sync, directory);
  }

  @Override
  public void close(int directory) throws StorageIoException {
    call(close, directory);
  }

  private static void call(FdCall function, int directory) throws StorageIoException {
    try (Arena arena = Arena.ofConfined()) {
      MemorySegment state = arena.allocate(STATE);
      check(function.call(state, directory), state);
    }
  }

  private static int check(int result, MemorySegment state) throws StorageIoException {
    if (result < 0) {
      throw new StorageIoException(
          switch (state.get(ValueLayout.JAVA_INT, ERRNO_OFFSET)) {
            case 17 -> StorageIoException.Reason.COLLISION;
            case 2 -> StorageIoException.Reason.MISSING;
            default -> StorageIoException.Reason.UNAVAILABLE;
          });
    }
    return result;
  }

  private static String segment(String name) {
    Objects.requireNonNull(name, "name");
    if (name.isEmpty()
        || name.equals(".")
        || name.equals("..")
        || name.indexOf('/') >= 0
        || name.indexOf('\0') >= 0) {
      throw new IllegalArgumentException("invalid storage segment");
    }
    return name;
  }
}
