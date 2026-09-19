# NK-BAT-001 全IO位置試験の独立並列実行仕様

PG-D-185、既存PT-BAT-110/MaintenanceRunRetirementTest.everyIoFailurePreservesState、015/SS343§6.16。Production/RD/UI/SSの仕様・期待値を変更しない試験実行方法の改善。未実装。正式20-03のsource凍結解除後に着手する。

直近全reactorは約16分、そのうち同classは約425秒。26operation・全6,768位置の逐次fault注入を固定4workerへ分配する。件数削減、mock DBへの置換、試験skip、coverage除外は行わない。各workerに独立PostgreSQL18 clusterと専用Connectionを与え、同一advisory keyの競合やConnection共有を避ける。既存main clusterを1worker、追加3clusterを逐次起動し、終了時に全追加clusterを停止する。各fixture/FFM/native FDはworker内で生成・解放し、threadを跨いで所有を渡さない。

正常実行の独立IO_INVENTORY、53root×4絶対path segment等の015の根拠は不変。TreeMapのoperation＋1起点occurrenceを独立列挙し、全6,768キーの一意集合を作る。round-robinで4分割し各位置の固定UNAVAILABLE/原因なし/suppressed0、注入実到達、FD/channel/listingゼロを従来通りassertする。全future正常終了後に実行済集合の完全一致と重複0を照合する。異常future/timeout/割込はtest失敗、握り潰し・合格算入は禁止。workerが失敗してもexecutor終端と全Connection/clusterのcloseを行う。

実fixtureの絶対path深度は従来通り`/tmp/<junit>/<retire>/var`の4segmentで固定。workerごとの中間directoryを追加しない。通常のJUnit test数・Production各coverage分母・独立trace oracleを維持する。追加3clusterのdisk/memory/CPU増を環境421へ明記し、選択PT・全reactor実測を073へ記録する。短縮率は実測完了前に主張せず、改善後も新機能/PT/部分成果の数は増やさない。

選択実行はJDK25.0.4/Maven3.9.12/PG18.6の既定offline引数と`-Dtest=ResourceScopeTest,MaintenanceRunRetirementTest`、test/JaCoCo report/SpotBugs check。既存16＋Storage8の24PTを再実行する。全38scope、48負canary、全6Java coverage100%の正式source固定再実行後のみ方式変更を認定する。資源逼迫や非決定性が発生すれば本案を中断し、従来逐次方式を維持する。
