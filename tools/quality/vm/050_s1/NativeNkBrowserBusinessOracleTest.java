package dev.codex.schubert.characterization;

import java.util.List;
import com.fasterxml.jackson.databind.node.ObjectNode;

/** Pure independent typed vectors; does not read credentials, DB, network, or VM. */
public final class NativeNkBrowserBusinessOracleTest {
  static void check(boolean value) { if (!value) throw new AssertionError("independent browser oracle vector"); }
  static void rejects(Runnable value) {
    try { value.run(); } catch (IllegalStateException expected) { return; }
    throw new AssertionError("negative fixture was accepted");
  }

  public static void main(String[] args) throws Exception {
    var json = NativeNkBrowserBusinessCohort.JSON;
    ObjectNode valid = (ObjectNode) json.readTree("{\"commit\":\"a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25\",\"schema\":\"028\",\"config\":\"1\",\"app\":\"0.1.0-SNAPSHOT\",\"protocol\":\"0.1.0-SNAPSHOT\"}");
    check(NativeNkBrowserBusinessCohort.information(valid));
    check(!NativeNkBrowserBusinessCohort.information(null));
    check(!NativeNkBrowserBusinessCohort.information(json.createArrayNode()));
    for (String key : List.of("commit", "schema", "config", "app", "protocol")) {
      ObjectNode changed = valid.deepCopy(); changed.remove(key); check(!NativeNkBrowserBusinessCohort.information(changed));
      changed = valid.deepCopy(); changed.put(key, "foreign"); check(!NativeNkBrowserBusinessCohort.information(changed));
      changed = valid.deepCopy(); changed.putNull(key); check(!NativeNkBrowserBusinessCohort.information(changed));
    }
    ObjectNode numeric = valid.deepCopy(); numeric.put("config", 1); check(!NativeNkBrowserBusinessCohort.information(numeric));
    ObjectNode extra = valid.deepCopy(); extra.put("extra", "x"); check(!NativeNkBrowserBusinessCohort.information(extra));
    var user = json.readTree("{\"id\":1,\"password_hash\":\"fixture\",\"role\":\"ADMIN\",\"version\":7,\"last_login_at\":null,\"failed_count\":0,\"failure_window_started_at\":null,\"locked_until\":null}");
    var expected = json.readTree("{\"id\":1,\"password_hash\":\"fixture\",\"role\":\"ADMIN\",\"version\":7}");
    check(expected.equals(NativeNkBrowserBusinessCohort.protectedUser(user)));
    check(user.has("last_login_at"));
    for (String key : List.of("password_hash", "role", "version")) {
      ObjectNode changed = (ObjectNode) user.deepCopy(); changed.put(key, "changed");
      check(!expected.equals(NativeNkBrowserBusinessCohort.protectedUser(changed)));
    }
    var rows = json.readTree("[{\"id\":\"00000000-0000-0000-0000-000000000001\",\"revoked\":false,\"reason\":null}]");
    check(NativeNkBrowserBusinessCohort.ids(rows).size() == 1);
    check(NativeNkBrowserBusinessCohort.session(rows, "00000000-0000-0000-0000-000000000001").path("revoked").isBoolean());
    rejects(() -> NativeNkBrowserBusinessCohort.session(rows, "00000000-0000-0000-0000-000000000002"));
    var missing = json.readTree("[{}]"); rejects(() -> NativeNkBrowserBusinessCohort.ids(missing));
    var duplicate = json.createArrayNode().add(rows.get(0)).add(rows.get(0)); rejects(() -> NativeNkBrowserBusinessCohort.ids(duplicate));
    check("'a''b'".equals(NativeNkBrowserBusinessCohort.literal("a'b")));
    check("PG3128 native 質問 <b>独立oracle</b>".equals(NativeNkBrowserBusinessCohort.BODY));
    var baseline = json.readTree(java.nio.file.Path.of("program/characterization/baseline/current/artifacts/CHR-U01.json").toFile());
    check(baseline.path("cards").equals(json.valueToTree(List.of("シナリオ閲覧", "検索", "アニメ視聴", "音楽", "ログ照会"))));
    check(NativeNkBrowserBusinessCohort.validMenu(List.of("シナリオ閲覧", "検索", "アニメ視聴", "音楽", "質問する", "通知", "質問回答", "ログ照会", "User管理")));
    check(!NativeNkBrowserBusinessCohort.validMenu(List.of("Scenario閲覧", "検索", "Animation視聴", "Music", "質問する", "通知", "質問回答", "Log照会", "User管理")));
    check(!NativeNkBrowserBusinessCohort.validMenu(null));
    check(!NativeNkBrowserBusinessCohort.validMenu(NativeNkBrowserBusinessCohort.MENU.reversed()));
    var duplicateMenu = new java.util.ArrayList<>(NativeNkBrowserBusinessCohort.MENU); duplicateMenu.add("User管理"); check(!NativeNkBrowserBusinessCohort.validMenu(duplicateMenu));
    check(NativeNkBrowserBusinessCohort.validSelfForms(List.of("PASSWORD")));
    for (Object invalid : List.of(List.of("STATUS", "ROLE", "PASSWORD", "UNLOCK"), List.of("PASSWORD", "UNLOCK"), List.of("ROLE"), List.of("PASSWORD", "PASSWORD"))) check(!NativeNkBrowserBusinessCohort.validSelfForms(invalid));
    check(!NativeNkBrowserBusinessCohort.validSelfForms(null));
    System.out.println("PG3128_PURE_ORACLE_PASS typedInfoVectors=20 protectedAccount=4 sessionNegative=3 menuCurrentBaselineAndNegative=6 selfNonlockedForms=6 sqlEscape=true networkReads=0");
  }
}
