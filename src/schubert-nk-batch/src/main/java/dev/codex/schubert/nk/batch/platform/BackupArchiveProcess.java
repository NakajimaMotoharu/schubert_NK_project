package dev.codex.schubert.nk.batch.platform;

import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.ResourceScope;
import java.io.Closeable;
import java.io.IOException;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.*;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.locks.LockSupport;
import java.util.function.LongSupplier;
import org.jspecify.annotations.*;

/**
 * NK-OPS-001; BAK/BKO/OPS009/UI251/SS341 6/343; PG304; PT-OPS-ARCHPROC001..008. Actual fixed tool
 * execution only. File adapter authenticates and borrows all retained FD paths until every
 * child/stdio closes. No artifact admission, manifest, DB success, or retention claim.
 */
@NullMarked
public final class BackupArchiveProcess {
  private static final long DEADLINE = TimeUnit.MINUTES.toNanos(30);
  private final InodeSecurityCalls security;
  private final Start start;
  private final LongSupplier clock;
  private final Optional<MorningParentBudget> parent;

  @FunctionalInterface
  interface Start {
    List<Process> execute(
        List<List<String>> commands, Map<String, String> environment, Optional<Path> output)
        throws IOException;
  }

  public BackupArchiveProcess(InodeSecurityCalls security) {
    this(security, new NativeStart(), System::nanoTime);
  }

  public BackupArchiveProcess(InodeSecurityCalls security, MorningParentBudget parent) {
    this(security, new NativeStart(), System::nanoTime, Optional.of(parent));
  }

  BackupArchiveProcess(InodeSecurityCalls security, Start start, LongSupplier clock) {
    this(security, start, clock, Optional.empty());
  }

  BackupArchiveProcess(
      InodeSecurityCalls security,
      Start start,
      LongSupplier clock,
      Optional<MorningParentBudget> parent) {
    this.security = Objects.requireNonNull(security, "security");
    this.start = Objects.requireNonNull(start, "process start");
    this.clock = Objects.requireNonNull(clock, "clock");
    this.parent = Objects.requireNonNull(parent, "parent budget");
  }

  /**
   * Dedicated fixed Unit/NSS identity is independently established by caller, not this UID claim.
   */
  public void dump(Path dump, Path pgpass, long backupUid) throws IOException {
    if (backupUid < 1 || backupUid > 0xffff_ffffL || security.effectiveUid() != backupUid)
      throw invalid();
    String destination = childPath(dump), passwordFile = childPath(pgpass);
    long began = clock.getAsLong();
    var environment = new HashMap<>(environment());
    environment.putAll(
        Map.of(
            "PGHOST",
            "127.0.0.1",
            "PGPORT",
            "5432",
            "PGUSER",
            "schubert_backup",
            "PGDATABASE",
            "schubert_nk",
            "PGPASSFILE",
            passwordFile,
            "PGCONNECT_TIMEOUT",
            "5"));
    execute(
        List.of(
            List.of(
                "/usr/bin/pg_dump",
                "--format=custom",
                "--no-owner",
                "--no-privileges",
                "--schema=schubert",
                "--schema=schubert_web_session",
                "--schema=schubert_meta",
                "--file=" + destination,
                "schubert_nk")),
        Map.copyOf(environment),
        Optional.empty(),
        new byte[0],
        began);
    execute(
        List.of(List.of("/usr/bin/pg_restore", "--list", destination)),
        environment(),
        Optional.empty(),
        new byte[0],
        began);
  }

  public void configuration(Path directory, Path output, List<String> allowlist)
      throws IOException {
    root();
    byte[] input = names(allowlist);
    long began = clock.getAsLong();
    try {
      execute(List.of(tar(directory)), environment(), Optional.of(held(output)), input, began);
    } finally {
      Arrays.fill(input, (byte) 0);
    }
  }

  /** No plaintext credential archive on disk: tar stdout is a kernel pipe straight to age. */
  public void credentials(Path directory, Path output, Path recipient, List<String> allowlist)
      throws IOException {
    root();
    byte[] input = names(allowlist);
    long began = clock.getAsLong();
    try {
      execute(
          List.of(
              tar(directory),
              List.of("/usr/bin/age", "--encrypt", "--recipients-file", childPath(recipient))),
          environment(),
          Optional.of(held(output)),
          input,
          began);
    } finally {
      Arrays.fill(input, (byte) 0);
    }
  }

  private static List<String> tar(Path directory) throws IOException {
    return List.of(
        "/usr/bin/tar",
        "--create",
        "--format=posix",
        "--numeric-owner",
        "--no-recursion",
        "--null",
        "--verbatim-files-from",
        "--directory=" + childPath(directory),
        "--files-from=-");
  }

  private static Map<String, String> environment() {
    return Map.of("PATH", "/usr/bin:/bin", "LANG", "C", "LC_ALL", "C");
  }

