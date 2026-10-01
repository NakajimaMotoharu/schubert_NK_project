package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;

import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.io.IOException;
import java.util.HashSet;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Trusted operator's borrowed startup capability only. Caller continuously holds M/A, dedicated
 * DB/advisory, complete original and signed old/candidate release proof, and independently proves
 * old normal30 receipts plus current whole-kernel termination. Observation is never authority or
 * historical close/run success. NK-OPS-001/OPS009/UI251/SS342/343/SSC144/PT-OPS-ROOTREC001..005.
 */
@NullMarked
public final class RootFailedStartRecovery {
  public record Evidence(
      StartupPermitRecords.Epoch invalid,
      StartupPermitRecords.Permit permit,
      String permitSha256,
      MaintenanceOwnerFrame owner,
      ServiceConfigFiles.Service service,
      MaintenanceOwnerFrame.Parent child) {
    public Evidence {
      Objects.requireNonNull(invalid);
      Objects.requireNonNull(permit);
      Objects.requireNonNull(permitSha256);
      Objects.requireNonNull(owner);
      Objects.requireNonNull(service);
      Objects.requireNonNull(child);
    }

    @Override
    public String toString() {
      return "FailedRootEvidence[actual=<redacted>]";
    }
  }

  @FunctionalInterface
  public interface Proof {
    void verify(Evidence expected) throws IOException;
  }

  private RootFailedStartRecovery() {}

  /** Read-only pre-stop capture under M. Does not retire, invalidate, issue, stop or resume. */
  public static Evidence observe(OwnedTransferDirectory root, InodeSecurityCalls security)
      throws IOException {
    return observe(root, security, new StartupPermitFiles.NioIo());
  }

  static Evidence observe(
      OwnedTransferDirectory root, InodeSecurityCalls security, StartupPermitFiles.Io io)
      throws IOException {
    var permits = new StartupPermitFiles(root, security, io, java.util.UUID::randomUUID);
    var invalid = permits.current();
    var names = new HashSet<String>();
    root.atDirectory(
        held -> {
          try (var entries = java.nio.file.Files.newDirectoryStream(held)) {
            for (var entry : entries) {
              var leaf = entry.getFileName();
              if (leaf == null) throw new IOException("startup recovery namespace unavailable");
              require(names.add(leaf.toString()));
            }
          }
          return Boolean.TRUE;
        });
    boolean api = names.contains(invalid.epoch() + ".API.start.intent");
    boolean web = names.contains(invalid.epoch() + ".WEB.start.intent");
    require(api != web && names.contains("permit-start.intent"));
    return read(
        root, security, io, api ? ServiceConfigFiles.Service.API : ServiceConfigFiles.Service.WEB);
  }

  private static Evidence read(
      OwnedTransferDirectory root,
      InodeSecurityCalls security,
      StartupPermitFiles.Io io,
      ServiceConfigFiles.Service service)
      throws IOException {
    var permits = new StartupPermitFiles(root, security, io, java.util.UUID::randomUUID);
    var invalid = permits.current();
    var revoked = permits.readRevoked(invalid);
    var sources = new StartupLaunchFiles(root, security, io, revoked.formerIssued(), true);
    var owner = sources.readOwner();
    var launch = sources.readLaunch(service);
    require(invalid.equals(permits.current()));
    return new Evidence(
        invalid,
        revoked.permit(),
        revoked.formerIssued().permitDigest().orElseThrow(),
        owner,
        service,
        launch.child());
  }

  /** Only after complete private preservation and actual physical closure, before new Epoch. */
  public static void retire(
      OwnedTransferDirectory root, InodeSecurityCalls security, Evidence expected, Proof proof)
      throws IOException {
    retire(root, security, new StartupPermitFiles.NioIo(), expected, proof);
  }

  static void retire(
      OwnedTransferDirectory root,
      InodeSecurityCalls security,
      StartupPermitFiles.Io io,
      Evidence expected,
      Proof proof)
      throws IOException {
    Objects.requireNonNull(expected);
    Objects.requireNonNull(proof);
    require(expected.equals(observe(root, security, io)));
    BackupStartIntentFiles.Gate gate =
        () -> {
          require(expected.equals(read(root, security, io, expected.service())));
          proof.verify(expected);
        };
    var service =
        new BackupStartIntentFiles(
            root,
            security,
            io,
            gate,
            expected.invalid().epoch() + "." + expected.service().name() + ".start.intent");
    var publication = new BackupStartIntentFiles(root, security, io, gate, "permit-start.intent");
    var serviceIntent = service.observeQuarantine();
    var publicationIntent = publication.observeQuarantine();
    try {
      service.retire(serviceIntent);
      root.sync();
      gate.verify();
      publication.retire(publicationIntent);
      root.sync();
      gate.verify();
      StartupLaunchFiles.requireNoServiceResidue(root, security, io);
    } catch (IOException | RuntimeException | Error failure) {
      try {
        quarantine(root, security, io, expected);
      } catch (IOException | RuntimeException | Error uncertain) {
        failure.addSuppressed(uncertain);
      }
      throw failure;
    }
  }

  /** Caller invokes under still-owned M/A after owned-resource close failure; never success. */
  public static void quarantine(
      OwnedTransferDirectory root, InodeSecurityCalls security, Evidence expected)
      throws IOException {
    quarantine(root, security, new StartupPermitFiles.NioIo(), expected);
  }

  static void quarantine(
      OwnedTransferDirectory root,
      InodeSecurityCalls security,
      StartupPermitFiles.Io io,
      Evidence expected)
      throws IOException {
    Objects.requireNonNull(expected);
    var marker =
        new BackupStartIntentFiles(
            root,
            security,
            io,
            () -> require(expected.equals(read(root, security, io, expected.service()))),
            "permit-start.intent");
    marker.quarantinePublication();
    root.sync();
  }
}
