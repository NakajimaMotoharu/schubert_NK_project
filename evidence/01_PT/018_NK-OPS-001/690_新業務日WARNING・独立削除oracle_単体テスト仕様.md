# 690 新業務日WARNING・独立削除oracle 単体テスト仕様

Program NK-OPS-001/NK-BAT-001/NK-DAT-001。対象MorningProcessMain.runCompleted・親Unit、pg1764～1769。関連OPS009/DAT009/MQ008、UI236/241/251、SS324§12.2/12.4・331/341/343/353、SSC278、BUG1162～1164/YKT930～932。実VMはMain2741/PG1638/BOM195e/boot3d69のまま、設計だけのmain更新を実配備と誤認しない。

| Test ID | fixture/操作 | 独立期待値・算出根拠 |
|---|---|---|
| PT-OPS-WARN1764 | 捕捉済Root13のreadonly PID1/Unit/原本二読 | 正常WARNING原本10とmanager failed10の不整合を保存。元start/endの差1614.187422秒、1800以内。合格へ置換しない |
| PT-OPS-WARN1765 | emitted projectのkey順反転・値/event順/重複key/cursor/型反例、実二読 | object key順だけ同値、全field/event同一、raw両読は別hash保管。wholeAccepted=false |
| PT-OPS-DAY1766/1767 | SS/DDL cutoff selector、null・日時境界、emitted namespace | inclusive session期限/strict Inbox・Outbox期限、未知routeは拒否。UTC依存欠落を旧失敗として残す |
| PT-OPS-UPW1768 | UI236の24byte DATA手組golden、各header/data境界改変、User参照欠落/巻戻し/多重/null | header256+DATA24=280、UserID12/version9/reserved3、独立AESGCM/zlib/AAD、USER参照一致/current version>=保存version。raw/password/key出力0 |
| PT-OPS-DAY1769 | 元24table全row、独立before selector、現在のrepeatable-read/read-only一像 | 許可削除IDの元全rowだけ除去、他原値不変。実結果をexpected生成に使わず、十batch・二progress・新HTTPログ/Outbox一対一/Session構造を照合 |

原before SHAa919274268cfd66a4478f83cfeff52c1bfc3fb12323209133218bdc72d01c23e。独立before候補期待は1768私有oracle SHAa1f2ff92e014509b67dfb727f41fe5165b75d18f271ee90a68b8f7518aefe030。User更新応答の有効1とAUTH_SESSION不在保護4を独立検証してからcurrent SQLを比較する。私有原値はguestroot0600に保持、公開は件数/hashだけ。

実行=PYTHONPATHをtools/quality、tools/quality/vm/050_s1、固定pyflakes3.4.0/runtimeに設定し、python3 -B -m unittest pg1764_warning_terminal_capture_test pg1765_warning_terminal_capture_v2_test pg1766_next_day_independent_candidates_test pg1767_next_day_independent_candidates_v2_test pg1768_next_day_inbox_oracle_test pg1769_next_day_rows_oracle_test。各実guest工具は新slot一回、旧失敗slotへ再発行しない。環境=Ubuntu26.04.1/x86-64/VM PG18.6/JDK25.0.4/Artemis2.56、host Python3.14、branchdev-foundation。対象固定source/command/終了code/hashは691及び公開manifest。

Coverage=Production四100未達、当工具独立試験はProduction coverageや正式PT数へ加算しない。null/未知/重複/並行変化のguardを試験、全並行/故障/native条件は残。Parent WARNINGの正規署名Unit配備・新PID1正常done・owned停止/全資源・nativeは別終了依存、未完。
