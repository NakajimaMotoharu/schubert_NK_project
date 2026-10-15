package dev.codex.schubert.nk.api.maintenance;

import static dev.codex.schubert.nk.api.file.AesCredentialFile.CONTEXT_CURRENT;
import static dev.codex.schubert.nk.api.file.AesCredentialFile.CONTEXT_PREVIOUS;
import static dev.codex.schubert.nk.api.file.AesCredentialFile.RESPONSE_CURRENT;
import static dev.codex.schubert.nk.api.file.AesCredentialFile.RESPONSE_PREVIOUS;

import dev.codex.schubert.nk.api.file.AesCredentialFile;
import dev.codex.schubert.nk.api.file.InspectorCredentialException;
import dev.codex.schubert.nk.api.file.InspectorCredentialLoader;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.messaging.outbound.SqlConnectionProvider;
import dev.codex.schubert.nk.api.security.AuthContextCodec;
import dev.codex.schubert.nk.api.security.ContextHash;
import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import java.io.IOException;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Arrays;
import java.util.EnumMap;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.LongSupplier;
import org.jspecify.annotations.NullMarked;

/**
 * Single-use synchronous private-inspector composition. Owns loaded keys, copies and codecs;
 * borrows reader root and connection provider. No main, HTTP/JMS, root closure or parent gate.
 * NK-DAT-001; DAT-009/OPS-009/MQ-008; UI212/241/251; SS324/341/343 6.5; QA-046/SSC-049/PG-D-135;
 * PT-DB-INBOX-141..152.
 */
@NullMarked
public final class InspectorProcess {
  private final CredentialSource credentials;
  private final SqlConnectionProvider connections;
  private final Set<String> fingerprintVersions;
  private final LongSupplier clock;
  private final Optional<MaintenanceOwnerFrame.Guard> parentGuard;
  private final AtomicBoolean started = new AtomicBoolean();

  public InspectorProcess(
      InspectorCredentialLoader credentials,
      SqlConnectionProvider connections,
      Set<String> fingerprintVersions) {
    this(
        Objects.requireNonNull(credentials, "credentials")::load,
        connections,
        fingerprintVersions,
        System::nanoTime);
  }

  InspectorProcess(
      CredentialSource credentials,
      SqlConnectionProvider connections,
      Set<String> fingerprintVersions,
      LongSupplier clock) {
    this(credentials, connections, fingerprintVersions, clock, Optional.empty());
  }

  /** Native assembly borrows the same authenticated owner throughout keys, SQL and receipts. */
  public static InspectorProcess withParent(
      InspectorCredentialLoader credentials,
      SqlConnectionProvider connections,
      Set<String> fingerprintVersions,
      MaintenanceOwnerFrame.Guard guard) {
    return new InspectorProcess(
        Objects.requireNonNull(credentials, "credentials")::load,
        connections,
        fingerprintVersions,
        System::nanoTime,
        Optional.of(Objects.requireNonNull(guard, "parent guard")));
  }

  InspectorProcess(
      CredentialSource credentials,
      SqlConnectionProvider connections,
      Set<String> fingerprintVersions,
      LongSupplier clock,
      Optional<MaintenanceOwnerFrame.Guard> parentGuard) {
    this.parentGuard = Objects.requireNonNull(parentGuard, "parent guard profile");
    this.credentials = Objects.requireNonNull(credentials, "credentials");
    this.connections = Objects.requireNonNull(connections, "connections");
    this.clock = Objects.requireNonNull(clock, "clock");
    this.fingerprintVersions = InspectorSettings.requireVersions(fingerprintVersions);
  }

