# F03 Log資源五scope二四のsourceレビュー仕様

NK-OPS-001/F03、Main28af、925の原.25/.75/2pp cap3 ordinary。RD OPS009/DAT009/UI251/SS341327・PG178/SSC063/BAT026029へ追跡する。

PT-OPS-LOGRS24-001: LogCleanupService.ownedのSessionLease release1とacquire/closeのStatement/ResultSet4、計五所有scope。body Runtime/Errorの記録と同一再throw、cleanupのknown(SQL/Batch/CleanupStopped)対unknown、固定secondary/同Throwable/no selfsuppression、直接一回/逆順closeと未取得解放無しを照合する。GC20/finally4の元行を区別する。
PT-OPS-LOGRS24-002: 現SS341327の明示範囲を越さず、借用Connection破棄/実lock/実DB・transaction rollback/autoCommit復元をこのproofから推定しない。transactionの元431は未分類のまま。constructor/API nullとnullable結果/既停止reason・割込を混同しない。
PT-OPS-LOGRS24-003: 前958+新24+残509=元1491を独立完全partition、raw/ordinal/ID/SourceSHA/SS原文・unique1439/duplicate52/Morning12/431保留を照合する。ExpectedはSS341327と手書き040の個別理由、production methodを呼ばない。

実行: env PYTHONPATH=tools/quality python3 -B evidence/01_PT/018_NK-OPS-001/input/023_owned_f03_source_context_metadata.py run evidence/01_PT/018_NK-OPS-001/input/040_f03_log_resource_decisions.json、続いて同post。新PG20000/Pythonmetadataのみ。全Main/POM/normal19740-SB19742/JAR不変。Product/fixture/JDBC/lock/SQL/Root/VM/PT/analyzer0、coverage未測定/全F03・451未受入/正式1964-53/技術46/新leaf0/工数null。3562/manifestへ実時/環境/HEAD/hash/終了を結合する。
