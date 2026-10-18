package dev.codex.schubert.characterization;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.microsoft.playwright.*;
import com.microsoft.playwright.options.FormData;
import com.microsoft.playwright.options.RequestOptions;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.nio.file.attribute.PosixFilePermissions;
import java.security.MessageDigest;
import java.util.*;
import java.util.concurrent.TimeUnit;

/** UI223224225226/SS313314323331332/QA048049/DIF016. No reset/start/stop/DB write.
 * Independent HTTP/DOM/SQL/JCA oracle. Credentials and session/token values stay in memory.
 * This is a finite PG/PT native cohort, not all CHR/IT/ST acceptance.
 */
public final class NativeNkBrowserBusinessCohort {
  static final ObjectMapper JSON = new ObjectMapper();
  static final Path PRIVATE = Path.of("/home/mini/codex/project1/work/pgpt-vm/private");
  static final String BASE = "https://10.0.2.15:55160";
  static final String SOURCE = "a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25";
  static final String BODY = "PG3128 native 質問 <b>独立oracle</b>";
  static final List<String> MENU = List.of("シナリオ閲覧", "検索", "アニメ視聴", "音楽", "質問する", "通知", "質問回答", "ログ照会", "User管理");
  static String stage = "ARGUMENT";
  static Path output;

  static void require(boolean value) {
    if (!value) throw new IllegalStateException("finite browser oracle failed at " + stage);
  }

  static String literal(String value) {
    return "'" + value.replace("'", "''") + "'";
  }

  static JsonNode query(String sql) throws Exception {
    List<String> command = new ArrayList<>(List.of("ssh", "-i", PRIVATE.resolve("vm-access").toString(), "-p", "22222", "-oBatchMode=yes", "-oConnectTimeout=5", "-oServerAliveInterval=5", "-oServerAliveCountMax=1", "-oIdentitiesOnly=yes", "-oStrictHostKeyChecking=yes", "-oUserKnownHostsFile=" + PRIVATE.resolve("known_hosts"), "ubuntu@127.0.0.1", "sudo -n -u postgres /usr/bin/psql -X -qAt -v ON_ERROR_STOP=1 -d schubert_nk"));
    Process process = new ProcessBuilder(command).redirectError(ProcessBuilder.Redirect.DISCARD).start();
    try (var input = process.getOutputStream()) {
      input.write(("BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY; SET LOCAL timezone='UTC'; SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='500ms';\n" + sql + ";\nCOMMIT;\n").getBytes(StandardCharsets.UTF_8));
    }
    byte[] bytes = process.getInputStream().readNBytes(67108865);
    require(process.waitFor(15, TimeUnit.SECONDS) && process.exitValue() == 0 && bytes.length <= 67108864);
    try { return JSON.readTree(bytes); } finally { Arrays.fill(bytes, (byte) 0); }
  }

  static JsonNode credential() throws Exception {
    Path input = PRIVATE.resolve("pg468-active-account.private.json");
    require(!Files.isSymbolicLink(input) && Files.isRegularFile(input) && Files.size(input) <= 4096 && Files.getPosixFilePermissions(input).equals(PosixFilePermissions.fromString("rw-------")));
    byte[] bytes = Files.readAllBytes(input);
    try {
      JsonNode value = JSON.readTree(bytes);
      require(value.isObject() && value.size() == 2 && value.path("username").isTextual() && value.path("password").isTextual() && value.path("username").textValue().matches("[a-z0-9_]{1,64}"));
      return value;
    } finally { Arrays.fill(bytes, (byte) 0); }
  }

  static JsonNode user(String username) throws Exception {
    JsonNode value = query("select coalesce(json_agg(to_jsonb(u)),'[]'::json) from schubert.app_users u where username=" + literal(username));
    require(value.isArray() && value.size() == 1);
    return value.get(0);
  }

  static JsonNode protectedUser(JsonNode user) {
    var value = user.deepCopy();
    var object = (com.fasterxml.jackson.databind.node.ObjectNode) value;
    object.remove(List.of("last_login_at", "failed_count", "failure_window_started_at", "locked_until"));
    return object;
  }

  static JsonNode sessions(long user) throws Exception {
    return query("select coalesce(json_agg(json_build_object('id',id,'revoked',revoked,'reason',revoke_reason) order by issued_at,id),'[]'::json) from schubert.auth_sessions where user_id=" + user);
  }

