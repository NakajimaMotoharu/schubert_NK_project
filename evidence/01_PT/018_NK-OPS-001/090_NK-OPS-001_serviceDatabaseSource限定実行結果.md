# ServiceDatabaseSource限定実行結果

2026-09-27 JST、PG287、NK-OPS-001。089のPT-OPS-DBSOURCE-001～006は全件成功。PG288と同じ選択実行で再確認した（終了16:24:16、exit0）。source SHA-256 `661d7372fa682ae575d1cc738a78f0790ce6cc3a64d1df6c702cc27855ebfe87`。

対象classのJaCoCo: instruction250/250、branch24/24、line65/65、method16/16、class1/1。全module coverageではなく、正式認定・実systemd配布・SCRAM・実NK受入ではない。未知例外のidentity、全物理接続admission、所有password消去、Properties clear、close後の新規接続拒否を独立assertした。既存formal PT-WEB-20260925-24は変更しない。

実行command・環境・hash・成功/未実行範囲は`evidence/provisional/PG288/manifest.json`。失敗した新規testのコンパイル試行は未実行として除外し、合格件数へ加えない。対象moduleの全静的解析と全回帰は未実施。関連SSC082/084、実装障害の新規起票なし。
