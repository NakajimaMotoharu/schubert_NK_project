import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

/** SSC141 / ROOTDEPLOY001: independent text vectors; no VM writes or runtime authority. */
public final class Pg406UnitDeltaTest {
  private static int assertions;
  private static final String CAPS = "CapabilityBoundingSet=CAP_SETUID CAP_SETGID CAP_SETPCAP CAP_SYS_PTRACE CAP_DAC_READ_SEARCH\n";

  public static void main(String[] args) throws Exception {
    if (args.length != 1) throw new IllegalArgumentException("repository path");
    for (String role : new String[] {"api", "web"}) {
      String name = "schubert-nk-" + role + ".service";
      String requires = role.equals("api")
          ? "Requires=schubert-nk-expiry-cleanup.service artemis.service postgresql.service\n"
          : "Requires=schubert-nk-api.service artemis.service postgresql.service\n";
      String oldExec = "ExecStart=/usr/bin/java -Xmx1g -cp /opt/schubert-nk/current/" + role
          + "/" + role + ".jar:/opt/schubert-nk/current/" + role
          + "/lib/* dev.codex.schubert.nk." + role + ".bootstrap."
          + (role.equals("api") ? "Api" : "Web") + "ProcessMain\n";
      String old = "# old\n[Unit]\n" + requires + "\n[Service]\n" + oldExec + "User=schubert-" + role + "\n";
      String expected = "# new comments are immaterial\n[Unit]\n"
          + (role.equals("api") ? "Requires=artemis.service postgresql.service\n" : requires)
          + "\n[Service]\nExecStart=!/usr/bin/java -Xmx1g -cp /opt/schubert-nk/current/operations/batch.jar:/opt/schubert-nk/current/operations/lib/* dev.codex.schubert.nk.batch.file.RootServiceLauncher "
          + role.toUpperCase(java.util.Locale.ROOT) + "\n" + CAPS + "User=schubert-" + role + "\n";
      accept(name, old, expected);
      reject(name, old, expected.replace("-Xmx1g", "-Xmx2g"));
      reject(name, old, expected.replace("CAP_DAC_READ_SEARCH", "CAP_DAC_OVERRIDE"));
      reject(name, old, expected.replace("ExecStart=!", "ExecStart="));
      reject(name, old, expected + "Environment=UNAPPROVED=1\n");
      reject(name, old, expected.replace("User=schubert-" + role, "User=root"));
      reject(name, old, expected.replace("\n", "\r\n"));
      reject(name, old, expected.stripTrailing());
      reject(name, old + oldExec, expected);
      reject(name, old, expected.replace(CAPS, ""));
      reject(name, old, expected.replace(CAPS, CAPS + CAPS));
      reject(name, old, expected.replace("Requires=", "Requires=unapproved.service "));
      var git = new ProcessBuilder("git", "show", "485e3da3b3f223d65e33ef32efa12bde2366283b:src/deployment/systemd/" + name + ".template")
          .directory(Path.of(args[0]).toFile()).start();
      byte[] previous = git.getInputStream().readAllBytes();
      if (git.waitFor() != 0) throw new AssertionError("saved signed Source template unavailable");
      Pg387TrustedDeployment.validateRootDelta(name, previous,
          Files.readAllBytes(Path.of(args[0], "src/deployment/systemd/" + name + ".template")));
      assertions++;
    }
    reject("other.service", "[Unit]\n", "[Unit]\n");
    System.out.println("ROOTDEPLOY001 PASS assertions=" + assertions + " vmWrites=0");
  }

  private static void accept(String name, String before, String after) {
    Pg387TrustedDeployment.validateRootDelta(name, bytes(before), bytes(after));
    assertions++;
  }

  private static void reject(String name, String before, String after) {
    try {
      Pg387TrustedDeployment.validateRootDelta(name, bytes(before), bytes(after));
    } catch (IllegalArgumentException | IllegalStateException expected) {
      assertions++;
      return;
    }
    throw new AssertionError("unapproved Unit delta admitted");
  }

  private static byte[] bytes(String value) {
    return value.getBytes(StandardCharsets.UTF_8);
  }
}
