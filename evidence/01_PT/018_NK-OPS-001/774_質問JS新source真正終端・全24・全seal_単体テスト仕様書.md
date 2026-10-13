# PG2450/2452/2454/2456 新source全受入

NK-OPS-001／SS331/332/341/343/353/354。新source cdbc/PG2428/BOM6e06の773普通起動は一回済み、再発行禁止。新run06236d14-a6f8-4d05-a6ff-49c713cc2647、cutoff2026-10-13T21:16:10.125382Z、activationc347b14a-2e59-41e6-993c-a07e537cbd00、bootb2d6、Root194154/t2910436、Invocation9024d0364d07478d9237b6941d725208/Job61387/start29104365495us。独立2450 actual0/payloadbd991d0bd5e971d91c585c63c38b36e3e66da272654f1ab34aaa090d456b67d4。

|Test ID|目的・独立期待値|
|---|---|
|PT-OPS-PG2450-001|currentboot・署名current・once-issuedJob/Invocation/startと実RootPID/ticks/argv/uid・active/run/begin同値を二読認証。旧91f/e142を拒否、起動停止0。|
|PT-OPS-PG2452-001|既observerがterminalを捕捉した後、当NKDONE1・元run/cutoff/activation・PID1同Jobdone/同Invocationsuccess/異常無しを独立二読。終了0/10・managerGC・null/不正state/旧run拒否固定vector、30分以内。現在GCのexit観測nullを0へ変えない。|
|PT-OPS-PG2454-001|新普通起動beforeSHA b89bdd48eecd46af684341c5d0c27f639ce1282a9732086419ca2060bdb2c251の全24と当run後rowsをrepeatable-read readonlyで取得。既SS同日oracleでBackup2SUCCESS/既成功cleanupSKIP/保護InboxWARNING/独立HTTP-session-SENT join、全旧row保持、追加と削除候補を独立算出。失敗分岐や予期せぬ値は成功へ追従せず原因分類。|
|PT-OPS-PG2456-001|2452/2454真正証跡→当source署名187/元DB/原本Backup/新正常終端・四ordinary owner/API-Web/socket/broker/Caddy/有限startup/nativeを封緘。旧native16は保全履歴であり新source受入ではない。|

独立fixtureは全実payload/static/entryを検査し、期待値をProduction methodで生成しない。親/API readyやclient0のみで全受入なし。実commandは固定PYTHONPATHで `python3 -B -m unittest pg2450_question_current_live_binding_test pg2456_question_current_acceptance_test`、固定commit/push後2452→2454→2456。既watch32004へ再付着し待ち中の同Root再演/停止/reloadなし。

初期実結果：2448/client71723=actual0/operatorbf394566f、起動は21:16:09Z、親完了ではない。2450 actual0/operatored76af1bd、独立fixture1成功。2452/2454/2456は未実行。実終端・coverageは取得後追記、正式1964/53／leaf0を維持。
