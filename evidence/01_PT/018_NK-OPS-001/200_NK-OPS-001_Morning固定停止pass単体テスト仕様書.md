# 200 NK-OPS-001 Morning固定停止pass・単体テスト仕様書

Program ID NK-OPS-001。対象`MorningStopPass.create/execute`、`MaintenanceUnitStopClient.Attempt`の借用結果、`MaintenanceUnitTermination`/`MorningUnitTerminals`。RD OPS-009、UI251/253、SS341 §4～5/343、SSC-100～102、PG338。親の連続M保持callback内で呼ぶ停止passであり、本class単独はM/A/原本/permitを所有しない。実VMのsystemctl停止は正式8 Unit未配備のため実行しない。

| Test ID | 事前条件・fixture、入力/操作 | 独立期待値 |
|---|---|---|
| PT-OPS-MPASS001 | 手書き固定8順、各client exit0、各whole-Unit終端、最後の全8再観測 | preflight1回→Caddy/Web/API/Cleanup/Inspector/Expiry/Backup/Artemisを1件ずつstop→対応Unit終端→最後に全8fresh、root検査18回。SS341/SSC100～102の順をliteral oracleとする |
| PT-OPS-MPASS002 | 全8 policy preflightが既知IOException | stop0回、終端0回、同例外identity。未配置Unitをfalse成功へ補完しない |
| PT-OPS-MPASS003 | 先頭または末尾clientが終端非0 | 対象Unitの終端を成功算入せず、後続stop/全8成功0。固定非秘密IOException |
| PT-OPS-MPASS004 | client exit0だがWEB whole-Unit未終端 | 次APIへのstop0、全8成功0。client終了codeとUnit/kernel終端を混同しない |
| PT-OPS-MPASS005 | Caddy attemptはUNKNOWN→UNKNOWN→exit0、後続7はexit0 | Caddyの実client終端前にはUnit観測0、reap2回後だけ8終端・全8再観測。固定100ms再試行は検証負荷だけ、成功条件ではない |
| PT-OPS-MPASS006 | 別threadのCaddy attemptを外側からUNKNOWNのまま保持し、後で終端へ遷移 | UNKNOWN中はcallerへ帰還せずM保持scopeを抜けない。解放後だけ全8を完了。期限/割込をUNKNOWN→成功へ変換しない |
| PT-OPS-MPASS007 | 割込flagを持ったreap fixture | await時は一時的に割込を外して実終端を回収し、戻り時にflagを維持。永久UNKNOWNで正常returnしない。実nativeのpreflightは開始前割込を拒否する別契約 |
| PT-OPS-MPASS008 | gate/stop/observer/context null、API actor | nullは契約違反。MORNING以外は停止client開始前に固定拒否。未知Runtime/Errorをcatchして正常化しない |
| PT-OPS-MPASS009 | Caddy attemptはUNKNOWNから非0終端へ遷移 | 実client回収は1回、Unit終端観測・次Unit stop・全8成功はすべて0。UNKNOWNからの非0を0へ丸めない |

ExpectedはProduction passを呼んで生成せず、上表のliteral順/件数・固定例外・thread latchで独立作成する。既存MCLIENT/MTERM/ROOTCTXの試験と合わせて正常・境界・異常・例外・null・並行・再試行を確認する。未解決client `UNKNOWN`の回収ループはM callback内で戻らない契約だが、ProcessBuilder.startがhandleを返す前の不明例外、systemd側hard timeoutと親A/permit/current invalidation、全Unit正式配備・broker clean journalはまだ後続。実親停止成功・R2/R3・coverage100%へ加算しない。実行command/環境/source commit、4coverage、F/E/S/static、BUG/SSC、sanitized evidence/hashは201に記録する。
