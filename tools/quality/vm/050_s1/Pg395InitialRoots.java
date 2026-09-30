import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.nio.file.*;
import java.nio.file.attribute.PosixFilePermissions;
import java.nio.channels.FileChannel;
import java.util.*;
import java.util.concurrent.TimeUnit;

/** SSC126/ISSROOT001. Isolated trusted initial provisioning, never a runtime repair.
 * New-only fixed NSS and three empty roots. Full signed current BOM, M/A, eight terminals,
 * preserved INVALID/original and undelivered-work refusal are mandatory before mutation.
 * Empty asset root does not mean master migration or whole Morning acceptance.
 */
public final class Pg395InitialRoots {
  private static final Path SAVE = Path.of("/var/lib/pgpt-s1-preservation");
  private static final List<Path> NEW = List.of(Path.of("/srv/schubert-nk/data/assets"),
      Path.of("/var/log/schubert-nk"), Path.of("/srv/schubert-nk/staging"));
  private static final List<Path> OLD = List.of(Path.of("/srv/schubert-nk/transfer"),
      Path.of("/srv/schubert-nk/backup"), Path.of("/var/lib/schubert-nk/artemis"));
  private static final String SOURCE = "a7cc8309ea498c645dd98115c4c6eb068ab0db74";
  public static void main(String[] args) throws Exception {
    if (args.length != 0 || !Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim()
        .equals("pgpt-r2-20260927-01")) throw new IllegalStateException("isolated instance only");
    Thread.currentThread().setUncaughtExceptionHandler((thread,error) ->
        System.err.println("PG395 INITIAL_ROOTS_REFUSED type=" + error.getClass().getName()
            + " diagnosticsRedacted=true partialChangesPreserved=true"));
    Pg387TrustedDeployment.RELEASE = Path.of("/opt/schubert-nk/releases/0.1.0-PG394");
    Pg387TrustedDeployment.LABEL = "PG394";
    Pg387TrustedDeployment.STEM = "pg394";
    Pg387TrustedDeployment.SOURCE = SOURCE;
    MaintenanceFileLock.create().tryExclusive(() -> Pg387TrustedDeployment.checked(() -> {
      Pg387TrustedDeployment.requireNoUndeliveredWork();
      preflightNew();
      var old = new ArrayList<Map<String,Object>>();
      for (var root : OLD) old.add(metadata(root));
      Pg387TrustedDeployment.stopAll();
      return StartupAdmissionFile.create().tryExclusive(admission ->
          Pg387TrustedDeployment.checked(() -> {
            Pg387TrustedDeployment.terminalAll();
            var approval = Pg387TrustedDeployment.verify();
            byte[] currentApproval = Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current"));
            require(Arrays.equals(currentApproval, approval.encode())
                && Files.readSymbolicLink(Path.of("/opt/schubert-nk/current"))
                    .equals(Pg387TrustedDeployment.RELEASE));
            require(StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup())
                .verify(approval).version().equals("0.1.0-PG394"));
            var prior = epoch();
            require(prior.state() == StartupPermitRecords.State.INVALID
                && prior.permitDigest().isEmpty()
                && prior.activation().run().id().equals(Pg387TrustedDeployment.ORIGINAL_RUN));
            require(MaintenanceRunFiles.create().execute(session ->
                session.observe(prior.activation())).equals(prior.activation()));
            preflightNew();
            // Before-images are private root-only, never printed or admitted as PT inputs.
            for (var name : List.of("passwd", "group", "shadow", "gshadow")) {
              Path saved = SAVE.resolve("pg395-initial-" + name);
              Files.copy(Path.of("/etc", name), saved);
              Files.setPosixFilePermissions(saved, PosixFilePermissions.fromString("r--------"));
              force(saved);
            }
            Path rules = SAVE.resolve("pg395-initial-sysusers.conf");
            Files.writeString(rules, "u schubert-data - \"Schubert NK immutable data\" /nonexistent /usr/sbin/nologin\n"
                + "u schubert-migration - \"Schubert NK migration\" /nonexistent /usr/sbin/nologin\n"
                + "m schubert-data schubert-read\n", StandardOpenOption.CREATE_NEW);
            Files.setPosixFilePermissions(rules, PosixFilePermissions.fromString("r--------"));
            force(rules);
            var process = new ProcessBuilder("/usr/bin/systemd-sysusers", rules.toString())
                .redirectOutput(ProcessBuilder.Redirect.DISCARD)
                .redirectError(ProcessBuilder.Redirect.DISCARD).start();
            require(process.waitFor(20, TimeUnit.SECONDS) && process.exitValue() == 0);
            var fixed = new FixedServiceIdentity();
            var data = fixed.resolveDataOwner();
            var migration = fixed.resolveMigration();
            create(NEW.get(0), data.uid(), fixed.dataReadGroup(), "rwxr-x---");
            create(NEW.get(1), 0, fixed.configurationGroup(), "rwxr-x---");
            create(NEW.get(2), migration.uid(), migration.gid(), "rwx------");
            for (int index = 0; index < OLD.size(); index++)
              require(old.get(index).equals(metadata(OLD.get(index))));
            require(epoch().equals(prior));
            require(Arrays.equals(currentApproval, Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current")))
                && Files.readSymbolicLink(Path.of("/opt/schubert-nk/current"))
                    .equals(Pg387TrustedDeployment.RELEASE));
            require(MaintenanceRunFiles.create().execute(session ->
                session.observe(prior.activation())).equals(prior.activation()));
            require(StartupReleaseManifest.createHost(fixed.configurationGroup())
                .verify(approval).version().equals("0.1.0-PG394"));
            Pg387TrustedDeployment.requireNoUndeliveredWork();
            Pg387TrustedDeployment.terminalAll();
            System.out.println("PG395 INITIAL_ROOTS completed=true newUsers=2 newRoots=3 oldRootsUnchanged=true"
                + " originalUnchanged=true invalidUnchanged=true runtimePermitIssued=false"
                + " masterMigrationAccepted=false");
            return true;
          })).orElseThrow();
    })).orElseThrow();
  }
  private static void preflightNew() throws Exception {
    for (var root : NEW) require(!Files.exists(root, LinkOption.NOFOLLOW_LINKS));
    for (var name : List.of("schubert-data", "schubert-migration")) {
      for (var database : List.of("passwd", "group")) {
        var query = new ProcessBuilder("/usr/bin/getent", database, name)
            .redirectOutput(ProcessBuilder.Redirect.DISCARD)
            .redirectError(ProcessBuilder.Redirect.DISCARD).start();
        require(query.waitFor(5, TimeUnit.SECONDS) && query.exitValue() == 2);
      }
    }
    for (var root : NEW) {
      var attrs = metadata(root.getParent());
      require(Integer.valueOf(0).equals(attrs.get("uid"))
          && ((int)attrs.get("mode") & 0170000) == 040000);
    }
  }
  private static void create(Path path, long uid, long gid, String mode) throws Exception {
    var calls = LinuxDirectoryCalls.create();
    // Opening from / verifies every existing ancestor NOFOLLOW; no parent is repaired.
    try (var parent = OwnedTransferDirectory.open(calls, path.getParent())) {
      parent.atDirectory(held -> {
        Path target = held.resolve(path.getFileName().toString());
        Files.createDirectory(target, PosixFilePermissions.asFileAttribute(
            PosixFilePermissions.fromString("rwx------")));
        Files.setAttribute(target, "unix:uid", Math.toIntExact(uid), LinkOption.NOFOLLOW_LINKS);
        Files.setAttribute(target, "unix:gid", Math.toIntExact(gid), LinkOption.NOFOLLOW_LINKS);
        Files.setPosixFilePermissions(target, PosixFilePermissions.fromString(mode));
        var actual = metadata(target);
        require(Integer.toUnsignedLong((int)actual.get("uid")) == uid
            && Integer.toUnsignedLong((int)actual.get("gid")) == gid
            && Integer.valueOf(mode.equals("rwxr-x---") ? 040750 : 040700).equals(actual.get("mode"))
            && (long)actual.get("dev") >= 0 && (long)actual.get("ino") > 0);
        try (var child = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), path)) {
          child.sync();
          child.atDirectory(p -> {
            require(LinuxInodeSecurity.create().accessAcl(p, 44).length == 0
                && !LinuxInodeSecurity.create().readOnlyFilesystem(p));
            return true;
          });
        }
        parent.sync();
        return true;
      });
    }
  }
  private static Map<String,Object> metadata(Path path) throws java.io.IOException {
    return Files.readAttributes(path, "unix:mode,uid,gid,dev,ino", LinkOption.NOFOLLOW_LINKS);
  }
  private static StartupPermitRecords.Epoch epoch() throws Exception {
    try (var held = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),
        Path.of("/run/schubert-nk/startup"))) {
      return new StartupPermitFiles(held, LinuxInodeSecurity.create()).current();
    }
  }
  private static void force(Path file) throws Exception {
    try (var held = FileChannel.open(file, StandardOpenOption.READ)) { held.force(true); }
  }
  private static void require(boolean accepted) throws java.io.IOException {
    if (!accepted) throw new java.io.IOException("fixed initial provisioning unavailable");
  }
}
