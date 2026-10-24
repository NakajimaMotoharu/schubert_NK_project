# 1727 Metric全26所在・Web pool残経路 限定照合

group1953/PG8114 fresh receipt・開始0.25/0.6/1.5pp上限10、source731d84d79fb44857dab999ef380f49d3d86ac375（Git HEADbc2588f66のsrcとの差0）。PG8116原manifest `e25ea0fbc94c5ba1b322d4d9b8bde9ad0ac3d7fa8a0bedfad83eec7704faa2ed` は終了0、普通PT0/target初期化0/実VM-DB-network0。origin/mainのSS351§6と全68 monitoring Main JavaのGit/hashを照合。全26名に28個の具体的source binding（API/Web両outboxの重複2を含む）を記録し、1720のliteral regexだけで未解決だった13名を「未実装」と断定しない。

| catalog群 | source所在 | 留保 |
|---|---|---|
| HTTP2 | Web HttpMetricRecorderのtyped HttpMetricContract参照、OverflowSafe registry | 当90の単体品質。実HTTP/asOf/owner/exporter受入ではない |
| MQ8＋redelivery/Inbox/mismatch | API各Recorder/圧力install helper | 同Layout/Destinationの供給観測、実JMS/ACK/再送への権限なし |
| outbox2 | API Rows/AgeとWeb固定store Recorder/Repository/Collector | 実接続・source/owner/tx/時刻・schedulerはHOLD |
| async/DB pool/query duration | API各Recorder/Collector/typed getters | API pool facadeのserviceはAPI固定、Web受入へ転用不可 |
| transfer2/Integrity/batch2/restart | Batch Transfer/IntegrityFailure/Batch/ProcessRestart Recorderとtyped catalog | 実walk/Morning/backup/restart等の権限なし |
| media2 | Web Streams/Bytes Recorder/Collector | 実stream/Range/owner/lifetimeへの結線は未受入 |

上表は索引で、名称26個・type/label allowlist・全具体的path/hash/fragmentは原manifestのcatalog各行に一意対応する。名前/型定義やsourceの存在だけを製造/PT/実公開完了にしない。Simple SDKの有限vector成功は、Prometheus/exporterの実registry互換性や収集結果の証明ではない。実backend/admission/generation/asOf/lifetime/scheduler/retention/Root/owner等の終了依存は全26で未受入のまま。

## 次の許可済み一経路

`WebJdbcPool.open`既sourceは独立technical-schema Hikari pool max2/min1・management登録falseを固定する（SS311/342、UI212/226）。当Web monitoring全12Mainに`nk_db_pool_connections`/DbPoolMetric facadeがなく、全Production Mainの当literal/type参照もAPI三部品とBatch catalogだけ。既API DbPoolMetricRecorderはservice APIを固定し、SS311のWeb→API業務artifact禁止とも整合してWebから流用しない。これを全host/実runtimeに監視がないという断定へ拡大しない。

Web fixed-service WEBの4state(active/idle/pending/max) gauge・借用HikariPoolMXBean/HikariConfigMXBeanの4getter観測・owner-local完全publicationを一群で実装する。新WebDbPoolMetricRecorder/Observation/Collectorと対応各8PTを予定。Web→API依存/実DataSource作成/open/getConnection/JMX lookup/control/credential取得を行わず、既正常Web依存にあるHikari7.1.0のinterface-only proxyをfixtureにする。MAX2の設定/admissionは既WebJdbcPoolの責務で、監視は取得したactual正値を表し勝手に2へclampしない。独立gettersの瞬間差からactive+idle<=maxを推測しない。負/maximum0はunknown、null境界は例外、取得故障はunknown後に元Throwable、STANDARDはgetter未呼出、private owner lock/並行/部分factory/borrowed ownerを普通PTで検証する。

本照合で設計変更/新業務仕様の推測はしない。実Web poolへのgenuine source/role/owner/asOf/lifetime・scheduler/exporter起動はHOLD維持、F03 Root11・拒否未特定操作の代替実行なし。新工程は別fresh receipt/固定見積と1728仕様で着手し、24新IDと必要既90を同sourceで再資格する。正式1964/53・原190新受入0/工数null/QA051final/PTALT0/原-v4-v5/既usage cursor/旧last27区間null/90再基底化0を不変更、限定監査/commit/PMO返信待ちで停止しない。
