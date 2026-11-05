# F03 BatchRun全八scope四八のsourceレビュー仕様

NK-OPS-001/F03、Main28af、905の原.5/1.5/4pp cap5 ordinary。RD OPS009/DAT009、UI251、SS331§8.3/SS332:15/25/27/SS341、Main PG163/BAT138..153へ追跡する。

PT-OPS-BR48-001: finish/abandonの各Statementとhistory/insert/replayedの各Statement/ResultSet、全8scopeの元CloseResource8。present aliasと原resource所有、取得直後のtyped try/finally、null失敗と逆順一度close、return前closeを確認する。
PT-OPS-BR48-002: 同8scopeのbody/cleanup RuntimeException/Errorの全32元観測。body primaryを記録して同一再throw、SQL対unknown/固定secondary/sameThrowable非self-suppressionを照合し、広いcatchで正常化しない。
PT-OPS-BR48-003: 全8finallyの条件付きcleanup失敗伝播。JdbcResourceFailuresは例外順位だけ、directcloseはRepositoryが実施し、SQLだけ外側で固定化する。全SQL/lock/CAS/history/replay/borrowed transactionは変更しない。
PT-OPS-BR48-004: 原1491を前446+新48+残997へ独立完全分割し全raw/ordinal/ID/source/context/SS原文hash、unique1439/duplicate52組を照合する。期待値はSS332の明示8scopeと手書き029各理由・未実施動的後条件。旧PG19088全14等は既証拠として保全し、このmetadataで再演/再加算しない。

実行: env PYTHONPATH=tools/quality python3 -B evidence/01_PT/018_NK-OPS-001/input/023_owned_f03_source_context_metadata.py run evidence/01_PT/018_NK-OPS-001/input/029_f03_batch_run_decisions.json、続いて同post。新PG19900/Python metadataのみ。Product/JDBC/close/rollback/Root/VM/PT/analyzer0、normal/Main/POM/JAR不変。coverage未測定・全F03/451未受入・正式1964-53/技術46/新leaf0/工数nullを維持する。結果3542/manifestへ日時/環境/HEAD/hash/終了を記録する。
