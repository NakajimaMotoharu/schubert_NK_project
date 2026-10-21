# PG6316 Outbox失敗graph独立二反例仕様

Program=NK-MSG-002/OutboxDispatcher.dispatch・OwnedOutboxDispatcher.run、RD ASY001/MQ006008、UI213241242、SS324/354/SSC322、BUG1572/YKT1328/1323。設計のみPR183/source4f3294898903b6d67a136bfc18569d07f8fcc77b→origin/main01c18b41f9b1c256ca3fb1fedc371914a8901a3b通常squash/fetch確認。三designファイル12insertのみ、未受入code/tool/evidence混入0。artifact登録は100identity上限で一回失敗、再送/既存attachment削除0。

全Production Mainは原4043資格済5eb同byte。追加は既二Testの各一methodだけ、独立期待値/既全Test不変更。正規pin JDK25.0.4/既Maven Spotless、元78391終了0/二Test format、全Main/gates/Current不変更。新38宣言/9suite定義と実scope lint一工具Test0（Production PT0）。

GRAPH322001=graph322001NestedFatalStopsOwnedWorkerBeforeAnotherDispatch。未接続SqlConnectionProviderが固定SQLException.suppressed Error、RTE.cause Error、JMS linked Exception.cause Error、SQL next.cause Error、cause/suppressed循環・重複、JMS linked/SQL next自己循環の六独立graphを投げる。固定LinkageError・synthetic literalだけ、production classifierでexpected生成しない。自己所有worker一回open・同thread一秒内終了・healthy false・wake拒否・固定NK_API_OUTBOX_FATALだけが期待。全資源はfinally join/元stderr復元、実VMや業務processに触れない。Error無しcyclic graphは二回周期に到達/healthy trueを確認し普通retryを維持する。matrixをJUnit件数へ水増し0。

GRAPH322002=graph322002NestedFatalNeverMarksOrdinaryFailureAndNonfatalCycleStillRetries。既専用temporary PostgreSQL18/Flyway fixtureに一行ずつ独立SS wireのdue QWKをenqueueし、claim後の未接続JMS provider取得だけで前記六graphをthrowする。期待=元Error同一性、DB open一回/claimのみ、PENDING/attempt0/last_error_code null/next NOW、lease owner graph/until NOW+10秒、JMS一回。最後のError無しcycleは従来report(1,0,1,0)、open2/ERROR/attempt1/JMS_SEND_FAILURE/next NOW+1秒（jitter0）。期待は独立SQL後条件/固定時刻/markerでありproduction結果から算出しない。fixture前後の削除はこのTest専用DBだけ、原本DB/Backupへ接続しない。

実行予定=clean Test-only commitから `PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg6316_outbox_graph_red.py` 一回、新only `pg6316-outbox-graph-red-v1`。実宣言38/9は期待総数でありPASSではない。元真正結果/失敗/未到達とhash回収までMain/Test/gates固定し、その後だけPGと同oracle greenへ進む。新graph fixtureのnull契約/DB例外/並行worker/再送・全edge分岐を同source品質で確認、未実行/failed/not-runを合格へ加えない。

群1537の.5/2/6は二対象込み、原/v4/正式1964/53/17/190/工数null不変更。QA051final/PTALT対象不明/実VM-current-Root-cohort-intent-permit HOLD/全保全物維持。通常仕様/commit/小受入で停止せず、元red後のPG/PTへ継続する。
