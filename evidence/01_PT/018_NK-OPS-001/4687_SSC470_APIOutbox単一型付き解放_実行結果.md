# 4687 SSC-470 API Outbox借用読取の実行結果

2026-11-18 JST、dev-foundation。候補 a02a3bf2e9a0daf282d47dffd48e42753daf078a、製品Core 5e0b5575cf14416389a30be0175b52f7ec685983。設計はPR437／ed689fd1e6e5eec3fd1509795789dc7e4085e788。JDK25.0.4、Maven3.9.12、JaCoCo0.8.15、JUnit Console1.13.4。指示と手順は4686、5186。終了時刻 2026-11-18T13:20:08.611153+00:00 UTC。

- PG39596元OUTBOXDB001～010とOUTBOXCONN001～008、追加OUTBOXDB011（行・文の二self境界）の全19、初回成功19、失敗0・error0・skip0・未実行0。PG39600標準独立post終了0。Collector、Repository/Snapshotの公開ABI差なし、九物理中一変更、正CRC8、元18期待は字句逆展開で維持。
- PG39606の測定無除外・旧exec合算0。対象3classの生line89/89、method14/14、class3/3、branch30/30、instruction379/379。支援Recorderの生不足は13行の明細、通常全九物理の未到達L6/M3/B9/I28。元PG25450の証拠は発生原因の照合に使用。
- 30件の生PMDを個別照合、適用0、Checkstyle/SpotBugs/NullAway当scope成功。PG39586で元fixture文字列3、PG39602/04で追加証跡工具のsource項目とTest名判定の誤りを保存。是正で同runの既成果を利用し、製品試験の再実行0。
- PG39606 evidence/01_PT/018_NK-OPS-001/evidence/PG39606-p00405-api-outbox-typed-close-independent-v1/manifest.json SHA256 1e3b26551a7f121e31b6afedfe7a562a557e02d6f2fd59dd1ce9bfbb71348424。BUG3292～3294、YKT2597。P004-05実DB/所有、全451、正式受入は継続。

### OUTBOXDB012 全読取後の二解放失敗

現候補 `9ee35bb454768ef48b4a62aca61e3a4c6ad2e1a8`。JDK 25.0.4、JUnit 5.13.4、JaCoCo 0.8.15。初回1/1、失敗／エラー／skip／未実行0。合成2変種で一次と二次各同一、列読取完了、RS→PS各一回と借用Connection非変更を確認。対象Repository無フィルター L38/60 M5/5 C1/1 B14/28 I128/242、Snapshotは未到達。旧試験の再実行0、別runを合算せず、実DBと正式451は保留。 [実行manifest](evidence/PG40954-p00405-outbox-pair-close-v1/manifest.json) SHA-256 `4222ed58b6ae5b785044e593584094a123e32f6be93ebcc10f2b8bbd6c5dde6d`。
