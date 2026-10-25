# G13.07 共有fixture7のDDL/共通Main責任根拠

2026-10-25 15:51 JST、G13_SHARED_FIXTURE7_SOURCE_V1/source64446不変更、開始.5/3/7pp/cap10。fresh06:50:14UTC使用2/残98/reset1793513544/secondarynull。現在窓残10以下/取得不能等まで継続、旧累計80/90停止なし。

source rootは`src/`。6DB fixture/所有Testは正規DDL・rolesを適用/検証する支援責任P00401へ対応付け、個別業務consumerの費用へ再配賦しない。実行JVM共通fixtureは全consumerの直接Main参照交差がServiceProcessResources一つであることとSSC316の目的を併せてP01804へ対応する。Main CPなしを架空参照へ変更しない。

|source|primary/cost|profile/根拠|
|---|---|---|
|schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/BatchDatabaseFixture.java|WBS-P004-01|SQL; Batch用の正規DDL/role適用fixture|
|schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/BatchFixtureOwnershipTest.java|WBS-P004-01|SQL_VIA:BatchDatabaseFixture; 同fixtureの所有・全24表・role/config後条件|
|schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/logging/ApiLogDatabaseFixture.java|WBS-P004-01|SQL; 共通API用の正規DDL/role適用fixture|
|schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/logging/ApiLogFixtureOwnershipTest.java|WBS-P004-01|SQL_VIA:ApiLogDatabaseFixture; 同fixtureの所有・全24表・role/config後条件|
|schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/logging/WebLogDatabaseFixture.java|WBS-P004-01|SQL; Web用の正規DDL/role適用fixture|
|schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/logging/WebLogDatabaseFixtureTest.java|WBS-P004-01|SQL_VIA:WebLogDatabaseFixture; 同fixtureのconfig/失敗/owned lifecycle|
|schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/OwnedRetentionProcess.java|WBS-P018-04|COMMON_MAIN:ServiceProcessResources; 全6consumerの直接Main共通集合がServiceProcessResources一つ、SSC316|

SQL profileは原485がP00401として持つdb内全SQLを正規source/snapshot/hashへ照合し、fixtureのdb root・roles/provisioning・migrationのliteral指定を確認。SQL_VIAは当moduleのfixtureへの実class symbol参照を確認する。共通Main profileは全直接consumer集合から直接Main class集合の交差を取り、ServiceProcessResourcesのみ・原owner/costとMain source hashが一致することを確認。consumerの全既知担当を関連として残し、未登録consumerは欠測/保留一覧へ分ける。これらはprimary根拠であり全依存/全method/oracleの網羅証明ではない。

原9386v3/9246/9534を固定hashで参照。Producerの既graphとpostの保存1910class独立byte解析を別経路にし、凍結表別parse、source/resource/consumerのhash、owner/cost、共通Mainの唯一性、偽profile/別module/欠落重複/実行成功捏造のnegativeを確認。旧949全canonical/関連/runtime/artifact witness・7近傍/元logical優先を保持。

許可は公開source/SQL本文/classfile byteの読取とmetadata工具vectorのみ。SQL/JDBC/DB/鍵/credential実体/子JVM/target compile-load-init/JUnit/実FD/native/Root/VM/Unit/intent/permit/配備/遠隔操作0。拒否操作の試行/既成功確認再演0、Currentbaseline/oracle変更0、安全HOLD維持。

見込Java1774→1781/1789/Test809→816/824/残15→8、限定949→956。独立確認後だけ計上し、file責任を全method/RD/UI/SS/TestID/oracle/終了依存/PGPT工数率/実PT/coverage/正式受入へ変換しない。費用G13.07一回、原941943/481484/見積受入意味・正式1964-53/17-190/工数null/QA051final/全current auditHOLD/全actualHOLD不変。保存後も残8の根拠/独立普通PGPTへ、小群/報告/PMO返信待ちで停止しない。
