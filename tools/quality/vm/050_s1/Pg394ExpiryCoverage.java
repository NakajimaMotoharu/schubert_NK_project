import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.bootstrap.*;
import java.nio.file.*;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** PG/PT-only native JaCoCo fixture, not application authority or runtime recovery. */
public final class Pg394ExpiryCoverage {
  public static void main(String[] args) throws Exception {
    if(args.length!=0 || !Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"))throw new IllegalStateException("isolated fixture only");
    Pg387TrustedDeployment.LABEL="PG394"; Pg387TrustedDeployment.STEM="pg394";
    Pg387TrustedDeployment.SOURCE="a7cc8309ea498c645dd98115c4c6eb068ab0db74";
    Pg387TrustedDeployment.RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG394");
    MaintenanceFileLock.create().tryExclusive(() -> {
      return Pg387TrustedDeployment.checked(() -> {
        Pg387TrustedDeployment.requireNoUndeliveredWork();
        Pg387TrustedDeployment.terminalAll();
        return StartupAdmissionFile.create().tryExclusive(admission -> Pg387TrustedDeployment.checked(() -> {
          Pg387TrustedDeployment.terminalAll();
          var approval=Pg387TrustedDeployment.verify();
          var current=ReleaseApproval.parse(Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current")));
          if(!Arrays.equals(current.encode(),approval.encode()))throw new IllegalStateException("current approval mismatch");
          StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verify(approval);
          Path directory=Path.of("/run/schubert-nk/pt-coverage/expiry");
          Files.createDirectory(directory);
          Files.setPosixFilePermissions(directory,java.nio.file.attribute.PosixFilePermissions.fromString("rwx------"));
          Path dropDirectory=Path.of("/etc/systemd/system/schubert-nk-expiry-cleanup.service.d");
          Files.createDirectory(dropDirectory);
          Files.setPosixFilePermissions(dropDirectory,java.nio.file.attribute.PosixFilePermissions.fromString("rwxr-xr-x"));
          Path drop=dropDirectory.resolve("pg394-native-coverage.conf");
          String exec=Files.readAllLines(Pg387TrustedDeployment.RELEASE.resolve("systemd/schubert-nk-expiry-cleanup.service"),StandardCharsets.UTF_8).stream().filter(line -> line.startsWith("ExecStart=/usr/bin/java ")).findFirst().orElseThrow();
          Path agent=Path.of("/opt/pgpt-tools-pg390/jacoco-agent.jar");
          if(!Files.isRegularFile(agent,LinkOption.NOFOLLOW_LINKS))throw new IllegalStateException("existing native agent unavailable");
          exec=exec.replace("ExecStart=/usr/bin/java ","ExecStart=/usr/bin/java -javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=destfile=/run/schubert-nk/pt-coverage/expiry/expiry.exec,append=false ");
          String content="[Service]\nReadWritePaths=/run/schubert-nk/pt-coverage/expiry\nExecStart=\n"+exec+"\n";
          Files.writeString(drop,content,StandardCharsets.UTF_8,StandardOpenOption.CREATE_NEW);
          Files.setPosixFilePermissions(drop,java.nio.file.attribute.PosixFilePermissions.fromString("rw-r--r--"));
          try(var f=FileChannel.open(drop,StandardOpenOption.READ)){f.force(true);}
          Pg387TrustedDeployment.sync(dropDirectory);
          var reload=new ProcessBuilder("/usr/bin/systemctl","daemon-reload").inheritIO().start();
          if(!reload.waitFor(20,java.util.concurrent.TimeUnit.SECONDS)||reload.exitValue()!=0)throw new IllegalStateException("reload failed");
          Pg387TrustedDeployment.terminalAll();
          if(!Files.readString(drop).equals(content))throw new IllegalStateException("coverage fixture readback");
          System.out.println("PG394 EXPIRY_COVERAGE_FIXTURE newOnly=true M_A=true signedSource=true unitsTerminal=true runtimeAuthority=false");
          return true;
        })).orElseThrow();
      });
    }).orElseThrow();
  }
}
