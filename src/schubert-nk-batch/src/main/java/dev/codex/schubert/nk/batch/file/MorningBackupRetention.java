package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;

import dev.codex.schubert.nk.batch.backup.BackupManifest;
import dev.codex.schubert.nk.batch.repository.MorningDatabaseSession;
import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.nio.file.Path;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.SortedMap;
import java.util.TreeMap;
import org.jspecify.annotations.NullMarked;

/** NK-OPS-001/BAK001/OPS009/UI251; SS341§6.3/343§6.17/SSC133; ISSRET001..008. */
@NullMarked
final class MorningBackupRetention {
  enum Mode {
    NEW_SUCCESS,
    REUSED_SUCCESS,
    FAILED
  }

  @FunctionalInterface
  interface Work<T> {
    T execute(MorningBackupRetention retained) throws IOException;
  }

  static final class Result {
    final Mode mode;
    final Optional<BackupManifest> current;
    final Optional<String> currentSha256;
    final List<String> before;
    final List<String> after;
    final List<String> deleted;
    final SortedMap<String, String> deletedSha256;
    final SortedMap<String, String> protectedNames;
    final SortedMap<String, BackupManifest> kept;
    final SortedMap<String, BackupArtifactVerifier.BundleSnapshot> files;
    final EnvironmentInodePolicy.Metadata root;

    private Result(
        Mode mode,
        Optional<BackupManifest> current,
        Optional<String> currentSha256,
        List<String> before,
        List<String> after,
        List<String> deleted,
        Map<String, String> deletedSha256,
        Map<String, String> protectedNames,
        Map<String, BackupManifest> kept,
        Map<String, BackupArtifactVerifier.BundleSnapshot> files,
        EnvironmentInodePolicy.Metadata root) {
      this.mode = mode;
      this.current = current;
      this.currentSha256 = currentSha256;
      this.before = List.copyOf(before);
      this.after = List.copyOf(after);
      this.deleted = List.copyOf(deleted);
      this.deletedSha256 = Collections.unmodifiableSortedMap(new TreeMap<>(deletedSha256));
      this.protectedNames = Collections.unmodifiableSortedMap(new TreeMap<>(protectedNames));
      this.kept = Collections.unmodifiableSortedMap(new TreeMap<>(kept));
      this.files = Collections.unmodifiableSortedMap(new TreeMap<>(files));
      this.root = root;
    }

    @Override
    public String toString() {
      return "RetentionResult[observations=<redacted>]";
    }
  }

  private final BackupManifestReader reader;
  private final BackupArtifactVerifier verifier;
  private final MorningDatabaseSession.Access database;
  private final MaintenanceOwnerFrame.Guard owner;
  private final long started;
  private final long thread = Thread.currentThread().threadId();
  private Optional<Result> retainedResult = Optional.empty();

  MorningBackupRetention(
      BackupManifestReader reader,
      BackupArtifactVerifier verifier,
      MorningDatabaseSession.Access database,
      MaintenanceOwnerFrame.Guard owner,
      long started) {
    this.reader = Objects.requireNonNull(reader);
    this.verifier = Objects.requireNonNull(verifier);
    this.database = Objects.requireNonNull(database);
    this.owner = Objects.requireNonNull(owner);
    this.started = started;
  }

  /**
   * BUG897/ISSRET009: same writable fixed-root adapter as MorningBackupArtifacts publication.
   * Host-view inspection ports remain read-only; the enclosing Root/M/A guard owns mutations.
   */
  static dev.codex.schubert.nk.storage.DirectoryCalls directoryCalls() {
    return dev.codex.schubert.nk.storage.LinuxDirectoryCalls.create();
  }

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SS343 fixed borrowed backup root; ISSRET/native real coverage")
  static <T> T use(
      Mode mode,
      Optional<BackupManifest> current,
      MorningDatabaseSession.Access database,
      MaintenanceOwnerFrame.Guard owner,
      Work<T> work)
      throws IOException {
    Objects.requireNonNull(mode);
    Objects.requireNonNull(current);
    Objects.requireNonNull(database);
    Objects.requireNonNull(owner);
    Objects.requireNonNull(work);
    owner.check();
    var identity = new dev.codex.schubert.nk.bootstrap.FixedServiceIdentity().resolveBackup();
    var root = OwnedTransferDirectory.open(directoryCalls(), Path.of("/srv/schubert-nk/backup"));
    return ResourceScope.use(
        root::close,
        () -> {
          var security = LinuxInodeSecurity.create();
          var retained =
              new MorningBackupRetention(
                  new BackupManifestReader(root, security, identity.uid(), identity.gid()),
                  new BackupArtifactVerifier(root, security, identity.uid(), identity.gid()),
                  database,
                  owner,
                  System.nanoTime());
          retained.collect(mode, current);
          T value = Objects.requireNonNull(work.execute(retained), "owned retention continuation");
          retained.recheck();
          return value;
        });
  }

  Result result() throws IOException {
    guard();
    return retainedResult.orElseThrow(EnvironmentInodePolicy::unavailable);
  }

