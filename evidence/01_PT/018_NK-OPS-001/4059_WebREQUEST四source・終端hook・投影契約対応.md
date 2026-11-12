# Web REQUEST 4 source・終端hook・投影契約対応

Program NK-MSG-002 / WBS-P006-03。RD MON003/MQ008、UI235242252、SS312§11/12・324§9・351§3.3/3.4、SSC172/336/329331、QA054。origin/main設計版・hash/own4source・Test/sourcehashはPG26662 manifest。

|対象|入力・独立期待値/Test ID|現在の扱い|
|---|---|---|
|HttpRequestLoggingValve/invoke/log|REQ001006/008/014016。実終端のfinalstatus/Coyotecontentbytes/elapsedns、POST/login固定route、lexicalscope finally、metadata欠落/malformed、completiononce、trustなし補完禁止、addressoverride無効|公開全sourceレビュー。whole9 fixtureはWebLogDatabaseFixture/実HTTPとactualWebStartup依存がありHOLD。pure methodだけ選択しない|
|WebRequestTrace/Scope|REQ004006008/QA054。serverrequest/event ID、closedrouteのみ、TopBar安全actor投影、first businesscorrelation、menu候補、oncecompletion、threadowner/nestedstrictorder/restore、100独立request|元PG25918全10/PG25920独立0。全32sourceとtarget5physicalが現在と同一、元source/runとaggregate L130/M36/C5/B42全miss0（自然zeroBranch sourceを含む原方針）を保持。新currentrun実行・全Web受入へ転用しない|
|WebRequestLogProducer/complete/completeOne/local/project|REQ005007009014/QA054。local安全JSON先行、同eventで2336byte WLGEVT01暗号化technicalINSERT、verified literalIP・registeredroute・safeactor、N9/N12上下限・clipping、unknownmethodOTHER、投影FAILED/metadataUNKNOWN/localfailure ownerterminal。MENU_VIEWEDは認証済正常menuGETだけREQUESTと別event/同HTTP request。LOG_SEARCHEDはAPI初回transactionのみ|全sourceとSS独立条件を対応。whole9の実DB・actualWebStartup依存HOLD。PG sourceレビューをJSON/wire/DB実PT成功にしない|
|WebLogOutboxRepository/enqueue/claim/mark/read|requiredSQLNULL22004、technical schema暗号のみ、UKfirst、callerTX、due/expired10s SKIPLOCKED1..100/sort、markowner/status/attempt/lease、1/5/30/60/300s jitter±10%・attempt100飽和|whole4実DBfixtureはHOLD、SQL/後条件期待を明記し未実行をPASSにしない|

QA050の15分は未確認session失効要求の継続retryでありWebLogではない。BUG2671/YKT2351の旧説明・元event/manifestをPG26664へ保持、PG26666でQA原文とSS3248.3/9の異なる対象を独立照合。閲覧spec4058とfuturetoolだけ訂正、Main/試験/原価格変更0、設計正本の変更不要。

PG26662 command `python3 -B evidence/01_PT/018_NK-OPS-001/input/1302_web_request_public_contract_audit.py` は公開source/metadata照合だけで真正終了0。新product実行/定義/oldexec合算0、actual四class binary/DB/server/VM/鍵操作0。日時/branch/core source/元source/run/hashと未確認範囲はmanifest。原625 /1 .087/.227/.455ppの期待値対応準備のみ完了、/2・DB/actualWebStartup/終了依存/全451・元190未受入。正式1964PT/53scope/工数nullを維持し、REQUEST単独でWebready/CHR/nativeを閉じない。
