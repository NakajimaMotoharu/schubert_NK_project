# Web SQL catalog・REQUEST投影graph PT仕様（PG前）

当結果は1452：同六Testbytesのsource d48a13f4d/元6608/38-13真正0、原6610資格d4fece4a・Receipt四100/REQUEST missL3M1。以下は実装前仕様・初期run計画として保持し、fixture変更とnewonly v2は1449/1450を優先する。

具体化：ReceiptFailureGraph329Test3/SHA7a544f472a5d0f1d28d4a1abe7d28ef00cc33fe005840a4696bb8c6f5eaadc63、RequestProjectionFailureGraph329Test3/SHA15aff325918c7451e2c5c727e0959655c27c1a0a9e42a92d01ada9c0345d002e。Main6855dcf9eと全旧Testbyte不変更、format59419終了0/管理三0/pyflakes0。`pg6600_web_catalog_graph_selected.py red`はnewonly18/9、Web停止時予測16/7/F4/not-run2、各003の既優先/非fatal結果は元で成功を期待。green38/13＝baseline12＋新6＋Receipt既8＋REQUEST既9＋WebStartup pure3、自己所有tempPG/Flywayの既domainは別PT_DEFAULT。原読取6604は全8511667/Jar/XML/counter/rawstatic、元成功・Current・全Test期待値を上書きしない。

群ORDINARY_JDBC_MAPPER329/event1625/開始.5/1.5/4ppを維持、原-v4残予測と混同しない。485実物ではReceiptReferenceRepository主WBS-P011-04、WebRequestLogProducer主WBS-P006-03、共通口P018-06/既費用を二重加算0。関連BUG1592/YKT1345/1348・SS312329330/314/3319.4/332/3513.4/354、QA048。parent実配賦/N/T/工数率null。

## 事前レビュー・適用境界

Receiptの既SQL/unknown優先（RCPT005）は維持する。元unknown primaryは同一instance＋固定ReceiptReferenceException secondary、SQL primary＋unknown closeはunknown closeを優先する。これをAPI primaryError規則でblind置換しない。固定Receipt catalogへ変換する選択SQLと、SQL同士のcleanupで捨てられるsecondarySQL graphだけを今回の適用候補とする。生のunknownを保持する経路まで一律に固定化・unwrapしない。

REQUESTはHTTP応答後terminal監査。通常SQL/RTE投影故障は既local PENDING→FAILED補足を維持し、HTTP status/body/監査event IDを変えない。内包Errorは通常故障の固定local JSONへ縮退させず、全取得済資源close/rollbackの後で同fatalを伝播する。rollbackの既direct Error優先とsameThrowable self-attach0は保持、suppression無効primaryに対する非Error型secondary内包Errorは失わない。

## 独立Test（予定二class・六method）

PT-WEB-RECEIPT-GRAPH329001：getConnection/setAutoCommitのSQL cause/suppressed/next内包Errorは同一fatal、取得前close0/取得後close1・rollback0。

002：read ResultSet/Statement/rollback/Connectionとregister Statement各cleanupのsecondarySQL graphを、SQL primaryと合成して同fatal。独立call counterで取得済scope各一回close/rollback1/commit0、成功を返さない。

003：非fatalSQL cycle/同一Throwableは原因・suppressedなし固定Receipt、unknown primary＋direct secondaryErrorは既unknown同一性＋固定marker、SQL primary＋unknown closeはunknown同一性、direct primaryError＋secondaryErrorは既primary同一性を保つ。これらは旧承認契約の防止oracleで、PG都合で変更しない。

PT-WEB-REQUEST-GRAPH329001：DataSource SQL graphの三edgeは同fatal、local PENDING一件だけ/FAILED追加0。

002：suppression無効Runtime primary＋rollbackSQL内包Error、及びprimary graphとsecondary graph双方にfatalがある場合の既cause優先を確認、rollback1/close1/commit0。既直接rollbackError優先は従来どおり。

003：非fatal循環SQLは既PENDINGと固定FAILED二local行、errorCode/level/HTTP観測を手書き期待値で確認する。

PT_DEFAULT、純Java proxy/公開合成入力/既固定wire・JCE fixture、実DB/VM/Root/current/failed cohort/原本・鍵・permit/外部通信なし。旧TestのBeforeAll DBには依存しない。期待値はSSと元例外identity/明示counter/固定JSON項目から独立に作り、Production methodで算出しない。6Test-only sourceで元反例を原XMLから確認→必要二Main/全Testbyte固定→既Receipt/REQUEST自己所有DB domainを含むgreen→同source原qualification/115site/必要まとめ全体。具体run/count/hashはTest宣言確定後、着手前に固定。正式/QA051final/PTALT代替0/全HOLD/原-v4維持、通常小群停止0。
