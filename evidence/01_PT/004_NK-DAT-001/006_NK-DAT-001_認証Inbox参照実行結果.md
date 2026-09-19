# NK-DAT-001 認証Inbox参照実行結果

2026-09-20 最新確定: 正式PT-WEB-20260920-12/source0d0abbb80e91d016f961042e9b9e09cb07b5f7a9、05:24:36～05:36:26 JST/Maven11:48/exit0、全1544PT（Protocol80/Storage82/API689/Web285/Batch367/CHR41）、failed/error/skipped0。6Java全line/method/class/branch100%、Production5 NullAway/Enforcer/Spotless/SpotBugs未解決0、固定path3method限定review継続・coverage除外追加なし、CHR SpotBugs未設定。18collector/41scope整合・60負canary成功。DB29/266＋Batch25/281＋OPS17/142＋QST2/16＋ASY1/5＋Web4/44＝78部分成果754PT（全1544の内数）、今回再開比+129PT/+13部分成果。PG194階層3画面16PTを限定認定、BUG213～216/YKT169～172/SSC071限定範囲完了。PG195本文モデルは仕様のみ。BUG195/206/YKT154/162/SSC063、実archive/親/質問受付全体/残Web/Logout/QA045/実NKgateは未完了。固定加重38.25～49.75%（中心44%、約38～50%）、3画面接続で前回から+1 point。残量49%で継続、元dev-web3file保全、PGPT/IT/ST未完了。以下は履歴。

最新正式判定: PT-WEB-20260909-25/source6dd862d0、2026-09-09 12:46:41 JST完了、全918件PASS、failed/error/skipped0、5 Java moduleの4種coverage100%、静的解析0。本仕様8 PTも全PASS。evidence/authentication-inspection/manifest.jsonの現行SHA-256は `3115c99ed3a5af54df1d0eb52fe1931d85b891b4a7e559b2cfb9cb499917d529`。8collector/23scopeの全hashとtrace負canary、V001～013/Current baseline不変、秘密pattern scanを確認。本scopeのcoverage/SQL分岐対応は同manifestと以下の個別結果へ追跡。鍵file読取/main/oneshot・親process・Question/通知参照/親chunk走査は未完了、BUG-014/SSC-049継続。

以下は初回・探索・旧正式runの履歴。旧hashは証跡commit d98961c6等の該当履歴を参照し、現行manifestのhashと混同しない。未確定という旧記述は本段落の対象sliceに限って更新済み。

最新回帰PT-WEB-20260909-18/source56935aa0、2026-09-09 09:44:09 JST終了、exit0。認証8件再PASS、全838件/全Java coverage100%/静的解析0。現在の `evidence/authentication-inspection/manifest.json` SHA-256は `0aad4daaf00b3db1e719017f10d1c7d2268027467a0e00a823dbfff9f907d031`。以下run14とhashは証跡commit46d0f118の初回確定履歴であり、現在のmanifestと区別する。

## 1. 状態

PG-D-120/005仕様のPT-DB-INBOX-009～016は正式PT-WEB-20260909-14で8件成功、failure/error/skipped0。source 5cb8f4329067806c98b4f09a92abbeae5ed4e5cc、dev-foundation、2026-09-09 07:53:30～07:58:34 JST、exit0。全806件（Protocol80/Storage34/API410/Web241/CHR41）成功、全5moduleのline/method/class/branch100%、SpotBugs0、NullAway/Enforcer/format PASS。追加classはline35/method2/class1/branch12すべてmissed0。8collectorの9scope（016の構造/認証を別収集）と全checksum確認成功。Program全体は未完了。

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

`evidence/authentication-inspection/manifest.json`/`results.xml`/`checksums.sha256`へrun/commit/環境/期待根拠/実結果/coverage/Test ID/hashを固定済み。manifest SHA-256: `322328253d6e6459180b2e56dbe4d7428520df4eb472099cfc4d009669821e54`。BUG-077/078/YKT-069は5cb8f432修正と本正式回帰で完了。DB削除/lock/最小role/oneshot/非認証参照は本806件に含めず、BUG-014/YKT-012/UIC-006/SSC-049を完了にしない。
