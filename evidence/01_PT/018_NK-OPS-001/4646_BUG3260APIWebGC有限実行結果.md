# BUG-3260 API・Web GC登録fixtureの有限終了結果

Core `bcc9e0673287c51950ecab9b36350abfcd4b2c69`、固定試験 `e27c0b0be816719370ae9f9ac5305550a51aae2c`。PG39208の全32件は初回全成功、失敗・エラー・skip・未実行は各0。4worker×各64、ack・bind・close各既条件とfinallyの最大10秒を両suiteで確認。元bodyと製品Mainは有限終了部分以外の差0。独立PG39212で10物理／3正CRC、Root静的適用0（PMD生30の理由は5114）。

Web対象生15L/5M/1C/6B/68I全到達。API生18L/5M/1C/97I全到達、branch 14/16。未到達2はinstallのString mode判定箇所。BUG3261/YKT2691に修正前起票した。局所fixtureの終了は完了、API生四・全F03/451は未受入。

Linux amd64/JDK25.0.4/Maven3.9.12、dev-foundation。[PG39214](evidence/PG39214-f03-api-web-gc-finite-independent-v1/manifest.json) SHA-256 `90a0e4d4e17197373ec49023e4bf31567a781db63b8039b3a65fda7697e7e726`。実行command・入力・CRC・XML・単一execと未フィルタ生位置を保存。
