# PG564 実Log・HTTP session独立照合仕様

Program NK-OPS-001。Production969d8ded10c0bf5841d9e3a5c531e922caf4a24a/PG548/schema028、PG554通常新run。WBS-N15.04の既群0058内（開始見積0.83/2/4.17週次共有pp固定、別配賦0）。正式1964PT/53scopeは不変更。Java PTではなく実経路の独立後条件工具試験。

関連: RD FUN-008/MON-003/AUT-001、UI226/232/235、SS314§7.2/324§9/351§3/352§11.2、WebRequestLogProducer/WebLogPayloadCodec/SessionPayloadCodec/SessionAttributeCodec、API Log ingest、DB app_logs/web_log_outbox/web_http_sessions。Productionのencode/decodeを期待値生成に使わない。

|Test ID|独立根拠・入力/操作|期待値|
|---|---|---|
|PT-OPS-PG564-001|UI232/235の0始点byte offsetsから手組み2336byte、PythonAESGCM固定鍵/nonce、SS314length-prefixAAD/closedJSON|literal header/data、AAD、Log/Outbox/local/session全値成功|
|002|tag末尾/別鍵/keyversion/別row AAD/短envelope/上限2335|復号拒否、plaintext返却なし|
|003|NULL/未知URI/actor混入/lease保持/ERROR/期限不正/重複行・event/旧Log改変|独立oracle拒否|
|004|匿名JSON null/unknown/dup key/型違い/BOM/末尾別document、metadata bool/null|closed schema拒否、認証/operation tokenを捏造しない|
|005|sealed PG553beforeとPG559v2after、全24現在DB/十Unit二読、PG554Web invocation原始journal、VM専用鍵をメモリだけ読取|114Message ID一意join、全114暗号wire/local/DB投影、SENT・leaseなし・再試行0、匿名session114、nonce/hashed cookie重複0|
|006|既原本/DB/Backup/source/boot/retired runtimeを保持するreadonlycollector|起動/停止/reload/SQLwrite0、raw鍵/cookie/CSRF/token/暗号平文出力0、new-only証跡|

003/004では正常例の各期待値を独立変更して拒否を検証する。実sessionのCSRF値を証跡へ出さず、SS314標準32random byte/64hex・version2・空operationTokens・匿名principal無し、row created<=access/idle8hのみを確認。Cookieとsessionの一対一joinはrawCookieを保有しないため未実施と明記、件数一致をCookie照合へ読み替えない。request final body byteのlocal/wire/DB一致は確認するが、client受信bodyとの独立byte比較はこの保存runでは未採取で、既SS351/SSC173のhost/実HTTP試験と最終品質へ残す。境界/再送/競合の全Production品質を本114正常GETから認定しない。

command:
`python3 -B tools/quality/vm/050_s1/pg564_log_session_oracle_test.py`
`PYTHONPATH=/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B -m pyflakes tools/quality/vm/050_s1/pg564*.py`
`python3 -B tools/quality/vm/050_s1/pg564_capture_log_session.py` （new-only一回、開始前source固定）

環境Ubuntu26.04 guest/JDK25.0.4/PostgreSQL18.6/hostPython3、Pythoncryptography独立AESGCM。鍵はguest root credentialから読取、32byte一時bytearrayをfinally消去。復号JSONはRAMのみ、safe件数/hashだけ永続化。新SAVE `/var/lib/pgpt-s1-preservation/pg564-independent-log-session-v1`、host W/pg564-log-session-capture-v1.{private.log,exit,safe.json}。実行日時/source/exit/hashは次の466結果へ記載。QA051比較範囲保留/CHR-L01正式PASS・IT/ST・coverage100未認定。