  /**
   * Re-entry is forbidden even after failure. Resume with a new instance and the same persisted
   * run. The returned internal status is usable only after the caller's remaining gates close.
   */
  public InspectionExecution execute(InspectionRun run)
      throws InspectorCredentialException, NoSuchAlgorithmException {
    Objects.requireNonNull(run, "run");
    if (!started.compareAndSet(false, true))
      throw new IllegalStateException("inspector instance has already executed");
    if (Thread.currentThread().isInterrupted())
      return new InspectionExecution(InspectionExecution.Status.INTERRUPTED, Optional.empty());
    checkParent();
    try (var keys = new OwnedKeys()) {
      keys.load(
          id -> {
            checkParent();
            return credentials.load(id);
          });
      checkParent();
      // Nullable previous values occur only at these existing, explicitly paired codec boundaries.
      try (var contexts =
              new AuthContextCodec(
                  keys.version(CONTEXT_CURRENT).orElseThrow(), keys.requiredCopy(CONTEXT_CURRENT),
                  keys.version(CONTEXT_PREVIOUS).orElse(null), keys.copies.get(CONTEXT_PREVIOUS));
          var snapshots =
              new ResponseSnapshotCodec(
                  keys.version(RESPONSE_CURRENT).orElseThrow(), keys.requiredCopy(RESPONSE_CURRENT),
                  keys.version(RESPONSE_PREVIOUS).orElse(null),
                      keys.copies.get(RESPONSE_PREVIOUS))) {
        var auth = new AuthenticationInboxInspector(snapshots, contexts, new ContextHash());
        var queries = new NonAuthenticationInboxInspector(snapshots);
        var cleanup =
            parentGuard.isPresent()
                ? new InboxCleanup(
                    connections, auth, queries, fingerprintVersions, parentGuard.orElseThrow())
                : new InboxCleanup(connections, auth, queries, fingerprintVersions);
        var result = new InspectionRunExecutor(cleanup, clock, parentGuard).run(run);
        checkParent();
        return result;
      }
    }
  }

  private void checkParent() throws InspectorCredentialException {
    if (parentGuard.isPresent())
      try {
        parentGuard.orElseThrow().check();
      } catch (IOException unavailable) {
        throw new InspectorCredentialException();
      }
  }

  @FunctionalInterface
  interface CredentialSource {
    Optional<InspectorAesCredential> load(AesCredentialFile id) throws InspectorCredentialException;
  }

  /** Operation-local ownership, never published or closed concurrently with a codec. */
  private static final class OwnedKeys implements AutoCloseable {
    private final EnumMap<AesCredentialFile, InspectorAesCredential> materials =
        new EnumMap<>(AesCredentialFile.class);
    private final EnumMap<AesCredentialFile, byte[]> copies =
        new EnumMap<>(AesCredentialFile.class);

    void load(CredentialSource source) throws InspectorCredentialException {
      for (var id : AesCredentialFile.values()) {
        var loaded = source.load(id);
        if (loaded.isEmpty()) {
          if (!id.optional()) throw new InspectorCredentialException();
        } else {
          var material = loaded.orElseThrow();
          materials.put(
              id, material); // Own before copy so any subsequent failure still destroys it.
          try {
            copies.put(id, material.copyKey());
          } catch (IllegalStateException closed) {
            throw new InspectorCredentialException();
          }
        }
      }
      if (version(CONTEXT_CURRENT).equals(version(CONTEXT_PREVIOUS))
          || version(RESPONSE_CURRENT).equals(version(RESPONSE_PREVIOUS)))
        throw new InspectorCredentialException();
      for (var context : List.of(CONTEXT_CURRENT, CONTEXT_PREVIOUS)) {
        byte[] contextKey = copies.get(context);
        if (contextKey == null) continue;
        for (var response : List.of(RESPONSE_CURRENT, RESPONSE_PREVIOUS)) {
          byte[] responseKey = copies.get(response);
          if (responseKey != null && MessageDigest.isEqual(contextKey, responseKey))
            throw new InspectorCredentialException();
        }
      }
    }

    Optional<String> version(AesCredentialFile id) {
      return Optional.ofNullable(materials.get(id)).map(InspectorAesCredential::version);
    }

    byte[] requiredCopy(AesCredentialFile id) {
      return Objects.requireNonNull(copies.get(id), "required credential copy");
    }

    @Override
    public void close() {
      for (byte[] copy : copies.values()) Arrays.fill(copy, (byte) 0);
      for (var material : materials.values()) material.close();
      copies.clear();
      materials.clear();
    }
  }
}
