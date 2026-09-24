# NK-ADM-001 Log照会Production組立単体テスト仕様書

PT-ADM-075/076 / PG256。対象は`LogQueryApplicationAssembly.create`、`ApiLogPathApplicationRuntime.startWithLoginAndLog`（Production）および`LogQueryApplicationServiceTest#adm075ProductionAssemblyUsesRealDependenciesAndNullContract`/`#adm076ProductionLogRouteReceivesThroughBroker`。RD FUN-008/AUT-002/MQ-006～010、UI225/232/235/241/242、SS311/312/314/323/324/332/351/352。Test IDをJUnit method・本書・010/evidence manifestで対応付ける。

目的: caller所有`FingerprintKeyRing`/`ResponseSnapshotCodec`、実PG18/Flyway、固定Clockから、ADMIN確認・read-only照会・Inbox/暗号化snapshot・監査のProduction依存graphが構築できること。事前fixtureは既存`LogApplicationFixture.seed`の合成ADMIN/session、独立SQLで投入したLog1件、SS324から独立配置した固定長LGSREQ01。入力は初回同一message1回と再送1回、さらにfactory4引数のnull。

期待値はProduction factoryやserviceを用いて生成しない。SS324固定Header result欄byte208～211が初回`0000`、再送`0200`、SS352のInbox後条件が同じmessageで1行、`app_logs`の`INBOX_REPLAYED`が1行とする。factory nullは各引数名の`NullPointerException`を起動前に返す。正常、再送、nullを本caseで確認し、境界/異常/例外/並行はPT-ADM-067～073の既存独立実PG試験が担当する。

PT-ADM-076は別fixtureの実Artemisを起動し、Production Login/Log受信親を同じ実PGに接続する。固定長LGSREQ01を実Queueへ2回送る。独立期待は返信bytes208～211の`0000`/`0200`、Inbox1行、再送監査1行、terminal0。Game-contextは非呼出し明示stubであり、全API起動/実NK CHRへ算入しない。

選択command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-api -Dtest=LogQueryApplicationServiceTest test`。正式環境/branch/commit、実行日時、終了code、coverage、入力/期待/実際、BUG/SSC、証跡path/hashは後続正式runと010/evidence manifest/実行結果へ記録する。未実行を合格に算入しない。