  Result collect(Mode mode, Optional<BackupManifest> current) throws IOException {
    Objects.requireNonNull(mode);
    Objects.requireNonNull(current);
    guard();
    require(retainedResult.isEmpty() && ((mode == Mode.FAILED) == current.isEmpty()));
    var root = reader.retentionRoot(started);
    require(root.device() >= 0 && root.inode() > 0);
    List<String> before = reader.retentionNames(started);
    var kept = new TreeMap<String, BackupManifest>();
    var files = new TreeMap<String, BackupArtifactVerifier.BundleSnapshot>();
    var protectedNames = new TreeMap<String, String>();
    Optional<String> currentSha = Optional.empty();
    if (current.isPresent()) {
      var manifest = current.orElseThrow();
      require(before.contains(manifest.directoryName()));
      var inspected = verifier.verifyWithin(manifest, started);
      guard();
      require(database.retainedBackupSuccessful(manifest, now()));
      guard();
      currentSha = Optional.of(inspected.manifest().sha256());
      kept.put(manifest.directoryName(), manifest);
      files.put(manifest.directoryName(), inspected);
    }
    if (mode == Mode.NEW_SUCCESS) {
      for (String name : before) {
        guard();
        if (kept.containsKey(name)) continue;
        if (!name.matches("[0-9]{8}-[0-9]{6}-[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}")) {
          protectedNames.put(name, name.endsWith(".part") ? "PART" : "UNKNOWN_NAME");
          continue;
        }
        if (!reader.retentionDirectory(name, started)) {
          guard();
          protectedNames.put(name, "NOT_DIRECTORY");
          continue;
        }
        if (!reader
            .retentionFiles(name, started)
            .equals(
                List.of(
                    "MANIFEST.json", "config.tar", "credentials.tar.age", "schubert_nk.dump"))) {
          guard();
          protectedNames.put(name, "UNEXPECTED_FILE_SET");
          continue;
        }
        var claim = reader.retentionClaim(name, started);
        guard();
        if (claim.isEmpty()) {
          protectedNames.put(name, "MALFORMED_MANIFEST");
          continue;
        }
        var manifest = claim.orElseThrow();
        var inspectedClaim = verifier.inspectRetention(manifest, started);
        guard();
        if (inspectedClaim.isEmpty()) {
          protectedNames.put(name, "CONTENT_MISMATCH");
          continue;
        }
        var inspected = inspectedClaim.orElseThrow();
        guard();
        if (!database.retainedBackupSuccessful(manifest, now())) {
          guard();
          protectedNames.put(name, "NON_SUCCESS_PAIR");
          continue;
        }
        guard();
        kept.put(name, manifest);
        files.put(name, inspected);
      }
    } else {
      for (String name : before) if (!kept.containsKey(name)) protectedNames.put(name, "READ_ONLY");
    }
    require(before.equals(reader.retentionNames(started)));
    require(root.equals(reader.retentionRoot(started)));
    var deleted = new ArrayList<String>();
    var deletedSha256 = new TreeMap<String, String>();
    if (mode == Mode.NEW_SUCCESS) {
      int extra = Math.max(0, kept.size() - 7);
      var selected = new ArrayList<>(kept.keySet()).subList(0, extra);
      require(!selected.contains(current.orElseThrow().directoryName()));
      for (String name : selected) {
        guard();
        var manifest = Objects.requireNonNull(kept.get(name));
        require(
            manifest.equals(
                reader
                    .retentionClaim(name, started)
                    .orElseThrow(EnvironmentInodePolicy::unavailable)));
        require(database.retainedBackupSuccessful(manifest, now()));
        guard();
        verifier.removeRetained(manifest, Objects.requireNonNull(files.get(name)), started, owner);
        deleted.add(name);
        deletedSha256.put(name, Objects.requireNonNull(files.get(name)).manifest().sha256());
        kept.remove(name);
        files.remove(name);
        var remaining = new ArrayList<>(before);
        remaining.removeAll(deleted);
        require(remaining.equals(reader.retentionNames(started)));
      }
    }
    guard();
    List<String> after = reader.retentionNames(started);
    var remaining = new ArrayList<>(before);
    remaining.removeAll(deleted);
    require(remaining.equals(after));
    var finalRoot = reader.retentionRoot(started);
    require(BackupArtifactVerifier.sameDirectoryInode(root, finalRoot));
    retainedResult =
        Optional.of(
            new Result(
                mode,
                current,
                currentSha,
                before,
                after,
                deleted,
                deletedSha256,
                protectedNames,
                kept,
                files,
                finalRoot));
    recheck();
    return result();
  }

  void recheck() throws IOException {
    guard();
    Result fixed = retainedResult.orElseThrow(EnvironmentInodePolicy::unavailable);
    require(fixed.root.equals(reader.retentionRoot(started)));
    require(fixed.after.equals(reader.retentionNames(started)));
    for (var entry : fixed.kept.entrySet()) {
      guard();
      var actual = reader.retentionClaim(entry.getKey(), started);
      require(actual.equals(Optional.of(entry.getValue())));
      require(
          Objects.requireNonNull(fixed.files.get(entry.getKey()))
              .equals(verifier.verifyWithin(entry.getValue(), started)));
      require(database.retainedBackupSuccessful(entry.getValue(), now()));
      guard();
    }
    require(fixed.root.equals(reader.retentionRoot(started)));
    require(fixed.after.equals(reader.retentionNames(started)));
    guard();
  }

  private void guard() throws IOException {
    require(thread == Thread.currentThread().threadId());
    owner.check();
  }

  private static Instant now() {
    return Instant.now().truncatedTo(ChronoUnit.MICROS);
  }
}
