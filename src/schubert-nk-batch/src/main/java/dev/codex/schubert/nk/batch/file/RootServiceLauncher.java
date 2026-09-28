package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.platform.RootReleaseAdmission;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.bootstrap.FixedServiceExecArguments;
import dev.codex.schubert.nk.bootstrap.FixedServiceIdentity;
import dev.codex.schubert.nk.bootstrap.StartupReleaseManifest;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.io.IOException;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Fail-closed Web/API root entry while permit/A/proof/FD/execve and full root gates are assembled.
 * Even a successful read-only preflight remains non-success, never readiness or authority. A Unit
 * must not point at this entry until the whole issuer and native same-PID replacement are verified.
 * NK-OPS-001; SYS002/004,OPS009; UI212/251/253; SS311/342§4.2/343; SSC086..089;
 * PG370/PT-OPS-RMAIN001..006; 471 R1/D04/D05.
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
    root.recheck(snapshot);
    var identity = new FixedServiceIdentity().resolve(service);
    RootReleaseAdmission.create(root, snapshot);
    var releaseHash =
        StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).sha256();
    RootCurrentPermitPreflight.verifyNative(root, snapshot, releaseHash);
    new FixedServiceExecArguments(service, identity).arguments();
    root.recheck(snapshot);
    // No permission to exec: full roots/Ops/schema, A-held recheck, held ELF and FD proof absent.
  }
}
