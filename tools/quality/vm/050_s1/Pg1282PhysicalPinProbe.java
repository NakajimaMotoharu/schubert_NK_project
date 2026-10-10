package dev.codex.schubert.nk.bootstrap;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

/** NCHANNEL1282001/002: actual fixed agent component, never application admission. */
public final class Pg1282PhysicalPinProbe {
  private Pg1282PhysicalPinProbe() {}

  private static long descriptors() throws IOException {
    try (var entries = Files.list(Path.of("/proc/self/fd"))) {
      return entries.count();
    }
  }

  private static void observe(boolean readOnly) throws IOException {
    try {
      NativeCoveragePrivateFile.verifyPinnedAgent();
      if (!readOnly) throw new AssertionError("read-write physical pin accepted");
    } catch (IOException refused) {
      if (readOnly) throw refused;
      if (!refused.getMessage().equals("fixed PT native capture unavailable")) throw refused;
    }
  }

  public static void main(String[] args) throws IOException {
    if (args.length != 1 || !(args[0].equals("RW") || args[0].equals("RO")))
      throw new IllegalArgumentException("closed physical pin test mode required");
    boolean readOnly = args[0].equals("RO");
    // Warm ordinary class/JAR handles before observing retained inode FD return.
    observe(readOnly);
    long before = descriptors();
    observe(readOnly);
    if (descriptors() != before) throw new AssertionError("retained pin FD leak");
    System.out.println(readOnly ? "RO_PIN_VERIFIED_FD_RETURNED" : "RW_PIN_REFUSED_FD_RETURNED");
  }
}
