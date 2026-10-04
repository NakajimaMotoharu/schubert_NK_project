package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;

import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.io.IOException;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Trusted operator's borrowed startup capability only. Caller continuously holds M/A, dedicated
 * DB/advisory, complete original and signed old/candidate release proof, and independently proves
 * approved fixed actual termination receipts plus current whole-kernel termination. SSC168's old
 * normal30/Web50 proof and SSC179's isolated timeout143/owned-stop143 proof are distinct; the
 * latter requires same-epoch canonical revoke and publication-first quarantine before Pair
 * retirement. Observation is never authority or historical close/run success.
 * NK-OPS-001/OPS009/UI251/SS342/343/SSC144/168/179/PT-OPS-ROOTREC001..005.
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

  /** Fixed two-child correlation, not physical closure or historical success authority. */
  public record PairEvidence(Evidence api, Evidence web) {
    public PairEvidence {
      Objects.requireNonNull(api);
      Objects.requireNonNull(web);
      if (api.service() != ServiceConfigFiles.Service.API
          || web.service() != ServiceConfigFiles.Service.WEB
          || api.invalid().state() != StartupPermitRecords.State.INVALID
          || !api.invalid().equals(web.invalid())
          || !api.permit().equals(web.permit())
          || !api.permitSha256().equals(web.permitSha256())
          || !api.owner().equals(web.owner())
          || api.child().pid() == web.child().pid()
          || api.child().invocation().equals(web.child().invocation()))
        throw new IllegalArgumentException("failed startup pair unavailable");
    }

    @Override
    public String toString() {
      return "FailedRootPair[actual=<redacted>]";
    }
  }

  @FunctionalInterface
  public interface PairProof {
    void verify(PairEvidence expected) throws IOException;
  }

  private RootFailedStartRecovery() {}

  /** SSC168/ROOTPAIR001: both fixed child intents, under continuously owned M. */
  public static PairEvidence observePair(OwnedTransferDirectory root, InodeSecurityCalls security)
      throws IOException {
    return observePair(root, security, new StartupPermitFiles.NioIo());
  }

  static PairEvidence observePair(
      OwnedTransferDirectory root, InodeSecurityCalls security, StartupPermitFiles.Io io)
      throws IOException {
    var expected = readPair(root, security, io);
    for (String name : pairNames(expected))
      new BackupStartIntentFiles(
              root,
              security,
              io,
              () -> require(expected.equals(readPair(root, security, io))),
              name)
          .observeQuarantine();
    require(expected.equals(readPair(root, security, io)));
    return expected;
  }

  private static PairEvidence readPair(
      OwnedTransferDirectory root, InodeSecurityCalls security, StartupPermitFiles.Io io)
      throws IOException {
    var api = read(root, security, io, ServiceConfigFiles.Service.API);
    var web = read(root, security, io, ServiceConfigFiles.Service.WEB);
    try {
      var pair = new PairEvidence(api, web);
      require(api.equals(read(root, security, io, ServiceConfigFiles.Service.API)));
      require(web.equals(read(root, security, io, ServiceConfigFiles.Service.WEB)));
      return pair;
    } catch (IllegalArgumentException invalid) {
      throw new IOException("failed startup pair unavailable");
    }
  }

  private static List<String> pairNames(PairEvidence expected) {
    String epoch = expected.api().invalid().epoch().toString();
    return List.of(epoch + ".WEB.start.intent", epoch + ".API.start.intent", "permit-start.intent");
  }

  /** All three inodes captured before unlink; fixed reverse start order under trusted proof. */
  public static void retirePair(
      OwnedTransferDirectory root,
      InodeSecurityCalls security,
      PairEvidence expected,
      PairProof proof)
      throws IOException {
    retirePair(root, security, new StartupPermitFiles.NioIo(), expected, proof);
  }

  static void retirePair(
      OwnedTransferDirectory root,
      InodeSecurityCalls security,
      StartupPermitFiles.Io io,
      PairEvidence expected,
      PairProof proof)
      throws IOException {
    Objects.requireNonNull(expected);
    Objects.requireNonNull(proof);
    require(expected.equals(observePair(root, security, io)));
    BackupStartIntentFiles.Gate gate =
        () -> {
          require(expected.equals(readPair(root, security, io)));
          proof.verify(expected);
        };
    var markers =
        pairNames(expected).stream()
            .map(name -> new BackupStartIntentFiles(root, security, io, gate, name))
            .toList();
    try {
      var intents = new java.util.ArrayList<BackupStartIntentFiles.Intent>();
      for (var marker : markers) intents.add(marker.observeQuarantine());
      for (int index = 0; index < markers.size(); index++) {
        markers.get(index).retire(intents.get(index));
        root.sync();
        gate.verify();
      }
      StartupLaunchFiles.requireNoServiceResidue(root, security, io);
      gate.verify();
    } catch (IOException | RuntimeException | Error failure) {
      try {
        quarantinePair(root, security, io, expected);
      } catch (IOException | RuntimeException | Error uncertain) {
        failure.addSuppressed(uncertain);
      }
      throw failure;
    }
  }

  /**
   * Restore publication first, then independently try both children; uncertainty is never success.
   */
  public static void quarantinePair(
      OwnedTransferDirectory root, InodeSecurityCalls security, PairEvidence expected)
      throws IOException {
    quarantinePair(root, security, new StartupPermitFiles.NioIo(), expected);
  }

  static void quarantinePair(
      OwnedTransferDirectory root,
      InodeSecurityCalls security,
      StartupPermitFiles.Io io,
      PairEvidence expected)
      throws IOException {
    Objects.requireNonNull(expected);
    var failure = new IOException("failed startup pair quarantine uncertain");
    for (String name :
        List.of(
            "permit-start.intent",
            expected.api().invalid().epoch() + ".API.start.intent",
            expected.api().invalid().epoch() + ".WEB.start.intent")) {
      try {
        var marker =
            new BackupStartIntentFiles(
                root,
                security,
                io,
                () -> require(expected.equals(readPair(root, security, io))),
                name);
        if (name.equals("permit-start.intent")) marker.quarantinePublication();
        else
          marker.quarantineService(
              expected.api().invalid(),
              name.endsWith(".API.start.intent")
                  ? ServiceConfigFiles.Service.API
                  : ServiceConfigFiles.Service.WEB);
        root.sync();
      } catch (IOException | RuntimeException | Error uncertain) {
        failure.addSuppressed(uncertain);
      }
    }
    if (failure.getSuppressed().length != 0) throw failure;
    require(expected.equals(observePair(root, security, io)));
  }

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