  private void root() throws IOException {
    if (security.effectiveUid() != 0) throw invalid();
  }

  private static Path held(Path path) throws IOException {
    Objects.requireNonNull(path, "held inode");
    if (!path.toString().matches("/proc/self/fd/[1-9][0-9]{0,9}")) throw invalid();
    long descriptor = Long.parseLong(path.toString().substring("/proc/self/fd/".length()));
    if (descriptor < 3 || descriptor > Integer.MAX_VALUE) throw invalid();
    return path;
  }

  private static String childPath(Path path) throws IOException {
    String text = held(path).toString();
    return "/proc/" + ProcessHandle.current().pid() + text.substring("/proc/self".length());
  }

  private static byte[] names(List<String> supplied) throws IOException {
    var files = List.copyOf(Objects.requireNonNull(supplied, "archive allowlist"));
    if (files.isEmpty() || files.size() > 32 || new HashSet<>(files).size() != files.size())
      throw invalid();
    StringBuilder result = new StringBuilder();
    for (String name : files) {
      if (!name.matches("[A-Za-z0-9][A-Za-z0-9._-]{0,63}")) throw invalid();
      result.append(name).append('\0');
    }
    return result.toString().getBytes(StandardCharsets.US_ASCII);
  }

  private void execute(
      List<List<String>> commands,
      Map<String, String> environment,
      Optional<Path> output,
      byte[] input,
      long began)
      throws IOException {
    if (Thread.currentThread().isInterrupted()) throw invalid();
    remaining(began);
    List<Process> processes;
    try {
      processes = Objects.requireNonNull(start.execute(commands, environment, output), "processes");
    } catch (IOException failure) {
      throw invalid();
    }
    try {
      List<StdinOwner> inputs = new ArrayList<>();
      ResourceScope.use(
          () -> terminate(processes),
          () ->
              streams(
                  processes,
                  0,
                  inputs,
                  () -> {
                    if (processes.size() != commands.size()) throw invalid();
                    inputs.getFirst().writeAndClose(input);
                    for (Process process : processes) {
                      long remaining = remaining(began);
                      try {
                        if (!process.waitFor(remaining, TimeUnit.NANOSECONDS)
                            || process.exitValue() != 0) throw invalid();
                      } catch (InterruptedException failure) {
                        Thread.currentThread().interrupt();
                        throw invalid();
                      }
                    }
                    if (Thread.currentThread().isInterrupted()) throw invalid();
                    return Boolean.TRUE;
                  }));
    } catch (IOException failure) {
      throw invalid();
    }
  }

  @FunctionalInterface
  interface Work {
    Boolean run() throws IOException;
  }

  private long remaining(long began) throws IOException {
    long elapsed = clock.getAsLong() - began;
    if (elapsed < 0 || elapsed >= DEADLINE) throw invalid();
    return parent.isPresent()
        ? Math.min(DEADLINE - elapsed, parent.orElseThrow().remainingNanos())
        : DEADLINE - elapsed;
  }

  private static Boolean streams(
      List<Process> processes, int index, List<StdinOwner> inputs, Work work) throws IOException {
    if (index == processes.size()) return work.run();
    Process process = processes.get(index);
    if (process == null) throw invalid();
    var output = process.getInputStream();
    return ResourceScope.use(
        () -> close(output),
        () -> {
          var input = process.getOutputStream();
          var owner = new StdinOwner(input);
          return ResourceScope.use(
              owner::close,
              () -> {
                var error = process.getErrorStream();
                return ResourceScope.use(
                    () -> close(error),
                    () -> {
                      if (output == null || input == null || error == null) throw invalid();
                      inputs.add(owner);
                      return streams(processes, index + 1, inputs, work);
                    });
              });
        });
  }

  private static void close(@Nullable Closeable stream) throws IOException {
    if (stream != null) stream.close();
  }

  private static final class StdinOwner {
    private final @Nullable OutputStream stream;
    private boolean closed;

    StdinOwner(@Nullable OutputStream stream) {
      this.stream = stream;
    }

    void writeAndClose(byte[] bytes) throws IOException {
      var owned = Objects.requireNonNull(stream, "admitted stdin");
      owned.write(bytes);
      close();
    }

    void close() throws IOException {
      if (!closed) {
        closed = true;
        BackupArchiveProcess.close(stream);
      }
    }
  }

  private static void terminate(List<Process> processes) throws IOException {
    // BUG271/SSC091: request every stop first; never release borrowed parent FDs while alive.
    ResourceScope.use(
        () -> holdTerminals(processes),
        () -> {
          terminate(processes, 0);
          return Boolean.TRUE;
        });
  }

  private static void holdTerminals(List<Process> processes) throws IOException {
    var interrupted = new AtomicBoolean(Thread.interrupted());
    try {
      holdTerminals(processes, 0, interrupted);
    } finally {
      if (interrupted.get()) Thread.currentThread().interrupt();
    }
  }

