# NK-OPS-001 親単調30分budget実行結果（PG366・暫定）

- 対象source: `29ef46656`、branch `dev-foundation`、2026-09-29 JST、Linux x86_64/JDK 25.0.4/Maven 3.9.12/SpotBugs 4.10.4.0/JaCoCo 0.8.15。
- 対象: [244仕様](244_NK-OPS-001_親単調30分budget単体テスト仕様書.md)の`PT-OPS-MBUDGET001..002`、`PT-OPS-BUCYCLE006`および既存`BUCYCLE001..005`。固定長30分=1,800,000,000,000nsはSS341から独立literalとして試験に与えた。実Unit、親実起動、実時計30分待機の受入ではない。
- 限定実行: 上記2 suite/8 PT、failure/error/skipped 0。`MorningParentBudget` classのJaCoCo missed I/B/L/M/C=`0/0/0/0/0`（covered `44/4/10/4/1`）。
- 全6回帰trigger: 親resource/security所有と期限切れ保持の変更。固定sourceで`./mvnw -o -q -Dmaven.repo.local=<固定m2> -Dnk.pt.repository=<本tree> -pl src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-api,src/schubert-nk-web,src/schubert-nk-batch clean test spotbugs:check jacoco:report`、終了0。363 suite/2,480 PT、failure/error/skipped 0、6 module SpotBugs 0。
- 全体JaCoCo missed I/B/L/M/C: ProtocolとStorage各`0/0/0/0/0`、Bootstrap`60/37/11/4/0`、API`95/3/32/4/0`、Web`80/1/25/4/0`、Batch`1403/29/306/120/15`。全4指標100%は未達であり、正式53 scope・実NK CHR受入へ加算しない。
- `MorningBackupUnitCycle` outer class missed=`132/8/30/8/0`。caller所有budgetは候補cycleへ注入したが、外部`MorningProcessMain`からは未結線。実30分hard-timeout、start後不確実時の実M/Aとmarker/Unit隔離、真正archive/Cleanup/permitは未実測。BUG322/SSC107/YKT254を完了扱いしない。
- Raw JUnit XML/JaCoCo XMLはGit格納外。path順のXML hash、対象source/test/spec hashと実測値は同階層`evidence/provisional/PG366-parent-budget/manifest.json`。credential/session/token/秘密keyなし。
