# RequestLogDetails現入力境界と静的非生成の単体仕様

NK-MSG-002／NK-OPS-001、WBS-P018-10.03/2、RD MON・TST、UI235／252、SS351 §3.3／10、PG-D-1172、451 §5。BUG-3644／YKT-2863。対象は `RequestLogDetails.normalize` と `<init>` のclassfile契約。Gson 2.14.0、JDK 25.0.4、現Protocolの3型を明示。DB/JMSなどの実呼出とQA056四型はscope外。実文字列は公開合成値。元fixturesのprivate reflectionは履歴を残して現実行から除く。

| Test ID | Fixtureと操作 | 独立期待 |
| --- | --- | --- |
| PT-IDEM-012 既3 | 固定scalar/role、null・欠落・異種JSON、余分な値、UTF-16不整合 | SS351の四key、固定role、固定拒否で比較。元3期待を変更しない。 |
| PT-IDEM-012-JSON-001／002 | 同一decoded key、wire actorRole、符号／小数／指数の固定境界 | literal JSON・数値の既期待で比較。 |
| PT-LOG-RAW002／003 | 固定未知key、公開診断マーカー | 安全な固定メッセージ、cause・suppressedなし。元2期待を変更しない。 |
| PT-LOG-RAW004 | ASCII JSONに文字 `A` のJSON escapeと先行空白、1024 byte。末尾に空白を加え1025 byte。信頼role ADMIN。 | 1024で独立固定JSON、1025で固定PermanentProtocolException、causeなし。バイト数は入力JDK UTF-8、期待JSONはliteral。 |
| PT-LOG-STATIC001 | 現JDK javapで当候補classfileのconstructorsを読む。初期化・呼出なし。 | 引数なし一件だけがACC_PRIVATE。raw coverageへ加算しない。 |

現正規入力8件の終了、同一execの元CRC、四指標と命令を別記。元RAW001の実行と旧カウンターを当scopeに足さない。欠落が残る場合はBUG-3644/YKT-2863と正式判定票へ記録。RequestLogDetailsは直接の入力／出力だけを対象にし、実sink、並行／再送／保持へ適用しない。再現command／対象source／入力物理hash／JUnit／raw証拠は実行結果のmanifestを参照する。
