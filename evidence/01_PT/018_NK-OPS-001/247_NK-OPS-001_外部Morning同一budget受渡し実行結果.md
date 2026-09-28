# NK-OPS-001 外部Morning同一budget受渡し結果（PG368・暫定）

- 対象source `51dcc4501`/`dev-foundation`、2026-09-29 JST、Linux x86_64/JDK25.0.4/Maven3.9.12/SpotBugs4.10.4.0/JaCoCo0.8.15。仕様[246](246_NK-OPS-001_外部Morning同一budget受渡し単体テスト仕様書.md)。
- MMAIN001～007/MBUDGET001～002/BUCYCLE001～006の選択3suite/15PT、failure/error/skipped0、SpotBugs0。Mainが引数0のとき単調budgetをAdmissionへ渡し、未組立ならexit30を維持することを確認。実時計30分、実root/Unit、親全処理・hard-timeoutの受入ではない。
- 横断security/resource triggerのProduction6固定source clean test/SpotBugs/JaCoCoはexit0、365suite/2,487PT F/E/S0、SpotBugs各0。Coverage missed I/B/L/M/C: Protocol/Storage各`0/0/0/0/0`、Bootstrap`60/37/11/4/0`、API`95/3/32/4/0`、Web`80/1/25/4/0`、Batch`1406/29/310/120/15`。`MorningProcessMain` outer=`14/0/6/3/0`（実root lambda/launcher未到達）、`MorningParentBudget`=`0/0/0/0/0`。全指標100%、正式53scope/実NK CHRは未達で、正式認定に加算しない。
- 同じbudgetを真正Backup cycle・Cleanup等へ渡す親全体は未組立。BUG322/SSC107/YKT254の実systemd hard-timeout後のUnit/marker/current/M/A保全を完了扱いしない。
- Raw JUnit/JaCoCo XMLはGit格納外、path順hashと対象source/test/spec hashは同階層`evidence/provisional/PG368-morning-entry-budget/manifest.json`に保存。秘密実体/原本/credentialなし。
