# Web監査sink故障・独立契約仕様

2026-10-20、Program NK-WEB-001/NK-MSG-002、WBS-F03主担当、群1334開始.25/1/3pp固定。SS312 §11/351 §3.1/352、既REQ014、451、462-PTPRE007。対象`WebRequestLogProducer.local/complete/metadataInvalid`、新`web.logging.WebAuditSinkContractTest`四method。Productionは既実装を点検、現時点修正不要。未特定拒否PTの代替ではなく通常独立PT。

独立PG点検：logger.isLoggable/logのRuntime失敗又はdisabled後、catchの外にあるowner signalを一度呼びfalseでreturnする。completeはfalseならDB/codec/JMS前にreturn。catchを空に見えることだけで成功扱いと断定せず、後続制御とSS351の固定terminal要件をjoinする。callback Runtimeはbounded IllegalStateException/cause無し、logger/owner Errorはunknown fatal identityを保持。null boundaryはconstructor/completeの検査を外に維持しNPE正常化は禁止、provider NPEはterminal signalという非成功へ対応。HTTP responseの変更/実server停止はこの部品の責務ではなく本fixtureでも実行しない。

|TestID|入力/操作|期待値・根拠|
|---|---|---|
|PT-F03-LOG001|disabled、isLoggable Runtime、log Runtime/NPEの四logger状態×HTTP200/400/500/metadataInvalid|各四回owner通知、DB呼出0、sink成功記録0。SS351 local failureはterminalであり投影開始しない|
|PT-F03-LOG002|disabled logger後owner callback NPE/AssertionError|NPEを成功へしない、固定`request audit terminal signal failed`/cause無し/suppressed0/一回通知。Errorは同identity、DB0|
|PT-F03-LOG003|logger query/writeの独立AssertionError|同Error identityを伝播、owner通知0/DB0/記録0。未知fatalを正常化・再試行しない|
|PT-F03-LOG004|正常メモリlogger、固定clock/app/config、metadataInvalid|手書きJSON全値=timestamp2026-10-20T00:00:00.000Z/serviceWEB/pt-1/cfg-1/WARN/SYSTEM/INTEGRITY_FAILED/UNKNOWN/WEB_REQUEST_LOG_METADATA_INVALIDだけ、Level.WARNING/一件、DB0/owner通知0|

fixtureはメモリlogger/計数DataSource spy/固定合成鍵（実encrypt未呼出）/固定時計とUUID。既test helperのsourceはProxyを作るだけ、BeforeAll/DBfixtureは起動しない。try-with-resourcesでcodecをclose。有限16完了呼出等で並行/再送は新しく増やさず、既terminal callbackの単一呼出契約に限定。実DB/HTTP/Artemis/VM/Unit/permission/credential/回収0、通常user自己snapshot/target/Maven/JVMだけなのでPT_DEFAULT。

実行`pg5738_local_audit_selected.py`：新clean source・new-only namespace、前群と同六compile/型null/SpotBugs・各module必要fixtureを使い、Web選択を上記四件へ置換（全12/7）。全XML集合一致/FES-flaky-rerun0/source固定/1664Main・六静的0が必要。既各enum fixtureは今回のreactor必要契約であり元成功へ加算しない。local methodのline/method/branch実counterを別抽出し、全Web/global100とは区別する。

PG5740で元static source849/hash/実class1664が当sourceと同じことを確認して既PMD警告を再束縛し、localのEmptyCatchBlock/broadcatch等の当spanだけ上記設計/通常PTへjoinする。PMD全再実行や警告非表示0、原raw1599を保持。レビューだけで実VM/所有/正常DONE/正式認定を閉じない。旧失敗/UNKNOWNとPTALT001/002保留、次結果でsource/command/exit/XML/coverage/hash・適用性と残存riskを記録する。
