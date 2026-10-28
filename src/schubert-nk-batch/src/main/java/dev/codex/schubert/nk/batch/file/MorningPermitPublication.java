package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;

import dev.codex.schubert.nk.batch.file.StartupPermitRecords.Epoch;
import dev.codex.schubert.nk.batch.file.StartupPermitRecords.Permit;
import dev.codex.schubert.nk.batch.file.StartupPermitRecords.State;
import dev.codex.schubert.nk.batch.platform.MorningParentBudget;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.batch.repository.MaintenanceRunState;
import dev.codex.schubert.nk.batch.repository.MorningDatabaseSession;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;

/**
 * SSC136: one original-continuation owner, allocated before A and borrowed by Main. Publication
 * commits only after Main's nested closes and A close; failures revoke under the still-held M/DB/
 * original. Root admission/normal S3 launch is a separate gate. NK-OPS-001 OPS009 UI251 SS343§6.17
 * PT295 ISSPUB001..006. No capability is returned outside the original continuation.
 */
@NullMarked
final class MorningPermitPublication {
  interface Intents extends AutoCloseable {
    void begin() throws IOException;

    void verify() throws IOException;

    void retire() throws IOException;

    void quarantine() throws IOException;

    @Override
    void close() throws IOException;
  }

  interface Store extends AutoCloseable {
    StartupPermitFiles files();

    @Override
    void close() throws IOException;
  }

  @FunctionalInterface
  interface OpenStore {
    Store open() throws IOException;
  }

  @FunctionalInterface
  interface OpenIntent {
    Intents open() throws IOException;
  }

  @FunctionalInterface
  interface Gate {
    void verify() throws IOException;
  }

  @FunctionalInterface
  interface Retain {
    void indefinitely();
  }

  private final Intents intents;
  private final OpenStore stores;
  private final OpenIntent recoveryIntents;
  private final Gate gate;
  private final Retain retainedRetain;
  private final long thread = Thread.currentThread().threadId();
  private Optional<Epoch> invalid = Optional.empty();
  private Optional<Epoch> retainedExpected = Optional.empty();
  private Optional<Permit> attempted = Optional.empty();
  private boolean started;
  private boolean issued;
  private boolean committed;
  private boolean aborted;

  MorningPermitPublication(
      Intents intents, OpenStore stores, OpenIntent recoveryIntents, Gate gate, Retain retain) {
    this.intents = Objects.requireNonNull(intents);
    this.stores = Objects.requireNonNull(stores);
    this.recoveryIntents = Objects.requireNonNull(recoveryIntents);
    this.gate = Objects.requireNonNull(gate);
    this.retainedRetain = Objects.requireNonNull(retain);
  }

  static MorningPermitPublication create(
      RootStartupContext root,
      RootStartupContext.Snapshot snapshot,
      MorningParentBudget budget,
      MaintenanceRunState state,
      MorningDatabaseSession.Access database,
      MorningNewRunAdmission.OriginalProof original)
      throws IOException {
    Gate gate =
        () -> {
          budget.requireWithin();
          root.recheck(snapshot);
          original.verify();
          database.recheckConsistent(state.activation().run());
          budget.requireWithin();
          root.recheck(snapshot);
        };
    // BUG390: this owner is allocated BEFORE backup begins. Do not demand its completed pair here.
    budget.requireWithin();
    root.recheck(snapshot);
    original.verify();
    budget.requireWithin();
    OpenIntent intents = () -> nativeIntent(root, snapshot);
    OpenStore stores = MorningPermitPublication::nativeStore;
    Retain retain = MorningPermitPublication::retainNative;
    return ResourceScope.handoff(
        intents::open,
        Intents::close,
        opened -> new MorningPermitPublication(opened, stores, intents, gate, retain));
  }

  void bind(Epoch epoch) throws IOException {
    owner();
    require(invalid.isEmpty() && epoch.state() == State.INVALID);
    invalid = Optional.of(epoch);
    retainedExpected = Optional.of(epoch);
  }

  Epoch expected() throws IOException {
    owner();
    return retainedExpected.orElseThrow(() -> new IOException("publication epoch unavailable"));
  }

