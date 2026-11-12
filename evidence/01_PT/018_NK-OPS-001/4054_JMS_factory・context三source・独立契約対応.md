# P00504 JMS factory/context 三source契約・独立証跡対応

Program NK-MSG-001 / WBS-P005-04。関連RD MQ-001～013/040～045、UI212213231、SS321（origin/mainの版とhashはmanifest）。PG/PT境界を変更しない。

|対象|入力・独立期待値・Test ID|現在の扱い|
|---|---|---|
|ArtemisConnectionFactoryProvider/create/open|SS321のloopback限定port、三window、timeout/reconnect/backoff、作成途中のclose/unknown所有登録。既ArtemisConnectionFactoryProviderTest4の原期待値と全文照合|PG sourceレビュー済。actual TemporaryInfrastructureException/ServiceProcessResources/接続factoryを使う全fixtureのPTはHOLD。断片選択で回避しない|
|JmsMessageFactory/createReply|PT-JMS-ENV001～008。256/280/320 byteの手組wire、response種別・total長・上限1000000、metadata順、null/空/予約/内部event、不正長、六write/header例外を独立assert|既PG23072全8、PG23074独立0を参照。Test/対象/初期化依存全sourceとnormal physicalの同一性を新PG26610で確認。既run原sourceを維持し、新実行・全依存全100へ読み替えない|
|TransactedJmsContextProvider/open|抽象のborrowed transacted context契約。実行codeなし|独立した空テストを作ってcoverageを増やさない|
|共有ReplySender/stage|ReplySenderStageContractTest原4。手組LGNRSP、persistent=2/TTL10000/FQQN/相関、借用contextへcommit/rollback/closeなし、provider例外同一性|PG18612元4成功のTest/対象/初期化依存source、normal physical同一。実broker TTL/ACK/transactionは未試験のまま|

実行は公開source/公開証跡のmetadata照合のみ。新product実行0、新test定義0、旧exec合算0。PG26610真正終了0、初回のpath写像guard終了1はPG26612へ保全しBUG2668/YKT2348を修正前起票。module共通写像の正例2・異prefix/異moduleの負例2、二loop統一で是正。秘密/原本/actual四class I/O/VM/DB/broker操作0。

625行原票の/1=.087/.227/.455ppの期待値対応準備だけ完了。/2=.163/.423/.845ppはfactory runtimeとC04終了依存により未受入、元190項目と451/F02/F03/正式認定を更新しない。価格減額は工数率でも専用実費でもない。

証跡 `evidence/PG26610-jms-factory-context-contract-v1/manifest.json` のpath/hash、全owned source・design版・各旧run/source・公開file検査数を参照。実行commandは `python3 -B evidence/01_PT/018_NK-OPS-001/input/1281_jms_factory_context_contract_audit.py`、branch dev-foundation、source/core Main・日時・verifier hashはmanifest。既成功の再演なし。
