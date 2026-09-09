package dev.codex.schubert.nk.storage;

import java.lang.foreign.Arena;
import java.lang.foreign.FunctionDescriptor;
import java.lang.foreign.Linker;
import java.lang.foreign.MemoryLayout;
import java.lang.foreign.MemorySegment;
import java.lang.foreign.StructLayout;
import java.lang.foreign.SymbolLookup;
import java.lang.foreign.ValueLayout;
import java.lang.invoke.MethodHandleProxies;
import java.nio.file.Path;
import java.util.Objects;
import java.util.Set;

/**
 * Linux/glibc LP64 retained inode access metadata. No content read, permission repair or child
 * process. NK-DAT-001; DAT-009/OPS-009/FIL-006; UI212/241/251; SS311/343 6.3;
 * QA-046/SSC-049/PG-D-133; PT-DB-INBOX-121..128.
 */
public final class LinuxInodeSecurity implements InodeSecurityCalls {
  private static final StructLayout STATE = Linker.Option.captureStateLayout();
  private static final long ERRNO_OFFSET =
      STATE.byteOffset(MemoryLayout.PathElement.groupElement("errno"));
  // glibc LP64 statvfs: eleven 64-bit fields and six 32-bit fields, flag is field9.
  // Matched against libc6-dev2.43 bits/statvfs.h; re-review on ABI/JDK changes.
  private static final MemoryLayout STATVFS =
      MemoryLayout.structLayout(
          MemoryLayout.sequenceLayout(11, ValueLayout.JAVA_LONG),
          MemoryLayout.sequenceLayout(6, ValueLayout.JAVA_INT));
  private static final long FLAG_OFFSET = 72;
  private final GetXattrCall getxattr;
  private final StatvfsCall statvfs;
  private final UidCall geteuid;

  public interface GetXattrCall {
    long call(
        MemorySegment state,
        MemorySegment path,
        MemorySegment name,
        MemorySegment value,
        long size);
  }

  public interface StatvfsCall {
    int call(MemorySegment state, MemorySegment path, MemorySegment value);
  }

  public interface UidCall {
    int call();
  }

  LinuxInodeSecurity(GetXattrCall getxattr, StatvfsCall statvfs, UidCall geteuid) {
    this.getxattr = Objects.requireNonNull(getxattr, "getxattr");
    this.statvfs = Objects.requireNonNull(statvfs, "statvfs");
    this.geteuid = Objects.requireNonNull(geteuid, "geteuid");
  }

  public static LinuxInodeSecurity create() {
    return create(
        Objects.requireNonNull(System.getProperty("os.name"), "os.name"),
        Objects.requireNonNull(System.getProperty("os.arch"), "os.arch"),
        Linker.nativeLinker().defaultLookup());
  }

  static LinuxInodeSecurity create(String os, String architecture, SymbolLookup symbols) {
    Objects.requireNonNull(os, "os");
    Objects.requireNonNull(architecture, "architecture");
    Objects.requireNonNull(symbols, "symbols");
    if (!os.equals("Linux")
        || !Set.of("amd64", "x86_64", "aarch64").contains(architecture)
        || symbols.find("gnu_get_libc_version").isEmpty()) throw unavailablePlatform();
    return new LinuxInodeSecurity(
        bind(
            symbols,
            "getxattr",
            GetXattrCall.class,
            FunctionDescriptor.of(
                ValueLayout.JAVA_LONG,
                ValueLayout.ADDRESS,
                ValueLayout.ADDRESS,
                ValueLayout.ADDRESS,
                ValueLayout.JAVA_LONG),
            Linker.Option.captureCallState("errno")),
        bind(
            symbols,
            "statvfs",
            StatvfsCall.class,
            FunctionDescriptor.of(ValueLayout.JAVA_INT, ValueLayout.ADDRESS, ValueLayout.ADDRESS),
            Linker.Option.captureCallState("errno")),
        bind(symbols, "geteuid", UidCall.class, FunctionDescriptor.of(ValueLayout.JAVA_INT)));
  }

  // PG-D-133/SSC-049: audited public FFM binding only; owner NK-DAT-001 PG, reviewed at PG gate
  // and each ABI/JDK update. PT121/125 exercise real binding, not a suppressed fallback.
  @SuppressWarnings("restricted")
  private static <T> T bind(
      SymbolLookup symbols,
      String name,
      Class<T> type,
      FunctionDescriptor descriptor,
      Linker.Option... options) {
    MemorySegment symbol = symbols.find(name).orElseThrow(LinuxInodeSecurity::unavailablePlatform);
    return MethodHandleProxies.asInterfaceInstance(
        type, Linker.nativeLinker().downcallHandle(symbol, descriptor, options));
  }

  private static IllegalStateException unavailablePlatform() {
    return new IllegalStateException("native inode security is unavailable");
  }

  @Override
  public byte[] accessAcl(Path held, int maximumBytes) throws StorageIoException {
    String path = capability(held);
    if (maximumBytes < 1 || maximumBytes > 65536)
      throw new IllegalArgumentException("invalid access ACL size limit");
    try (Arena arena = Arena.ofConfined()) {
      return readAcl(arena, path, maximumBytes);
    }
  }

  // BUG-097/YKT-088: one lexical owner closes Arena; result classification borrows it.
  private byte[] readAcl(Arena arena, String path, int maximumBytes) throws StorageIoException {
    MemorySegment state = arena.allocate(STATE);
    MemorySegment value = arena.allocate(maximumBytes);
    long size =
        getxattr.call(
            state,
            arena.allocateFrom(path),
            arena.allocateFrom("system.posix_acl_access"),
            value,
            maximumBytes);
    if (size == -1) {
      int errno = state.get(ValueLayout.JAVA_INT, ERRNO_OFFSET);
      if (errno == 61 || errno == 95) return new byte[0];
    }
    if (size < 1 || size > maximumBytes) throw failure();
    return value.asSlice(0, size).toArray(ValueLayout.JAVA_BYTE);
  }

  @Override
  public boolean readOnlyFilesystem(Path held) throws StorageIoException {
    String path = capability(held);
    try (Arena arena = Arena.ofConfined()) {
      MemorySegment state = arena.allocate(STATE);
      MemorySegment value = arena.allocate(STATVFS);
      if (statvfs.call(state, arena.allocateFrom(path), value) != 0) throw failure();
      return (value.get(ValueLayout.JAVA_LONG, FLAG_OFFSET) & 1) != 0;
    }
  }

  @Override
  public long effectiveUid() {
    return Integer.toUnsignedLong(geteuid.call());
  }

  private static String capability(Path held) {
    Objects.requireNonNull(held, "held inode");
    String path = held.toString();
    if (!path.matches("/proc/self/fd/(0|[1-9][0-9]{0,9})")
        || Long.parseLong(path.substring(14)) > Integer.MAX_VALUE)
      throw new IllegalArgumentException("invalid held inode capability");
    return path;
  }

  private static StorageIoException failure() {
    return new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
  }
}