  Epoch issue(Permit permit, StartupPermitFiles.IssueProof proof) throws IOException {
    Objects.requireNonNull(permit);
    Objects.requireNonNull(proof);
    owner();
    require(!started && !committed && !aborted && invalid.isPresent());
    attempted = Optional.of(permit);
    started = true; // even begin/force/close uncertainty belongs to this supervised attempt
    intents.begin();
    gate.verify();
    int[] phase = {0};
    Epoch result =
        ResourceScope.acquire(
            stores::open,
            Store::close,
            store ->
                store
                    .files()
                    .issue(
                        invalid.orElseThrow(),
                        permit,
                        (boundary, current) -> {
                          owner();
                          // PG-D804/2476: ordinal failure precedes any phase mutation.
                          int observedPhase = boundary.ordinal();
                          int expectedPhase = phase[0];
                          phase[0]++;
                          require(observedPhase == expectedPhase);
                          if (boundary == StartupPermitFiles.IssuePhase.AFTER_READBACK) {
                            require(current.state() == State.ISSUED);
                            store.files().verifyPublication(current, permit);
                            retainedExpected =
                                Optional.of(current); // only after actual exact issued readback
                          } else require(current.equals(invalid.orElseThrow()));
                          intents.verify();
                          gate.verify();
                          proof.verify(boundary, current);
                          gate.verify();
                          intents.verify();
                        }));
    require(phase[0] == 3 && result.equals(retainedExpected.orElseThrow()));
    issued = true;
    gate.verify();
    return result;
  }

  /** Only the owner calls this AFTER normal A and all subordinate resource closure. */
  void commit() throws IOException {
    owner();
    require(issued && !committed);
    gate.verify();
    intents.verify();
    ResourceScope.acquire(
        stores::open,
        Store::close,
        store -> {
          store.files().verifyPublication(retainedExpected.orElseThrow(), attempted.orElseThrow());
          return true;
        });
    gate.verify();
    intents.retire();
    intents.close();
    committed = true;
  }

  /**
   * Called inside the original scope before normal unwind, including after intent close failure.
   */
  void abort() {
    if (aborted) return;
    if (!started) {
      try {
        intents.close();
        aborted = true;
      } catch (IOException | RuntimeException | Error unknown) {
        retain();
      }
      return;
    }
    try {
      owner();
      // Fresh fixed handles; consumed close descriptors are never reused.
      ResourceScope.acquire(
          recoveryIntents::open,
          Intents::close,
          quarantine -> {
            quarantine.quarantine();
            return true;
          });
      ResourceScope.acquire(
          stores::open,
          Store::close,
          store -> {
            var revoked = store.files().revoke(invalid.orElseThrow(), attempted.orElseThrow());
            require(
                revoked.equals(invalid.orElseThrow()) && store.files().current().equals(revoked));
            return true;
          });
      retainedExpected = invalid;
      intents.close();
      aborted = true;
    } catch (IOException | RuntimeException | Error unknown) {
      retain();
    }
  }

  private void owner() throws IOException {
    require(thread == Thread.currentThread().threadId());
  }

  private void retain() {
    retainedRetain.indefinitely();
    throw new IllegalStateException("publication owner retention returned");
  }

  private static Intents nativeIntent(RootStartupContext root, RootStartupContext.Snapshot snapshot)
      throws IOException {
    return ResourceScope.handoff(
        () -> BackupStartIntentFiles.createPublication(root, snapshot),
        BackupStartIntentFiles::close,
        files ->
            new Intents() {
              private Optional<BackupStartIntentFiles.Intent> token = Optional.empty();

              public void begin() throws IOException {
                token = Optional.of(files.begin());
              }

              public void verify() throws IOException {
                files.requirePresent(token.orElseThrow());
              }

              public void retire() throws IOException {
                files.retire(token.orElseThrow());
              }

              public void quarantine() throws IOException {
                files.quarantinePublication();
              }

              public void close() throws IOException {
                files.close();
              }
            });
  }

  @edu.umd.cs.findbugs.annotations.SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = edu.umd.cs.findbugs.annotations.SuppressMatchType.EXACT,
      justification = "SS343 SSC136 fixed startup root, no caller-selected path")
  private static Store nativeStore() throws IOException {
    var calls = LinuxDirectoryCalls.create();
    Path path = Path.of("/run/schubert-nk/startup");
    return ResourceScope.handoff(
        () -> OwnedTransferDirectory.open(calls, path),
        OwnedTransferDirectory::close,
        root -> {
          var files = new StartupPermitFiles(root, LinuxInodeSecurity.create());
          return new Store() {
            public StartupPermitFiles files() {
              return files;
            }

            public void close() throws IOException {
              root.close();
            }
          };
        });
  }

  private static void retainNative() {
    for (; ; ) {
      java.util.concurrent.locks.LockSupport.parkNanos(
          java.util.concurrent.TimeUnit.SECONDS.toNanos(1));
      Thread.interrupted(); // preserve ownership until the existing external hard deadline
    }
  }
}
