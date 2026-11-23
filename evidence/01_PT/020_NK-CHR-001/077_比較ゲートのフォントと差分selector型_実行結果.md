# 比較ゲートのフォントと差分セレクターの型 実行結果

2026-11-23 JST、PT-CHR-DEF-017、BUG-3707、YKT-2909。修正 `89d08b06b11ac52792acb162349db50e39a7a675`、空配列追試 `ce6e89ce9c16fb9e2e9397c90803d15e188880dd`。

修正前の選択1件は6入力すべてで診断が欠けた。修正後の合成定義22件は全成功。フォントの空配列の1分岐が最初の生測定で未到達だったため、既定のフォント不足診断を照合する入力を追加した。再試験の22件は失敗・エラー・skip 0。当4メソッド・85行・56分岐の生積算は、再試験の単一execで全到達。工具全体の未到達は原カウンタに保持。Checkstyle0。製品試験、実CHR、Current baselineと実環境への操作なし。

[実行manifest](evidence/PG43458-chr-font-selector-types-current-v3/manifest.json)
