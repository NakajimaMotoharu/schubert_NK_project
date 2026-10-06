import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.concurrent.TimeUnit;

/** SSC196 tool-owned metadata-only sender; never startup, stop or database authority. */
final class Pg477UnitReferences {
  private final Process process;
  private final InputStream input;
  private final OutputStream output;
  private boolean closed;

  Pg477UnitReferences(Path tools, String mode) throws Exception {
    if (tools == null || mode == null || (!mode.equals("verify") && !mode.equals("activate"))) throw new IOException("fixed references refused");
    Path log = tools.resolve("refs-" + mode + ".private.log");
    Files.createFile(log, java.nio.file.attribute.PosixFilePermissions.asFileAttribute(
        java.nio.file.attribute.PosixFilePermissions.fromString("rw-------")));
    process = new ProcessBuilder("/usr/bin/python3", "-B", tools.resolve("pg477_unit_references.py").toString(), mode)
        .redirectError(log.toFile()).start();
    input = process.getInputStream();
    output = process.getOutputStream();
    await("REF_READY");
  }

  static boolean reply(String expected, byte[] bytes) {
    return expected != null && java.util.Set.of("REF_READY", "REF_CHECKED", "REF_CONFIGURED", "REF_RELEASED").contains(expected)
        && bytes != null && bytes.length <= 64
        && java.util.Arrays.equals((expected + "\n").getBytes(StandardCharsets.US_ASCII), bytes);
  }

  private void await(String expected) throws Exception {
    long end = System.nanoTime() + TimeUnit.SECONDS.toNanos(expected.equals("REF_CONFIGURED") ? 65 : 5);
    var bytes = new ByteArrayOutputStream();
    while (System.nanoTime() < end) {
      while (input.available() > 0) {
        int value = input.read();
        if (value < 0 || bytes.size() == 64) throw new IOException("reference reply unavailable");
        bytes.write(value);
        if (value == 10) {
          if (!reply(expected, bytes.toByteArray())) throw new IOException("reference reply unavailable");
          return;
        }
      }
      // Process exit is only a transport failure here, never metadata/Unit success evidence.
      if (process.waitFor(10, TimeUnit.MILLISECONDS) && input.available() == 0)
        throw new IOException("reference sender ended early");
    }
    throw new IOException("reference reply unavailable");
  }

  private void command(String value, String expected) throws Exception {
    if (closed) throw new IOException("reference sender already closed");
    output.write((value + "\n").getBytes(StandardCharsets.US_ASCII));
    output.flush();
    await(expected);
  }

  void check() throws Exception { command("check", "REF_CHECKED"); }
  void configure() throws Exception { command("configure", "REF_CONFIGURED"); }

  /** Caller invokes only after DB/schema/readback normal return; unknown never gets retried. */
  void release() throws Exception {
    command("release", "REF_RELEASED");
    if (!process.waitFor(5, TimeUnit.SECONDS) || process.exitValue() != 0)
      throw new IOException("reference return unavailable");
    output.close();
    input.close();
    process.getErrorStream().close();
    closed = true;
  }
}
