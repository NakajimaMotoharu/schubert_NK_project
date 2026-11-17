# BackupManifestCodec 単体実行結果

NK-BAT-001、WBS-P017-05/F03。Core/Unit `47aeed19a157661363ffab5c4b5054f6b20230a1`、PG38226/38228。元PT-BAT-186～193のwhole16と新NAMESPACE 1の全17成功、失敗・エラー・skip・未実行0。対象codecは全7 Code、line 79、method 7、class 1、branch 12、instruction 393を同じ実行のrawで網羅。全7物理CRC、独立元golden 965 byte、後始末、試験中の保留型非初期化を確認。

PG38222はMain7とTestの数値終了0。PG38224 v2でCheckstyle、format、SpotBugs Max/Lowはいずれも終了0、PMDの12 siteは個別適用性判定で未分類・適用0。公開及びprivateのjavap宣言は同一、共有6物理byte同一。元compile runnerの後段不良と静的・判定レコード名の二種類の前処理不良はBUG-3214、compile／製品PT再実行なし。実Backup、配置、DB、鍵、native、全451は継続。

[PG38228 独立証跡](../018_NK-OPS-001/evidence/PG38228-backup-manifest17-independent-v1/manifest.json) SHA-256 `6b01141de2d64078a30492a635d088b0933521722737572638e8317762748a22`。
