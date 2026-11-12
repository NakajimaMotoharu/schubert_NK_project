# Login 10 source・閾値lock・独立期待値対応

Program NK-AUT-001 / WBS-P007-01、RD AUT001/FUN001009/MQ021/MON004/DAT009、UI225226234252、SS312§4・314§4/5/12・324§5/331332、SSC009/013014・QA055。正本origin/main版/hashとown10全hashはPG26698 manifest。

|対象|具体入力/独立期待値/Test ID|現在の扱い|
|---|---|---|
|AuthenticationService/LockedLoginAttempt/LoginAccount/Reason|PT-AUT004。匿名InboxNEWだけ照合、prelockedはhashなし/延長なし、ACTIVEかつmatchだけ成功、disabled/不存在もdummy同factor・共通失敗形。CallerTX中のcounter/session/audit、全終了でchar配列消去、固定infra。numericIPのみ/表示名と比較key分離|元Authmemory16 target1は現source/physical同一で原run限定参照、wholedep資格へ拡張しない。全実DB8はHOLD|
|LoginAttemptState/Kind/Repository|PT-AUT003/D01D05。User5/IP10、15分窓はstrict超過だけreset、窓端一致は加算、lock終端一致は照合可（その失敗で再lock可）。ceilRetry0..900、lock中counter/期限不変。User→IP lock順/UPsert、SQLNULL/enum/role/status/affected1/rollbackcaller|元window9 target2は正規normal CRC・source SHA一致を保持、現State5の新runとしない。全Repo6実DBHOLD。SQL±1µsの現実行は未確認|
|PasswordPolicy/Hasher|PT-AUT001002、4063仕様/4065結果。Login1..256byteとcreation12..128codepoint/256byteを分離、NFC/username比較/control・surrogate拒否、caller消去。pbkdf2-v1/salt16/310000/SHA256/256bit/96hex固定、unknown世代deny|現PG26710原6全成功→PG26712独立0。Main/Test変更0、原群内通常PT、追加予算0。既surrogate guardを理由なく改変しない|
|LoginAuditWriter|PT-AUT004。同成功/失敗TX SECURITY action・result/reason/retry、NFC安全displayusername・numericIP・message/correlation、insert1、password/context等除外、独立commit/closeなし|公開source/SQL期待を対応、元AuditPort/Memory scopeだけ保持しDB/全owner受入へしない|

旧window9のsource/byte identityは原source2SHA/normal CRCで確認し、原run/旧counterを保存する。原9/16と現6のcoverage・件数を合算して全owner合格にしない。PG26698 command `python3 -B evidence/01_PT/018_NK-OPS-001/input/1316_login_ten_contract_audit.py` はsource/metadata照合、PG26714は原window2source SHA追加確認だけ。actual DB/login/session/鍵/credential/VM/Root/held四class I/O0。

原625 /1 .087/.227/.455ppの期待値対応準備だけ完了。/2 .163/.423/.845pp、依存P00401/P00601、実DB・session・criticalaudit・全451/元190は未受入。正式1964PT/53scopeと工数null維持。QA055の固定lock文とHTTP Retry-Afterは別画面gateであり、ここからCHR/HTTP完了を宣言しない。PBKDF2 p95と通常業務混在はLinux IT/STへ引継ぎ、単体case時間を性能合格へしない。
