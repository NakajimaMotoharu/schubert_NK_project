package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.platform.RootReleaseAdmission;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.MaintenanceRunState;
import dev.codex.schubert.nk.batch.repository.MorningDatabaseSession;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.ServiceCredentialLocation;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.nio.file.Path;
import java.time.Clock;
import java.time.temporal.ChronoUnit;
import java.util.Objects;
import java.util.UUID;
import java.util.function.Supplier;
import org.jspecify.annotations.NullMarked;

/**
 * Fresh-run admission under the caller's continuous M. A dedicated DB session owns its advisory
 * lock across the three-reference absence check, durable original start and the entire supplied
 * continuation. The run-file scope also remains open until that continuation returns. This class
 * never chooses a resume target, stops Units, acquires A, invalidates current or grants a permit;
 * the external Morning main must remain fail-closed until the full parent is connected. NK-BAT-001
 * /NK-OPS-001; OPS009/UI251/SS341§3-5/343§6.15/SSC055/094; PG343/PT-OPS-MNEW001 onward.
 */
@NullMarked
final class MorningNewRunAdmission {
  @FunctionalInterface
  interface Gate {
    void verify() throws IOException;
  }

  @FunctionalInterface
  interface References {
    void requireUnused(BatchRun run) throws IOException;
  }

  @FunctionalInterface
  interface DatabaseWork<T> {
    T execute(References references) throws IOException;
  }

  interface Database {
    <T> T execute(DatabaseWork<T> work) throws IOException;
  }

  @FunctionalInterface
  interface Files {
    MaintenanceRunState start(BatchRun run, UUID activation) throws IOException;
  }

  @FunctionalInterface
  interface FileWork<T> {
    T execute(Files files) throws IOException;
  }

  interface Originals {
    <T> T execute(FileWork<T> work) throws IOException;
  }

  @FunctionalInterface
  interface Continuation<T> {
    T execute(MaintenanceRunState state) throws IOException;
  }

  private final Gate root;
  private final Database database;
  private final Originals originals;
  private final Clock clock;
  private final Supplier<UUID> identities;

  static MorningNewRunAdmission create(
      RootStartupContext context, RootStartupContext.Snapshot expected) throws IOException {
    Objects.requireNonNull(context, "Morning root context");
    Objects.requireNonNull(expected, "Morning root identity");
    if (expected.service() != RootStartupContext.Service.MORNING) throw unavailable();
    context.recheck(expected);
    var release = RootReleaseAdmission.create(context, expected);
    var session =
        new MorningDatabaseSession(
            "jdbc:postgresql://127.0.0.1:5432/schubert_nk", context, expected, release);
    return new MorningNewRunAdmission(
        () -> context.recheck(expected),
        new Database() {
          @Override
          public <T> T execute(DatabaseWork<T> work) throws IOException {
            Objects.requireNonNull(work, "dedicated DB work");
            var credentials = openCredentials();
            return ResourceScope.use(
                credentials::close,
                () -> {
                  var reader =
                      new RootBatchCredentialReader(credentials, LinuxInodeSecurity.create());
                  return session.execute(reader.read(), db -> work.execute(db::requireUnused));
                });
          }
        },
        new Originals() {
          @Override
          public <T> T execute(FileWork<T> work) throws IOException {
            Objects.requireNonNull(work, "owned run-file work");
            return MaintenanceRunFiles.create().execute(files -> work.execute(files::start));
          }
        },
        Clock.systemUTC(),
        UUID::randomUUID);
  }

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SS343 6.15 fixes the root Morning systemd private credential namespace")
  static OwnedTransferDirectory openCredentials() throws IOException {
    Path path;
    try {
      path = ServiceCredentialLocation.read(System.getenv()).directory();
    } catch (IllegalArgumentException invalid) {
      throw unavailable();
    }
    if (!path.equals(Path.of("/run/credentials/schubert-nk-morning-controller.service")))
      throw unavailable();
    return OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), path);
  }

  MorningNewRunAdmission(
      Gate root, Database database, Originals originals, Clock clock, Supplier<UUID> identities) {
    this.root = Objects.requireNonNull(root, "Morning root gate");
    this.database = Objects.requireNonNull(database, "dedicated batch DB owner");
    this.originals = Objects.requireNonNull(originals, "durable original owner");
    this.clock = Objects.requireNonNull(clock, "UTC clock");
    this.identities = Objects.requireNonNull(identities, "fresh identities");
  }

  <T> T execute(Continuation<T> continuation) throws IOException {
    Objects.requireNonNull(continuation, "same-run continuation");
    root.verify();
    var run =
        new BatchRun(
            Objects.requireNonNull(identities.get(), "new run identity"),
            Objects.requireNonNull(clock.instant(), "run cutoff").truncatedTo(ChronoUnit.MICROS));
    var activation = Objects.requireNonNull(identities.get(), "new activation identity");
    if (run.id().equals(activation)) throw unavailable();
    T result =
        database.execute(
            references -> {
              root.verify();
              references.requireUnused(run);
              root.verify();
              return originals.execute(
                  files -> {
                    root.verify();
                    var state =
                        Objects.requireNonNull(files.start(run, activation), "started original");
                    if (!state.activation().run().equals(run)
                        || !state.activation().id().equals(activation)
                        || state.completion().isPresent()) throw unavailable();
                    root.verify();
                    T completed =
                        Objects.requireNonNull(continuation.execute(state), "Morning continuation");
                    root.verify();
                    return completed;
                  });
            });
    root.verify();
    return Objects.requireNonNull(result, "Morning new-run result");
  }

  private static IOException unavailable() {
    return new IOException("Morning new-run admission unavailable");
  }
}
