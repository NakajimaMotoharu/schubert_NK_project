package dev.codex.schubert.nk.storage;

import java.lang.foreign.Arena;
import java.lang.foreign.FunctionDescriptor;
import java.lang.foreign.Linker;
import java.lang.foreign.MemorySegment;
import java.lang.foreign.SymbolLookup;
import java.lang.foreign.ValueLayout;
import java.lang.invoke.MethodHandleProxies;
import java.nio.file.Path;
import java.util.Objects;
import java.util.Set;
import org.jspecify.annotations.Nullable;

/**
 * Fresh Linux/glibc LP64 statfs classification of an already retained inode. No mount-table lookup,
 * content read, state cache, permission repair or authorization. ext2/3/4 share one kernel magic;
 * the internal family admits exactly the previously approved union, not an asserted mount name.
 * NK-OPS-001; OPS009/FIL006/SYS004; UI251; SS343/353 SSC269; PT-OPS-FSTYPE-001..004.
 */
public final class LinuxFilesystemClassifier {
  // glibc LP64 bits/statfs.h: seven words, fsid(two int), three words, four spare words.
  // sizeof=120/alignment=8, f_type is the first word. Re-review on JDK/ABI changes.
  private static final long SIZE = 120;
  private final StatfsCall statfs;

  @FunctionalInterface
  public interface StatfsCall {
    int call(MemorySegment path, MemorySegment state);
  }

  LinuxFilesystemClassifier(StatfsCall statfs) {
    this.statfs = Objects.requireNonNull(statfs, "fresh statfs");
  }

  public static LinuxFilesystemClassifier create() {
    return create(
        Objects.requireNonNull(System.getProperty("os.name")),
        Objects.requireNonNull(System.getProperty("os.arch")),
        Linker.nativeLinker().defaultLookup());
  }

  static LinuxFilesystemClassifier create(String os, String arch, SymbolLookup symbols) {
    Objects.requireNonNull(os);
    Objects.requireNonNull(arch);
    Objects.requireNonNull(symbols);
    if (!os.equals("Linux")
        || !Set.of("amd64", "x86_64", "aarch64").contains(arch)
        || symbols.find("gnu_get_libc_version").isEmpty()) throw platformUnavailable();
    return new LinuxFilesystemClassifier(bind(symbols));
  }

  @SuppressWarnings("restricted")
  private static StatfsCall bind(SymbolLookup symbols) {
    var symbol = symbols.find("statfs").orElseThrow(LinuxFilesystemClassifier::platformUnavailable);
    return MethodHandleProxies.asInterfaceInstance(
        StatfsCall.class,
        Linker.nativeLinker()
            .downcallHandle(
                symbol,
                FunctionDescriptor.of(
                    ValueLayout.JAVA_INT, ValueLayout.ADDRESS, ValueLayout.ADDRESS)));
  }

  /** Caller proves inode security independently. This result never confers readiness. */
  public String filesystem(@Nullable Path held) throws StorageIoException {
    if (held == null) throw new IllegalArgumentException("invalid held inode capability");
    String path = held.toString();
    if (!path.matches("/proc/self/fd/(0|[1-9][0-9]{0,9})")
        || Long.parseLong(path.substring(14)) > Integer.MAX_VALUE)
      throw new IllegalArgumentException("invalid held inode capability");
    var arena = Arena.ofConfined();
    return ResourceScope.use(
        arena::close,
        () -> {
          var state = arena.allocate(SIZE, 8);
          if (statfs.call(arena.allocateFrom(path), state) != 0) throw unavailable();
          long magic = state.get(ValueLayout.JAVA_LONG, 0);
          if (magic == 0xEF53L) return "ext2/ext3/ext4";
          if (magic == 0x58465342L) return "xfs";
          if (magic == 0x9123683EL) return "btrfs";
          if (magic == 0x01021994L) return "tmpfs";
          throw unavailable();
        });
  }

  private static StorageIoException unavailable() {
    return new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
  }

  private static IllegalStateException platformUnavailable() {
    return new IllegalStateException("native filesystem classification is unavailable");
  }
}