  private static void holdTerminals(List<Process> processes, int index, AtomicBoolean interrupted)
      throws IOException {
    if (index == processes.size()) return;
    ResourceScope.use(
        () -> holdTerminals(processes, index + 1, interrupted),
        () -> {
          Process process = processes.get(index);
          if (process != null) holdTerminal(process, interrupted);
          return Boolean.TRUE;
        });
  }

  private static void holdTerminal(Process process, AtomicBoolean interrupted) {
    // Quarantine, not an extension of the successful-work budget. Fixed Unit/cgroup timeout is
    // mandatory at the caller. Unknown observation is never a reason to free/reuse the capability.
    while (true) {
      try {
        if (!process.isAlive()) break;
        if (process.waitFor(5, TimeUnit.SECONDS)) break;
      } catch (InterruptedException failure) {
        interrupted.set(true);
        Thread.interrupted();
      } catch (RuntimeException | Error first) {
        // Preserve the first unknown primary, as ResourceScope does. Subsequent observations
        // remain quarantined and cannot turn the pending failure into successful termination.
        holdAfterUnknown(process, interrupted);
        throw first;
      }
    }
  }

  private static void holdAfterUnknown(Process process, AtomicBoolean interrupted) {
    while (true) {
      try {
        if (!process.isAlive() || process.waitFor(5, TimeUnit.SECONDS)) return;
      } catch (InterruptedException failure) {
        interrupted.set(true);
        Thread.interrupted();
      } catch (RuntimeException | Error subsequent) {
        backoff(interrupted);
      }
    }
  }

  private static void backoff(AtomicBoolean interrupted) {
    LockSupport.parkNanos(TimeUnit.MILLISECONDS.toNanos(10));
    if (Thread.interrupted()) interrupted.set(true);
  }

  private static void terminate(List<Process> processes, int index) throws IOException {
    if (index == processes.size()) return;
    ResourceScope.use(
        () -> terminate(processes, index + 1),
        () -> {
          Process process = processes.get(index);
          if (process != null && process.isAlive()) {
            process.destroy();
            try {
              if (!process.waitFor(5, TimeUnit.SECONDS)) throw invalid();
            } catch (InterruptedException failure) {
              Thread.currentThread().interrupt();
              throw invalid();
            }
          }
          return Boolean.TRUE;
        });
  }

  private static IOException invalid() {
    return new IOException("backup archive execution failed");
  }

  static final class NativeStart implements Start {
    @FunctionalInterface
    interface Pipeline {
      List<Process> start(List<ProcessBuilder> builders) throws IOException;
    }

    @FunctionalInterface
    interface Pending {
      void hold(Throwable first);
    }

    private final Pipeline pipeline;
    private final Pending pending;

    NativeStart() {
      this(ProcessBuilder::startPipeline);
    }

    NativeStart(Pipeline pipeline) {
      this(pipeline, new PendingHold());
    }

    NativeStart(Pipeline pipeline, Pending pending) {
      this.pipeline = Objects.requireNonNull(pipeline, "pipeline");
      this.pending = Objects.requireNonNull(pending, "pending");
    }

    static final class PendingHold implements Pending {
      private final Runnable pause;

      PendingHold() {
        this(() -> LockSupport.parkNanos(TimeUnit.MILLISECONDS.toNanos(10)));
      }

      PendingHold(Runnable pause) {
        this.pause = Objects.requireNonNull(pause, "pause");
      }

      @Override
      public void hold(Throwable first) {
        // Fixed one-shot Unit only. No acquired handle proves a partly spawned pipeline terminal.
        // Keep every borrowed capability alive until the Unit's whole cgroup is externally stopped.
        // No successful return/rethrow-after-kill claim. Clear interrupts to avoid a busy park
        // loop.
        while (true) {
          Thread.interrupted();
          pause.run();
        }
      }
    }

    @Override
    public List<Process> execute(
        List<List<String>> commands, Map<String, String> environment, Optional<Path> output)
        throws IOException {
      List<ProcessBuilder> builders = new ArrayList<>();
      for (List<String> command : commands) {
        var builder = new ProcessBuilder(command).redirectError(ProcessBuilder.Redirect.DISCARD);
        builder.environment().clear();
        builder.environment().putAll(environment);
        builders.add(builder);
      }
      var last = builders.getLast();
      last.redirectOutput(
          output
              .map(path -> ProcessBuilder.Redirect.to(path.toFile()))
              .orElse(ProcessBuilder.Redirect.DISCARD));
      if (Thread.currentThread().isInterrupted()) throw invalid();
      try {
        return pipeline.start(builders);
      } catch (IOException | RuntimeException | Error first) {
        pending.hold(first);
        // Package PT port may return; Production pending never does. Never report success.
        throw invalid();
      }
    }
  }
}
