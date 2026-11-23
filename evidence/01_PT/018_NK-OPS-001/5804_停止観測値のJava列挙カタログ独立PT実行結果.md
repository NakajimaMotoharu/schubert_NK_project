# 停止観測値のJava列挙カタログ独立PT実行結果

PG43410、2026-11-23 JST。試験source `6069bfbf6ed2ebdc3e740abcfa40cd8a638a2892`、製品Core `87927ea17c1c8dbef528bc0c6882c24b1fe7c871`。MSTOP001～007とMCATALOG001/002の9件が成功し、失敗・エラー・skippedは各0。元7件の試験本文はbyte不変。定義追加は2件。

Java 25.0.4でfixtureのcompile／JUnitの終了0、Google Java FormatおよびCheckstyleの現再確認も終了0。Javaの固定Unit名から正規サービス名への対応、固定理由名・異なる表記の拒否、呼出側配列変更後の取得と固定診断を独立値で確認した。

現Batchに一致する4クラスで生L83/M26/C4/B56/I596、miss各0。単一exec、独立CRC・129 probe照合。実Unit、Root、資格・配置、実停止、親P018-04、全451は未受入。BUG-3703の元書式終了1と是正結果を保持。

仕様 [5803](5803_停止観測値のJava列挙カタログ独立PT仕様書.md)・[manifest](evidence/PG43410-mstop-catalog-current-nine-v2/manifest.json)（SHA256 8495fab3d2efb3ca9c2034e624a646de6b284ebb5d7e9cb4b2c61d4af267c2d4）。

BUG-3704の現再試験PG43416。既存の手書き完全サービス名を同じ負入力に使い、製品期待は同じ。追加PMD一件を解消し、旧九生siteを記録。現JUnit9全成功、四物理の生L83/M26/C4/B56は全到達。証拠 evidence/01_PT/018_NK-OPS-001/evidence/PG43416-mstop-catalog-oracle-style-nine-v1/manifest.json（SHA256 13957ad8d054dd44acde828cd8d770780d536689a703af5f70edddf3b64c2c2f）。
