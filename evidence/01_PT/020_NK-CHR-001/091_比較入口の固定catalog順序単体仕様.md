# 比較入口の固定catalog順序単体仕様

NK-CHR-001、WBS-P020-01.02/2、RD TST-001/TST-004、UI264、SS355 §5・§10。PT-CHR-CATALOG-ORDER001。BUG-3806、YKT-2964。対象 `ArtifactComparator.compare` とG01の同一順序の定義。用意するのは既存の合成24組、承認済み公開定義および自所有一時ディレクトリ。

| 操作 | 独立期待 |
|---|---|
| 規定の公開catalogをコピーし、合成Current/NKを比較 | 成功。元fixtureのDIFと比較結果を使用。 |
| 同コピーのA01とA02だけを入れ替え、全24組を比較 | 失敗。個別診断は `CATALOG_CASE_ORDER` 一件。期待件数と比較件数は各24、差分の未登録件数は0。 |
| 既存G01で正規定義、順序違反を照合 | 正規定義に失敗なし。順序違反は既存 `CONTRACT_CASE_ORDER`。 |

公開原定義・Current baselineは変更しない。実キャプチャ、実ブラウザ、認証やサービスには接続しない。
