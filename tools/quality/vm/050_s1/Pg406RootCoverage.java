import dev.codex.schubert.nk.batch.file.MaintenanceFileLock;
import dev.codex.schubert.nk.batch.file.StartupAdmissionFile;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.Arrays;

/** PT297 isolated instrumentation only. No runtime permit/gate/expected replacement. */
public final class Pg406RootCoverage {
  public static void main(String[] args) throws Exception {
    if (args.length != 0 || !Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim()
        .equals("pgpt-r2-20260927-01")) throw new IllegalStateException("isolated fixed fixture");
    MaintenanceFileLock.create().tryExclusive(() -> StartupAdmissionFile.create().tryExclusive(fd -> {
      return Pg387TrustedDeployment.checked(() -> {
        Pg387TrustedDeployment.terminalAll();
        Pg387TrustedDeployment.requireNoUndeliveredWork();
        String name = "schubert-nk-api.service";
        Path installed = Path.of("/etc/systemd/system", name);
        Path signed = Path.of("/opt/schubert-nk/releases/0.1.0-PG406/systemd", name);
        if (!Arrays.equals(Files.readAllBytes(installed), Files.readAllBytes(signed)))
          throw new IllegalStateException("signed Root Unit base");
        String text = Files.readString(installed, StandardCharsets.UTF_8);
        String start = text.lines().filter(s -> s.startsWith("ExecStart=")).findFirst().orElseThrow();
        if (!start.startsWith("ExecStart=!/usr/bin/java ") || !start.endsWith("RootServiceLauncher API"))
          throw new IllegalStateException("Root entry");
        Path agent = Path.of("/opt/pgpt-tools-pg390/jacoco-agent.jar");
        if (!Files.isRegularFile(agent, LinkOption.NOFOLLOW_LINKS)) throw new IllegalStateException("fixed agent");
        var metadata = Files.readAttributes(agent, "unix:uid,gid,mode,nlink,size,dev,ino,ctime,lastModifiedTime", LinkOption.NOFOLLOW_LINKS);
        if (!Integer.valueOf(0).equals(metadata.get("uid")) || !Integer.valueOf(1).equals(metadata.get("nlink"))
            || Files.size(agent) > 1048576) throw new IllegalStateException("agent metadata");
        String digest = java.util.HexFormat.of().formatHex(java.security.MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(agent)));
        if (!digest.equals("fb5b0036a0899ea97edfa0fc2c7985b55f3f7c5695028163e5e60d4f3cf6075d")
            || !metadata.equals(Files.readAttributes(agent, "unix:uid,gid,mode,nlink,size,dev,ino,ctime,lastModifiedTime", LinkOption.NOFOLLOW_LINKS)))
          throw new IllegalStateException("agent exact pinned bytes");
        Path output = Path.of("/run/schubert-nk/pt-coverage/root-api");
        Path drop = Path.of("/etc/systemd/system/schubert-nk-api.service.d");
        if (Files.exists(output, LinkOption.NOFOLLOW_LINKS) || Files.exists(drop, LinkOption.NOFOLLOW_LINKS))
          throw new IllegalStateException("preserve prior fixture");
        Files.createDirectory(output);
        Files.setPosixFilePermissions(output, java.nio.file.attribute.PosixFilePermissions.fromString("rwx------"));
        Files.createDirectory(drop);
        Files.setPosixFilePermissions(drop, java.nio.file.attribute.PosixFilePermissions.fromString("rwxr-xr-x"));
        String instrumented = start.replace("ExecStart=!/usr/bin/java ",
            "ExecStart=!/usr/bin/java -javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=destfile=/run/schubert-nk/pt-coverage/root-api/root-api.exec,append=false,dumponexit=true ");
        Path fixture = drop.resolve("pg406-root-coverage.conf");
        Files.writeString(fixture, "# PT297 native Root same-byte coverage; not Production base or readiness\n[Service]\nExecStart=\n"
            + instrumented + "\nReadWritePaths=/run/schubert-nk/pt-coverage/root-api\n", StandardCharsets.UTF_8, StandardOpenOption.CREATE_NEW);
        Files.setPosixFilePermissions(fixture, java.nio.file.attribute.PosixFilePermissions.fromString("rw-r--r--"));
        try (var file = FileChannel.open(fixture, StandardOpenOption.READ)) { file.force(true); }
        try (var directory = FileChannel.open(drop, StandardOpenOption.READ)) { directory.force(true); }
        var reload = new ProcessBuilder("/usr/bin/systemctl", "daemon-reload").inheritIO().start();
        if (!reload.waitFor(20, java.util.concurrent.TimeUnit.SECONDS) || reload.exitValue() != 0)
          throw new IllegalStateException("reload unknown, preserve fixture");
        Pg387TrustedDeployment.terminalAll();
        System.out.println("PG406 ROOT_COVERAGE_PREPARED signedBaseUnchanged=true permitsIssued=0 gatesReplaced=0");
        return Boolean.TRUE;
      });
    }).orElseThrow()).orElseThrow();
  }
}
