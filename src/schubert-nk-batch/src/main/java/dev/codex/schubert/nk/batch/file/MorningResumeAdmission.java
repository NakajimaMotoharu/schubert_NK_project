package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.platform.RootReleaseAdmission;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import dev.codex.schubert.nk.batch.repository.MaintenanceRunState;
import dev.codex.schubert.nk.batch.repository.MorningDatabaseSession;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.ResourceScope;
import java.io.IOException;
import java.util.Objects;
import java.util.UUID;
import java.util.function.Supplier;
import org.jspecify.annotations.NullMarked;

/**
 * Explicit same-run resume under the caller's continuous M. Dedicated DB session/advisory is
 * acquired before the fixed durable graph can be republished; existing references are then checked
 * against that original run/cutoff. Both owners and callback-scoped backup/handoff capability
 * remain held through the continuation. No run is auto-selected and no changed cutoff, stopped
 * Unit, current INVALID, backup result or permit is inferred. NK-BAT-001/NK-OPS-001;
 * OPS009/UI251/SS341§11/343§6.15/SSC055/094; PG345/346/PT-OPS-MRESUME001 onward.
 */
@NullMarked
final class MorningResumeAdmission {
  @FunctionalInterface
  interface Gate {
    void verify() throws IOException;
  }

  @FunctionalInterface
  interface DatabaseWork<T> {
    T execute(MorningDatabaseSession.Access database) throws IOException;
  }

  interface Database {
    <T> T execute(DatabaseWork<T> work) throws IOException;
  }

  @FunctionalInterface
  interface Files {
    MaintenanceRunState resume(UUID runId, UUID nextActivation) throws IOException;

    default void verify(MaintenanceActivation activation) throws IOException {
      throw unavailable();
    }
  }

  @FunctionalInterface
  interface FileWork<T> {
    T execute(Files files) throws IOException;
  }

  interface Originals {
    <T> T execute(FileWork<T> work) throws IOException;
  }

  private final Gate root;
  private final Database database;
  private final Originals originals;
  private final Supplier<UUID> identities;

  static MorningResumeAdmission create(
      RootStartupContext context, RootStartupContext.Snapshot expected) throws IOException {
    Objects.requireNonNull(context, "Morning root context");
    Objects.requireNonNull(expected, "Morning root identity");
    if (expected.service() != RootStartupContext.Service.MORNING) throw unavailable();
    context.recheck(expected);
    var release = RootReleaseAdmission.create(context, expected);
    var session =
        new MorningDatabaseSession(
            "jdbc:postgresql://127.0.0.1:5432/schubert_nk", context, expected, release);
    return new MorningResumeAdmission(
        () -> context.recheck(expected),
        new Database() {
          @Override
          public <T> T execute(DatabaseWork<T> work) throws IOException {
            Objects.requireNonNull(work, "dedicated DB work");
            var credentials = MorningNewRunAdmission.openCredentials();
            return ResourceScope.use(
                credentials::close,
                () -> {
                  var reader =
                      new RootBatchCredentialReader(credentials, LinuxInodeSecurity.create());
                  return session.execute(reader.read(), work::execute);
                });
          }
        },
        new Originals() {
          @Override
          public <T> T execute(FileWork<T> work) throws IOException {
            Objects.requireNonNull(work, "owned run-file work");
            return MaintenanceRunFiles.create()
                .execute(
                    files ->
                        work.execute(
                            new Files() {
                              public MaintenanceRunState resume(UUID runId, UUID activation)
                                  throws IOException {
                                return files.resume(runId, activation);
                              }

                              public void verify(MaintenanceActivation activation)
                                  throws IOException {
                                context.recheck(expected);
                                files.observe(activation);
                                context.recheck(expected);
                              }
                            }));
          }
        },
        UUID::randomUUID);
  }

  MorningResumeAdmission(
      Gate root, Database database, Originals originals, Supplier<UUID> identities) {
    this.root = Objects.requireNonNull(root, "Morning root gate");
    this.database = Objects.requireNonNull(database, "dedicated batch DB owner");
    this.originals = Objects.requireNonNull(originals, "durable original owner");
    this.identities = Objects.requireNonNull(identities, "next activation source");
  }

  <T> T execute(UUID runId, MorningNewRunAdmission.Continuation<T> continuation)
      throws IOException {
    Objects.requireNonNull(runId, "explicit resume run");
    Objects.requireNonNull(continuation, "same-run continuation");
    return executeOwned(runId, (state, ignored) -> continuation.execute(state));
  }

  <T> T executeOwned(UUID runId, MorningNewRunAdmission.OwnedContinuation<T> continuation)
      throws IOException {
    Objects.requireNonNull(continuation, "owned same-run continuation");
    return executeVerified(
        runId, (state, database, ignored) -> continuation.execute(state, database));
  }

  <T> T executeVerified(UUID runId, MorningNewRunAdmission.VerifiedContinuation<T> continuation)
      throws IOException {
    Objects.requireNonNull(runId, "explicit resume run");
    Objects.requireNonNull(continuation, "owned same-run continuation");
    root.verify();
    UUID nextActivation = Objects.requireNonNull(identities.get(), "next activation identity");
    if (runId.equals(nextActivation)) throw unavailable();
    T result =
        database.execute(
            databaseAccess -> {
              root.verify();
              return originals.execute(
                  files -> {
                    root.verify();
                    MaintenanceRunState state =
                        Objects.requireNonNull(
                            files.resume(runId, nextActivation), "resumed durable original");
                    if (!state.activation().run().id().equals(runId)) throw unavailable();
                    root.verify();
                    databaseAccess.requireConsistent(state.activation().run());
                    root.verify();
                    long ownerThread = Thread.currentThread().threadId();
                    var alive = new java.util.concurrent.atomic.AtomicBoolean(true);
                    T completed;
                    try {
                      completed =
                          Objects.requireNonNull(
                              continuation.execute(
                                  state,
                                  databaseAccess,
                                  () -> {
                                    if (!alive.get()
                                        || Thread.currentThread().threadId() != ownerThread)
                                      throw unavailable();
                                    root.verify();
                                    files.verify(state.activation());
                                    root.verify();
                                  }),
                              "Morning continuation");
                    } finally {
                      alive.set(false);
                    }
                    root.verify();
                    return completed;
                  });
            });
    root.verify();
    return Objects.requireNonNull(result, "Morning resume result");
  }

  private static IOException unavailable() {
    return new IOException("Morning same-run resume unavailable");
  }
}