  static Set<String> ids(JsonNode rows) {
    Set<String> values = new HashSet<>();
    require(rows.isArray());
    for (JsonNode row : rows) require(row.path("id").isTextual() && row.path("id").textValue().matches("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}") && values.add(row.path("id").textValue()));
    return values;
  }

  static JsonNode session(JsonNode rows, String id) {
    for (JsonNode row : rows) if (id.equals(row.path("id").textValue())) return row;
    throw new IllegalStateException("expected fresh session missing");
  }

  static JsonNode business(long excludedQuestion) throws Exception {
    return query("select json_build_object('questions',(select coalesce(jsonb_agg(to_jsonb(q) order by id),'[]') from schubert.questions q where id<>" + excludedQuestion + "),'answers',(select coalesce(jsonb_agg(to_jsonb(a) order by id),'[]') from schubert.answers a where question_id<>" + excludedQuestion + "),'jobs',(select coalesce(jsonb_agg(to_jsonb(j) order by id),'[]') from schubert.async_jobs j where question_id<>" + excludedQuestion + "),'notifications',(select coalesce(jsonb_agg(to_jsonb(n) order by id),'[]') from schubert.notifications n where question_id<>" + excludedQuestion + "))");
  }

  static String digest(JsonNode value) throws Exception {
    return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(JSON.writeValueAsBytes(value)));
  }

  static JsonNode allRows() throws Exception {
    List<String> tables = new ArrayList<>();
    for (String name : List.of("answers", "app_logs", "app_users", "async_jobs", "audio_files", "auth_sessions", "batch_runs", "entry_audio_links", "games", "inbox_inspection_progress", "log_cleanup_progress", "login_ip_attempts", "media_assets", "mq_outbox", "notifications", "questions", "request_inbox", "script_entries", "script_files", "speakers")) tables.add("schubert." + name);
    for (String name : List.of("pending_context_revocations", "web_http_sessions", "web_log_outbox", "web_receipt_references")) tables.add("schubert_web_session." + name);
    List<String> expressions = new ArrayList<>();
    for (String table : tables) expressions.add(literal(table) + ",(select coalesce(jsonb_agg(j order by j::text),'[]'::jsonb) from(select to_jsonb(t) j from " + table + " t) q)");
    JsonNode value = query("select jsonb_build_object(" + String.join(",", expressions) + ")");
    require(value.isObject() && value.size() == 24); return value;
  }

  static String clockInstant(JsonNode value) {
    require(value != null && value.isTextual());
    try {
      return java.time.OffsetDateTime.parse(value.textValue()).toInstant().toString();
    } catch (java.time.DateTimeException invalid) {
      throw new IllegalStateException("invalid guest clock witness", invalid);
    }
  }

  static Map<String, Object> guestClock() throws Exception {
    long started = System.nanoTime();
    String hostBefore = java.time.Instant.now().toString();
    String instant = clockInstant(query("select to_json(clock_timestamp())"));
    String hostAfter = java.time.Instant.now().toString();
    long ended = System.nanoTime();
    require(ended - started >= 0 && ended - started <= TimeUnit.SECONDS.toNanos(30));
    return Map.of("clockSource", "guest-postgresql.clock_timestamp", "instant", instant,
        "hostStartNanos", started, "hostEndNanos", ended,
        "hostBeforeUtc", hostBefore, "hostAfterUtc", hostAfter);
  }

  static void privateValue(String name, Object value) throws Exception {
    require(name.matches("[a-z-]+\\.private\\.json"));
    byte[] bytes = JSON.writeValueAsBytes(value);
    try (var file = java.nio.channels.FileChannel.open(output.resolve(name), Set.of(StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE, LinkOption.NOFOLLOW_LINKS), PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rw-------")))) {
      var buffer = java.nio.ByteBuffer.wrap(bytes); while (buffer.hasRemaining()) file.write(buffer); file.force(true);
    } finally { Arrays.fill(bytes, (byte) 0); }
  }

  static void record(String id, Map<String, Object> measurements) throws Exception {
    Map<String, Object> value = new TreeMap<>(measurements);
    value.put("testId", id); value.put("status", "PASS"); value.put("source", SOURCE);
    value.put("timeUTC", java.time.Instant.now().toString()); value.put("formalAccepted", false);
    value.put("secretsSaved", false);
    try (var file = java.nio.channels.FileChannel.open(output.resolve(id + ".safe.json"), Set.of(StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE, LinkOption.NOFOLLOW_LINKS), PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rw-------")))) {
      var bytes = java.nio.ByteBuffer.wrap(JSON.writeValueAsBytes(value)); while (bytes.hasRemaining()) file.write(bytes); file.force(true);
    }
  }

  static void source() throws Exception {
    Process process = new ProcessBuilder("ssh", "-i", PRIVATE.resolve("vm-access").toString(), "-p", "22222", "-oBatchMode=yes", "-oConnectTimeout=5", "-oIdentitiesOnly=yes", "-oStrictHostKeyChecking=yes", "-oUserKnownHostsFile=" + PRIVATE.resolve("known_hosts"), "ubuntu@127.0.0.1", "/usr/bin/curl -fsS --max-time 5 http://127.0.0.1:8081/actuator/info").redirectError(ProcessBuilder.Redirect.DISCARD).start();
    byte[] bytes = process.getInputStream().readNBytes(4097);
    require(process.waitFor(10, TimeUnit.SECONDS) && process.exitValue() == 0 && bytes.length <= 4096);
    try {
      JsonNode info = JSON.readTree(bytes);
      require(information(info));
    } finally { Arrays.fill(bytes, (byte) 0); }
  }

  static boolean information(JsonNode info) {
    return info != null && info.isObject() && info.size() == 5
        && info.path("commit").isTextual() && SOURCE.equals(info.path("commit").textValue())
        && info.path("schema").isTextual() && "028".equals(info.path("schema").textValue())
        && info.path("config").isTextual() && "1".equals(info.path("config").textValue())
        && info.path("app").isTextual() && "0.1.0-SNAPSHOT".equals(info.path("app").textValue())
        && info.path("protocol").isTextual() && "0.1.0-SNAPSHOT".equals(info.path("protocol").textValue());
  }

  static void menu(Page page, String username) {
    require(page.url().equals(BASE + "/") && page.locator("h1").innerText().equals("schubert NK"));
    require(page.locator(".login-user").innerText().equals(username) && page.locator(".login-role").innerText().equals("ADMIN"));
    // SS313/UI264 + immutable Current CHR-U01 display labels, not UI223's logical names.
    require(validMenu(page.locator("nav.menu-grid a.menu-item strong").allInnerTexts()));
  }

  static boolean validMenu(List<String> titles) { return MENU.equals(titles); }
  static boolean validSelfForms(Object operations) { return List.of("PASSWORD").equals(operations); }

  static FormData questionForm(String csrf, String token, String body) {
    return FormData.create().set("_csrf", csrf).set("operation_token", token).set("question", body);
  }

  static JsonNode question(String token, long owner) throws Exception {
    require(token.matches("[0-9a-f-]{36}"));
    return query("select json_build_object('rows',(select coalesce(json_agg(to_jsonb(q)),'[]') from schubert.questions q where operation_token=" + literal(token) + "::uuid and owner_user_id=" + owner + "),'inbox',(select count(*) from schubert.request_inbox where operation_token=" + literal(token) + "::uuid and owner_user_id=" + owner + " and request_layout_id='QSBREQ01'))");
  }

  static void run(String[] args) throws Exception {
    require(args.length == 2 && Set.of("preflight", "run").contains(args[0]));
    output = Path.of(args[1]); require(!Files.exists(output)); Files.createDirectory(output, PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rwx------")));
    stage = "CRED-RO";
    JsonNode account = credential(); String username = account.path("username").textValue(), password = account.path("password").textValue();
    JsonNode beforeUser = user(username); long owner = beforeUser.path("id").longValue();
    require(beforeUser.path("role").asText().equals("ADMIN") && beforeUser.path("status").asText().equals("ACTIVE") && beforeUser.path("failed_count").intValue() == 0 && beforeUser.path("locked_until").isNull());
    NativeNkBootstrapAuthentication.independentPassword(beforeUser.path("password_hash").textValue(), password);
    record("PT-NBR-001", Map.of("readOnlyJcaCredentialQualified", true, "passwordResetIssued", false));
    if (args[0].equals("preflight")) return;
    // BUG1454: audit/DB timestamps originate in the guest, not the Browser host.
    // Capture independently before any source HTTP probe; never derive a bound from rows.
    Map<String, Object> lowerClock = guestClock();
    String lower = (String) lowerClock.get("instant");
    stage = "SOURCE"; source();
    privateValue("before-rows.private.json", allRows());
    JsonNode oldBusiness = business(-1); Set<String> initialIds = ids(sessions(owner)); List<String> fresh = new ArrayList<>();
    try (Playwright pw = Playwright.create(); Browser browser = pw.chromium().launch(new BrowserType.LaunchOptions().setHeadless(true));
         BrowserContext first = browser.newContext(CurrentCharacterizationTest.desktopOptions(false).setProxy("socks5://127.0.0.1:55169"));
         BrowserContext second = browser.newContext(CurrentCharacterizationTest.desktopOptions(false).setProxy("socks5://127.0.0.1:55169"));
         BrowserContext third = browser.newContext(CurrentCharacterizationTest.desktopOptions(false).setProxy("socks5://127.0.0.1:55169"))) {
      stage = "LOGIN-MENU";
      List<Page> pages = new ArrayList<>(); Set<String> previousIds = initialIds;
      for (BrowserContext context : List.of(first, second, third)) {
        Page page = CurrentCharacterizationTest.login(context, BASE, new CharacterizationEnvironment.Credential(username, password)); menu(page, username); pages.add(page);
        require(context.cookies().stream().anyMatch(c -> c.secure && c.httpOnly && c.path.equals("/") && String.valueOf(c.sameSite).equalsIgnoreCase("LAX")));
        Set<String> now = ids(sessions(owner)); Set<String> added = new HashSet<>(now); added.removeAll(previousIds); require(added.size() == 1 && now.containsAll(previousIds)); fresh.add(added.iterator().next()); previousIds = now;
      }
      record("PT-NBR-002", Map.of("realChromiumLogins", 3, "adminMenuLiteralOrder", true, "secureHttpOnlyLax", true));
      stage = "DIF016";
      JsonNode rows = sessions(owner); require(session(rows, fresh.get(0)).path("revoked").booleanValue() && session(rows, fresh.get(0)).path("reason").asText().equals("REPLACED"));
      require(!session(rows, fresh.get(1)).path("revoked").booleanValue() && !session(rows, fresh.get(2)).path("revoked").booleanValue());
      require(query("select count(*) from schubert.auth_sessions where user_id=" + owner + " and not revoked and expires_at>clock_timestamp()").intValue() == 2);
      pages.get(0).navigate(BASE + "/scenarios"); require(pages.get(0).url().startsWith(BASE + "/login"));
      record("PT-NBR-003", Map.of("maximumActive", 2, "oldestFreshRevokedReplaced", true, "revokedBrowserDenied", true));
      Page page = pages.get(2);
      stage = "ADMIN-READ"; Response response = page.navigate(BASE + "/admin/users/" + owner); require(response != null && response.status() == 200);
      require(page.locator("dd.username").innerText().equals(username) && page.locator("dd.role").innerText().equals("ADMIN") && validSelfForms(page.locator("form[data-operation]").evaluateAll("forms => forms.map(f => f.dataset.operation)")));
      require(protectedUser(beforeUser).equals(protectedUser(user(username)))); record("PT-NBR-004", Map.of("adminRead200", true, "noAccountMutation", true));
      stage = "CSRF";
      APIResponse denied = third.request().post(BASE + "/questions/new", RequestOptions.create().setForm(FormData.create().set("question", BODY)));
      try { require(denied.status() == 403); } finally { denied.dispose(); }
      record("PT-NBR-005", Map.of("missingCsrfHttp", 403));
      stage = "QUESTION-INVALID"; response = page.navigate(BASE + "/questions/new"); require(response != null && response.status() == 200);
      String token = page.locator("form.question-input input[name=operation_token]").inputValue(); String csrf = page.locator("form.question-input input[name=_csrf]").inputValue();
      require(token.matches("[0-9a-f-]{36}") && !csrf.isEmpty() && question(token, owner).path("rows").size() == 0);
      APIResponse invalid = third.request().post(BASE + "/questions/new", RequestOptions.create().setForm(questionForm(csrf, token, "invalid\nline")).setMaxRedirects(0));
      try { require(invalid.status() == 400); } finally { invalid.dispose(); }
      require(question(token, owner).path("rows").size() == 0 && question(token, owner).path("inbox").intValue() == 0);
      record("PT-NBR-006", Map.of("newlineHttp", 400, "businessRowsCreated", 0, "samePendingTokenKept", true));
      stage = "QUESTION-SUBMIT"; page.locator("textarea[name=question]").fill(BODY);
      Response submitted = page.waitForResponse(r -> r.url().equals(BASE + "/questions/new") && r.request().method().equals("POST"), () -> page.locator("form.question-input button[type=submit]").click());
      require(submitted.status() == 302); page.waitForURL(BASE + "/questions/accepted/*");
      String accepted = page.url(), receipt = page.locator("dd.receipt").innerText();
      require(receipt.matches("[0-9A-HJKMNP-TV-Z]{26}") && accepted.equals(BASE + "/questions/accepted/" + receipt) && page.locator("dd.question-body").innerText().equals(BODY) && page.locator("dd.question-body b").count() == 0);
      JsonNode q = question(token, owner); require(q.path("rows").size() == 1 && q.path("inbox").intValue() == 1);
      JsonNode row = q.path("rows").get(0); long questionId = row.path("id").longValue();
      require(row.path("body").asText().equals(BODY) && row.path("receipt_id").asText().equals(receipt) && !row.path("is_deleted").booleanValue());
      JsonNode locator = query("select coalesce(json_agg(to_jsonb(r)),'[]'::json) from schubert_web_session.web_receipt_references r where receipt_id=" + literal(receipt));
      require(locator.size() == 1 && locator.get(0).size() == 3 && locator.get(0).path("question_id").longValue() == questionId);
      record("PT-NBR-007", Map.of("submitHttp", 302, "exactBusinessRows", 1, "escapedHtml", true, "locatorOnlyThreeFields", true));
      stage = "QUESTION-REPLAY";
      APIResponse replay = third.request().post(BASE + "/questions/new", RequestOptions.create().setForm(questionForm(csrf, token, BODY)).setMaxRedirects(0));
      try { require(replay.status() == 302 && ("/questions/accepted/" + receipt).equals(replay.headers().get("location"))); } finally { replay.dispose(); }
      require(q.equals(question(token, owner))); record("PT-NBR-008", Map.of("sameTokenSameInputHttp", 302, "duplicateBusinessRows", 0, "sameReceipt", true));
      stage = "QUESTION-REFRESH"; response = page.reload(); require(response != null && response.status() == 200 && page.locator("dd.question-body").innerText().equals(BODY)); require(q.equals(question(token, owner)));
      record("PT-NBR-009", Map.of("refreshHttp", 200, "updateInboxCountUnchanged", true));
      stage = "NOTIFICATION"; response = page.navigate(BASE + "/notifications"); require(response != null && response.status() == 200);
      require(page.locator("tr.notification-row").filter(new Locator.FilterOptions().setHasText(receipt)).count() == 1);
      require(query("select count(*) from schubert.notifications where question_id=" + questionId + " and owner_user_id=" + owner).intValue() == 1);
      record("PT-NBR-010", Map.of("notificationHttp", 200, "ownerNotificationCount", 1));
      stage = "LOGOUT";
      for (Page active : List.of(pages.get(1), page)) { active.navigate(BASE + "/"); active.locator("form.logout-form button[type=submit]").click(); active.waitForURL(BASE + "/login*"); }
      rows = sessions(owner);
      for (int i : List.of(1, 2)) require(session(rows, fresh.get(i)).path("revoked").booleanValue() && session(rows, fresh.get(i)).path("reason").asText().equals("LOGOUT"));
      record("PT-NBR-011", Map.of("freshSessionsLogoutRevoked", 2, "noAdminReset", true));
      stage = "INDEPENDENT-POST"; require(protectedUser(beforeUser).equals(protectedUser(user(username))) && oldBusiness.equals(business(questionId)));
      source(); record("PT-NBR-012", Map.of("protectedAccountUnchanged", true, "allPriorFourBusinessTablesUnchanged", true, "businessBeforeSha256", digest(oldBusiness), "sameSourceBeforeAfter", true));
    }
    stage = "READONLY-DELIVERY-DRAIN";
    long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(90);
    while (query("select count(*) from schubert_web_session.web_log_outbox where created_at>=" + literal(lower) + "::timestamptz and status<>'SENT'").intValue() != 0) {
      require(System.nanoTime() < deadline); Thread.sleep(2000);
    }
    privateValue("after-rows.private.json", allRows());
    Map<String, Object> upperClock = guestClock();
    privateValue("context.private.json", Map.of("owner", owner, "lower", lower,
        "upper", upperClock.get("instant"), "clockDomain", "guest-postgresql-realtime",
        "lowerClock", lowerClock, "upperClock", upperClock));
  }

  public static void main(String[] args) {
    try { run(args); System.out.println("PG3128_BROWSER_COHORT_PASS mode=" + args[0] + " all24ExternalOraclePending=true formal=false secrets=false"); }
    catch (Throwable failure) {
      System.err.println("PG3128_BROWSER_COHORT_FAILED stage=" + stage + " type=" + failure.getClass().getName() + " secretsRedacted=true");
      System.exit(1);
    }
  }
}
