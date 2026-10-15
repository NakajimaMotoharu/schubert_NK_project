package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.net.StandardProtocolFamily;
import java.net.UnixDomainSocketAddress;
import java.nio.channels.Channels;
import java.nio.channels.SocketChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.List;
import java.util.UUID;

/**
 * PT-OPS-LFACT001..007/SS343/451. Isolated real Unit's default-factory rejection tests. Never a
 * normal Morning entry, permit issuer or production deployment. Independent OS observer must attest
 * the deliberately malformed approval read and absence of downstream actions per case.
 */
public final class NativeLegacyAdmissionNegative {
  private static final String SOURCE = "a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25";
  private static final UUID RUN = UUID.fromString("11111111-1111-4111-8111-111111111111");

  private NativeLegacyAdmissionNegative() {}

  @FunctionalInterface
  private interface Attempt {
    void execute() throws IOException;
  }

  private record Case(String id, Attempt attempt) {}

  private static String forbiddenCallback() {
    throw new AssertionError("business callback forbidden after malformed approval");
  }

  private static List<Case> cases() {
    return List.of(
        new Case(
            "PT-OPS-LFACT001",
            () -> MorningControlScope.executeOwned((state, database) -> forbiddenCallback())),
        new Case(
            "PT-OPS-LFACT002",
            () ->
                MorningControlScope.executeOwnedEpoch(
                    (state, database, epoch) -> forbiddenCallback())),
        new Case(
            "PT-OPS-LFACT003",
            () ->
                MorningControlScope.executeResumeOwned(
                    RUN, (state, database) -> forbiddenCallback())),
        new Case(
            "PT-OPS-LFACT004",
            () ->
                MorningControlScope.executeResumeOwnedEpoch(
                    RUN, (state, database, epoch) -> forbiddenCallback())),
        new Case(
            "PT-OPS-LFACT005",
            () -> MorningBackupStage.resume(RUN, (request, begins) -> forbiddenCallback())),
        new Case(
            "PT-OPS-LFACT006", () -> MorningControlScope.execute(state -> forbiddenCallback())),
        new Case(
            "PT-OPS-LFACT007",
            () -> MorningControlScope.executeResume(RUN, state -> forbiddenCallback())));
  }

  private static void exchange(
      BufferedWriter writer, BufferedReader reader, String request, String expected)
      throws IOException {
    writer.write(request);
    writer.newLine();
    writer.flush();
    if (!expected.equals(reader.readLine()))
      throw new IOException("independent negative-fault witness unavailable");
  }

  private static void execute(String[] args) throws Exception {
    if (args.length != 2
        || !args[0].equals("/run/pgpt-negative-3210/watch.sock")
        || !Path.of(args[1]).getParent().equals(Path.of("/var/lib/pgpt-negative-3210"))
        || !Path.of(args[1]).getFileName().toString().matches("case-cohort-[a-z0-9-]{1,40}"))
      throw new IllegalArgumentException("fixed private negative fixture only");
    Path out = Files.createDirectory(Path.of(args[1]));
    Files.setPosixFilePermissions(out, PosixFilePermissions.fromString("rwx------"));
    var context = RootStartupContext.create();
    var root = context.capture(RootStartupContext.Service.MORNING);
    try (var channel = SocketChannel.open(StandardProtocolFamily.UNIX)) {
      channel.connect(UnixDomainSocketAddress.of(args[0]));
      var writer = new BufferedWriter(Channels.newWriter(channel, StandardCharsets.UTF_8));
      var reader = new BufferedReader(Channels.newReader(channel, StandardCharsets.UTF_8));
      exchange(
          writer, reader, "HELLO|" + ProcessHandle.current().pid() + "|" + root.boot(), "READY");
      for (var test : cases()) {
        context.recheck(root);
        exchange(writer, reader, "BEGIN|" + test.id(), "ARMED|" + test.id());
        boolean refused = false;
        try {
          test.attempt().execute();
        } catch (IOException expected) {
          // This alone never passes: observer must prove the exact approval read
          // and no later DB/start/stop/permit action, not an earlier unrelated gate.
          refused = true;
        }
        if (!refused) throw new AssertionError("malformed release must not be admitted");
        context.recheck(root);
        exchange(writer, reader, "END|" + test.id(), "ACCESSED|" + test.id());
        String value =
            "{\"testId\":\""
                + test.id()
                + "\",\"status\":\"PASS\",\"source\":\""
                + SOURCE
                + "\",\"expectedRefusal\":true,\"independentApprovalReadWitness\":true,"
                + "\"businessCallbackCount\":0,\"formalAccepted\":false}\n";
        Path result = out.resolve(test.id() + ".safe.json");
        Files.writeString(result, value, StandardCharsets.UTF_8, StandardOpenOption.CREATE_NEW);
        Files.setPosixFilePermissions(result, PosixFilePermissions.fromString("rw-------"));
      }
      exchange(writer, reader, "COMPLETE|7", "SEALED|7");
    }
    Files.writeString(
        out.resolve("complete.safe.json"),
        "{\"actualExit\":0,\"cases\":7,\"wholeAccepted\":false,\"formalAccepted\":false}\n",
        StandardCharsets.UTF_8,
        StandardOpenOption.CREATE_NEW);
    System.out.println("PG3216_NEGATIVE_CASES_PASS cases7=true businessEntry0=true formal=false");
  }

  public static void main(String[] args) {
    try {
      execute(args);
    } catch (Throwable failed) {
      System.err.println("PG3216_NEGATIVE_CASES_FAIL type=" + failed.getClass().getSimpleName());
      System.exit(1);
    }
  }
}
