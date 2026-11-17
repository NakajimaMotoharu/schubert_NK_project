# ReceiptReference 単体テスト仕様

WBS-P011-04／P018-10.03（CATALOG-040）／F03、QA048、SS331 §9.4とSS351、RCPT001-BOUNDARY／NEGATIVE／VALUE、BUG-3216・YKT-2431。

- 境界はSS331のASCII 26文字、question IDの1と999999999999、独立固定UTC millisecond値の3項目を照合。
- 負値はnull、空、短長、除外文字、非ASCII、question IDの上下、1ns端数。外部データを含まない固定エラー理由を期待。
- 同値は別由来の同時刻と同じ構成を用い、変更した三field各1例を別要素にする。固定の秘匿診断を直接照合。

全3試験は純合成値。実Web、DB、鍵、HTTP、権限、元repository/controller試験は参照対象。Main変更なし。JDK、実行ID、同一sourceと単一exec、CRCと全物理CodeはPG38244以降。
