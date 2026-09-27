import java.io.*;
import java.nio.file.*;
import java.nio.file.attribute.*;
import java.security.*;
import java.util.*;
import org.apache.activemq.artemis.cli.commands.*;
import org.apache.activemq.artemis.utils.PasswordMaskingUtil;
import picocli.CommandLine;

/** Isolated VM provisioning only, no Production admission or secret output. */
public final class ProvisionBroker {
  private static final Path INSTANCE = Path.of("/var/lib/schubert-nk/artemis");
  private static final Path CREDENTIALS = Path.of("/etc/schubert-nk/credentials");
  public static void main(String[] args) throws Exception {
    if (args.length != 0 || !Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim()
        .equals("pgpt-r2-20260927-01") || !System.getProperty("user.name").equals("root"))
      throw new IllegalStateException("isolated root fixture required");
    var create = new Create();
    new CommandLine(create).parseArgs(INSTANCE.toString(), "--user=pgpt-initial", "--role=bootstrap",
        "--require-login", "--nio", "--no-web", "--no-autotune", "--no-autocreate",
        "--no-amqp-acceptor", "--no-mqtt-acceptor", "--no-stomp-acceptor", "--no-hornetq-acceptor");
    create.setHome(Path.of("/opt/apache-artemis-2.56.0").toFile());
    create.setPassword(random());
    var discard = new PrintStream(OutputStream.nullOutputStream());
    create.execute(new ActionContext(InputStream.nullInputStream(), discard, discard));
    var users = new Properties();
    var roles = new Properties();
    for (var identity : Map.of("api", "nk_api", "web", "nk_web", "ops", "nk_ops",
        "maintenance", "nk_mq_maintenance").entrySet()) {
      String name = "schubert_" + identity.getKey();
      String password = random();
      Path credential = CREDENTIALS.resolve("mq-" + identity.getKey());
      Files.writeString(credential, password + "\n", StandardOpenOption.CREATE,
          StandardOpenOption.TRUNCATE_EXISTING);
      Files.setPosixFilePermissions(credential, PosixFilePermissions.fromString("rw-------"));
      users.setProperty(name, PasswordMaskingUtil.getHashProcessor().hash(password));
      roles.setProperty(identity.getValue(), name);
    }
    for (var item : Map.of("artemis-users.properties", users, "artemis-roles.properties", roles).entrySet()) {
      var path = INSTANCE.resolve("etc").resolve(item.getKey());
      try (var output = Files.newOutputStream(path)) { item.getValue().store(output, "Private VM fixture"); }
      Files.setPosixFilePermissions(path, PosixFilePermissions.fromString("rw-------"));
    }
    System.out.println("PGPT_VM_BROKER_CREATED credentialsGenerated=true valuesPrinted=false admitted=false");
  }
  private static String random() {
    byte[] bytes = new byte[32]; new SecureRandom().nextBytes(bytes);
    try { return Base64.getUrlEncoder().withoutPadding().encodeToString(bytes); }
    finally { Arrays.fill(bytes, (byte) 0); }
  }
}
