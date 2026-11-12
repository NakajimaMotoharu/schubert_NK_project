# Outbox 12 source・SQL/再送/DLQ 独立期待値対応

Program NK-MSG-002 / WBS-P006-02、RD ASY001/MQ006008、UI213241242、SS324§8/SS332§7、SSC155/320322330。正本origin/main版/hash・12source hash・入力Test/oracle/未確認はPG26656 manifest。

|対象|具体入力と独立期待値・Test ID|状態|
|---|---|---|
|Destination/Entry/Request/DlqMetadata/Report/Integrity/SendException/RetrySchedule 原8|OutboxModel4/Dlq2/Report3/Policy4。N12/attempt0..100、clonedbody、DLQ original!=dispatch/QWK001/320、ASCII128/deliverypositive/year1..9999/micros、counter長整数加算、address2限定。retry1/5/30/60/300s±10%は明示18期待値表とfraction/null/範囲外|全source/oracle全文照合。元13試験・8physical全codeのPG9754/9756→23738を同byte範囲で保持。現Test2は旧実行時からsource差あり、現wholeTest実行や新実測へ読み替えない|
|JdbcOutboxRepository/RequiredColumn|PT-IDEM009011/JdbcOutboxPort9。enqueue callerTXとNULL id deny、due/expired10s leaseのSKIPLOCKED/order1..100、owner/id/status/attempt付きmark、100cap/固定redactederror、SQL bind順・件数・戻値・resource後条件|公開sourceとSQL独立後条件レビュー。PG21014原9/21028独立は原sourceの限定証跡として保持、実DB/現owner全体受入は未確認|
|JmsSender/Dispatcher/OwnedDispatcher|PT-IDEM010011/GRAPH322/QST-OUTBOX001004。wire/fullpayload identity先行、persistent/FQQN/TTL0、dispatch duplicateID/originalDLQmetadata、JMSownedcommit/rollback/close、短DBclaim-send-mark、fatalgraphと有限duplicate探索、fixedstderr、workerstart/wake/正常ownedjoin|直接actual Temporary class又は実DB/brokerのwholefixtureはHOLD。元Owned7のtargetだけの限定証跡を保持し現依存全体・nativeへ転用しない。通常sourceレビューはPT PASSにしない|

A4-03原18はOutboxObservationRepository10/OutboxMetricCollector8という監視契約。本項目の業務Outboxの13・JDBC9へ合算せず、費用も再計上しない。QA050の15分周期は未確認session失効要求の継続再試行（初期5秒/30秒/5分の後）であり、API/WebログOutboxのSS324§8.3/9 application5分capと別契約。BUG2671/YKT2351訂正: 旧誤記・元event/manifestはPG26664へ保持し、PG26666の正本QA/SS独立照合へ対応する。

PG26656は公開source/公開manifest/XMLと既normal physical hash metadataだけの照合、真正終了0、新product実行0/新定義0/oldexec合算0、actual四class binary/DB/broker/VM/鍵I/O0。原625 /1=.087/.227/.455ppの期待値対応準備のみ完了。/2=.163/.423/.845pp、P00401/P00503依存・actual sender/dispatcher/DB/broker/全451・元190は未受入。工数率null/正式1964PT53scopeを維持。specとmanifestのTestID/path/hashにより対応する。

command `python3 -B evidence/01_PT/018_NK-OPS-001/input/1298_outbox_twelve_public_contract_audit.py`、branch dev-foundation、Main629、source/OS証跡・元run/日時・verifierhashは各manifest。確認目的の元成功試験再演なし。
