# JDBC役割metadata小共通化 仕様

2026-10-31 / PG-D985 / WBS-G03.05 / 着手0.5/1.5/3共有pp cap10、開始used52/reset1793774153。BUG2155/56再発予防の内部工具整備として別費用分類し、元群/原見積りを変更しない。先行index G03.05=0、既工具名のgeneric候補もなし。

複製しない最小範囲は(1) JdbcResourceFailures.replaceのprimary/cleanup引数と同一throw symbol、(2) var alias=present(resource)の宣言/同resourceだけ。公開文字列を受け不変tuple/alias名を返す純Python部品とし、file/exec/network/Java class load/Production method/Test選択/資格・HOLD判断/expected生成を含めない。callerが固定source/hash/PMD座標/型集合/全scope・個別設計根拠を別に照合しなければ用途判断にも使用しない。

対象文法は明示三primary名(statementFailure/rowFailure/rowsFailure)、ASCII Java identifierのcleanup、同一identifierへのthrow、resource statement/rows、literal present呼出。完全Java parserや型解析ではない。空sourceは候補0、未知文形を推測修復しない。sourceはstr/最大1048576文字・通常LF・NUL/CR/未解決Unicode escapeなし、aliasは一行/最大8192文字/明示resource。null/bytes/不正形は固定ValueErrorで拒否し入力本文を診断へ埋めない。範囲外の構文は新しいreview/版が必要。

Q-JDBCROLE001～008（qualifierの八method）で、三primary・cleanup名変更・同arg/throw・position・不変性、差替え/helper違い/逆順/condition欠落/曖昧source/null/型/長さ/alias引数・未知resource等の純metadataを正負検査する。既BatchRun/CleanupTerminalの全16siteは固定旧review/hashから期待role/lineを読み、当Sourceのmetadata候補へ結合するだけで、元PT/旧工具を再実行しない。旧成功をProduction runtime資格へ転用しない。

libraryはtools/quality/jdbc_role_metadata_v1.py、qualifierはPG16068。新発見PG/tool是正として記録し、Source/Test/台帳上位/registry2125/四256/374/正式1964-53/工数null/全HOLDは不変更。Python有限metadata検査をJava四counterやProduct PTへ加算しない。既実行16004/06/58/60/61/62のbyteは変更せず、次の独立reviewから適用する。
