# 075 NK-WEB-002 受付参照単体テスト仕様書

PG447/PG-D357、QA048/SSC169/175。RD FUN001/AUT004/DAT009/OPS009、UI226/236/241/242/251、SS313/331§9.4/332/341/343。製造と独立PTを同変更群で進め、未実行は合格にしない。

| Test ID | Program/class/method | 独立期待値・fixture・操作 |
|---|---|---|
| RCPT001 | ReceiptReference constructor | literal26文字Crockford ID・N12境界1/999999999999・UTC millisecond。null/未知文字/長さ25,27/0/上限+1/submillisecondを拒否、秘密toStringなし |
| RCPT002 | ReceiptReferenceRepository register/find | 独立literal3値→実Web role短TX insert/select。新登録/同値冪等、異値は元3値不変/非成功、missing Optional.empty、commit後fresh row確認 |
| RCPT003 | V026 DDL/grant | catalog列3/PK/index/NN/check、web SELECT/INSERT/DELETEのみ、UPDATE/業務SELECT拒否、backup SELECT、app/batch直接DML拒否、PUBLIC function EXECUTE拒否・batch固定signatureだけ |
| RCPT004 | maintenance_cleanup_web_receipt_references/atomic shared step | 実PG隔離fixtureの物理質問不存在だけ削除、存在/論理削除保持、当日両backup/run/advisory/cutoff/完全handle、limit1..1000/null/∞/unknown、locked eligibleはLOCK_BUSY非完了、DELETEとcount同TXrollback/commit、累積旧3kind保全 |
| RCPT005 | register/find fault/concurrency | JDBC境界/SQL/row-null/unknown/runtime/commit/close故障、100同値/競合並行、外部API/JMS中DBTX保持0。expectedはliteralSQL/件数でProduction呼出しから生成しない |
| RCPT006 | SCR019 fresh IF030/POST保持token | 正規API結果ごとowner/id/receipt/timeを照合、missing/mismatch/削除/他人/API未知error、HTML escape、stored snapshot/session fallback0、同token再操作から同確定結果を補完、新質問重複0 |

RCPT006独立HTTP細分：A=GET新form/最大10/全pending拒否、B=POST4400byte（question256..4351/token4352..4387/reserved12）と真正reply320byte（receipt256/26、id282/12、JST294/17、reserved9）のliteral oracle、C=0000/0200/応答喪失と同token再操作・DB保存gap補完・first-write、D=退役/用途不一致/不在/失効409・API0/新UUID0、E=accepted毎GETfresh MessageID/locatorTX0・現在owner/id/receipt/UTC時刻・削除/missing/API失効、F=HTML escape/200codepoint/JST/3固定link/no更新GET/no session body、G=null/未知/SQL・commit-close非成功/CSRF・readonly未配線拒否、H=100並行same receipt immutable/同token/全owned資源0。入力/expectedはUI236 byte offsetとliteral DB後条件から作り、production methodでexpectedを生成しない。既存Current baseline不変更。実装前計画であり、未実行を合格へ加算しない。

環境は隔離PostgreSQL18/JDK25.0.4/Maven3.9.12。実行command/source/run/終了code/XML/4counter/静的/BUG/YKTとsafe manifest/hashは076へ記録。DBC条件は独立SQL/canonical設計に基づき、DDLだけではnative Backup/restore受入としない。JDBC負試験/null契約、API proof接続とnative全Webは段階的に追加し、100%未達/未実行scopeを明示する。
