# DIF-012 不正Rangeの承認項目の比較単体仕様

NK-CHR-001、ArtifactComparator.compare、WBS-P020-01.02/2、BUG-3318、YKT-2699、PER-004/TST-002、UI237/264、SS333/355。元CurrentのCHR-M04とCHR-M07の固定総長を独立に使い、両不正RangeのHTTP整数500→416とContent-Rangeの元観測→総長付き形式を一件ずつ比較する。statusとContent-Rangeのselectorは各位置と一致する必要がある。隣接する比較やCurrent baselineは維持する。

| Test ID | 合成入力と操作 | 独立期待 |
|---|---|---|
| PT-CHR-DEF034 | M04観測を維持しM07のstatus観測だけを取り除く | 別caseによるDIF使用で充足せず、M07 statusは未登録差分 |
| PT-CHR-DEF035 | M04のContent-Range総長を固定総長と違う値とする | 値の不一致を検出し未登録差分 |
| PT-CHR-DEF036 | statusのJSON PointerにContent-Range selectorを記録 | 同じDIF内でも別の項目名は拒否し、statusは未登録差分 |
| PT-CHR-DEF037 | M07のNK statusとして404を保存 | 416以外を許容せず未登録差分 |

元161＋新4の同source全165。仮のHTTPサービスや実mediaを開かず、自己所有TempDirに明示JSONのみを作成する。正常、必須欠落、不正値、型、selectorを比較し、実経路の性能、並行、再送、nativeは範囲外。実行command、環境、終了、coverageの証拠は対の結果へ置く。
