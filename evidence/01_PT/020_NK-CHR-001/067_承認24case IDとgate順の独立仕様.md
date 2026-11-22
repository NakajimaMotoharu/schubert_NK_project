# 承認24case IDとgate順

NK-CHR-001、WBS-P020-01.02/2、UI264、SS355 §5/§8、BUG-3639。期待の独立出典はSS355の八Groupに記載するID。Current 23＋N01のNK_ONLY定義、NK 24、承認差分16、実原本hashは既契約を使う。

| Test ID | 合成入力 | 期待 |
|---|---|---|
| PT-CHR-DEF083 | 通常の24 catalogからS03を外し、同じ欄へ範囲外のS99を記載。両artifactの固定fixtureは元のまま | 比較FAIL、CATALOG_CASE_IDS、Current/NKで本来の証拠範囲と食い違う |
| PT-CHR-DEF084 | gate contractのA03を同GroupのA99へ置換。件数24、重複0を維持 | CONTRACT_CASE_ORDER |
| PT-CHR-DEF085 | gate contractの正規先頭二IDを交換。同じ24 IDを維持 | CONTRACT_CASE_ORDER。元の配列は成功 |

既存の局所218件を許可済み20 suiteと同一の選択方式で維持する。合成一時領域のみ。実CHR、FileStore所有、既baseline再取得は対象外。
