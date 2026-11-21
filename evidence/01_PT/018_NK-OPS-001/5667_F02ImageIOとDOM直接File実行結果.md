# 5667 F02 ImageIOとDOMの直接File引数検査結果

WBS-F02-b。BUG-3487／YKT-2780。前提と期待値は5666。PG41378の修正前検査では直接Fileの既知違反6件の検出が欠けた。変更467c1db702はImageIO.read/writeとDocumentBuilder.parseのFile引数だけを追加し、InputStreamと別ownerを区別した。

PG41380は新規合成10件・既存合成43件を検査し、期待した29検出と非該当ケースが一致した。監査の違反あり終了1はfixtureの期待値で、検証wrapper終了0。実ファイル操作や製品PT実行は0件。

PG41382は製品Core 007b96d8の現Protocol包装176物理classと他5合成anchorを検査し、6203依存・3953呼出し、5規則の指摘0。Protocol以外の製品包装および六module全体の正式F02は未認定。

- evidence/01_PT/018_NK-OPS-001/evidence/PG41380-f02-image-xml-file-green-v1/manifest.json SHA-256 ba691f8abfca0c34417b196e979e67cbc36f332d5ee951652cfcf1a2ea76155b
- evidence/01_PT/018_NK-OPS-001/evidence/PG41382-f02-current-protocol-image-xml-file-v1/manifest.json SHA-256 8633f3c20aab3695608b44c3d5d2d57ea484cd8eede06f05f931501769419b12
