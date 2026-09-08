# NK-DAT-001 認証Inbox参照実行結果

## 1. 状態

PG-D-120/005仕様のPT-DB-INBOX-009～016は探索8件成功、failure/error/skipped0。追加AuthenticationInboxInspectorのline35/method2/class1/branch12すべてmissed0（instruction144/complexity8もmissed0）、SpotBugs0、NullAway/Enforcer/format PASS。正式clean回帰/収集前でProgram全体未完了。既存構造8件の正式結果は004を参照する。

## 2. 探索履歴（全てdev-foundation、正式source固定前）

| 実行 | 結果 | 対応 |
|---|---|---|
| 2026-09-09 07:45:27 JST終了、session84294 | Maven exit1、PT未実行 | offline prefix spotbugsを解決できず。version付き完全座標を指定して再実行、環境追加download不要 |
| 07:46:48 JST終了、session66209 | testCompile exit1、新8件未実行。Protocol5/Storage16成功 | 明示closeの-Werror違反BUG-077を5884155eで先行起票後是正 |
| 07:47:53 JST終了、session24245 | testCompile exit1、新8件未実行 | 新fixture constructorへContextHashのchecked例外宣言漏れ。test scaffoldの宣言を追加。Production変更なし |
| 07:48:54 JST終了、session85412 | 8件、5failure/0error/0skip、exit1 | DB時刻表現4件/Logout error N17 filler1件のfixture不備。BUG-078/YKT-069を95379dc5で先行起票 |
| 07:51:50 JST終了、session26050 | 8件成功、Protocol5/Storage16も成功、exit0 | UTC/JST双方でInstant一致、N17 errorゼロ正常/space異常。追加class全coverage100%、静的解析0 |

部分探索command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=FieldCodecTest,OwnedTransferDirectoryTest,AuthenticationInboxInspectorTest org.jacoco:jacoco-maven-plugin:0.8.15:prepare-agent test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check`。当該累積coverageを全体gate合格とはしない。生ログ/鍵/context/暗号文/DB dumpは証跡へ保存しない。

## 3. YKT-069と非更新確認

| 対象 | 実施・根拠 |
|---|---|
| DB issued/lastAccess/expiry | 4ケースの後条件をgetTimestamp().toInstant()と独立ISO期待値で比較。接続UTC/JST双方で同じInstantを確認。DB設定やProductionは変更しない |
| Login X17 issued/expiry | 成功時JST固定値、失敗時space。後日role/name/status/idle期限変更で元snapshotを不整合扱いしない |
| Logout N17 revoked | 成功時固定JST、error時17桁zero。spaceの不正fixtureを独立negativeへ追加。owner/UUID/hash/失効false/±1msも拒否 |
| null/JDBC/鍵/並行 | caller null、autocommit/closed connection/SQL例外、鍵previous/wrong/unknown/close、100並行の正常/不整合。session時間/失効状態/監査数/入力暗号byteが不変。proxyがcommit/rollback/closeを禁止 |

正式回帰後、`evidence/authentication-inspection/manifest.json`/`results.xml`/`checksums.sha256`へrun/commit/環境/期待根拠/実結果/coverage/Test ID/hashを固定する。BUG-077/078/YKT-069は正式再試験待ち。DB削除/lock/最小role/oneshot/非認証参照は未実施でBUG-014/YKT-012/UIC-006/SSC-049を完了にしない。
