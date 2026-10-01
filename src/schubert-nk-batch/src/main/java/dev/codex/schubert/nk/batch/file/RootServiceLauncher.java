package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.platform.RootReleaseAdmission;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.bootstrap.FixedServiceExecArguments;
import dev.codex.schubert.nk.bootstrap.FixedServiceIdentity;
import dev.codex.schubert.nk.bootstrap.StartupProofFrame;
import dev.codex.schubert.nk.bootstrap.StartupReleaseManifest;
import dev.codex.schubert.nk.storage.*;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Web/API Root full preflight and same-PID native replacement. A normal return is always failure;
 * replacement alone is not ordinary-service readiness. The complete candidate must be tested in the
 * isolated PG/PT VM before a production Unit is accepted. NK-OPS-001; SYS002/004,OPS009;
 * UI212/251/253; SS311/342§4.2/343; SSC086..089; PG370/PT-OPS-RMAIN001..006; 471 R1/D04/D05.
 */
@NullMarked
public final class RootServiceLauncher {
  @FunctionalInterface
  interface Admission {
    void verify(ServiceConfigFiles.Service service) throws IOException;
  }

  private RootServiceLauncher() {}

  public static void main(String[] args) {
    System.exit(run(args, RootServiceLauncher::preflight));
  }

  static int run(String[] args, Admission admission) {
    Objects.requireNonNull(args, "fixed service arguments");
    Objects.requireNonNull(admission, "root admission");
    if (args.length != 1) return 70;
    ServiceConfigFiles.Service service;
    switch (args[0]) {
      case "WEB" -> service = ServiceConfigFiles.Service.WEB;
      case "API" -> service = ServiceConfigFiles.Service.API;
      default -> {
        return 70;
      }
    }
    try {
      admission.verify(service);
      return 30;
    } catch (IOException known) {
      return 30;
    }
  }

  private static void preflight(ServiceConfigFiles.Service service) throws IOException {
    var root = RootStartupContext.create();
    var actor =
        switch (service) {
          case WEB -> RootStartupContext.Service.WEB;
          case API -> RootStartupContext.Service.API;
        };
    var snapshot = root.capture(actor);
    var acquired =
        StartupAdmissionFile.create()
            .tryExclusiveObserved(
                admission -> {
                  root.recheck(snapshot);
                  var identity = new FixedServiceIdentity().resolve(service);
                  var release = RootReleaseAdmission.create(root, snapshot);
                  var releaseHash =
                      StartupReleaseManifest.createHost(
                              new FixedServiceIdentity().configurationGroup())
                          .sha256();
                  var issued = RootCurrentPermitPreflight.readNative(root, snapshot, releaseHash);
                  var owner = RootStartupPending.observe(root, snapshot, issued);
                  RootStartupPending.awaitLaunch(root, snapshot, issued, owner);
                  RootServiceExecutableAdmission.withSetpriv(
                      root,
                      snapshot,
                      held -> {
                        var facts =
                            RootServiceFacts.inspect(
                                root, snapshot, service, issued, owner, release);
                        if (!identity.equals(new FixedServiceIdentity().resolve(service)))
                          throw new IOException("root service identity unavailable");
                        if (!issued.equals(
                            RootCurrentPermitPreflight.readNative(root, snapshot, releaseHash)))
                          throw new IOException("root service permit unavailable");
                        RootStartupPending.awaitLaunch(root, snapshot, issued, owner);
                        var frame =
                            proof(
                                service,
                                snapshot,
                                admission,
                                identity,
                                issued,
                                facts.rootsSha256());
                        var arguments =
                            new FixedServiceExecArguments(service, identity).arguments();
                        LinuxSealedProof.create()
                            .withProof(
                                frame.encode(),
                                proofFd -> {
                                  root.recheck(snapshot);
                                  owner.parentsGuard().check();
                                  LinuxExecDescriptors.create()
                                      .withInherited(
                                          admission.descriptor(),
                                          proofFd,
                                          () ->
                                              LinuxProcessExec.create()
                                                  .replace(
                                                      held,
                                                      arguments,
                                                      environment(
                                                          service,
                                                          snapshot,
                                                          admission.descriptor(),
                                                          proofFd)));
                                  return Boolean.TRUE;
                                });
                      });
                  return Boolean.TRUE;
                });
    // A successful same-PID exec cannot return. Busy/normal return is never readiness.
    if (acquired.isEmpty()) throw new IOException("startup admission unavailable");
    throw new IOException("root service replacement unavailable");
  }

  static StartupProofFrame proof(
      ServiceConfigFiles.Service service,
      RootStartupContext.Snapshot self,
      StartupAdmissionFile.Admission admission,
      FixedServiceIdentity.Value identity,
      RootCurrentPermitPreflight.Observed issued,
      String rootsSha)
      throws IOException {
    Objects.requireNonNull(service);
    Objects.requireNonNull(self);
    Objects.requireNonNull(admission);
    Objects.requireNonNull(identity);
    Objects.requireNonNull(issued);
    Objects.requireNonNull(rootsSha);
    var fields = new HashMap<String, String>();
    fields.put("service", service.name());
    fields.put("boot_id", self.boot());
    fields.put("invocation_id", self.invocation());
    fields.put("pid", Long.toString(self.pid()));
    fields.put("start_ticks", Long.toString(self.startTicks()));
    fields.put("admission_fd", Integer.toString(admission.descriptor()));
    fields.put("admission_device", Long.toUnsignedString(admission.device()));
    fields.put("admission_inode", Long.toUnsignedString(admission.inode()));
    fields.put("service_uid", Long.toString(identity.uid()));
    fields.put("service_gid", Long.toString(identity.gid()));
    fields.put("service_groups", identity.groupArgument());
    fields.put("permit_epoch", issued.current().epoch().toString());
    fields.put("permit_sha256", issued.current().permitDigest().orElseThrow());
    fields.put("release_sha256", issued.permit().releaseDigest());
    fields.put(
        "config_sha256",
        service == ServiceConfigFiles.Service.API
            ? issued.permit().apiConfigDigest()
            : issued.permit().webConfigDigest());
    fields.put("roots_sha256", rootsSha);
    fields.put("broker_invocation_id", issued.permit().brokerInvocation());
    EnvironmentInodePolicy.require(
        self.service().name().equals(service.name())
            && issued.current().boot().toString().equals(self.boot())
            && issued.current().boot().equals(issued.permit().boot())
            && issued.current().epoch().equals(issued.permit().epoch())
            && issued.current().activation().equals(issued.permit().activation())
            && rootsSha.equals(issued.permit().rootsDigest()));
    return StartupProofFrame.fromFields(fields);
  }

  static Map<String, String> environment(
      ServiceConfigFiles.Service service,
      RootStartupContext.Snapshot self,
      int admission,
      int proof)
      throws IOException {
    Objects.requireNonNull(service);
    Objects.requireNonNull(self);
    EnvironmentInodePolicy.require(self.service().name().equals(service.name()));
    String credentials = "/run/credentials/" + self.service().unit();
    EnvironmentInodePolicy.require(credentials.equals(System.getenv("CREDENTIALS_DIRECTORY")));
    return Map.of(
        "INVOCATION_ID",
        self.invocation(),
        "CREDENTIALS_DIRECTORY",
        credentials,
        "SCHUBERT_NK_CONFIG_DIR",
        "/etc/schubert-nk",
        "SCHUBERT_NK_STARTUP_ADMISSION_FD",
        Integer.toString(admission),
        "SCHUBERT_NK_STARTUP_PROOF_FD",
        Integer.toString(proof));
  }
}
