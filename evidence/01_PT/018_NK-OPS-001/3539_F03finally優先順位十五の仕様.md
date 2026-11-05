# F03 finally優先順位十五のsourceレビュー仕様

NK-OPS-001/F03、Main28af、903の原.25/.75/2pp cap3 ordinary。RD DAT009/OPS009/MQ004005008、UI212231251、SS332/343 JDBC契約・SS321 SSC332 Web fatal契約を各既存Main traceへ結合する。

PT-OPS-FIN15-001: BackupStep/CleanupStep/ExpiryAudit/InspectionSummary/RunReference/SchemaHistory/ServiceDatabaseの七method計14finally観測。cleanup失敗時にだけhelper.replaceで既知SQL/未知Runtime/Error/primary無しを分け、同一unknown主障害と固定secondaryを保つ。直接closeは各scope一度、ResultSet→Statement、borrowed Connectionは非所有。単純なfinally throwの禁止を一括除外せず、全行の条件付きthrowと所定の異常伝播を確認する。
PT-OPS-FIN15-002: Web ArtemisReplyConsumers.deliveryFailureのfinally1件。選択済同一Errorを通知failureより優先して再throwし、API halt/notifyとの相違を保つ。診断graph/実rollback/Root等の動的未証明は維持する。
PT-OPS-FIN15-003: 元1491の先行431+今回15+未分類1045を独立post再構成し、全raw/ordinal/ID/hash/context/canonical設計原文とunique1439/duplicate52組を照合する。既PG19860/19870/19880の成功を新PTへ換算しない。028各理由と動的後条件を期待値根拠とし、production methodでexpectedを算出しない。

実行: env PYTHONPATH=tools/quality python3 -B evidence/01_PT/018_NK-OPS-001/input/023_owned_f03_source_context_metadata.py run evidence/01_PT/018_NK-OPS-001/input/028_f03_finally_priority_decisions.json、続いて同post。未使用PG19890、Python metadataのみ。全Main/POM/normal19740/SB19742/JAR不変を読取確認。Product/fixture/JDBC/close/通知/rollback/Root/VM/PT/analyzer実行0、coverage未測定/全F03・451未受入/正式1964-53/技術46/新leaf0/工数null。結果3540/manifestへ環境・日時・HEAD・hash・終了を追跡する。
