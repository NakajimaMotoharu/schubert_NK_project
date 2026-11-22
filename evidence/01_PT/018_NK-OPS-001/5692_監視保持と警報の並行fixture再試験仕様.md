# 5692 監視保持と警報の並行fixture再試験仕様

BUG-3589／YKT-2824、WBS-F03/2-2-b、RD171・UI252 §5・SS351 §7–8。製品は f8532c27c2666570fe450f285c5a5436aacd8e7e の正規Batch JAR。元の固定入力は1700・1541・PG40986。修正はテスト用の有界workerのchecked例外宣言。JDK25、独立した一時run、固定fixture、JVM内の供給値で確認した。

| Test ID | 操作 | 独立期待 |
|---|---|---|
| RETCONF007 | 64件の交互DEBUG/STANDARD、8workerと有界終了 | DEBUGは15日と5,000,000,000 byte、STANDARDは0/0、元値は不変 |
| PT-OPS-MONMODE-007 | 64件の並行供給、8workerと有界終了 | DEBUGとSTANDARDの属性が混ざらず元観測は不変 |
| PT-OPS-MONPIPE-006 | 同一WEB/TRANSFERに64件、四workerと有界終了 | 1～64を各一度観測し、終了後に一つの警報がcount64 |

PG42586の2件とPG42588の1件が成功。各manifestのbeginでsource、対象型、toolchain、argv、終端とJUnit XML hashを追跡できる。適用SpotBugs 0、意図したnull陰性3を保持。PMD生17は有界ownerの生成・終了とequals(null)陰性。解析対象の型欠落とCheckstyle 0。coverage再計測なし。元の局所coverageは同一製品バイトを照合したPG42582で確認できる。実監視・全451と正式受入は未判定。

- evidence/01_PT/018_NK-OPS-001/evidence/PG42586-f03-retention-mode-fixture-two-retests-v1/manifest.json SHA256 221cb80407bec5a566a4286bf7567de1aca8c8a5bb76e8c50524a1fac58b29fa
- evidence/01_PT/018_NK-OPS-001/evidence/PG42588-f03-policy-engine-fixture-retest-v1/manifest.json SHA256 be59537c36b3cf7d72312ef2cc9a38a847c4e4dd0c4a12af0c7a90c019cd05d7
