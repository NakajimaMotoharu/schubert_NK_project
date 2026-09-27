package dev.codex.schubert.nk.storage;

import java.lang.foreign.*;
import java.lang.invoke.MethodHandleProxies;
import java.nio.file.Path;
import java.util.*;
import org.jspecify.annotations.NullMarked;

/**
 * Same-PID replacement through a retained, admitted ELF inode, never a fork or shell.
 * NK-OPS-001/OPS009; UI212/251; SS341/342/343; SSC086; PT-OPS-EXEC-001..008. The root launcher owns
 * executable admission, fixed argv/env policy, credential cleanup and the explicitly inherited
 * A/proof descriptors. This native boundary does not grant admission.
 */
@NullMarked
public final class LinuxProcessExec {
  private final ExecCall exec;

  public interface ExecCall {
    int call(MemorySegment executable, MemorySegment arguments, MemorySegment environment);
  }

  public static LinuxProcessExec create() {
    return create(
        Objects.requireNonNull(System.getProperty("os.name"), "os.name"),
        Objects.requireNonNull(System.getProperty("os.arch"), "os.arch"),
        Linker.nativeLinker().defaultLookup());
  }

  @SuppressWarnings("restricted")
  static LinuxProcessExec create(String os, String architecture, SymbolLookup symbols) {
    Objects.requireNonNull(os, "os");
    Objects.requireNonNull(architecture, "architecture");
    Objects.requireNonNull(symbols, "symbols");
    if (!os.equals("Linux") || !Set.of("amd64", "x86_64", "aarch64").contains(architecture))
      throw new IllegalStateException("native process replacement is unavailable");
    var address =
        symbols
            .find("execve")
            .orElseThrow(
                () -> new IllegalStateException("native process replacement is unavailable"));
    return new LinuxProcessExec(
        MethodHandleProxies.asInterfaceInstance(
            ExecCall.class,
            Linker.nativeLinker()
                .downcallHandle(
                    address,
                    FunctionDescriptor.of(
                        ValueLayout.JAVA_INT,
                        ValueLayout.ADDRESS,
                        ValueLayout.ADDRESS,
                        ValueLayout.ADDRESS))));
  }

  LinuxProcessExec(ExecCall exec) {
    this.exec = Objects.requireNonNull(exec, "exec");
  }

  /**
   * Never returns: successful exec replaces the JVM and its heap; any native return is failure.
   * Inputs are bounded non-secret vectors prepared by the trusted launcher, not user data. A
   * failure exposes neither errno nor executable/argv/env/cause. Unknown Java failures escape.
   */
  public void replace(Path heldExecutable, List<String> arguments, Map<String, String> environment)
      throws StorageIoException {
    Objects.requireNonNull(heldExecutable, "held executable");
    var argv = List.copyOf(arguments);
    var env = new TreeMap<>(Map.copyOf(environment));
    String path = heldExecutable.toString();
    if (!path.matches("/proc/self/fd/(0|[1-9][0-9]{0,9})")) throw invalid();
    try {
      Integer.parseInt(path.substring(14));
    } catch (NumberFormatException failure) {
      throw invalid();
    }
    if (argv.isEmpty() || argv.size() > 64 || env.size() > 32) throw invalid();
    for (String argument : argv) validate(argument);
    var entries = new ArrayList<String>();
    for (var entry : env.entrySet()) {
      if (!entry.getKey().matches("[A-Z][A-Z0-9_]{0,63}")) throw invalid();
      validate(entry.getValue());
      entries.add(entry.getKey() + "=" + entry.getValue());
    }
    // This arena never leaves the calling thread and is not an externally supplied resource.
    // Explicit finally avoids a TWR suppression branch on a native operation that cannot return
    // successfully; a real successful exec replaces this entire JVM, including the arena.
    Arena arena = Arena.ofConfined();
    try {
      exec.call(arena.allocateFrom(path), vector(arena, argv), vector(arena, entries));
    } finally {
      arena.close();
    }
    throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
  }

  private static void validate(String value) {
    if (value.length() > 4096
        || value.chars().anyMatch(character -> character < 32 || character == 127)) throw invalid();
  }

  private static MemorySegment vector(Arena arena, List<String> strings) {
    var pointers = arena.allocate(ValueLayout.ADDRESS, strings.size() + 1L);
    for (int index = 0; index < strings.size(); index++)
      pointers.setAtIndex(ValueLayout.ADDRESS, index, arena.allocateFrom(strings.get(index)));
    pointers.setAtIndex(ValueLayout.ADDRESS, strings.size(), MemorySegment.NULL);
    return pointers;
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("invalid process replacement input");
  }
}
