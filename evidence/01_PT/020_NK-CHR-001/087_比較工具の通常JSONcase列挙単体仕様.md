# 比較工具の通常JSON case列挙 単体テスト仕様

NK-CHR-001、SS355 §4、WBS-P020-01.01/2-b、BUG-3769、YKT-2945。対象は `GateCli.caseIds`。Test ID PT-CHR-CASEFILE001。通常のJSON成果物 `CHR-L01.json` と `CHR-A03.json`、同じ名義パターンのディレクトリ `CHR-A04.json`、対象外の `notes.txt` を、JUnit所有の一時ディレクトリへ用意する。固定期待値は順序付き `CHR-A03`、`CHR-L01` の2つ。実Current baseline・実運用ケース・実比較CLIや公開処理を使わない。元版・修正版の対象バイト、独立期待値、JUnit終端を分け、失敗を合格へ計上しない。
