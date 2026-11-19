package dev.codex.schubert.nk.batch.platform;

import dev.codex.schubert.nk.api.bootstrap.JdbcFailureGraph;
import java.io.Closeable;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Fixed NSS name lookup, independent of the file being admitted. NK-OPS-001; OPS-009/UI251; SS343
 * 6.12; SSC-049/063, PG-D-155/174, BUG195/YKT154; PT-OPS-GID-001..008/017052. No shell,
 * enumeration, inherited secret environment, raw stdout diagnostic or target-derived fallback GID.
 */
@NullMarked
public final class ConfigurationGroupResolver {
  private static final char GROUP_FIELD_SEPARATOR = ':';

  private static final byte[] PREFIX = "schubert:".getBytes(StandardCharsets.US_ASCII);
  private final Start start;

  @FunctionalInterface
  interface Start {
    Process execute(List<String> command) throws IOException;
  }

  public ConfigurationGroupResolver() {
    this(command -> NativeProcess.builder(command).start());
  }

  ConfigurationGroupResolver(Start start) {
    this.start = Objects.requireNonNull(start, "group lookup start");
  }

  /** Returns only the canonical positive unsigned32 GID after all owned stdio has closed. */
  public long resolve() throws IOException {
    require(!Thread.currentThread().isInterrupted());
    byte[] bytes = new byte[65537];
    try {
      Process process =
          Objects.requireNonNull(
              start.execute(List.of("/usr/bin/getent", "group", "schubert")), "lookup process");
      long[] result = {0};
      scope(
          () -> terminate(process),
          () -> {
            var output = process.getInputStream();
            scope(
                () -> finish(output),
                () -> {
                  var input = process.getOutputStream();
                  scope(
                      () -> finish(input),
                      () -> {
                        var error = process.getErrorStream();
                        scope(
                            () -> finish(error),
                            () -> {
                              Objects.requireNonNull(output, "lookup stdout");
                              Objects.requireNonNull(input, "lookup stdin");
                              Objects.requireNonNull(error, "lookup stderr");
                              var readers = Executors.newVirtualThreadPerTaskExecutor();
                              scope(
                                  readers::close,
                                  () -> {
                                    var pending = readers.submit(() -> read(output, bytes));
                                    // Retain TERM-before-join: no reader writes into the buffer
                                    // after it is wiped.
                                    scope(
                                        () -> terminate(process),
                                        () -> {
                                          require(process.waitFor(5, TimeUnit.SECONDS));
                                          require(process.exitValue() == 0);
                                          result[0] = parse(bytes, readResult(pending));
                                        });
                                  });
                            });
                      });
                });
          });
      require(!Thread.currentThread().isInterrupted());
      return result[0];
    } catch (InterruptedException failure) {
      Thread.currentThread().interrupt();
      JdbcFailureGraph.preserveFatal(failure);
      throw unavailable();
    } catch (IOException failure) {
      // Normalize known I/O only after all owned scopes have finished.
      throw unavailable();
    } finally {
      Arrays.fill(bytes, (byte) 0);
    }
  }

  // PG174/SSC063/BUG195: checked lookup IO is not the StopGate exception contract.
  private static void scope(Closeable release, ProcessResourceScope.QueryWork work)
      throws IOException, InterruptedException {
    try {
      work.run();
    } catch (IOException | InterruptedException | RuntimeException | Error primary) {
      try {
        release.close();
      } catch (IOException | RuntimeException | Error cleanup) {
        if ((primary instanceof IOException || primary instanceof InterruptedException)
            && !(cleanup instanceof IOException)) {
          if (primary instanceof InterruptedException) Thread.currentThread().interrupt();
          throw cleanup;
        }
        primary.addSuppressed(unavailable());
      }
      throw primary;
    }
    release.close();
  }

  private static void terminate(Process process) {
    if (process.isAlive()) process.destroy();
  }

  private static void finish(@Nullable Closeable resource) throws IOException {
    if (resource != null) resource.close();
  }

  private static int readResult(Future<Integer> pending) throws IOException, InterruptedException {
    try {
      return pending.get();
    } catch (ExecutionException failure) {
      Throwable cause = Objects.requireNonNull(failure.getCause(), "reader failure");
      if (cause instanceof IOException) throw unavailable();
      if (cause instanceof RuntimeException) {
        JdbcFailureGraph.preserveFatal(cause);
        throw new IllegalStateException("configuration group reader failed");
      }
      // The owned Callable invokes only read: IOException, unchecked exception or Error.
      throw (Error) cause;
    }
  }

  private static int read(InputStream input, byte[] bytes) throws IOException {
    int position = 0;
    while (position < bytes.length) {
      int remaining = bytes.length - position;
      int count = input.read(bytes, position, remaining);
      if (count == -1) break;
      require(count > 0 && count <= remaining);
      position += count;
    }
    return position;
  }

  /** Package-only byte parser; caller owns and clears the full buffer on every exit. */
  static long parse(byte[] bytes, int length) throws IOException {
    Objects.requireNonNull(bytes, "group bytes");
    require(length >= 13 && length <= 65536 && length <= bytes.length);
    require(Arrays.equals(bytes, 0, PREFIX.length, PREFIX, 0, PREFIX.length));
    require(bytes[length - 1] == '\n');
    int[] separators = new int[3];
    int count = 0;
    for (int index = 0; index < length - 1; index++) {
      int value = Byte.toUnsignedInt(bytes[index]);
      require(value >= 32 && value != 127);
      if (value == GROUP_FIELD_SEPARATOR) {
        if (count < separators.length) separators[count] = index;
        count++;
      }
    }
    require(count == 3);
    int begin = separators[1] + 1;
    int end = separators[2];
    int digits = end - begin;
    require(digits >= 1 && digits <= 10);
    require(bytes[begin] != '0');
    long group = 0;
    for (int index = begin; index < end; index++) {
      int value = Byte.toUnsignedInt(bytes[index]);
      require(value >= '0' && value <= '9');
      group = group * 10 + value - '0';
    }
    // Nonempty ASCII digits and a nonzero leading digit already establish the lower bound.
    require(group <= 0xffff_ffffL);
    return group;
  }

  private static void require(boolean accepted) throws IOException {
    if (!accepted) throw unavailable();
  }

  private static IOException unavailable() {
    return new IOException("configuration group lookup failed");
  }

  static final class NativeProcess {
    private NativeProcess() {}

    static ProcessBuilder builder(List<String> command) {
      var builder = new ProcessBuilder(command).redirectError(ProcessBuilder.Redirect.DISCARD);
      var environment = builder.environment();
      environment.clear();
      environment.putAll(Map.of("PATH", "/usr/bin:/bin", "LANG", "C", "LC_ALL", "C"));
      return builder;
    }
  }
}
