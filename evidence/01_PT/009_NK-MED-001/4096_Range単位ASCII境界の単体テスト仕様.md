# NK-MED-001 Range単位ASCII境界の単体テスト仕様

対象は HttpByteRangeParser.parseFirst、FUN-005～007、UI223/237、SS333 §10.1、WBS-P009-04/2、BUG-3470。単位名はSS333の `bytes=` と、ASCII tokenを定義するRFC 9110 §5.6.2／§14.1を根拠とする。 [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html#section-14.1)

| Test ID | 全長と入力 | 独立期待値 |
| --- | --- | --- |
| PT-MED-RANGE-UNIT-001 | 3、`byte\\u017F=0-0` | U+017FはASCII tokenの字句外。Unsatisfiable |
| PT-MED-RANGE-UNIT-002 | 3、`bYtEs=1-2,0-0` | 最初の閉区間1～2のみ採用。2 − 1 ＋ 1 で長さ2 |

JDK 25.0.4、JUnit Platform 1.13.4、JaCoCo 0.8.15を使用する。実行はリポジトリ直下で `python3 evidence/01_PT/018_NK-OPS-001/input/5619_range_unit_ascii.py red` または `green`。前者は修正前sourceの2件。後者は修正後sourceでこの2件と既存parser試験6件を同じrunで計測する。既存6件が正常、境界、異常、例外、null、並行を担う。再送は状態を持たないこの純粋選択メソッドの試験対象外。実環境を使わず、製品が計算した結果を期待値生成に流用しない。実行条件、source、終了内訳、原本hashとcoverageは結果文書に記録する。
