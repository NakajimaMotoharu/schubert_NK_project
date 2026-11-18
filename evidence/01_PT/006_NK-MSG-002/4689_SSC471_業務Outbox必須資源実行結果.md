# 4689 SSC-471 業務Outboxの必須JDBC資源実行結果

2026-11-18 JST、dev-foundation、製品Core 15ee95822be0f4387e1e127cf43d43a08945c3c6、固定試験candidate 583dad40fbfe1e7a29c445351da0a3d9c66346d3。設計PR438／907de7ce26b0cc2bfc1a7530fc75f8ae845e9161。JDK25.0.4、Maven3.9.12、JaCoCo0.8.15、JUnit Console1.13.4。終了日時 2026-11-18T13:50:48.039805+00:00 UTC。指示と独立期待は4688と元007、手順5193～5195。

- PG39653の元JDBC001～009・追加010～012全12初回成功、失敗・error・skip・未実行0。PG39654の独立標準post終了0。PG39656で現JDBC経路一型の生line178/178、method13/13、class1/1、branch40/40、instruction699/699。十物理・正CRC8、支援生不足40明細、除外・旧exec合算0。旧全9の検証は原PG21014/28・PG39634を参照。
- 四文・二行欠落時の22004、借用Connectionの不変、取得release1、元一次と行＋文の抑制、JDK自己例外とcause、元16独立workerの有限終了を確認。固定SQL/UTC/リース/再送・元9期待の字句逆一致、公開ABI同一。
- PG39640/43のSpotBugs所有指摘各3を保持、最終PG39648は0。生PMD27個別適用0、未分類0、NullAway/Checkstyle/format合格。初期specとpackage所有のメタデータを訂正した。製品の実行は固定candidateに一度。
- evidence/01_PT/018_NK-OPS-001/evidence/PG39656-p00405-business-outbox-resource-independent-v1/manifest.json SHA256 284573282c4f427c0a0c16072b3019af4485d264b952667ab44d470fd8d82aee。BUG3296～3298、YKT2597／2387。実DB/JMS・dispatcher／正式P004-05・P006-02・全451は継続。
