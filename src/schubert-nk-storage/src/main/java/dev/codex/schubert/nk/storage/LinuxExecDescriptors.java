package dev.codex.schubert.nk.storage;

import java.lang.foreign.FunctionDescriptor;
import java.lang.foreign.Linker;
import java.lang.foreign.SymbolLookup;
import java.lang.foreign.ValueLayout;
import java.lang.invoke.MethodHandleProxies;
import java.util.Objects;
import java.util.Set;
import org.jspecify.annotations.NullMarked;

/**
 * Temporarily inherits exactly two caller-owned descriptors across same-PID exec.
 * NK-OPS-001/OPS009; UI212/251; SS341/342/343; SSC086; PT-OPS-XFD-001..008. The trusted root caller
 * already owns/admitted readonly A and sealed public proof, reserves both descriptors, and must not
 * concurrently close/reassign them. This is not FD admission.
 */
@NullMarked
public final class LinuxExecDescriptors {
  private static final int FD_CLOEXEC = 1;

  private final FcntlCall fcntl;

  public interface FcntlCall {
    int call(int descriptor, int command, int argument);
  }

  @FunctionalInterface
  public interface Operation {
    void execute() throws java.io.IOException;
  }

  public static LinuxExecDescriptors create() {
    return create(
        Objects.requireNonNull(System.getProperty("os.name"), "os.name"),
        Objects.requireNonNull(System.getProperty("os.arch"), "os.arch"),
        Linker.nativeLinker().defaultLookup());
  }

  @SuppressWarnings("restricted")
  static LinuxExecDescriptors create(String os, String architecture, SymbolLookup symbols) {
    Objects.requireNonNull(os, "os");
    Objects.requireNonNull(architecture, "architecture");
    Objects.requireNonNull(symbols, "symbols");
    if (!os.equals("Linux") || !Set.of("amd64", "x86_64", "aarch64").contains(architecture))
      throw new IllegalStateException("native descriptor inheritance is unavailable");
    var symbol =
        symbols
            .find("fcntl")
            .orElseThrow(
                () -> new IllegalStateException("native descriptor inheritance is unavailable"));
    return new LinuxExecDescriptors(
        MethodHandleProxies.asInterfaceInstance(
            FcntlCall.class,
            Linker.nativeLinker()
                .downcallHandle(
                    symbol,
                    FunctionDescriptor.of(
                        ValueLayout.JAVA_INT,
                        ValueLayout.JAVA_INT,
                        ValueLayout.JAVA_INT,
                        ValueLayout.JAVA_INT),
                    Linker.Option.firstVariadicArg(2))));
  }

  LinuxExecDescriptors(FcntlCall fcntl) {
    this.fcntl = Objects.requireNonNull(fcntl, "fcntl");
  }

  /**
   * Requires distinct reserved FD128..65535, initially CLOEXEC. Never closes borrowed FDs. This
   * scope is not startup/exec success: a callback may inspect flags before deciding whether to
   * exec. Every Java exit restores flags, even a normal callback or partial transition. A real
   * successful exec replaces this process. Compound unknown failure precedence is ResourceScope.
   */
  public void withInherited(int lockDescriptor, int proofDescriptor, Operation operation)
      throws StorageIoException {
    Objects.requireNonNull(operation, "operation");
    if (lockDescriptor < 128
        || lockDescriptor > 65535
        || proofDescriptor < 128
        || proofDescriptor > 65535
        || lockDescriptor == proofDescriptor)
      throw new IllegalArgumentException("invalid descriptor inheritance input");
    inherit(lockDescriptor, () -> inherit(proofDescriptor, operation));
  }

  private void inherit(int descriptor, Operation operation) throws StorageIoException {
    if (fcntl.call(descriptor, 1, 0) != FD_CLOEXEC)
      throw unavailable(); // F_GETFD: exactly FD_CLOEXEC
    ResourceScope.use(
        () -> set(descriptor, FD_CLOEXEC),
        () -> {
          set(descriptor, 0); // F_SETFD: only the reserved descriptor becomes inheritable
          operation.execute();
          return Boolean.TRUE;
        });
  }

  private void set(int descriptor, int flags) throws StorageIoException {
    if (fcntl.call(descriptor, 2, flags) != 0) throw unavailable();
  }

  private static StorageIoException unavailable() {
    return new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
  }
}
