# SSC-461 Batch二JDBC境界の実行結果

Core 15ecf4bd1daa3da62a9f62ea288f51846c6cb6b6、Unit source dcea88287dde71a677ce9b68d97fdcb939d884d0。3箇所の呼出移管、元試験本文21は同一。実PG38614は21/21、真正0、F/E/skip/選定内未実行0。独立PG38616は7物理、6CRC実行、package-infoは自然NoCode。PG38620の未フィルタで変更2型・Bootstrap adapterと他純値は全到達。旧Storage一引数入口と旧SQL lambdaのみ2行・1method・1分岐・10命令未到達。全scope合格欄はfalseを維持した。

PG38604/06 strict NullAway、Checkstyle／GJF／SpotBugs0、PMD生1は旧enum所有を証明するcaller-owned配列null。型付きJDBC診断以外のSQL/close/identity/ロックは差分なし。5/104上位位置を移管、BUG3233／YKT2680未完。証跡 evidence/01_PT/018_NK-OPS-001/evidence/PG38620-f02-batch-jdbc-graph-two-owners-independent-v1/manifest.json SHA256 2a9e952e003cd71e70149257fdbb8b79667f520c72219e1047cb2da6022cd230。
