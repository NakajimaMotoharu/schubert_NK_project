# 185 NK-OPS-001 Cleanup子原本照合限定実行結果

2026-09-28 JST、PG330/SSC-104、branch `dev-foundation`、source `39033ab2e8577b41906a539d4c65d41db80f1091`。RD OPS-009/BAK-001、UI251、SS341/343。PT-OPS-MRF001～004、既存MaintenanceRunFilesTest 24件。Linux host/JDK25.0.4/Maven3.9.12/JaCoCo0.8.15/SpotBugs4.10.4.0。

| 入力・独立期待値 | 実際・判定 |
|---|---|
| 手書きNKRUN1/NKACT1/NKDONE1原本、同/別run・activation・cutoff、完了済、2回scan間交換、close故障、null | MRF001～004 PASS。選択MaintenanceRunFilesTest 28件（従来24＋新4）とStorage8/Bootstrap8の計44件 F/E/S0、3module SpotBugs0。書込/create/force/publish/unlink/sync 0 |
| 変更した`MaintenanceRunFiles.Session`の4指標 | line429/429・branch162/162・method53/53・class1/1、missed0。新`observeCleanup`該当10行・全分岐missed0、除外0 |
| security共有変更のProduction全体回帰 | 6module clean2,292PT/337suite、F/E/S0、SpotBugs全0、build exit0。内訳 Protocol80/Storage149/Bootstrap175/API742/Web555/Batch591。JaCoCo report exit0 |
| Production全体coverage100% | Protocol/Storage四指標missed0。Bootstrap branch37/line11/method4、API 1/19/3、Web 1/19/3、Batch branch0/line42/method19が未網羅。全module class missed0 |

初回限定試験の試行は`-Dtest`の依存module選択不一致で0件実行として失敗し、次はformat不一致でBatch試験前に停止。いずれも合格算入しない。修正後の選択試験と全回帰のみ上記合格とする。TDD中の重複done分岐は既存`graph`のpending不変条件で到達不能と確定し、SS343とcode commentへ導出を記録して除去した。承認済み仕様不一致の実装済障害ではなく、BUG起票対象なし。

証跡: `evidence/provisional/PG330-six-security/manifest.json` SHA256 `fda9d986a0c3423b9cad0f4355234f1b477d90a24ece49316c72f97e5c01fd58`。日時・command・exit・input/expected/actual・coverage・source/log SHAはmanifest参照。sanitized 337 JUnit XML＋coverage/static各6の349file、source2、Git外原始log2のhash不一致0。JUnit properties/output/failure/skipped除去、保存証跡の秘密pattern scan0。

この限定観測は親連続M/A・子真正Unit/private mount・両backup実現物・DB advisory・DELETE権限の証明ではない。実Cleanup/Artemis・Web/API外部起動/CHR未実施。正式認定source/run `858713c0bf310ae8bf62078b0a1cedbce4e968db`/`PT-WEB-20260925-24`、1964PT/53scope、暫定中心48.3%は据置。
