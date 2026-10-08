# PG583 新HTTP Log・匿名session独立仕様結果

## 実結果追記（2026-10-08 17:54JST）

operator 7808610b02b2342ace37e468fc1693be0b3180f7/actual0、Log117→2336byte暗号wire117→SENT117→DB/local117全照合、/login116と/css/**1が独立literal群一致、匿名session116閉鎖暗号/CSRF/8h検証。旧三表全行保持/全24と十Unit二読不変、duplicate nonce/message/session0・keys/plaintext export0・start/stop/SQL変異0。payloadSHA 6333dd1cd706e147021cf64e44ad94d4c9abaea795beca6231e47cf3a328f6e0、requestJournalSHA 7a22c99d6fdde22b57d96a3287c1a8308746ae1e5131ad6d33777dba752f254c、hostsafeSHA15e894f0a4d90926861a7b8601fb38e33d055ad8b7688edfbec4b10b56272fd3。実期間未測定/時刻は結果記録時刻、下記未実施は事前履歴。旧PG564歴史結果は不変更・YKT636新collector九metadata実正常確認済み。QA051最終比較/全formal/global100とは別、該当後条件のみ成功。

Program NK-OPS-001/pg583_log_oracle.verify/pg583_capture_log.main、RD FUN008/MON003/AUT001/UI232235/SS314324351352354、Test PT-OPS-PG583-001～004。Production969/PG548/PG573当run/PG579after。001=Web当INVのREQUEST local117・DB app_logs117・web_log_outbox117の一意message/correlation/request join、期待GET/login200=116、GET/css/**200=1、旧全三表行不変。002=PythonAESGCM独立AAD/NKENC1/2336byte・UIliteraloffset/padding/closedJSON/投影detailsとlocalDB全欄・SENT/再送0/lease-null/nonce重複0。003=新匿名session116・独立AAD/閉鎖format2/CSRF64hex/operation空/8h、旧115未再削除。004=全24/十Unit二読不変・keys memory-onlyゼロ化/サービス操作0。

独立literal6fixture（新2/既4）/未知route/count/status/null/暗号tag/旧session変異・固定payload置換数/embeddedcompile/Pyflakes成功。旧PG564 login default仕様維持、CSS独立許可literalだけ追加、Production期待値生成0。command python3 -B tools/quality/vm/050_s1/pg583_capture_log.py、Ubuntu26.04/cryptography/PythonAESGCM/PG18.6、実source/exit/時刻/hashは実後追記。hostnew-onlypg583-* / guestpg583-independent-log-session-v1、rawkey/plaintext/ID/tokenGit保存0。未実施合格加算0/正式更新0/QA051保留。既PG573群1.03/2.5/5.67ppの後条件内、新枠二重計上0。
