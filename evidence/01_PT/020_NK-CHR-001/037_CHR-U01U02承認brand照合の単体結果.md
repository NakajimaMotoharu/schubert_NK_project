# CHR-U01/U02 承認済みブランド項目の比較単体結果

NK-CHR-001／P020-01.02/2、2026-11-19 JST、dev-foundation、工具source `9c4580bb6cb6ef61e3e0075afb623a878493703b`。DIF-001のA01とU01/U02の承認済み四観測を固定し、他四titleや未登録差分を維持した。元148＋PT-CHR-DEF021～025の全153件・20 suitesがPG39922と是正後PG39923でそれぞれ成功。各失敗・error・skip・未実行0。元候補のSpotBugs指摘1を保持し、二つの診断を保持した短絡判定へ是正した。PG39927は17物理のSpotBugs 0、CS・整形0、PMD生6を全個別照合して適用・未分類0。

PG39928は正本UI264と元Currentの /brand、/titles/0・1、不変の四titleを固定値と比較した。単一session/CRCでComparator二物理の無除外 L243/M42/C2/B124/I1312の未到達0。工具全体の既BUG-3311の生不足 L2/M1/B1/I12と他DIFの横展開、実NKと451は未受入。異なる二sourceのcoverageやPTは合算しない。

BUG-3315/3316局所完了、YKT-2699全体OPEN。PGPT-20261008-6058。実行コマンド・元と現の終了、XML/exec、OS/JDKは結果manifestを参照する。証拠 `evidence/01_PT/018_NK-OPS-001/evidence/PG39928-p020-approved-all-brand-independent-v1/manifest.json`、SHA256 `1456cb3979e2db104ac52a897ad35f8890566f268cbe3d55d6fa411b8575870c`。
