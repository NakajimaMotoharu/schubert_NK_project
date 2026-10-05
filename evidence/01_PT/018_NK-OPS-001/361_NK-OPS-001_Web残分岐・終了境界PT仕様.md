# Web残分岐・終了境界PT仕様（PG473）

NK-WEB-002/NK-OPS-001、RD SYS002004/AUT002004/MON003、UI212222226252253、SS313314321342343352/451、PG-D378。PG472/c8の同host+8native（NoMatch0）からWeb残5branch/19line/2methodを抽出。未実装新helperのTDD初回失敗は障害へ算入しないが、既実装の仕様違反は修正前915/916へ登録する。

|Test ID|class/method|独立期待値・観点|
|---|---|---|
|PT-OPS-WEB-REM001|WebRuntimeHealth.ready|null managementはfalse/provider0、同capture objectのfalse/trueを一回だけ評価、provider例外は同一identityで伝播。管理readyの上書きや新取得0。|
|PT-OPS-WEB-REM002|WebRuntimeFailureSignal|独立AtomicBoolean false→Runnable/Consumer callback true、繰返し/並行でもtrue、Throwable値は保持/ログ0、closeや新権限0、constructor invariant。|
|PT-OPS-WEB-REM003|WebNativeRuntime.requireMappings/start|手書きUIルート全32の完全一致のみ正常、missing/extra/wrong regex拒否・固定IOException。初回DB fixture拒否後に二度目startは固定IOException/再借用0、borrowed key未close/partial brokerだけ所有close、null契約。|
|PT-OPS-WEB-REM004|WebRuntimeExecution.execute|独立順序start→await→stop→close。start/await IO・runtime/fatal各identity、Lifecycleは固定IOException、finally stop/close一回。close IO/runtime/fatalは固定診断→実UNKNOWN保持、後段/外scope close0。偽retainer戻りを正常扱いしない。|
|PT-OPS-WEB-REM005|WebTerminalCapture/Owner|capture前open/verify/停止通知、capture後verify/完了通知/close/終了callbackの順序。各境界IO/runtime/fatalとcloseのsuppressed identity、callback未実行、open失敗close0、null契約。同native default factoryは固定WEB/ORDINARY/元INV/実FixedStopHold・pinned checkpointを維持、外部override追加0。|
|PT-OPS-WEB-REM006|WebProcessMain.run/main|argv70/IO0、独立invalid config70/callback0、read IOException50/callback0、startup IO50/その他例外原identity。native/非native終了の固定診断、captureの前後所有verify、scope close正常後だけ終了callback。host fake boundaryを実native受入へ算入0。|

Test fixtureはsynthetic credentials・独立literal順序/例外/HTTP route、provider/clock/例外値をproduction methodでexpectedへ変換しない。scope不可視の成功は推定しない。新package-local seamはtestabilityのみでproduction defaultとscope順序不変、public factory/env/credential/実Root authority override無し。既Root原本/Backup/native/privateを保持。

実command・日時・source/commit・XML/FES/coverage/static/hashは結果文書/manifestへ保存。選択成功を全体へ加算せず、変更群固定後451 fresh全6→同source必要native。line/method/class/branch100に届かなければ未達を記録、除外/意味の無いassertion/Current baseline変更は禁止。正式run24/1964PT53scope/48.3%は実証まで据置。
