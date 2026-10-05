package dev.codex.schubert.characterization;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.microsoft.playwright.Browser;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.Playwright;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.PosixFilePermission;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;

/**
 * SS355/QA051: external shared-Current L01 OBSERVATION, not a PASS or all24 gate. Never resets
 * logs/accounts, starts/stops an application, filters action values, or changes Current baseline.
 * The caller separately authenticates source/parent/fixture and owns private output protection.
 */
public final class NativeNkL01Capture472 {
  private static final Path PRIVATE = Path.of("/home/mini/codex/project1/work/pgpt-vm/private");
  private static final ObjectMapper JSON = new ObjectMapper();

  private NativeNkL01Capture472() {}

  static boolean arguments(String[] args) {
    return args!=null && args.length==3
        && "/home/mini/codex/project1/work/pgpt-runs/PG379/pg472-l01-v1".equals(args[0])
        && "c8ad413437be409f70ec37bdba33c5e3cd21790b".equals(args[1])
        && PRIVATE.resolve("pg468-active-account.private.json").toString().equals(args[2]);
  }
  public static void main(String[] args) throws Exception {
    if (!arguments(args))
      throw new IllegalArgumentException("new private output, exact source and retained active credential required");
    Path output = Path.of(args[0]);
    NativeNkBootstrapAuthentication.actualSource(args[1]);
    Files.createDirectory(output);
    Files.setPosixFilePermissions(
        output,
        Set.of(
            PosixFilePermission.OWNER_READ,
            PosixFilePermission.OWNER_WRITE,
            PosixFilePermission.OWNER_EXECUTE));
    Path credentials = Path.of(args[2]);
    if (Files.isSymbolicLink(credentials) || !Files.getPosixFilePermissions(credentials)
        .equals(Set.of(PosixFilePermission.OWNER_READ, PosixFilePermission.OWNER_WRITE)))
      throw new IllegalStateException("private credential permission differs");
    byte[] credentialBytes=Files.readAllBytes(credentials);
    if(credentialBytes.length>4096)throw new IllegalStateException("private credential bounds differ");
    com.fasterxml.jackson.databind.JsonNode retained;
    try{retained=JSON.readTree(credentialBytes);}finally{java.util.Arrays.fill(credentialBytes,(byte)0);}
    if(retained.size()!=2 || !retained.path("username").isTextual() || !retained.path("password").isTextual())
      throw new IllegalStateException("private credential shape differs");
    var account = new CharacterizationEnvironment.Credential(retained.path("username").textValue(),retained.path("password").textValue());
    var before =
        query("select json_build_object('maxId',coalesce(max(id),0)) from schubert.app_logs");
    long watermark = before.path("maxId").longValue();
    try (Playwright playwright = Playwright.create();
        Browser browser =
            playwright.chromium().launch(new BrowserType.LaunchOptions().setHeadless(true));
        BrowserContext context =
            browser.newContext(
                CurrentCharacterizationTest.desktopOptions(false)
                    .setProxy("socks5://127.0.0.1:55169"))) {
      Page page = CurrentCharacterizationTest.login(context, "https://10.0.2.15:55160", account);
      var observed =
          CurrentCharacterizationTest.captureLogProjection(
              page,
              "https://10.0.2.15:55160",
              () -> {
                // Fixed collection settle, not browser retry or an expected-value generator.
                Thread.sleep(10_000);
                var data =
                    query(
                        "select json_build_object('actions',coalesce(json_agg(action order by id),'[]'::json),"
                            + "'types',coalesce(json_agg(category order by id),'[]'::json)) from schubert.app_logs where id>"
                            + watermark);
                List<String> actions =
                    JSON.convertValue(
                        data.get("actions"),
                        new com.fasterxml.jackson.core.type.TypeReference<List<String>>() {});
                List<String> types =
                    JSON.convertValue(
                        data.get("types"),
                        new com.fasterxml.jackson.core.type.TypeReference<List<String>>() {});
                return new CurrentCharacterizationTest.LogProjectionRows(actions, types);
              });
      Map<String, Object> record = new TreeMap<>(observed);
      record.put("caseId", "CHR-L01");
      record.put("status", "OBSERVED_NOT_ACCEPTED");
      record.put("productionSource", args[1]);
      record.put("watermarkOnlyIsNotEventCorrelation", true);
      record.put("outageReplayNotTested", true);
      JSON.writerWithDefaultPrettyPrinter()
          .writeValue(output.resolve("L01-observed.private.json").toFile(), record);
      Files.setPosixFilePermissions(
          output.resolve("L01-observed.private.json"),
          Set.of(PosixFilePermission.OWNER_READ, PosixFilePermission.OWNER_WRITE));
      System.out.println(
          "NK_CHR_L01_OBSERVED sharedCurrentDriver=true resets0=true actionNormalization0=true pass=false fullGate=false");
    }
  }

  private static com.fasterxml.jackson.databind.JsonNode query(String sql) throws Exception {
    var process =
        new ProcessBuilder(
                "ssh",
                "-i",
                PRIVATE.resolve("vm-access").toString(),
                "-p",
                "22222",
                "-oBatchMode=yes",
                "-oConnectTimeout=5",
                "-oIdentitiesOnly=yes",
                "-oStrictHostKeyChecking=yes",
                "-oUserKnownHostsFile=" + PRIVATE.resolve("known_hosts"),
                "ubuntu@127.0.0.1",
                "sudo -n -u postgres /usr/bin/psql -X -qAt -v ON_ERROR_STOP=1 -d schubert_nk")
            .redirectError(ProcessBuilder.Redirect.DISCARD)
            .start();
    try (var input = process.getOutputStream()) {
      input.write(
          ("BEGIN READ ONLY; SET LOCAL statement_timeout='5s';\n" + sql + ";\nCOMMIT;\n")
              .getBytes(java.nio.charset.StandardCharsets.UTF_8));
    }
    byte[] bytes = process.getInputStream().readNBytes(131073);
    if (!process.waitFor(10, java.util.concurrent.TimeUnit.SECONDS)) {
      process.destroy();
      if (!process.waitFor(5, java.util.concurrent.TimeUnit.SECONDS))
        throw new IllegalStateException("private query child did not terminate");
      throw new IllegalStateException("private projection query deadline");
    }
    if (process.exitValue() != 0 || bytes.length > 131072)
      throw new IllegalStateException("private projection query unavailable");
    return JSON.readTree(bytes);
  }
}
