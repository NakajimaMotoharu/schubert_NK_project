# 4691 SSC-472 WebLog Outbox必須JDBC資源の実行結果

2026-11-18 JST、dev-foundation、製品Core 0e93b5a35d126bdf2500d0820082d7c2e4ff5db7、固定試験 5da568241452ea1625407fa7b350477d61a43a3d。設計PR439／5aafdc4bff5e8a4c15db9a8000ddf3f1fd17f774。JDK25.0.4、Maven3.9.12、JaCoCo0.8.15、JUnit Console1.13.4。終了日時 2026-11-18T14:07:22.750839+00:00 UTC。手順5200/5201/5202、独立期待046と4690。

- PG39680全23（元1～20＋追加21～23）初回成功23、失敗・error・skip・未実行0。PG39684独立標準post終了0。同execのPG39690無filter対象一型はline144/144、method12/12、class1/1、branch39/39、instruction560/560。物理5・正CRC4。支援生不足32明細。除外・旧exec合算0。
- 四文一行欠落の既固定22004、未取得closeなし、行→文一回、自己抑制時のcauseと文失敗抑制、元二worker有限終了、同source公開ABI。元SQL/UTC/lease/再送を逆展開で確認。QA050のLogout再試行には影響しない。
- 当適用静的0。生PMD21件を個別対応、SpotBugs0、NullAway/Checkstyle/format成功。Webの既provided SpotBugs annotations 4.10.4から公開jsr305を受けるためproduction POM差0。
- evidence/01_PT/018_NK-OPS-001/evidence/PG39690-p00405-weblog-outbox-resource-independent-v1/manifest.json SHA256 01a97e515b066ddae4d91f21f12f4f9347b750b7b0f0415a99c7c5b0548ec2ed。BUG3300/3301、YKT2597/2387。実DB/JMS・dispatcher、P006-03全、全451は継続。
