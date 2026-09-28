# 198 NK-OPS-001 Morning全Unit終端・単体テスト仕様書

Program ID NK-OPS-001。対象`MorningUnitTerminals.requireQuiescent`、`MaintenanceUnitTermination.create`。RD OPS-009、UI251/253、SS341 §5/343、SSC-100、PG337。親M/A保持中に固定8 Unitのfresh whole-Unit/kernel終端を確認する読取だけであり、実停止・Artemis clean journal・permitではない。

| Test ID | fixture・入力/操作 | 独立期待値 |
|---|---|---|
| PT-OPS-MTERMS001 | 固定8 enumを観測portへ順次入力、全true | Caddy→Web→API→Cleanup→Inspector→Expiry→Backup→Artemis各1回。SS341/SSC100の列挙順を手書きliteralにし、Production iterationからexpectedを作らない |
| PT-OPS-MTERMS002 | 先頭Caddy falseと最終Artemis false | 先頭は1件で停止、末尾は8件後に固定IOException。どちらもsuccess不可。未知Unit/activeをinactiveへ補完しない |
| PT-OPS-MTERMS003 | `StopGateException`、固定IOException、未知Runtimeを個別注入 | 既知stop異常はcause/suppressedなし固定IOExceptionへredact。IOExceptionと未知Runtimeは同identityで失敗、正常扱いしない |
| PT-OPS-MTERMS004 | 観測port/context null、API actor fixture | nullは境界違反。API actorはnative管理照会前に拒否し、Morning root以外は8対象の権限を得ない |
| PT-OPS-MTERMS005 | 事前割込、1件目割込、最終件割込 | 観測0/1/8件の後に非成功。割込flagを維持し、最終件直後の競合もsuccessにしない |

各観測は既存`MaintenanceUnitTermination`のloaded/12field/固定cgroup/全nested processと前後identity検査に依存し、同classのMTERM PTを回帰する。並行start禁止は親M/A・正式Unit配備・起動許可の後続条件であり、この読取だけで保証しない。再送・再観測ではcacheを使わず毎回8件を新規照会。null/NPEをcatchして正常化せず、JaCoCo除外なし。実行日時・command・環境・source commit、F/E/S/static、4coverage、関連BUG/SSC、sanitized evidence/hashは199へ記録する。
