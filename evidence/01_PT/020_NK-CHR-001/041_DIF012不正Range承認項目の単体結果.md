# DIF-012 不正Rangeの承認項目の比較単体結果

NK-CHR-001／P020-01.02/2、2026-11-19 JST、dev-foundation、工具source `fb7318d2933be50e899db7fd30a23614e3aeddd0`。M04とM07の各statusは整数416、Content-Rangeは元Currentの保持総長の形式と項目名に限定した。元161とPT-CHR-DEF034～037の全165件／20 suitesを両候補で各一回実行し成功。F/E/skip/未実行0。初候補のPMD生8中の適用2を保持し、fixtureの文字列だけを是正した。現PMD生6全非該当、Checkstyle・整形0、同一17物理のSpotBugs 0を同byteで参照。

PG39970の独立XML／単一exec／CRCで、Comparator二物理の未除外 L272/M44/C2/B136/I1440未到達0、工具全体のBUG-3311生不足は維持。元Current27と他の項目を保持。実NK、実media、実HTTPおよび全451は未実施・未受入。

BUG-3318/3319局所完了、YKT-2699継続。PGPT-20261008-6064。コマンド・環境・元／現の終了・XML・execの証拠 `evidence/01_PT/018_NK-OPS-001/evidence/PG39970-p020-invalid-range-independent-v1/manifest.json`、SHA256 `6f55d07f90b0fda668c7dc607258cf4c5223eee68ab48c9b33fa24dd66df7a12`。
