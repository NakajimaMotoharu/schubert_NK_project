# CHR-U01/U02 承認済みブランド項目の比較単体仕様

NK-CHR-001、ArtifactComparator.compare/checkBrand、WBS-P020-01.02/2、BUG-3315、YKT-2699。RD SYS-001、UI264 §5、SS355 §8、元CurrentのCHR-U01/U02を独立期待根拠とする。メニューのブランド文字と共通style観測順のメニュー・検索titleにだけ承認済みブランド変更を適用する。元の検索以外の四titleと比較順、A01を維持する。

| Test ID | 合成fixture | 独立期待 |
|---|---|---|
| PT-CHR-DEF021 | U02の検索titleがCurrentと同一で、検索titleの観測が欠落。 | 生差分漏れが0でも必須の承認観測不足で不合格。 |
| PT-CHR-DEF022 | U01のブランドは変更されているが、U01の観測が欠落。他caseのDIF-001は保持。 | U01のブランドは未登録差分。別caseの使用で免除しない。 |
| PT-CHR-DEF023 | U02の検索titleは変更されているが、その観測が欠落。 | 検索titleは未登録差分。メニューtitleだけの観測では不足。 |
| PT-CHR-DEF024 | U02の検索title観測のJSON Pointerが別titleの位置になっている。 | 不合格。観測対象の承認位置不一致と検索titleの未登録差分。 |
| PT-CHR-DEF025 | U02の承認二titleを維持して、三番目のtitleに異なる合成値を入れる。 | 変更された一件が未登録差分。既存の二観測は有効。 |

全Current/NK合成24事例の正fixtureに、実構造の /brand と /titles/0、/titles/1、独立の固定語形を設定する。基準Currentを読み直しても書き換えない。元工具148件・新5件、実行品fixture/Browser/DB/ネットワーク負荷なし。欠落、不正pointer、順序の独立実測、追加の適用条件は同一sourceの結果へ記録する。
