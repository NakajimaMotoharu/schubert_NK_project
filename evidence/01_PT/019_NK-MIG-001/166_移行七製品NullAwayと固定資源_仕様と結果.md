# 移行七製品のNullAwayと静的品質

NK-MIG-001、WBS-F03/2-2-b、SS332/343、451。対象はGames、Column、Constraint、Content、Reference、Finalizer、Asset stagingの製品Main七件。PG42836／42840／42854／42868の通常PT・資源所有・null境界・同一例外の独立期待を参照。GAMES/V004、COLUMN/CONSTRAINT、CONTENT/REF/FINAL/ASSETSTAGEのTest IDは既記録と同じ。

PG42870 (2026-11-23 JST)。Core e8368d22c4、JDK25、Maven 3.9.12 offline。既許可の補助30物理とJSpecify／JSR305を固定した。root POMと同じNullAway 0.14.1／Error Prone 2.50.0でcompile成功、診断0。compile結果の17物理は現JARと全てbyte一致。SpotBugs 4.10.4は同17物理、例外／見付からない型／指摘0。Checkstyle0。PMD生74件は、資源境界のSQL・unchecked・Errorの30箇所を二重分類した60件と、自己抑制の参照同一性14件。対応する行と根拠を記録し、既存の例外・close契約を維持した。

初回はImmutable注釈の既存JSR305補助入力を入れ忘れ、compile終了1。v2の正規補助入力で是正した。独立合成NullableLengthを同構成で拒否することも確認。負例の診断確認は実出力の引用符を含めて照合した。製品JUnitを再実行せず、先行PT・coverageはその元runのまま参照する。実DB、COPY、全製品451と正式受入は未判定。[PG42870 manifest](evidence/PG42870-migration-seven-main-typed-v2/manifest.json)
