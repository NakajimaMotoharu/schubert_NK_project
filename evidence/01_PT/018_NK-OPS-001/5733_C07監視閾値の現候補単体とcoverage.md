# C07 監視閾値の現候補単体

NK-OPS-001、WBS-C07、UI252／SS351、PT-OPS-THRESH-001～015。元15の期待は独立の監視閾値、継続秒数、null・NaN・負値・Long境界と故障値。キュー70/90%は Long.MAX_VALUE に比率を掛け切り上げ、その直前を含む各2値。PG40638元JARから警報閾値の製品methodに4箇所の差があり、PG40798-v2の変更後compile物理の一時保全が残らず、PG42598の現物理確認は選択014の一件。現Batch JARの適用クラスで同15件を一度検証した。

PG42888、2026-11-23 JST、Core e8368d22c4、JDK25／JaCoCo0.8.15。v1は既許可ObservationContextを物理目録に含める前に停止し、JUnit実行0。v2は通常15成功、F/E/S0、AlertThresholdsの行72、method25、class1、branch110、命令438で全missed0。Crc c7e8ebe7687f7b0f、162/162 probe。単一exec・同世代のJARとSDK。実alert送信、実ファイル／broker、全C07、全451は別の受入条件。[PG42888 manifest](evidence/PG42888-c07-alert-thresholds-current-v2/manifest.json)
