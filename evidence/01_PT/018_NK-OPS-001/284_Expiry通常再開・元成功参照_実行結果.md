# 284 Expiry通常再開・元成功参照：限定結果

Source `9ac9455eee98327dc98e8047c6958b118845689b`、dev-foundation。2026-09-30 16:00:14 JST、Java25.0.4/Maven3.9.12/JaCoCo0.8.15/SpotBugs4.10.4.0。仕様283のEREQ005/ESKIP001を含む全6 clean回帰2,560PT/375suite F/E/S0・static6module0、exit0。

固定ASCII golden（NKEXPIRY1/NKEXPIRYSKIP1）と独立SQLfixtureの元SUCCESS/今回SKIPPED別handle、fresh selected0、元audit全列不変、誤cutoff/終端/数量/null等を検証。BUG352 oracle型誤認の初回F1とBUG353静的4警告は不合格履歴として保持し、修正後だけ算入する。BUG351のSource直接原因は修正したが真正Broker/Expiry worker・audit生成/再開受入はNOT-RUN。

全Source未網羅B/L/M/C=359/1243/279/24。Expiry request class=6/1/0/0、CleanupExpiryExecution=50/151/6/0。100%ではない。正式PT-WEB-20260925-24を更新しない。

エビデンス：`evidence/provisional/PG388-cleanup-dependencies/manifest.json` SHA-256 `757a2f32494a28f02e086c14a76803a971278092051c0c28fc2185b4d62139ed`。sanitized JUnitのExpiryWorkerRequestTest/CleanupExpiryExecutionTest/ExpiryAuditRepositoryTest・固定Source/環境/command・全6coverage・BUG/SSCへ一意追跡。raw秘密/電文/token/DB dumpは格納していない。
