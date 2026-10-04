package dev.codex.schubert.characterization;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.microsoft.playwright.Browser;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.Playwright;
import com.microsoft.playwright.Response;
import java.nio.file.Path;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;

/**
 * A01-only external capture, no application/DB/start/stop/reset ownership. SS355 §12. Same Current
 * driver and browser settings. Parent/TLS/source witnesses remain separate. This main is not an
 * all24 Characterization gate and never marks L01 as run.
 */
public final class NativeNkA01Capture {
  private NativeNkA01Capture() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 3)
      throw new IllegalArgumentException("reportsRoot newEvidenceRoot baseline required");
    Path reports = Path.of(args[0]);
    Path output = Path.of(args[1]);
    TargetAdapter target =
        TargetAdapter.create("nk", "https://10.0.2.15:55160", reports, output, Set.of("10.0.2.15"));
    ObjectMapper json = new ObjectMapper();
    Map<String, Object> expected =
        json.readValue(
            Path.of(args[2]).toFile(),
            new com.fasterxml.jackson.core.type.TypeReference<Map<String, Object>>() {});
    assertEquals("CHR-A01", expected.get("caseId"));
    assertEquals("schubert - ログイン", expected.get("title"));
    // Exactly one approved field; never mutate Current baseline or derive from production.
    expected.put("title", "schubert NK - ログイン");
    try (Playwright playwright = Playwright.create();
        Browser browser =
            playwright.chromium().launch(new BrowserType.LaunchOptions().setHeadless(true))) {
      try (BrowserContext context =
          browser.newContext(
              CurrentCharacterizationTest.desktopOptions(false)
                  .setProxy("socks5://127.0.0.1:55169"))) {
        Page page = context.newPage();
        Response response = page.navigate(target.endpoint("/login").toString());
        Map<String, Object> observed =
            CurrentCharacterizationTest.captureLoginDisplay(page, response);
        Map<String, Object> actual = new TreeMap<>(observed);
        actual.put("caseId", "CHR-A01");
        actual.put("status", "PASS");
        assertEquals(json.valueToTree(expected), json.valueToTree(actual));
        ArtifactSink sink = new ArtifactSink(target.evidenceRoot());
        sink.write("CHR-A01", observed);
        System.out.println(
            "NK_CHR_A01_PASS sameCurrentDriver=true literalBaselinePlusDIF001TitleOnly=true csrfRedacted=true otherCasesNotRun=true fullGate=false");
      }
    }
  }
}
