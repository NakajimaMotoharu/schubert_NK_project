# 基盤規約・解析gate個別照合仕様（個別未受入）

2026-10-15、PG3378、WBS-F01/F03、Production a9/PG2802。正本origin/main756a891d9はfetch後も同一。SS311 SSC084/088/126/142の六Production artifact（protocol/storage/bootstrap/api/web/batch）と、別program/characterization試験moduleを区別する。Root reactorは七子moduleだがProduction六、Characterizationを混在/欠落させた六という意味ではない。F01/F03のownedArtifactsは空であり、文書・gate契約の非実行scope。Java coverage除外や全Java100%認定ではない。

## F01：規約の確定・全scope

411の§1～14を全文照合した。Java25/preview禁止、package/class/method/constant名、module方向、nullとconstructor invariant、例外/transaction/lock、logging/redaction/security/CSRF/owner、SQL/DDL/JDBC型、NFC/固定長byte/padding、並行/JMS/file、testability/独立oracle、format/static、禁止事項、reviewの実施規則を含む。正常/異常/null/再送・競合・資源所有・秘密/traceへ責務を割当て、RD/UI/SSをcode都合で変えない優先順位を維持する。

BUG1297先行03f61c686。411/431の現在module表が旧五個だったため、既承認Bootstrap・Storage consumer・API/Web/Root Batch参照の限定境界を同期した。compatibility package名をartifact依存と取り違えず、実親/各POMの内部依存集合と照合する。411§10の純粋単体の外部依存禁止と、SS354/利用者が承認した隔離DB/JMS/Linux/native/専用LAN HTTP component PTを区別した。秘密や利用者本番data依存の一般解禁、IT/ST合格への読み替え、期待値/品質条件緩和は行わない。

YKT1063の対象は411/401/421/431/441/451/README＋SS311/354＋実七POM。401のSSC084・431の現在Module表・421の実六moduleコマンド/導入履歴・441の個別判断・451のproduction全scope方針・READMEの設計正本branchを照合する。2026-09の五module旧成功runは履歴として不変更、現在表だけを修正する。主担当Program母数20/941artifact/190WBSを変更しない。文書UTF8/LF/末尾改行/必須全topic・六catalog・依存graph・source/POM hashをPT-QUALITY-FOUNDATION001で確認し、実code遵守/全品質認定とは分離する。

## F03：実装済みgateと未確定を区別

| 観点 | 現在の証拠 | 判定の限界 |
|---|---|---|
| NullAway/JSpecify/Error Prone | 001/114・PG3360正compile0/負compile1/独立四診断、POM/fixture全四hashがcurrent/a9一致。新wholeの全Production六compileも必要 | 未注釈外部APIの安全を静的だけで保証せず、DB/null/欠落/未知negativeを各ownerで維持 |
| Lint/Werror・Enforcer | 全Productionの親継承25/[3.9.12,4)/dependencyConvergence/UTF8・locale/timezone、全六実compileとsource/POM byteを照合 | 非production Characterizationやshell/SQL/JSの全gateへ加点しない |
| Spotless/生成一致 | 001/115・実pinned long文字列default反例/skip正常、70生成byte一致/変造一件拒否/全protected不変、全六実spotless:check | 機能oracleは独立UI vectorであり同一生成器比較だけではない |
| SpotBugs | 既全3350/3352/3354・新3372/3374/3376のMax/Low全六指摘0を実証後に接続 | 新全体は現在稼働中、途中を合格0 |
| PMD/Checkstyle | 現POMで実行設定なし。411/451の記載に対する採用/同等性・責務の技術判断は未確定として保全 | 未導入/未実行を違反0/PASSにしない。明示採用範囲の確定と必要な実検証前にF03をACCEPTEDにしない |

F01は規約の確定という文書scope、F03は規定gateの実稼働scopeであり、一方を他方の完了へ自動伝播させない。両対象の三criteria/独立証拠/終了依存をhash reviewとstrict auditで個別判定する。本文は仕様/照合であり、まだ受入更新なし。正式1964/53・個別15/190・工数null・QA051final保留・原/v3予測を維持する。
