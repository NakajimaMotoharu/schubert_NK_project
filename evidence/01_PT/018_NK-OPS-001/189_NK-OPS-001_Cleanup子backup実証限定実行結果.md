# 189 NK-OPS-001 Cleanup子backup実証限定実行結果

2026-09-28 JST、PG332/SSC-104、branch `dev-foundation`、source `92ba3e1cfc54bf9d2de681e6700128b3a27a5d85`。RD OPS-009/BAK-001、UI251、SS341/343。PT-OPS-CBA001～005の10 method。Linux host/JDK25.0.4/Maven3.9.12/Node24.19.0/PostgreSQL18/Flyway/JaCoCo0.8.15/SpotBugs4.10.4.0。

| 入力・独立期待値 | 実際・判定 |
|---|---|
| 188の公開固定4file/MANIFEST golden SHA、手書きSQLの同run両SUCCESS・26/67byte/共通ended。再送 | 同一manifestを返し、borrowed root/Connection開存、autoCommit復元、DB row/実file不変。10 PT methodと依存Storage8/Bootstrap8の選択26件 F/E/S0、3module SpotBugs0 |
| 同size別byte、request digest違い、RUNNING・row count不一致、read-only/transaction/isolation誤り、null | DB前またはDB transaction内で固定非成功、SUCCESS行への補完0・DELETE 0。nullはAPI契約違反としてNPEを正常化しない |
| 4つの割込境界、SQL/rollback/復元/未知例外の複合故障 | 非成功。rollback失敗ではautoCommit復元を試みず、未知primary identityを保全。失敗Connectionは呼出側破棄責務 |
| 変更`CleanupBackupAdmission`の4指標 | line52/52・branch28/28・method7/7・class1/1、missed0、除外0 |
| Production全体security回帰 | 同sourceで6module `clean test spotbugs:check` exit0、2,310PT/338suite F/E/S0、SpotBugs全0。内訳Protocol80/Storage149/Bootstrap175/API742/Web555/Batch609。JaCoCo `report` exit0 |
| Production全体coverage100% | Protocol/Storage四指標missed0。Bootstrap branch37/line11/method4、API 1/19/3、Web 1/19/3、Batch 0/42/19は未網羅。全module class missed0 |

初回限定の依存moduleに対する`-Dtest`指定2回は0件実行で停止し、単独Batch指定は旧install依存でcompile不能、修正後の選択試験ではformatと静的解析の指摘をcodeで解消した。TDD中のrollback回数期待値は手書きoracle再点検で1回へ修正した。これらの失敗試行を合格に算入しない。実装済み承認仕様違反の障害は発見せず、BUG起票対象なし。

最終証跡: `evidence/provisional/PG332-six-security/manifest.json` SHA256 `1c5515bfd30e0fab43e9e9f732eaf8482f8efe0b680e9652e7f750cd0b096154`。日時・command・exit・input/expected/actual・coverage・source2/log2 SHAはmanifest参照。Sanitized JUnit338 XML＋coverage/static各6＝350file、source2、Git外原始log2の計354 hash不一致0。JUnit properties/output/failure/skipped除去、保存証跡の秘密pattern scan0。

本結果は4fileとDB両SUCCESSの限定観測であり、外側`CleanupDatabaseSession`との本番結線、親連続M/A・同原本・全actor終端、真正Cleanup Unit/DELETE/Artemis受入ではない。正式認定source/run `858713c0bf310ae8bf62078b0a1cedbce4e968db`/`PT-WEB-20260925-24`、1964PT/53scope、暫定中心48.3%は据置。
