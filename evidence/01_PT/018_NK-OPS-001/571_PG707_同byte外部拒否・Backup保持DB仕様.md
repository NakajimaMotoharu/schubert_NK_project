# PG707 同byte外部拒否とBackup保持DB

NK-OPS-001/NK-ADM-001/NK-BAT-001、RD OPS009/DAT009、UI251、SS343/341/354、451、WBS-P018-08.02/P017-01.02。本群は同一owner接続経路のtest-only補完、Production9bd・VM PG682不変更。二leaf現行残予算各.67/1.67/3.67pp（群1.34/3.34/7.34）固定、native操作N15や全回帰K01二重費0。

PT-ADM-BOOT707001：実別JVMのBootstrapAdminMain公開入口。空環境・argv空/overrideの独立入力、期待exit70/stdout空/stderr固定`Initial ADMIN bootstrap finished\n`、credential/所有/SQL前に拒否。既JaCoCo agentだけ継承、環境空・特権/固定nativeprofileなし・15s実deadline/失敗時ownedchild停止。OS admissionの正常実証拠とは別、Reflection/private呼出/人工正常claimsなし。

MDB707001：新isolated PostgreSQL fixture/既DDL、固有run707…/固定cutoff2026-12-01T15Z。正規public Session begin→FAILEDペアterminal→manifest型のretention claims、期待false（FAILED2、1行欠落、両方欠落）、早すぎる時刻IOException、null時刻拒否。fixture adminによる列原値/件数/statusの独立SQL後条件で各期待値を検査。VM/current DBへ書込0、fixtureのdeleteのみ。所有callback後close・db fixture停止は既ライフサイクル。正常成功は既bresume001、各手fixture値はProductionでexpected生成0。

command：`python3 -B tools/quality/vm/050_s1/pg707_selected.py`、JDK25.0.4/Maven3.9.12/offlineM2/spotless/Spotbugs4.10.4/JaCoCo.8.15/PG18.6。着手前・終了後全6mainclass byteをPG680と照合、新onlyW/pg707-owner-negatives-v1、旧exec・三reports・静的report保全、新selected API2suite/batch1suite/FES0/XML・実exit・hashを独立collectorで判定する。試験仕様/残counter/actualcommitは実後記、現在未実行。全回帰と工程正式は別・既成功流用0・skipped/not-run加点0。
