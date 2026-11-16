# WBS66 P004-03 参照DAO純JDBC単体仕様

Program NK-DAT-001 / WBS-P004-03 / SS332、SS331§3.12、DAT009/OPS009/UI251。
Production Core e4794ddf45487268883334d0f8773d89bd47dcba。実DB依存の元8件はHOLDのまま変更/実行しない。
新たな独立unitはRunReferenceRepositoryへのConnection/PreparedStatement/ResultSetのメモリ内Proxyのみ。Driver/DB起動・接続・service/Root/VM/鍵/intent/permit/native/四保留型classfileを使用しない。SQLを実行するDBは存在せず、文字列とbind値/順序を独立literalで照合する。

RRF-PURE-001: SQL全文literal、timeout5、UUID・OffsetDateTime UTC、先グレゴリオ暦/1年/9999年とmicrosecond、正常結果の四BooleanとborrowedConnection非変更、row→statement各一回close。
RRF-PURE-002: 16投影のうち全false以外15正常、四flag/anyReference/redactionを独立boolean演算で照合。全falseはSQL整合性障害。
RRF-PURE-003: constructor/read null、autoCommit/readOnly/isolation、開始/終端interrupt、flag保持、close後条件。
RRF-PURE-004: statement/row/column null、0row/2row、全false、SQLDataExceptionのredacted repository failure化。
RRF-PURE-005: 各JDBC呼出位置（bind2、column4、next2を個別）SQL例外、資源獲得/解放counts、borrowedConnection不変。
RRF-PURE-006: 同位置RuntimeException/Error、primaryとclose secondaryのSQL/Runtime/Error precedence、戻る例外のidentity・redacted suppressed、row/statement両close。
RRF-PURE-007: SQLExceptionのcause/suppressed/next内Errorの伝播、直接SQL failureのmessage/cause/suppressedにprovider診断を残さない。
RRF-PURE-008: 独立fixtureの並行呼出、共有borrowed connectionを捏造しない。有限Futureとfinally shutdown、失敗を握り潰さない。

期待値はSS332から記述したSQL文字列・独立入力とboolean/時刻literal・例外identity・fixture側資源counter。Production methodでexpectedを生成しない。新規fixtureは未実装→初回検証をTDDとして扱う。実装済みproduction違反なら修正前915/916起票。source/static/command/exit/XML/CRC/raw四counterは同凍結sourceで記録。shared utility全scope及び実DB lock/visibility、DurableRecordFiles/MaintenanceRunFiles、F02/F03の終了依存をこのunitで成立させない。元P004-03の正式受入加算は全5artifact・個別4判定・終了依存が成立後だけ。

見積は追加発見の独立純JDBC qualificationとして低.4/標準1.2/高3.6pp、cap4。元P004-03/2の.423ppは固定・未完のまま。新追加1.2と消化は別記し、元計画消化と混同しない。
