import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import java.lang.foreign.FunctionDescriptor;
import java.lang.foreign.Linker;
import java.lang.foreign.ValueLayout;
import java.lang.invoke.MethodHandle;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashSet;
import java.util.Set;

/** PT-OPS-NATIVE-007/008; privilege-phase feasibility only, NOT a Production startup gate. */
public final class NativeInheritedLockProbe {
  @SuppressWarnings("restricted")
  public static void main(String[] args) throws Throwable {
    if (args.length != 3 || !(args[0].equals("api") || args[0].equals("web")))
      throw new IllegalArgumentException("fixed fixture service required");
    if (LinuxInodeSecurity.create().effectiveUid() != Long.parseLong(args[1]))
      throw new AssertionError("wrong effective UID");
    var symbols = Linker.nativeLinker().defaultLookup();
    MethodHandle fcntl = Linker.nativeLinker().downcallHandle(symbols.find("fcntl").orElseThrow(),
        FunctionDescriptor.of(ValueLayout.JAVA_INT, ValueLayout.JAVA_INT, ValueLayout.JAVA_INT, ValueLayout.JAVA_INT),
        Linker.Option.firstVariadicArg(2));
    MethodHandle close = Linker.nativeLinker().downcallHandle(symbols.find("close").orElseThrow(),
        FunctionDescriptor.of(ValueLayout.JAVA_INT, ValueLayout.JAVA_INT));
    try {
      if (((int) fcntl.invokeExact(3, 3, 0) & 3) != 0)
        throw new AssertionError("lock FD is not read-only");
      int flags = (int) fcntl.invokeExact(3, 1, 0);
      if (flags < 0 || (flags & 1) != 0) throw new AssertionError("FD not inherited across exec");
      if ((int) fcntl.invokeExact(3, 2, flags | 1) != 0
          || ((int) fcntl.invokeExact(3, 1, 0) & 1) != 1)
        throw new AssertionError("cannot set CLOEXEC after reception");
      var attributes = Files.readAttributes(Path.of("/proc/self/fd/3"), "unix:mode,uid,nlink,ino");
      if (!Integer.valueOf(0100600).equals(attributes.get("mode"))
          || !Integer.valueOf(0).equals(attributes.get("uid"))
          || !Integer.valueOf(1).equals(attributes.get("nlink")))
        throw new AssertionError("wrong lock inode metadata");
      var expectedGroups = new HashSet<>(Set.of(args[2].split(",")));
      boolean groups = false, privileges = false;
      int zeroCaps = 0;
      for (String line : Files.readAllLines(Path.of("/proc/self/status"))) {
        if (line.startsWith("Groups:"))
          groups = new HashSet<>(Set.of(line.substring(7).trim().split("\\s+"))).equals(expectedGroups);
        if (line.startsWith("NoNewPrivs:")) privileges = line.trim().endsWith("1");
        if (line.matches("Cap(Inh|Prm|Eff|Bnd|Amb):\\s+0+")) zeroCaps++;
      }
      if (!groups || !privileges || zeroCaps != 5) throw new AssertionError("privilege drop mismatch");
      System.out.println("PT-OPS-NATIVE-" + (args[0].equals("api") ? "007" : "008")
          + " HOLD sameOFD=true readonly=true cloexec=true fixedGroups=true zeroCaps=true productionGate=false");
      Path release = Path.of("/run/schubert-nk/pgpt-inherited/" + args[0] + ".release");
      long deadline = System.nanoTime() + 30_000_000_000L;
      while (!Files.isRegularFile(release)) {
        if (System.nanoTime() >= deadline) throw new AssertionError("fixture release timeout");
        Thread.sleep(50);
      }
    } finally {
      if ((int) close.invokeExact(3) != 0) throw new AssertionError("lock FD close failed");
    }
    NativeResourceProbe.main(new String[] {args[0]});
    System.out.println("PT-OPS-NATIVE-" + (args[0].equals("api") ? "007" : "008") + " PASS lock.closed=true");
  }
}
