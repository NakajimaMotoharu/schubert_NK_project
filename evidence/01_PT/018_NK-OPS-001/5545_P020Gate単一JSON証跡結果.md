# PG40996／PG40998 比較ゲート証跡の文書終端

合成テストのみ。修正前は新PT-CHR-SYN007一件が拒否期待を満たさず終了1。修正 `3f9fd515747e00268a03f82939c1497cbdbdeed8` 後は元210＋新1が211/211、失敗・エラー・skip・未実行各0。生指標はGateContractValidator当型 L498/M57/C1/B261/I2644に未到達なし。ツール全体はGateCliの実FileStoreを通らないため未到達L2/M1/B1/I12。元FileStore付き211は別sourceで保持。

Checkstyle、formatter、SpotBugs指摘0。PMDは元終了4、生1（局所Mapのみ、適用外根拠を記録）、抑制変更なし。製品PT、実CHR、正式加算0。

[修正前](evidence/PG40996-p020-gate-single-json-doc-red-v1/manifest.json) [修正後](evidence/PG40998-p020-gate-single-json-doc-green-v1/manifest.json) [静的適用判断](evidence/PG41000-p020-single-json-reader-static-v1/disposition.json)。
