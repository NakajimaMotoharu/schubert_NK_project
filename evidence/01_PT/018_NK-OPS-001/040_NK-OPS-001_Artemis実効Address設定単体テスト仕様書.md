# NK-OPS-001 Artemis実効Address設定 PT仕様

PG237。対象 `ArtemisAddressSettingsReadinessClient.verify` と Ops管理要求。RD MQ-001/002/009/010、UI231/251/253、SS321 §5/10/13・342 §4、QA-041/042、UIC-001/002、SSC-075。`broker.xml`の静的parseだけでなく、稼働Brokerの `getAddressSettingsAsJSON` が返す6業務Addressの実効設定を検証する。Ops Core sessionはcaller所有。管理request/replyの一時資源は2秒でclose/deleteする。credential/生JSONをlog・証跡へ出さない。

| Test ID | 事前条件・入力/操作 | 独立期待値 |
|---|---|---|
| PT-OPS-MQ-010 | SS321 broker.xmlを隔離実Artemisで起動しOps roleのCore sessionで6 Address設定を読む | 6件全てANYCAST業務の固定設定と一致。SS321 §5のbyte/message matrixを独立表として使用し、max memory/page合計がUI231の256MiB/500、1GiB/10000等と一致。借用sessionはcloseしない。一時Addressは残存0 |
| PT-OPS-MQ-011 | 6 Addressの各容量、共通paging/DLQ/Expiry/再配送/auto-create/metricsのうち1値を変異、null/欠落/空/未知Addressを投入 | 誤値・欠落・未知値は全て固定redacted起動失敗。正常な他5件を混ぜても1件の逸脱を通さない。期待はSS321 §5.1～5.4の固定値から個別に作る |
| PT-OPS-MQ-012 | 管理操作の拒否、timeout/null reply、malformed/非JSON、provider例外、close故障、先行割込 | 固定redacted起動失敗、2秒上限・一時reply cleanup。既存PT-OPS-MQ-008/009のACL/timeout/割込を共通request経路で再確認し、借用sessionはcloseしない |

正常・境界・異常・例外・null・role拒否・同一sessionを持つ反復照会を対象とする。実行: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-batch -Dtest=ArtemisAddressSettingsReadinessClientTest,ArtemisManagementReadinessClientTest test`（隔離PG18/Artemis2.56.0、`dev-foundation`）。Coverageは対象全instruction/line/method/class/branch100%、正式全reactor・48以降の全scope/hash、SpotBugs0、負canaryを別記録する。TestでProduction matcherを期待値生成に呼ばない。PG/PT未了・失敗・flaky・skippedは合格に算入しない。Journal復旧/acceptor/全role/Queue閾値/Expiry purge、本番credential・実NK CHRは別gate。結果・日時・commit・BUG/SSC・証跡path/hashは041と `evidence/manifest.json`へ記録する。
